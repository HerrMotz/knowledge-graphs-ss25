#!/usr/bin/env python3
"""owl2vec_pipeline.py – one‑shot OWL2Vec* runner

• Merges an ontology (RDF/XML) with generated data (Turtle)
• Runs OWL2Vec* twice (two configs)
• Relocates its fixed‑name output files into a tidy results folder
• Repairs OWL2Vec* vector text (missing header, spaces in labels)

Usage
-----
$ python owl2vec_pipeline.py path/to/ontology.owl path/to/data.ttl \
                          --outdir embeddings --sample 500

Resulting *embeddings/* directory::
    merged.owl
    cfg1.vec.txt   cfg1.vec.bin
    cfg2.vec.txt   cfg2.vec.bin
"""

from __future__ import annotations

import argparse
import configparser
import logging
import random
import shutil
import subprocess
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
    """Guess rdflib parser format from file extension."""
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
    logging.info("Loading ontology … %s", onto_file)
    g.parse(str(onto_file), format=_rdf_format(onto_file))

    g_data = rdflib.Graph()
    logging.info("Loading data     … %s", data_file)
    g_data.parse(str(data_file), format=_rdf_format(data_file))

    if sample_triples is not None and sample_triples < len(g_data):
        logging.info("Sampling %d of %d data triples", sample_triples, len(g_data))
        triples = random.sample(list(g_data), sample_triples)
    else:
        triples = list(g_data)

    for t in triples:
        g.add(t)

    g.serialize(str(dest_file), format="xml")
    logging.info("Merged graph saved → %s  (%d triples)", dest_file.name, len(g))

# ---------------------------------------------------------------------------
# OWL2Vec* configuration helpers
# ---------------------------------------------------------------------------


def _cache_dir_for(outfile: Path) -> Path:
    """Return a per‑configuration cache directory path."""
    return outfile.parent / f"{outfile.stem}_cache"


