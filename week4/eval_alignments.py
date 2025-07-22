#!/usr/bin/env python3
import rdflib
from pathlib import Path

ALIGN = rdflib.Namespace("http://knowledgeweb.semanticweb.org/heterogeneity/alignment#")
RDF = rdflib.RDF


def load_alignment(path):
    g = rdflib.Graph()
    g.parse(path)
    triples = set()
    for cell in g.subjects(RDF.type, ALIGN.Cell):
        e1 = g.value(cell, ALIGN.entity1)
        e2 = g.value(cell, ALIGN.entity2)
        rel = str(g.value(cell, ALIGN.relation))
        triples.add((str(e1), str(e2), rel))
    return triples


def normalize(mappings, sym_rels={"="}):
    norm = set()
    for a, b, r in mappings:
        if r in sym_rels and b < a:
            a, b = b, a
        norm.add((a, b, r))
    return norm


def evaluate(candidate, reference):
    tp = len(candidate & reference)
    fp = len(candidate - reference)
    fn = len(reference - candidate)
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return tp, fp, fn, prec, rec, f1


if __name__ == "__main__":
    ref = normalize(load_alignment("./reference/reference-mappings-pizza_align.ttl"))
    print("Loaded reference mappings:", len(ref))

    systems = {
        "aml":      "outputs_reference_ontology/aml_alignment.rdf",
        "own":      "outputs_reference_ontology/own_alignment_api.ttl",
        "bertmap":  "outputs_reference_ontology/bertmap_alignment.ttl",
        "chatllm":  "outputs_reference_ontology/chatllm_alignment.ttl",
    }

    for name, path in systems.items():
        if not Path(path).exists():
            print(path)
            continue
        cand = normalize(load_alignment(path))
        tp, fp, fn, p, r, f1 = evaluate(cand, ref)
        print(f"{name:10s}  TP:{tp:3d}  FP:{fp:3d}  FN:{fn:3d}  P:{p:.3f}  R:{r:.3f}  F1:{f1:.3f}")
