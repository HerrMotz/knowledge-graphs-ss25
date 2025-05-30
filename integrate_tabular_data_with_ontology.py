import csv
import json
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD

# Initialize RDF Graph
g = Graph()
base_uri = "http://ontology.daniel-motz.de/ontology#"
g.bind("", base_uri)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)

# Define Namespaces
ONT = Namespace(base_uri)
WD = Namespace("http://www.wikidata.org/entity/")

# Add new property: hatStadt
hatStadt = URIRef(base_uri + "hatStadt")
g.add((hatStadt, RDF.type, OWL.ObjectProperty))
g.add((hatStadt, RDFS.domain, ONT.Pizzeria))
g.add((hatStadt, RDFS.range, OWL.Thing))

# Load mappings
with open('ingredient_qid_map.json') as f:
    ing_qid_map = json.load(f)
with open('city_qid_map.json') as f:
    city_qid_map = json.load(f)

# Known ontology ingredients mapping
KNOWN_INGREDIENTS = {
    "ananas": "Ananas",
    "broccoli": "Brokkoli",
    "mozzarella": "Mozzarella",
    "pepperoni": "Pepperoniwurst",
    "salami": "Salami",
    "ham": "Schinken",
    "tomato sauce": "Tomatensauce"
}

# Process data.csv and ingredients.jsonl
pizzerias = {}  # Cache pizzerias: (name, address, city) -> URI
pizza_count = 0

with open('data.csv', 'r') as csv_file, open('ingredients.jsonl', 'r') as jsonl_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        # Read corresponding JSONL line
        ing_data = json.loads(jsonl_file.readline())
        if not ing_data.get('is_pizza', False):
            continue  # Skip non-pizza items

        # Create or get Pizzeria
        pizz_key = (row['name'], row['address'], row['city'])
        if pizz_key not in pizzerias:
            pizz_uri = ONT[f"Pizzeria_{len(pizzerias)}"]
            pizzerias[pizz_key] = pizz_uri

            # Add pizzeria details
            g.add((pizz_uri, RDF.type, ONT.Pizzeria))
            address_str = f"{row['address']}, {row['city']}, {row['state']}, {row['postcode']}, {row['country']}"
            g.add((pizz_uri, ONT.adresse, Literal(address_str)))

            # Link to city via Wikidata
            city_name = row['city']
            if city_name in city_qid_map:
                city_qid = city_qid_map[city_name]['qid']
                if city_qid:
                    g.add((pizz_uri, hatStadt, WD[city_qid]))

        # Create Pizza individual
        pizza_uri = ONT[f"Pizza_{pizza_count}"]
        pizza_count += 1
        g.add((pizza_uri, RDF.type, ONT.Pizza))
        g.add((pizza_uri, ONT.gehörtZuPizzeria, pizzerias[pizz_key]))
        g.add((pizza_uri, ONT.preis, Literal(float(row['item value']), datatype=XSD.decimal)))

        # Add ingredients
        for ing_name in ing_data['ingredients']:
            norm_name = ing_name.strip().lower()

            # Check known ontology ingredients
            if norm_name in KNOWN_INGREDIENTS:
                ing_uri = ONT[KNOWN_INGREDIENTS[norm_name]]
            else:
                # Use Wikidata mapping or create new
                if norm_name in ing_qid_map and ing_qid_map[norm_name]['qid']:
                    qid = ing_qid_map[norm_name]['qid']
                    ing_uri = ONT[f"Ingredient_wd_{qid}"]
                    g.add((ing_uri, RDF.type, ONT.Zutat))
                    g.add((ing_uri, OWL.sameAs, WD[qid]))
                else:
                    # Fallback: create new ingredient
                    slug = norm_name.replace(' ', '_')
                    ing_uri = ONT[f"Ingredient_{slug}"]
                    g.add((ing_uri, RDF.type, ONT.Zutat))

            g.add((pizza_uri, ONT.enthaeltZutat, ing_uri))

if __name__ == "__main__":
    # Save to Turtle
    g.serialize('pizza_data.ttl', format='turtle')