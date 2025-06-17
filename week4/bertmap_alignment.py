#!/usr/bin/env python3
"""
bertmap_equivalence_script.py

Compute equivalence alignments between two OWL ontologies using DeepOnto's BERTMap
and generate a Turtle file containing owl:equivalentClass / owl:equivalentProperty triples.

Usage:
    python bertmap_equivalence_script.py src.owl tgt.owl --output alignments.ttl
"""

import argparse
import csv
import logging
import pathlib

from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL

from deeponto.onto import Ontology
from deeponto.align.bertmap import BERTMapPipeline, DEFAULT_CONFIG_FILE


def run_bertmap(src_onto_path: str, tgt_onto_path: str, config_path: str | None, work_dir: str) -> pathlib.Path:
    """Run BERTMap and return path to the repaired_mappings.tsv file."""
    work_dir = pathlib.Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    if config_path:
        config = BERTMapPipeline.load_bertmap_config(config_path)
    else:
        config = BERTMapPipeline.load_bertmap_config(DEFAULT_CONFIG_FILE)

    # redirect all intermediate files to the working directory
    config.output_path = str(work_dir)

    logging.info("Loading ontologies …")
    src_onto = Ontology(src_onto_path)
    tgt_onto = Ontology(tgt_onto_path)

    logging.info("Running BERTMap … (this may take a while)")
    bertmap = BERTMapPipeline(src_onto, tgt_onto, config)
    # global matching is executed automatically in constructor

    # Locate the mapping file produced by BERTMap
    match_dir = work_dir / ("bertmap" if config.model == "bertmap" else "bertmaplt") / "match"
    mapping_file = match_dir / "repaired_mappings.tsv"
    if not mapping_file.exists():
        # fall back to filtered mappings if repair not enabled
        mapping_file = match_dir / "filtered_mappings.tsv"

    if not mapping_file.exists():
        raise FileNotFoundError(f"Could not locate mapping file inside {match_dir}")

    return mapping_file


def mappings_to_ttl(mapping_tsv: pathlib.Path, src_onto_path: str, tgt_onto_path: str, ttl_out: str) -> None:
    """Convert the TSV mappings into Turtle equivalence triples."""
    src_graph = Graph().parse(src_onto_path)
    tgt_graph = Graph().parse(tgt_onto_path)

    out_graph = Graph()
    out_graph.bind("owl", OWL)

    with mapping_tsv.open(encoding="utf8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        # fall back to positional columns if no header
        use_header = reader.fieldnames is not None and len(reader.fieldnames) >= 2
        if not use_header:
            f.seek(0)
            reader = csv.reader(f, delimiter="\t")

        for row in reader:
            if use_header:
                src_iri = URIRef(row["SrcEntity"])
                tgt_iri = URIRef(row["TgtEntity"])
            else:
                src_iri = URIRef(row[0])
                tgt_iri = URIRef(row[1])

            # Decide predicate based on entity types declared in either ontology
            if (
                (src_iri, RDF.type, OWL.ObjectProperty) in src_graph
                or (tgt_iri, RDF.type, OWL.ObjectProperty) in tgt_graph
                or (src_iri, RDF.type, OWL.DatatypeProperty) in src_graph
                or (tgt_iri, RDF.type, OWL.DatatypeProperty) in tgt_graph
            ):
                predicate = OWL.equivalentProperty
            else:
                predicate = OWL.equivalentClass

            out_graph.add((src_iri, predicate, tgt_iri))

    out_graph.serialize(destination=ttl_out, format="turtle")
    logging.info("Saved equivalence triples to %s", ttl_out)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute equivalences between two ontologies with BERTMap and write a Turtle alignment."
    )
    parser.add_argument("src_onto", help="Source ontology file (.owl/.xml/.ttl/...)")
    parser.add_argument("tgt_onto", help="Target ontology file (.owl/.xml/.ttl/...)")
    parser.add_argument(
        "-o",
        "--output",
        help="Output TTL file for equivalence triples (default: ./equivalences.ttl)",
        default="equivalences.ttl",
    )
    parser.add_argument("-c", "--config", help="Optional YAML config for BERTMap", default=None)
    parser.add_argument("-w", "--work-dir", help="Working directory for BERTMap outputs", default="bertmap_work")
    args = parser.parse_args()

    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    mapping_file = run_bertmap(args.src_onto, args.tgt_onto, args.config, args.work_dir)
    mappings_to_ttl(mapping_file, args.src_onto, args.tgt_onto, args.output)


if __name__ == "__main__":
    main()
