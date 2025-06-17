#!/usr/bin/env python3
"""
bertmap_equivalence_script.py

Compute equivalence alignments between two OWL ontologies using DeepOnto's BERTMap
and generate a Turtle file containing owl:equivalentClass / owl:equivalentProperty triples.

GPU SUPPORT (CUDA):
    The script auto-detects an available NVIDIA GPU via PyTorch **or** lets you
    force the device with `--device`.  The selected device is injected into the
    BERTMap config (``config.device``) and exported to the environment variable
    ``CUDA_VISIBLE_DEVICES`` so that the whole DeepOnto stack runs on GPU.

Usage:
    python bertmap_equivalence_script.py src.owl tgt.owl \
        --output alignments.ttl            # optional
        --device auto|cpu|cuda|cuda:1      # optional (default: auto)
        --config my_bertmap.yaml           # optional custom config
        --work-dir bertmap_work            # optional work dir
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import pathlib
import sys
from typing import Final

import torch
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, OWL

from deeponto.onto import Ontology
from deeponto.align.bertmap import BERTMapPipeline, DEFAULT_CONFIG_FILE

def _resolve_device(cli_choice: str) -> str:
    """Resolve requested device from CLI into a valid torch device string."""
    if cli_choice == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"

    if cli_choice.startswith("cuda"):
        if not torch.cuda.is_available():
            logging.warning("CUDA requested but no GPU visible → falling back to CPU")
            return "cpu"
        # allow cuda, cuda:0, cuda:1 …
        return cli_choice

    return "cpu"  # fallback / explicit "cpu"


def _prepare_environment(device: str) -> None:
    """Optionally set CUDA_VISIBLE_DEVICES so downstream libraries honour the choice."""
    if device.startswith("cuda"):
        # When device is "cuda" we keep existing visibility; when "cuda:X" we expose only X
        if ":" in device:
            idx = device.split(":", 1)[1]
            os.environ["CUDA_VISIBLE_DEVICES"] = idx
            logging.info("Using GPU device cuda:%s (CUDA_VISIBLE_DEVICES=%s)", idx, idx)
        else:
            logging.info("Using first available GPU (CUDA_VISIBLE_DEVICES stays unchanged)")
    else:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        logging.info("Using CPU only (CUDA_VISIBLE_DEVICES cleared)")


def run_bertmap(
    src_onto_path: str,
    tgt_onto_path: str,
    config_path: str | None,
    work_dir: str,
    device: str,
) -> pathlib.Path:
    """Run BERTMap on *device* and return path to the repaired_mappings.tsv file."""
    work_dir_p = pathlib.Path(work_dir)
    work_dir_p.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Load config & inject device and output path
    # ------------------------------------------------------------------
    if config_path:
        config = BERTMapPipeline.load_bertmap_config(config_path)
    else:
        config = BERTMapPipeline.load_bertmap_config(DEFAULT_CONFIG_FILE)

    # DeepOnto config objects are often simple dicts or OmegaConf. Either way we
    # can treat them like attribute access and dict assignment is safe.
    config["device"] = device  # type: ignore[arg-type]
    config.output_path = str(work_dir_p)  # type: ignore[attr-defined]

    logging.info("Selected device: %s", device)

    # ------------------------------------------------------------------
    # Load ontologies & run the pipeline
    # ------------------------------------------------------------------
    logging.info("Loading ontologies …")
    src_onto = Ontology(src_onto_path)
    tgt_onto = Ontology(tgt_onto_path)

    logging.info("Running BERTMap … (this may take a while; GPU utilised where possible)")
    bertmap = BERTMapPipeline(src_onto, tgt_onto, config)
    # instantiation triggers matching by default

    # ------------------------------------------------------------------
    # Locate BERTMap's output mapping file
    # ------------------------------------------------------------------
    match_dir = work_dir_p / ("bertmap" if config.model == "bertmap" else "bertmaplt") / "match"  # type: ignore[attr-defined]
    mapping_file = match_dir / "repaired_mappings.tsv"
    if not mapping_file.exists():
        # fall back to filtered mappings if repair not enabled
        mapping_file = match_dir / "filtered_mappings.tsv"

    if not mapping_file.exists():
        raise FileNotFoundError(f"Could not locate mapping file inside {match_dir}")

    return mapping_file


def mappings_to_ttl(
    mapping_tsv: pathlib.Path,
    src_onto_path: str,
    tgt_onto_path: str,
    ttl_out: str,
) -> None:
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
                src_iri = URIRef(row["SrcEntity"])  # type: ignore[index]
                tgt_iri = URIRef(row["TgtEntity"])  # type: ignore[index]
            else:
                src_iri = URIRef(row[0])  # type: ignore[index]
                tgt_iri = URIRef(row[1])  # type: ignore[index]

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
        description="Compute equivalences between two ontologies with BERTMap (GPU-aware) and write a Turtle alignment.",
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
    parser.add_argument(
        "-d",
        "--device",
        choices=["auto", "cpu", "cuda"] + [f"cuda:{i}" for i in range(torch.cuda.device_count() or 1)],
        default="auto",
        help="Select computation device (default: auto - pick CUDA if available)",
    )

    args = parser.parse_args()
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Resolve device & set environment before heavy imports start initialising CUDA context
    device: Final[str] = _resolve_device(args.device)
    _prepare_environment(device)

    logging.info("torch sees CUDA: %s", torch.cuda.is_available())

    mapping_file = run_bertmap(
        args.src_onto,
        args.tgt_onto,
        args.config,
        args.work_dir,
        device,
    )
    mappings_to_ttl(mapping_file, args.src_onto, args.tgt_onto, args.output)


if __name__ == "__main__":
    main()
