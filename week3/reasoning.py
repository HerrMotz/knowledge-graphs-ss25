from rdflib import Graph, Literal
from rdflib import RDF, RDFS, Namespace
from rdflib.namespace import OWL, XSD
from owlrl import DeductiveClosure, OWLRL_Semantics

SCHEMA = Namespace("http://schema.org/")

def remove_invalid_owl_triples(graph):
    to_remove = []

    for s, p, o in graph:
        # Rule 1: Subject must not be a Literal
        if isinstance(s, Literal):
            to_remove.append((s, p, o))

        # Rule 2: owl:sameAs must not involve literals at all
        elif p == OWL.sameAs and (isinstance(s, Literal) or isinstance(o, Literal)):
            to_remove.append((s, p, o))

    # Remove all offending triples
    for triple in to_remove:
        graph.remove(triple)

    return graph


if __name__ == "__main__":
    # Step 1: Load base ontology and data
    g = Graph()
    g.parse("../week1/ontology.xml", format="xml")
    g.parse("../week2/pizza_data.ttl", format="turtle")


    print(f"Original triples: {len(g)}")

    # Step 2: Apply OWL RL reasoning
    DeductiveClosure(OWLRL_Semantics).expand(g)

    remove_invalid_owl_triples(g)

    print(f"After reasoning: {len(g)}")

    # Step 3: Save extended graph to TTL
    g.serialize(destination="inferred_data.ttl", format="turtle")
    print("Inferred graph saved to 'inferred_data.ttl'")
