#!/usr/bin/env python3
"""
Compute **equivalence alignments** (BERTMap) *and* **subsumption alignments** (BERTSubs)
for two OWL ontologies with **DeepOnto**, exporting results in Turtle.

Key points
~~~~~~~~~~
* Uses **BERTMapPipeline** for ≡ relations with its shipped default YAML.
* Uses **BERTSubsInterPipeline** for ⊑/⊒ relations - there is **no default YAML** for
  this model, so you must either pass one via `--subs-config` or let the script fall
  back to *built-in* hyper-parameters provided programmatically by the pipeline.
* Fully GPU-aware via a `--device` option (`auto`, `cpu`, `cuda`, or `cuda:N`).
* Generates two TTL files: one for equivalences, one for subsumption triples.

Example call
~~~~~~~~~~~~
```bash
python bertmap_alignment.py src.owl tgt.owl \
       --output equivalences.ttl \
       --subs-output subsumptions.ttl \
       --device cuda:0               # optional (default: auto)
       --config my_bertmap.yaml      # optional custom BERTMap config
       --subs-config my_bertsubs.yaml# optional custom BERTSubs config
       --work-dir bertmap_work       # optional work dir
```
"""

from __future__ import annotations

import argparse
import csv
import logging
import os
import pathlib
from typing import Final, MutableMapping

import torch
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS, OWL

from deeponto.onto import Ontology
from deeponto.align.bertmap import BERTMapPipeline, DEFAULT_CONFIG_FILE as BM_DEFAULT_CFG
from deeponto.align.bertsubs import BERTSubsInterPipeline, DEFAULT_CONFIG_FILE_INTER as BS_DEFAULT_CFG

#######################################################################################
# Device helpers                                                                      #
#######################################################################################

def _resolve_device(cli_choice: str) -> str:
    """Resolve requested device from CLI into a valid torch device string."""
    if cli_choice == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"

    if cli_choice.startswith("cuda"):
        if not torch.cuda.is_available():
            logging.warning("CUDA requested but no GPU visible → falling back to CPU")
            return "cpu"
        return cli_choice  # allow cuda, cuda:0, cuda:1 …

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

#######################################################################################
# Config helpers                                                                      #
#######################################################################################

def _load_config(
    pipeline_cls,
    user_cfg_path: str | None,
    default_cfg_path: str | None,
    device: str,
) -> MutableMapping[str, object]:
    """Load DeepOnto YAML config or construct a reasonable default.

    The priority is:
    1. **User-supplied file** via CLI
    2. **Library-shipped YAML** (e.g. BERTMap's `DEFAULT_CONFIG_FILE`)
    3. **Programmatic defaults** provided by the pipeline class (if available)
    4. Empty dict → pipeline should rely on hard-coded defaults internally
    """

    config: MutableMapping[str, object]

    if user_cfg_path:
        config = pipeline_cls.load_bertmap_config(user_cfg_path)  # type: ignore[attr-defined]
        logging.info("Loaded %s config from %s", pipeline_cls.__name__, user_cfg_path)
    elif default_cfg_path and pathlib.Path(default_cfg_path).exists():
        config = pipeline_cls.load_bertmap_config(default_cfg_path)  # type: ignore[attr-defined]
        logging.info("Loaded default %s config from %s", pipeline_cls.__name__, default_cfg_path)
    elif hasattr(pipeline_cls, "get_default_config"):
        # Newer DeepOnto versions expose programmatic defaults
        config = pipeline_cls.get_default_config()  # type: ignore[attr-defined]
        logging.info("Using built-in default config for %s", pipeline_cls.__name__)
    else:
        config = {}  # type: ignore[assignment]
        logging.warning(
            "Running %s with *minimal* defaults - consider supplying a YAML config!",
            pipeline_cls.__name__,
        )

    # Inject/override desired device for all downstream models
    config["device"] = device
    return config

#######################################################################################
# Alignment pipelines                                                                 #
#######################################################################################