def write_cfg(merged_owl: Path, *, embed_size: int, walk_depth: int,
              reasoner: Optional[str], outfile: Path) -> Path:
    """Write OWL2Vec* INI config. Return the cache dir path."""
    cache_dir = _cache_dir_for(outfile)
    cfg = configparser.ConfigParser()

    cfg["BASIC"] = {"ontology_file": str(merged_owl)}
    cfg["DOCUMENT"] = {
        "cache_dir": str(cache_dir),
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
    logging.info("Config written → %s", outfile.name)
    return cache_dir

# ---------------------------------------------------------------------------
# Vector‑file post‑processing helpers
# ---------------------------------------------------------------------------


def _sanitize_word2vec_file(src: Path, dst: Path, vect_dim: int) -> None:
    """Rewrite *src* so tokens are single words (spaces→underscores) and save to *dst*."""
    with src.open("r", encoding="utf8") as fin, dst.open("w", encoding="utf8") as fout:
        header = fin.readline().strip().split()
        if len(header) == 2 and header[0].isdigit() and header[1].isdigit():
            total, dim = map(int, header)
            if dim != vect_dim:
                logging.warning("Header dimension %d differs from expected %d", dim, vect_dim)
            fout.write(f"{total} {vect_dim}\n")
        else:
            # Missing header – caller handles later; rewind.
            fin.seek(0)
        for line in fin:
            parts = line.rstrip().split()
            if len(parts) < vect_dim + 1:
                logging.debug("Skipping malformed line: %s", line[:80])
                continue
            token_parts = parts[: len(parts) - vect_dim]
            vec_parts = parts[-vect_dim:]
            token = "_".join(token_parts)
            fout.write(token + " " + " ".join(vec_parts) + "\n")


def _load_vectors_resilient(txt_path: Path) -> KeyedVectors:
    """Load Word2Vec text, repairing header + token issues common in OWL2Vec*."""
    try:
        return KeyedVectors.load_word2vec_format(txt_path, binary=False)
    except (ValueError, IndexError):
        # Either missing header or spaces in token names.
        with txt_path.open("r", encoding="utf8") as fin:
            first_non_blank = next((l for l in fin if l.strip()), "")
        items = first_non_blank.rstrip().split()
        vect_dim = len(items) - 1  # rough guess

        # Ensure header exists
        header_added = False
        with txt_path.open("r", encoding="utf8") as fin:
            first_line = fin.readline()
            if not (first_line.strip().split()[:2] and first_line.strip().split()[0].isdigit()):
                header_added = True

        temp_with_header = txt_path.with_suffix(".hdr") if header_added else txt_path
        if header_added:
            with txt_path.open("r", encoding="utf8") as fin, temp_with_header.open("w", encoding="utf8") as fout:
                data_lines = [l for l in fin if l.strip()]
                fout.write(f"{len(data_lines)} {vect_dim}\n")
                fout.writelines(data_lines)

        # Sanitize tokens containing spaces
        sanitized = txt_path.with_suffix(".san")
        _sanitize_word2vec_file(temp_with_header, sanitized, vect_dim)
        kv = KeyedVectors.load_word2vec_format(sanitized, binary=False)

        sanitized.unlink(missing_ok=True)
        if header_added and temp_with_header != txt_path:
            temp_with_header.unlink(missing_ok=True)
        return kv

# ---------------------------------------------------------------------------
# OWL2Vec* runner
# ---------------------------------------------------------------------------


def run_owl2vec(cfg_file: Path, cache_dir: Path, output_prefix: Path) -> None:
    """Run OWL2Vec* and relocate its embeddings to *output_prefix*.* files."""

    logging.info("Running OWL2Vec* – %s", cfg_file.stem)
    subprocess.run(["owl2vec_star", "standalone", "--config_file", str(cfg_file)], check=True)

    output_dir = cache_dir / "output"
    txt_files = sorted(output_dir.glob("*.embeddings.txt"))
    if not txt_files:
        logging.error("No embeddings produced in %s", output_dir)
        return

    txt_src = txt_files[0]
    txt_dst = output_prefix.with_suffix(".vec.txt")
    bin_dst = output_prefix.with_suffix(".vec.bin")

    shutil.copy2(txt_src, txt_dst)
    logging.info("Copied vectors → %s", txt_dst.relative_to(output_prefix.parent))

    kv = _load_vectors_resilient(txt_dst)
    kv.save_word2vec_format(bin_dst, binary=True)
    logging.info("Converted to binary → %s", bin_dst.relative_to(output_prefix.parent))

# ---------------------------------------------------------------------------
# CLI entry‑point
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> None:
    p = argparse.ArgumentParser(description="Merge ontology + data and run OWL2Vec* twice")
    p.add_argument("ontology", type=Path, help="Ontology file (RDF/XML)")
    p.add_argument("data", type=Path, help="Generated data (Turtle)")
    p.add_argument("--outdir", type=Path, default=Path("owl2vec_output"), help="Results directory")
    p.add_argument("--sample", type=int, default=500, help="Max triples from data for speed")
    args = p.parse_args(argv)

    args.outdir.mkdir(parents=True, exist_ok=True)

    merged = args.outdir / "merged.owl"
    merge_graphs(args.ontology, args.data, sample_triples=args.sample, dest_file=merged)

    # Config 1
    cfg1 = args.outdir / "cfg1.ini"
    cache1 = write_cfg(merged, embed_size=200, walk_depth=2, reasoner=None, outfile=cfg1)
    run_owl2vec(cfg1, cache1, args.outdir / "cfg1")

    # Config 2
    cfg2 = args.outdir / "cfg2.ini"
    cache2 = write_cfg(merged, embed_size=400, walk_depth=4, reasoner="elk", outfile=cfg2)
    run_owl2vec(cfg2, cache2, args.outdir / "cfg2")

    logging.info("All done ✔︎  Embeddings in %s", args.outdir)


if __name__ == "__main__":
    main()
