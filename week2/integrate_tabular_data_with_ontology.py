import csv
import json
from pathlib import Path
from datetime import datetime
import re

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD, BNode, URIRef
from rdflib.collection import Collection

# -------------------------
# Config
# -------------------------
BASE_URI = "http://ontology.daniel-motz.de/ontology#"
ONTOLOGY_FILE = "../week1/ontology.xml"
DATA_CSV = "data.csv"
ING_JSONL = "ingredients.jsonl"
CITY_QID_MAP = "city_qid_map.json"
ING_QID_MAP = "ingredient_qid_map.json"
CLUSTER_JSON = "cluster_labels.json"   # <--- NEW
OUTPUT_TTL = "pizza_data.ttl"
FUZZY_SCORE_THRESHOLD = 85

# -------------------------
# Namespaces
# -------------------------
ONT = Namespace(BASE_URI)
SCHEMA = Namespace("http://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")


# -------------------------
# Fuzzy matcher
# -------------------------
try:
    from rapidfuzz import process, fuzz

    def fuzzy_best(label, candidates):
        match = process.extractOne(label, candidates, scorer=fuzz.WRatio)
        return (match[0], match[1]) if match else (None, 0)
except Exception:  # rapidfuzz not installed
    from difflib import SequenceMatcher

    def fuzzy_best(label, candidates):
        best, score = None, 0.0
        for c in candidates:
            s = SequenceMatcher(None, label.lower(), c.lower()).ratio() * 100
            if s > score:
                best, score = c, s
        return best, score


# -------------------------
# Helpers
# -------------------------

def norm(s: str) -> str:
    return (s or "").strip().lower()


def slug(s: str) -> str:
    return norm(s).replace(" ", "_").replace("/", "_").replace('"', "").replace("'", "")


def rdf_list_members(graph: Graph, node):
    try:
        return list(Collection(graph, node))
    except Exception:
        return []


def extract_canonical_ingredients(ont_graph: Graph, pizza_class_uri) -> set:
    """Collect ingredient URIs from owl:Restrictions on ONT.enthaeltZutat for a given pizza class."""
    ingredients = set()
    for restriction in ont_graph.objects(pizza_class_uri, RDFS.subClassOf):
        if (restriction, RDF.type, OWL.Restriction) not in ont_graph:
            continue
        if (restriction, OWL.onProperty, ONT.enthaeltZutat) not in ont_graph:
            continue

        # owl:hasValue
        for ing in ont_graph.objects(restriction, OWL.hasValue):
            ingredients.add(ing)

        # owl:someValuesFrom / owl:allValuesFrom
        for pred in (OWL.someValuesFrom, OWL.allValuesFrom):
            for val in ont_graph.objects(restriction, pred):
                # unionOf / intersectionOf
                for coll_pred in (OWL.unionOf, OWL.intersectionOf):
                    for coll in ont_graph.objects(val, coll_pred):
                        for member in rdf_list_members(ont_graph, coll):
                            ingredients.add(member)
                # direct class / individual
                if (val, RDF.type, ONT.Zutat) in ont_graph or (val, RDF.type, OWL.NamedIndividual) in ont_graph:
                    ingredients.add(val)
    return ingredients


def build_pizza_class_index(ont_graph: Graph):
    label_to_uri = {}
    uri_to_ings = {}

    for cls in ont_graph.subjects(RDF.type, OWL.Class):
        # select subclasses of ONT.Pizza
        if (cls, RDFS.subClassOf, ONT.Pizza) not in ont_graph:
            continue
        label = ont_graph.value(cls, RDFS.label) or ont_graph.value(cls, SCHEMA.name)
        if not label:
            continue
        label_norm = norm(str(label))
        label_to_uri[label_norm] = cls
        uri_to_ings[cls] = extract_canonical_ingredients(ont_graph, cls)

    return label_to_uri, uri_to_ings


