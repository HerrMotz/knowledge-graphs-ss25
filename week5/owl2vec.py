#!/usr/bin/env python3
"""owl2vec_pipeline.py

Merge an ontology (RDF/XML) with generated data (Turtle) and run OWL2Vec* twice
with different configurations.

Usage
-----
$ python owl2vec_pipeline.py path/to/ontology.owl path/to/data.ttl \
                          --outdir embeddings --sample 500
--------------------------

Tip: If OWL2Vec* complains about Java, install `openjdk‑17‑jdk` and ensure the
`java` command is on your $PATH.
"""

from __future__ import annotations  # enables postponed evaluation of annotations

import argparse
import logging
import random
import subprocess
import configparser
from pathlib import Path
from typing import List, Optional

import rdflib
from gensim.models import KeyedVectors

logging.basicConfig(level=logging.INFO,
                    format="[%(levelname)s] %(message)s")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _rdf_format(path: Path) -> str:
    """Guess rdflib parser format from a file extension."""
    ext = path.suffix.lower()
    if ext in {".ttl", ".turtle"}:
        return "turtle"
    if ext in {".rdf", ".owl", ".xml"}:
        return "xml"
    raise ValueError(f"Cannot guess RDF format for '{path}'.")


def merge_graphs(onto_file: Path, data_file: Path, *, sample_triples: Optional[int],
                 dest_file: Path) -> None:
    """Load two RDF files, optionally subsample triples, and write RDF/XML."""
    g = rdflib.Graph()
    logging.info("Loading ontology  … %s", onto_file)
    g.parse(str(onto_file), format=_rdf_format(onto_file))  # FIXED

    g_data = rdflib.Graph()
    logging.info("Loading data      … %s", data_file)
    g_data.parse(str(data_file), format=_rdf_format(data_file))  # FIXED

    if sample_triples is not None and sample_triples < len(g_data):
        logging.info("Sampling %d of %d data triples", sample_triples, len(g_data))
        triples = random.sample(list(g_data), sample_triples)
    else:
        triples = list(g_data)

    for t in triples:
        g.add(t)

    g.serialize(str(dest_file), format="xml")  # OPTIONAL: cast here too
    logging.info("Merged graph saved as %s (%d triples)", dest_file, len(g))


def write_cfg(merged_owl: Path, *, embed_size: int, walk_depth: int,
              reasoner: Optional[str], outfile: Path) -> None:
    """Write a minimal OWL2Vec* INI config file to *outfile*."""
    cfg = configparser.ConfigParser()

    cfg["BASIC"] = {
        "ontology_file": str(merged_owl),
    }
    cfg["DOCUMENT"] = {
        "cache_dir": str(outfile.parent / "cache"),
        "ontology_projection": "yes",
        "projection_only_taxonomy": "no",
        "multiple_labels": "yes",
        "avoid_owl_constructs": "no",
        "save_document": "yes",
        "axiom_reasoner": reasoner or "none",
        "walker": "random",
        "walk_depth": str(walk_depth),
        "URI_Doc": "yes",
        "Lit_Doc": "yes",
        "Mix_Doc": "no",
    }
    cfg["MODEL"] = {
        "embed_size": str(embed_size),
        "iteration": "10",
        "window": "5",
        "min_count": "1",
        "negative": "25",
        "seed": "42",
    }

    with outfile.open("w", encoding="utf8") as fh:
        cfg.write(fh)

    logging.info("Config written to %s", outfile)


def run_owl2vec(cfg_file: Path, output_prefix: Path) -> None:
    """Execute OWL2Vec* and convert its text vectors to binary."""
    logging.info("Running OWL2Vec*  … configuration %s", cfg_file.name)
    subprocess.run([
        "owl2vec_star", "standalone", "--config_file", str(cfg_file)
    ], check=True)

    txt_file = output_prefix.with_suffix(".vec.txt")
    bin_file = output_prefix.with_suffix(".vec.bin")

    if txt_file.exists():
        kv = KeyedVectors.load_word2vec_format(txt_file, binary=False)
        kv.save_word2vec_format(bin_file, binary=True)
        logging.info("Saved vectors: %s (text), %s (binary)", txt_file.name, bin_file.name)
    else:
        logging.error("Expected %s was not created by OWL2Vec*", txt_file)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Merge ontology & data into OWL, then run OWL2Vec* twice.")
    parser.add_argument("ontology", type=Path, help="Ontology file (RDF/XML)")
    parser.add_argument("data", type=Path, help="Generated data file (Turtle)")
    parser.add_argument("--outdir", type=Path, default=Path("owl2vec_output"),
                        help="Directory for intermediate and result files")
    parser.add_argument("--sample", type=int, default=500,
                        help="Max. triples from the data file (speed‑up)")
    args = parser.parse_args(argv)

    args.outdir.mkdir(parents=True, exist_ok=True)

    merged_owl = args.outdir / "merged.owl"
    merge_graphs(args.ontology, args.data, sample_triples=args.sample,
                 dest_file=merged_owl)

    # ---- Configuration #1: default size 200, shallow walks, no reasoning ----
    cfg1 = args.outdir / "cfg1.ini"
    write_cfg(merged_owl, embed_size=200, walk_depth=2, reasoner=None,
              outfile=cfg1)
    run_owl2vec(cfg1, args.outdir / "cfg1")

    # ---- Configuration #2: bigger vectors, deeper walks, ELK reasoning  ----
    cfg2 = args.outdir / "cfg2.ini"
    write_cfg(merged_owl, embed_size=400, walk_depth=4, reasoner="elk",
              outfile=cfg2)
    run_owl2vec(cfg2, args.outdir / "cfg2")

    logging.info("All done ✔︎ — embeddings are in %s", args.outdir)


if __name__ == "__main__":
    main()