def run_bertmap(
    src_onto_path: str,
    tgt_onto_path: str,
    user_cfg_path: str | None,
    work_dir: str,
    device: str,
) -> pathlib.Path:
    """Run **BERTMap** and return path to its final TSV mapping file."""

    work_dir_p = pathlib.Path(work_dir)
    work_dir_p.mkdir(parents=True, exist_ok=True)

    # Load config & inject device
    config = _load_config(BERTMapPipeline, user_cfg_path, BM_DEFAULT_CFG, device)
    config["output_path"] = str(work_dir_p)

    logging.info("Selected device for BERTMap: %s", device)

    # Load ontologies & execute pipeline
    logging.info("Loading ontologies for BERTMap …")
    src_onto = Ontology(src_onto_path)
    tgt_onto = Ontology(tgt_onto_path)
    logging.info("Running BERTMap … (GPU used where available)")
    _ = BERTMapPipeline(src_onto, tgt_onto, config)

    # Locate output mapping file
    match_dir = work_dir_p / "bertmap" / "match"
    mapping_file = _pick_mapping_file(match_dir)
    return mapping_file


def run_bertsubs(
    src_onto_path: str,
    tgt_onto_path: str,
    user_cfg_path: str | None,
    work_dir: str,
    device: str,
) -> pathlib.Path:
    """Run **BERTSubsInterPipeline** and return path to its final TSV mapping file."""

    work_dir_p = pathlib.Path(work_dir)
    work_dir_p.mkdir(parents=True, exist_ok=True)

    logging.info("Selected device for BERTSubs: %s", device)

    # Load ontologies & execute pipeline
    logging.info("Loading ontologies for BERTSubs …")
    src_onto = Ontology(src_onto_path)
    tgt_onto = Ontology(tgt_onto_path)
    logging.info("Running BERTSubs … (GPU used where available)")
    _ = BERTSubsInterPipeline(src_onto, tgt_onto, BS_DEFAULT_CFG)

    # Locate output mapping file
    match_dir = work_dir_p / "bertsubs" / "match"
    mapping_file = _pick_mapping_file(match_dir)
    return mapping_file


#######################################################################################
# Utility helpers                                                                     #
#######################################################################################

def _pick_mapping_file(match_dir: pathlib.Path) -> pathlib.Path:
    """Return the best available mapping file produced by DeepOnto."""
    f = match_dir / "logmap-repair" / "mappings_repaired_with_LogMap.tsv"
    if f.exists():
        return f

    f = match_dir / "repaired_mappings.tsv"
    if f.exists():
        return f

    f = match_dir / "filtered_mappings.tsv"
    if f.exists():
        return f

    raise FileNotFoundError(f"Could not locate mapping file in {match_dir}")


#######################################################################################
# Conversion helpers                                                                  #
#######################################################################################

def mappings_to_ttl(
    mapping_tsv: pathlib.Path,
    src_onto_path: str,
    tgt_onto_path: str,
    ttl_out: str,
    predicate_decider,
) -> None:
    """Convert a DeepOnto TSV mapping into Turtle triples using *predicate_decider*."""

    src_graph = Graph().parse(src_onto_path)
    tgt_graph = Graph().parse(tgt_onto_path)
    out_graph = Graph()
    out_graph.bind("owl", OWL)
    out_graph.bind("rdfs", RDFS)

    with mapping_tsv.open(encoding="utf8") as f:
        # Flexible reader: DeepOnto may include headers starting with SrcEntity	TgtEntity…
        reader = csv.DictReader(f, delimiter="\t")
        has_header = reader.fieldnames is not None and set(reader.fieldnames) >= {"SrcEntity", "TgtEntity"}

        if not has_header:
            # Reset file pointer and treat TSV as plain 2-column without header
            f.seek(0)
            reader = csv.reader(f, delimiter="\t")  # type: ignore[assignment]

        for row in reader:  # type: ignore[arg-type]
            src_iri, tgt_iri = (
                (URIRef(row["SrcEntity"]), URIRef(row["TgtEntity"]))  # type: ignore[index]
                if has_header
                else (URIRef(row[0]), URIRef(row[1]))  # type: ignore[index]
            )

            pred = predicate_decider(src_iri, tgt_iri, src_graph, tgt_graph)
            out_graph.add((src_iri, pred, tgt_iri))

    out_graph.serialize(destination=ttl_out, format="turtle")
    logging.info("Saved %d triples to %s", len(out_graph), ttl_out)