def build_ingredient_lookup(ont_graph: Graph):
    """Return dict norm_label -> URI for all named ingredients (instances of Zutat or its subclasses)."""
    lookup = {}
    # find all individuals with rdf:type ONT:Zutat OR any subclass of Zutat
    zutat_classes = set([ONT.Zutat]) | set(ont_graph.subjects(RDFS.subClassOf, ONT.Zutat))

    for ind in ont_graph.subjects(RDF.type, OWL.NamedIndividual):
        types = set(ont_graph.objects(ind, RDF.type))
        if types & zutat_classes:
            label = ont_graph.value(ind, RDFS.label) or ont_graph.value(ind, SCHEMA.name) or ind.split("#")[-1]
            lookup[norm(str(label))] = ind
    # catch individuals without explicit NamedIndividual type
    for ind in ont_graph.subjects(RDF.type, None):
        if ind in lookup:  # already added
            continue
        types = set(ont_graph.objects(ind, RDF.type))
        if types & zutat_classes:
            label = ont_graph.value(ind, RDFS.label) or ont_graph.value(ind, SCHEMA.name) or ind.split("#")[-1]
            lookup[norm(str(label))] = ind
    return lookup


def decide_ingredients_for_item(menu_label: str, jsonl_ings: list, label_to_uri, uri_to_ings):
    if not label_to_uri:
        return False, None, jsonl_ings
    best_label, score = fuzzy_best(norm(menu_label), list(label_to_uri.keys()))
    if best_label and score >= FUZZY_SCORE_THRESHOLD:
        cls = label_to_uri[best_label]
        return True, cls, uri_to_ings.get(cls, set())
    return False, None, jsonl_ings


def ensure_ingredient_node(g: Graph, ont_graph: Graph, name_norm: str, ing_qid_map: dict, ont_lookup: dict):
    """Reuse ontology ingredient individual if present, else mint new one in ONT namespace."""
    if name_norm in ont_lookup:
        return ont_lookup[name_norm]

    slugged = slug(name_norm)
    ing_uri = ONT[slugged]
    if (ing_uri, RDF.type, ONT.Zutat) not in g:
        g.add((ing_uri, RDF.type, ONT.Zutat))
        g.add((ing_uri, RDF.type, OWL.NamedIndividual))
        g.add((ing_uri, RDFS.label, Literal(name_norm)))
        if name_norm in ing_qid_map and ing_qid_map[name_norm].get("qid"):
            g.add((ing_uri, OWL.sameAs, WD[ing_qid_map[name_norm]["qid"]]))
    # update lookup to avoid dupes later
    ont_lookup[name_norm] = ing_uri
    return ing_uri


# -------------------------
# Cluster integration
# -------------------------

