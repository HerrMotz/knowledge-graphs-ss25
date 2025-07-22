#!/usr/bin/env python3
"""
bertmap2alignment.py
Convert BERTMap equivalence axioms (classes *and* properties) to Alignment API TTL.

Supports:
  - owl:equivalentClass
  - owl:equivalentProperty

Usage:
    python bertmap2alignment.py in.ttl out.ttl --default-score 1.0
"""
import argparse
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import OWL, RDF, XSD, RDFS

ALIGN = Namespace("http://knowledgeweb.semanticweb.org/heterogeneity/alignment#")

# Map input predicates to Alignment API relation symbols
REL_MAP = {
    OWL.equivalentClass: "=",
    OWL.equivalentProperty: "=",
    # RDFS.subClassOf: "<",
    # (RDFS.subPropertyOf): "<",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="BERTMap TTL file")
    ap.add_argument("output", help="Alignment API TTL output file")
    ap.add_argument("--default-score", type=float, default=1.0,
                    help="Score to assign to each produced cell (default: 1.0)")
    args = ap.parse_args()

    g_in = Graph()
    g_in.parse(args.input, format="turtle")

    g_out = Graph()
    g_out.bind("align", ALIGN)
    g_out.bind("xsd", XSD)

    aln = BNode()
    g_out.add((aln, RDF.type, ALIGN.Alignment))

    for pred, relation in REL_MAP.items():
        for s, _, o in g_in.triples((None, pred, None)):
            cell = BNode()
            g_out.add((aln, ALIGN.map, cell))
            g_out.add((cell, RDF.type, ALIGN.Cell))
            g_out.add((cell, ALIGN.entity1, URIRef(str(s))))
            g_out.add((cell, ALIGN.entity2, URIRef(str(o))))
            g_out.add((cell, ALIGN.relation, Literal(relation)))
            g_out.add((cell, ALIGN.measure, Literal(args.default_score, datatype=XSD.float)))

    g_out.serialize(destination=args.output, format="turtle")

if __name__ == "__main__":
    main()
