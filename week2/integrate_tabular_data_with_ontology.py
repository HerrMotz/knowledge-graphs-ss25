import csv
import json
from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, XSD, BNode

# Known ontology ingredients mapping
KNOWN_INGREDIENTS = {
    "ananas": "Ananas",
    "broccoli": "Brokkoli",
    "mozzarella": "Mozzarella",
    "pepperoni": "Pepperoniwurst",
    "salami": "Salami",
    "ham": "Schinken",
    "tomato sauce": "Tomatensauce",
}

# Initialize RDF Graph
g = Graph()
BASE_URI = "http://ontology.daniel-motz.de/ontology#"
g.bind("", BASE_URI)
g.bind("owl", OWL)
g.bind("rdfs", RDFS)
g.bind("schema", "http://schema.org/")

# Define Namespaces
ONT = Namespace(BASE_URI)
SCHEMA = Namespace("http://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")

# Load mappings
with open('city_qid_map.json') as f:
    cities_map = json.load(f)
with open('ingredient_qid_map.json') as f:
    ing_qid_map = json.load(f)

# Process data.csv and ingredients.jsonl
pizzerias = {}
pizza_count = 0

with open('data.csv', 'r') as csv_file, open('ingredients.jsonl', 'r') as jsonl_file:
    csv_reader = csv.DictReader(csv_file)
    for i, row in enumerate(csv_reader):
        # Read JSONL line - could be an object or array
        json_line = jsonl_file.readline().strip()
        if not json_line:
            continue

        try:
            pizza_data = json.loads(json_line)
        except json.JSONDecodeError:
            continue

        # Normalize to list of pizzas
        pizzas = pizza_data if isinstance(pizza_data, list) else [pizza_data]

        for pizza in pizzas:
            if not pizza.get('is_pizza', False):
                continue  # Skip non-pizza items

            # Create or get Pizzeria
            pizz_key = (row['name'], row['address'], row['city'], row['state'], row['country'])
            if pizz_key not in pizzerias:
                pizz_uri = ONT[f"Pizzeria_{len(pizzerias)}"]
                pizzerias[pizz_key] = pizz_uri

                # Add pizzeria details
                g.add((pizz_uri, RDF.type, ONT.Pizzeria))
                g.add((pizz_uri, RDF.type, SCHEMA.FoodEstablishment))
                g.add((pizz_uri, RDFS.label, Literal(row['name'])))
                g.add((pizz_uri, SCHEMA.name, Literal(row['name'])))

                # Create schema.org address structure
                address_node = BNode()
                g.add((address_node, RDF.type, SCHEMA.PostalAddress))
                g.add((address_node, SCHEMA.streetAddress, Literal(row['address'])))

                addr_map = [('state', SCHEMA.addressRegion),
                            ('postcode', SCHEMA.postalCode),
                            ('country', SCHEMA.addressCountry),
                            ('city', SCHEMA.city)] # add city as a literal, it will be also added as a wikidata item, but SCHEMA defines this value to be of type TEXT
                for key, predicate in addr_map:
                    literalValue = row[key]
                    if literalValue:
                        g.add((address_node, predicate, Literal(literalValue)))

                # Link address to pizzeria
                g.add((pizz_uri, SCHEMA.address, address_node))

                # Additionally, to the literal value 'city' in the schema.org address, add a reference to the wikidata
                # item, if one was found.
                city = row["city"]
                if city:
                    city_data = cities_map.get(city, {})
                    city_uri = WD[city_data['qid']] if city_data.get('qid') else None
                    if city_uri:
                        g.add((address_node, SCHEMA.containedInPlace, city_uri))

            # Create MenuItem individual
            pizza_name = pizza.get('name', row['menu item'])
            pizza_slug = pizza_name.replace(' ', '_').replace('"', '').replace("'", "")
            menu_item_uri = ONT[f"MenuItem_{pizza_slug}_{pizza_count}"]
            menu_item_description = row["item description"]
            pizza_count += 1

            g.add((menu_item_uri, RDFS.label, Literal(pizza_name)))
            if menu_item_description:
                g.add((menu_item_uri, RDFS.comment, Literal(menu_item_description)))

            # Add menu item properties
            g.add((menu_item_uri, RDF.type, SCHEMA.MenuItem))
            g.add((menu_item_uri, RDF.type, ONT.Pizza))  # Also type as ontology Pizza
            g.add((menu_item_uri, SCHEMA.name, Literal(pizza_name)))

            # Add price information
            try:
                _p = float(row['item value'])
            except ValueError:
                _p = None

            if _p is not None:
                price = Literal(_p, datatype=XSD.decimal)
                g.add((menu_item_uri, SCHEMA.price, price))
                g.add((menu_item_uri, SCHEMA.priceCurrency, Literal(row['currency'])))

            # Link to pizzeria
            g.add((menu_item_uri, ONT.gehoertZuPizzeria, pizzerias[pizz_key]))

            # Add description if available
            if row['item description']:
                g.add((menu_item_uri, SCHEMA.description, Literal(row['item description'])))

            # Add ingredients
            for ing_name in pizza.get('ingredients', []):
                norm_name = ing_name.strip().lower()
                slug = norm_name.replace(' ', '_').replace('"', '').replace("'", "")

                # Use existing ontology ingredient if available
                if norm_name in KNOWN_INGREDIENTS:
                    ing_uri = ONT[KNOWN_INGREDIENTS[norm_name]]
                    g.add((menu_item_uri, ONT.enthaeltZutat, ing_uri))
                else:
                    # Create new ingredient
                    ing_uri = ONT[slug]
                    g.add((ing_uri, RDF.type, ONT.Zutat))
                    g.add((menu_item_uri, ONT.enthaeltZutat, ing_uri))

                # with Wikidata link if it exists
                if norm_name in ing_qid_map and ing_qid_map[norm_name].get('qid'):
                    qid = ing_qid_map[norm_name]['qid']
                    g.add((ing_uri, OWL.sameAs, WD[qid]))

    # Save to Turtle
    g.serialize('pizza_data.ttl', format='turtle')