# ------------------------------------------------------------------
# Predicate deciders for equivalence vs. subsumption
# ------------------------------------------------------------------

def _equiv_predicate(src, tgt, src_g, tgt_g):  # noqa: N802
    if (
        (src, RDF.type, OWL.ObjectProperty) in src_g
        or (tgt, RDF.type, OWL.ObjectProperty) in tgt_g
        or (src, RDF.type, OWL.DatatypeProperty) in src_g
        or (tgt, RDF.type, OWL.DatatypeProperty) in tgt_g
    ):
        return OWL.equivalentProperty
    return OWL.equivalentClass


def _subs_predicate(src, tgt, src_g, tgt_g):  # noqa: N802
    if (
        (src, RDF.type, OWL.ObjectProperty) in src_g
        or (tgt, RDF.type, OWL.ObjectProperty) in tgt_g
        or (src, RDF.type, OWL.DatatypeProperty) in src_g
        or (tgt, RDF.type, OWL.DatatypeProperty) in tgt_g
    ):
        return RDFS.subPropertyOf
    return RDFS.subClassOf

#######################################################################################
# Main CLI                                                                            #
#######################################################################################

def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Compute equivalence (BERTMap) *and* subsumption (BERTSubs) alignments "
            "between two ontologies (GPU-aware) and export Turtle triples."
        ),
    )
    parser.add_argument("src_onto", help="Source ontology file (.owl/.xml/.ttl/…)")
    parser.add_argument("tgt_onto", help="Target ontology file (.owl/.xml/.ttl/…)")

    # Output files
    parser.add_argument(
        "-o",
        "--output",
        default="equivalences.ttl",
        help="Output TTL file for equivalence triples (default: equivalences.ttl)",
    )
    parser.add_argument(
        "-s",
        "--subs-output",
        default="subsumptions.ttl",
        help="Output TTL file for subsumption triples (default: subsumptions.ttl)",
    )

    # Configs & work dir
    parser.add_argument("-c", "--config", help="YAML config for BERTMap", default=None)
    parser.add_argument("--subs-config", help="YAML config for BERTSubs", default=None)
    parser.add_argument(
        "-w", "--work-dir", help="Working directory to store DeepOnto outputs", default="bertmap_work"
    )

    # Device handling
    parser.add_argument(
        "-d",
        "--device",
        choices=["auto", "cpu", "cuda"] + [f"cuda:{i}" for i in range(torch.cuda.device_count() or 1)],
        default="auto",
        help="Computation device (default: auto → choose CUDA if available)",
    )

    args = parser.parse_args()
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Resolve device early (before heavy imports cause CUDA initialisation)
    device: Final[str] = _resolve_device(args.device)
    _prepare_environment(device)
    logging.info("torch sees CUDA available: %s", torch.cuda.is_available())

    # ------------------------------------------------------------------
    # BERTMap equivalence alignment
    # ------------------------------------------------------------------
    bm_mapping_file = run_bertmap(
        args.src_onto,
        args.tgt_onto,
        args.config,
        args.work_dir,
        device,
    )
    mappings_to_ttl(
        bm_mapping_file,
        args.src_onto,
        args.tgt_onto,
        args.output,
        _equiv_predicate,
    )

    # ------------------------------------------------------------------
    # BERTSubs subsumption alignment
    # ------------------------------------------------------------------
    bs_mapping_file = run_bertsubs(
        args.src_onto,
        args.tgt_onto,
        args.subs_config,
        args.work_dir,
        device,
    )
    mappings_to_ttl(
        bs_mapping_file,
        args.src_onto,
        args.tgt_onto,
        args.subs_output,
        _subs_predicate,
    )


if __name__ == "__main__":
    main()