def integrate_clusters_into_tbox(
    g: Graph,
    ont_graph: Graph,
    ingredient_lookup: dict,
    ing_qid_map: dict,
    cluster_file: str
):
    """
    Adds:
      - :ExpertIngredientCategory (if missing)
      - :AIIngredientCategory (subclass of Expert)
      - For each top category: subclass of :AIIngredientCategory
      - For each cluster: subclass of that top category, equivalentClass owl:oneOf(list of individuals)
      - Ingredient individuals (re-used or created)
    """

    # Load JSON
    try:
        clusters_root = json.loads(Path(cluster_file).read_text(encoding="utf-8"))
        clusters = clusters_root.get("ingredient_level2_clusters", clusters_root)
    except Exception as e:
        print(f"[WARN] Could not read {cluster_file}: {e}")
        return

    timestamp = datetime.now().isoformat()
    run_tag = f"AI_CLUSTERS_{timestamp}"

    # Ensure meta TBox terms exist
    def ensure_class(uri: URIRef, label: str):
        if (uri, RDF.type, OWL.Class) not in g:
            g.add((uri, RDF.type, OWL.Class))
            g.add((uri, RDFS.label, Literal(label)))
        return uri

    def ensure_annot_prop(uri: URIRef):
        if (uri, RDF.type, OWL.AnnotationProperty) not in g:
            g.add((uri, RDF.type, OWL.AnnotationProperty))

    # Annotation property to flag AI
    ensure_annot_prop(ONT.aiGenerated)
    ensure_annot_prop(ONT.aiRunTag)

    ExpertCat = ensure_class(ONT.ExpertIngredientCategory, "Expert Ingredient Category")
    AICat = ensure_class(ONT.AIIngredientCategory, "AI Ingredient Category")

    if (AICat, RDFS.subClassOf, ExpertCat) not in g:
        g.add((AICat, RDFS.subClassOf, ExpertCat))

    # Iterate over top categories
    for top_label, cluster_dict in clusters.items():
        top_slug = slug(top_label) + "_ToppingCategory"
        top_uri = ONT[top_slug]

        # Create top category class (subclass of AICat)
        if (top_uri, RDF.type, OWL.Class) not in g:
            g.add((top_uri, RDF.type, OWL.Class))
        g.add((top_uri, RDFS.subClassOf, AICat))
        g.add((top_uri, RDFS.label, Literal(f"Ingredient Category: {top_label}", lang="en")))
        g.add((top_uri, RDFS.comment, Literal("Manual expert category (top level)")))
        g.add((top_uri, ONT.aiGenerated, Literal(True, datatype=XSD.boolean)))
        g.add((top_uri, ONT.aiRunTag, Literal(run_tag)))

        # Now per cluster
        for cluster_label, term_list in cluster_dict.items():
            cluster_slug = slug(cluster_label) + "_Toppings"
            cluster_uri = ONT[cluster_slug]

            # class node
            if (cluster_uri, RDF.type, OWL.Class) not in g:
                g.add((cluster_uri, RDF.type, OWL.Class))
            g.add((cluster_uri, RDFS.subClassOf, top_uri))
            g.add((cluster_uri, RDFS.label, Literal(f"AI cluster ({timestamp}): {cluster_label}", lang="en")))
            g.add((cluster_uri, RDFS.comment, Literal("AI-generated ingredient cluster")))
            g.add((cluster_uri, ONT.aiGenerated, Literal(True, datatype=XSD.boolean)))
            g.add((cluster_uri, ONT.aiRunTag, Literal(run_tag)))

            # ensure ingredient individuals & build owl:oneOf list
            member_uris = []
            for raw in term_list:
                n = norm(raw)
                if not n:
                    continue
                ing_uri = ensure_ingredient_node(g, ont_graph, n, ing_qid_map, ingredient_lookup)
                member_uris.append(ing_uri)

            # Build equivalentClass owl:oneOf (...)
            if member_uris:
                anon = BNode()
                list_node = BNode()
                Collection(g, list_node, member_uris)
                g.add((anon, RDF.type, OWL.Class))
                g.add((anon, OWL.oneOf, list_node))
                g.add((cluster_uri, OWL.equivalentClass, anon))


# -------------------------
# MAIN
# -------------------------

