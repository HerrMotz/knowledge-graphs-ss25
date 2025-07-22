from rdflib import Graph
from rdflib import RDF, RDFS, Namespace
from rdflib.namespace import OWL, XSD
from owlrl import DeductiveClosure, OWLRL_Semantics

SCHEMA = Namespace("http://schema.org/")


if __name__ == "__main__":
    # Step 1: Load base ontology and data
    g = Graph()
    g.parse("../week1/ontology.xml", format="xml")
    g.parse("../week2/pizza_data.ttl", format="turtle")

    # Tell every reasoner that these are data properties
    g.add((SCHEMA.price, RDF.type, OWL.DatatypeProperty))
    g.add((SCHEMA.price, RDFS.range, XSD.decimal))

    g.add((SCHEMA.priceCurrency, RDF.type, OWL.DatatypeProperty))
    g.add((SCHEMA.priceCurrency, RDFS.range, XSD.string))

    print(f"Original triples: {len(g)}")

    # Step 2: Apply OWL RL reasoning
    DeductiveClosure(OWLRL_Semantics).expand(g)

    print(f"After reasoning: {len(g)}")

    # Step 3: Save extended graph to TTL
    g.serialize(destination="inferred_data.ttl", format="turtle")
    print("Inferred graph saved to 'inferred_data.ttl'")
