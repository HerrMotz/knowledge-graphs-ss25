#!/usr/bin/env python3
"""
bertmap2alignment.py

Transform BERTMap equivalence assertions like:
    <A> owl:equivalentClass <B> .

into Alignment API RDF (AML/LogMap style):

@prefix align: <http://knowledgeweb.semanticweb.org/heterogeneity/alignment#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

[] a align:Alignment ;
   align:map [
      a align:Cell ;
      align:entity1 <A> ;
      align:entity2 <B> ;
      align:relation "=" ;
      align:measure "1.0"^^xsd:float
   ] .

Usage:
    python bertmap2alignment.py outputs/bertmap_equivalences.ttl outputs/bertmap_equivalences_alignment_api.ttl --default-score 1.0
"""
import argparse
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import OWL, XSD

ALIGN = Namespace("http://knowledgeweb.semanticweb.org/heterogeneity/alignment#")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="BERTMap TTL file", default="outputs/bertmap_equivalences.ttl")
    ap.add_argument("output", help="Alignment API TTL output file", default="outputs/bertmap_alignment.ttl")
    ap.add_argument("--default-score", type=float, default=1.0,help="Score to assign to each cell (default: 1.0)")
    args = ap.parse_args()

    # Read BERTMap graph
    g_in = Graph()
    g_in.parse(args.input, format="turtle")

    # Create alignment graph
    g_out = Graph()
    g_out.bind("align", ALIGN)
    g_out.bind("xsd", XSD)

    # One Alignment root node
    alignment_bnode = BNode()

    g_out.add((alignment_bnode, g_out.namespace_manager.compute_qname("rdf:type")[1], ALIGN.Alignment))

    # Find equivalence axioms
    for s, p, o in g_in.triples((None, OWL.equivalentClass, None)):
        cell = BNode()
        g_out.add((alignment_bnode, ALIGN.map, cell))
        g_out.add((cell, g_out.namespace_manager.compute_qname("rdf:type")[1], ALIGN.Cell))
        g_out.add((cell, ALIGN.entity1, s if isinstance(s, URIRef) else URIRef(str(s))))
        g_out.add((cell, ALIGN.entity2, o if isinstance(o, URIRef) else URIRef(str(o))))
        g_out.add((cell, ALIGN.relation, Literal("=")))
        g_out.add((cell, ALIGN.measure, Literal(args.default_score, datatype=XSD.float)))

    # Write result
    g_out.serialize(destination=args.output, format="turtle")

if __name__ == "__main__":
    main()