def main():
    # Load mappings
    cities_map = json.loads(Path(CITY_QID_MAP).read_text(encoding="utf-8"))
    ing_qid_map = json.loads(Path(ING_QID_MAP).read_text(encoding="utf-8"))

    # Master output graph
    g = Graph()
    g.bind("", BASE_URI)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("schema", SCHEMA)

    # Load ontology
    ont_graph = Graph()
    ont_graph.parse(ONTOLOGY_FILE)

    # Copy ontology triples into output graph
    for t in ont_graph:
        g.add(t)

    # Index ontology data
    label_to_uri, uri_to_ings = build_pizza_class_index(ont_graph)
    ingredient_lookup = build_ingredient_lookup(ont_graph)

    # --- integrate clusters into TBox before adding pizzas ---
    integrate_clusters_into_tbox(
        g=g,
        ont_graph=ont_graph,
        ingredient_lookup=ingredient_lookup,
        ing_qid_map=ing_qid_map,
        cluster_file=CLUSTER_JSON
    )

    # Rebuild lookup after adding possible new ingredients
    ingredient_lookup = build_ingredient_lookup(g)

    pizzerias = {}
    pizza_count = 0

    with open(DATA_CSV, "r", encoding="utf-8") as csv_file, open(ING_JSONL, "r", encoding="utf-8") as jsonl_file:
        csv_reader = csv.DictReader(csv_file)
        for i, row in enumerate(csv_reader):
            json_line = jsonl_file.readline().strip()
            if not json_line:
                continue
            try:
                pizza_data = json.loads(json_line)
            except json.JSONDecodeError:
                continue

            pizzas = pizza_data if isinstance(pizza_data, list) else [pizza_data]

            for pizza in pizzas:
                if not pizza.get("is_pizza", False):
                    continue

                # --- Pizzeria node ---
                pizz_key = (row["name"], row["address"], row["city"], row["state"], row["country"])
                if pizz_key not in pizzerias:
                    pizz_uri = ONT[f"Pizzeria_{len(pizzerias)}"]
                    pizzerias[pizz_key] = pizz_uri

                    g.add((pizz_uri, RDF.type, ONT.Pizzeria))
                    g.add((pizz_uri, RDF.type, SCHEMA.FoodEstablishment))
                    g.add((pizz_uri, RDFS.label, Literal(row["name"])))
                    g.add((pizz_uri, SCHEMA.name, Literal(row["name"])))

                    address = BNode()
                    g.add((address, RDF.type, SCHEMA.PostalAddress))
                    g.add((address, SCHEMA.streetAddress, Literal(row.get("address"))))

                    addr_map = [
                        ("state", SCHEMA.addressRegion),
                        ("postcode", SCHEMA.postalCode),
                        ("country", SCHEMA.addressCountry),
                        ("city", SCHEMA.addressLocality),
                    ]
                    for key, pred in addr_map:
                        val = row.get(key)
                        if val:
                            g.add((address, pred, Literal(val)))

                    g.add((pizz_uri, SCHEMA.address, address))

                    city = row.get("city")
                    if city:
                        city_data = cities_map.get(city, {})
                        if city_data.get("qid"):
                            g.add((address, SCHEMA.containedInPlace, WD[city_data["qid"]]))

                # --- Menu item / pizza individual ---
                pizza_name = pizza.get("name", row["menu item"]) or "Pizza"
                slug = pizza_name.replace(" ", "_").replace('"', "").replace("'", "")
                menu_item_uri = ONT[f"MenuItem_{slug}_{pizza_count}"]
                pizza_count += 1

                g.add((menu_item_uri, RDF.type, SCHEMA.MenuItem))
                g.add((menu_item_uri, RDF.type, ONT.Pizza))
                g.add((menu_item_uri, RDFS.label, Literal(pizza_name)))
                g.add((menu_item_uri, SCHEMA.name, Literal(pizza_name)))

                desc = row.get("item description")
                if desc:
                    g.add((menu_item_uri, RDFS.comment, Literal(desc)))
                    g.add((menu_item_uri, SCHEMA.description, Literal(desc)))

                # price
                try:
                    price_val = float(row.get("item value"))
                except (TypeError, ValueError):
                    price_val = None
                if price_val is not None and price_val != 0:
                    g.add((menu_item_uri, ONT.preis, Literal(str(price_val), datatype=XSD.decimal)))
                    g.add((menu_item_uri, SCHEMA.priceCurrency, Literal(row.get("currency"))))

                # pizzeria link
                g.add((menu_item_uri, ONT.gehoertZuPizzeria, pizzerias[pizz_key]))

                # --- Ingredient decision ---
                use_ont, class_uri, ing_candidates = decide_ingredients_for_item(
                    pizza_name, pizza.get("ingredients", []), label_to_uri, uri_to_ings
                )

                if use_ont:
                    g.add((menu_item_uri, RDF.type, class_uri))
                    for ing_uri in ing_candidates:
                        g.add((menu_item_uri, ONT.enthaeltZutat, ing_uri))
                else:
                    for ing_name in pizza.get("ingredients", []):
                        ing_uri = ensure_ingredient_node(
                            g, ont_graph, norm(ing_name), ing_qid_map, ingredient_lookup
                        )
                        g.add((menu_item_uri, ONT.enthaeltZutat, ing_uri))

    g.serialize(OUTPUT_TTL, format="turtle")

    with open(OUTPUT_TTL, 'r+', encoding='utf-8') as f:
        ttl_data = f.read()

        # Ensure xsd prefix is included
        if 'xsd:' not in ttl_data:
            ttl_data = '@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n' + ttl_data

        # Replace schema1:price value with xsd:decimal annotation
        updated_ttl = re.sub(
            r'(:preis\s)(\d+\.\d+)',
            r'\1"\2"^^xsd:decimal',
            ttl_data
        )

        # Go back to the beginning and overwrite the file
        f.seek(0)
        f.write(updated_ttl)
        f.truncate()

    print(f"Wrote {OUTPUT_TTL}")


if __name__ == "__main__":
    main()
