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
    "tomato sauce": "Tomatensauce"
}

BASE_URI = "http://ontology.daniel-motz.de/ontology#"
# Define Namespaces
ONT = Namespace(BASE_URI)
SCHEMA = Namespace("http://schema.org/")
WD = Namespace("http://www.wikidata.org/entity/")

def main():
    # Initialize RDF Graph
    g = Graph()
    g.bind("", BASE_URI)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("schema", "http://schema.org/")

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
            # Read ingredients data
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

                # Create schema.org address structure
                address_node = BNode()
                g.add((address_node, RDF.type, SCHEMA.PostalAddress))
                g.add((address_node, SCHEMA.streetAddress, Literal(row['address'])))

                # Link city to Wikidata if available
                city = row['city']
                if city in cities_map and cities_map[city].get('qid'):
                    city_uri = WD[cities_map[city]['qid']]
                    g.add((address_node, SCHEMA.addressLocality, city_uri))
                else:
                    g.add((address_node, SCHEMA.addressLocality, Literal(city)))

                g.add((address_node, SCHEMA.addressRegion, Literal(row['state'])))
                g.add((address_node, SCHEMA.postalCode, Literal(row['postcode'])))
                g.add((address_node, SCHEMA.addressCountry, Literal(row['country'])))

                # Link address to pizzeria
                g.add((pizz_uri, SCHEMA.address, address_node))

            # Create Pizza individual
            pizza_uri = ONT[f"Pizza_{pizza_count}"]
            pizza_count += 1
            g.add((pizza_uri, RDF.type, ONT.Pizza))
            g.add((pizza_uri, ONT.gehörtZuPizzeria, pizzerias[pizz_key]))
            g.add((pizza_uri, ONT.preis, Literal(float(row['item value']), datatype=XSD.decimal)))

            # Add ingredients
            for ing_name in ing_data['ingredients']:
                norm_name = ing_name.strip().lower()

            # Use existing ontology ingredient if available
            if norm_name in KNOWN_INGREDIENTS:
                ing_uri = ONT[KNOWN_INGREDIENTS[norm_name]]
            else:
            # Create new ingredient with Wikidata link
                if norm_name in ing_qid_map and ing_qid_map[norm_name].get('qid'):
                    qid = ing_qid_map[norm_name]['qid']
                    ing_uri = ONT[f"Ingredient_wd_{qid}"]
                    g.add((ing_uri, OWL.sameAs, WD[qid]))
                else:
                    # Fallback: create new ingredient
                    slug = norm_name.replace(' ', '_')
                    ing_uri = ONT[f"Ingredient_{slug}"]

            g.add((ing_uri, RDF.type, ONT.Zutat))

            g.add((pizza_uri, ONT.enthaeltZutat, ing_uri))

            # Save to Turtle
            g.serialize('pizza_data.ttl', format='turtle')

if __name__ == "__main__":
    main()