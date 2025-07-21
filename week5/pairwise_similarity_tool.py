#!/usr/bin/env python3
"""pairwise_similarity_tool.py

Unified CLI for analysing OWL2Vec* (or similar) embeddings. Two sub‑commands:

  • ``random`` – sample *k* entities at random, build a cosine‑similarity
    matrix, and display ⁄ save a heat‑map.
  • ``pairs``  – compute cosine similarities for explicit pairs read from a
    plain‑text file.

Usage (place *global* options **after** the sub‑command):

    # 30‑entity heat‑map shown interactively
    python pairwise_similarity_tool.py random --vec model.vec -k 30

    # Compare pairs from file and save results
    python pairwise_similarity_tool.py pairs --vec model.vec \
        --pairs pairs.txt --output similarities.txt
"""
from __future__ import annotations

import argparse
import os
import random
import sys
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

###############################################################################
# Vector‑loading helpers
###############################################################################

def load_vectors_binary(filepath: str) -> KeyedVectors:  # noqa: D401
    """Load *binary* Word2Vec vectors via *gensim*."""
    return KeyedVectors.load_word2vec_format(filepath, binary=True)


def load_vectors_text(filepath: str):  # -> TextModel
    """Load *text* Word2Vec *.vec* files in a robust manner."""

    vectors: dict[str, np.ndarray] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) < 2:
                continue

            # Skip common header line: "<num_vectors> <dim>"
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                continue

            entity = parts[0]
            try:
                vector = np.array([float(x) for x in parts[1:]], dtype=np.float32)
            except ValueError:
                print(
                    f"Warning: line {lineno}: could not parse vector for '{entity}', skipped.",
                    file=sys.stderr,
                )
                continue
            vectors[entity] = vector

    class TextModel(dict):
        """Tiny wrapper that mimics the subset of *KeyedVectors* we need."""

        @property  # noqa: D401
        def key_to_index(self):  # type: ignore[override]
            return {k: i for i, k in enumerate(self.keys())}

        def __getitem__(self, key):  # type: ignore[override]
            if key not in self:
                raise KeyError(key)
            return super().__getitem__(key)

    return TextModel(vectors)  # type: ignore[return-value]


def load_vectors(filepath: str, binary: bool):  # -> KeyedVectors | TextModel
    """Choose binary or text loader based on flag."""
    return load_vectors_binary(filepath) if binary else load_vectors_text(filepath)

###############################################################################
# Random‑sampling helpers
###############################################################################

def sample_entities(model, k: int) -> List[str]:
    vocab = list(model.key_to_index.keys())
    if k > len(vocab):
        raise ValueError(f"Model contains only {len(vocab)} entities; cannot sample {k}.")
    return random.sample(vocab, k)


def build_similarity_matrix(model, entities: Sequence[str]) -> np.ndarray:
    matrix = np.vstack([model[e] for e in entities])
    return cosine_similarity(matrix)

def plot_similarity(sim_matrix: np.ndarray, entities: Sequence[str], output: str | None = None) -> None:
    fname, fmt = None, None
    if output:
        root, ext = os.path.splitext(output)
        ext = ext.lower().lstrip(".")
        supported = {
            "eps",
            "jpeg",
            "jpg",
            "pdf",
            "pgf",
            "png",
            "ps",
            "raw",
            "rgba",
            "svg",
            "svgz",
            "tif",
            "tiff",
            "webp",
        }
        if ext in supported:
            fname, fmt = output, ext
        else:
            fname, fmt = f"{root}.png", "png"
            print(
                f"Warning: extension '.{ext}' not recognised – falling back to PNG at '{fname}'.",
                file=sys.stderr,
            )

    plt.figure(figsize=(10, 8))
    im = plt.imshow(sim_matrix, vmin=-1, vmax=1, cmap="coolwarm")
    plt.colorbar(im, label="Cosine similarity")
    plt.xticks(range(len(entities)), entities, rotation=90, fontsize=7)
    plt.yticks(range(len(entities)), entities, fontsize=7)
    plt.title(f"Pairwise Cosine Similarity (n={len(entities)})")
    plt.tight_layout()

    if fname:
        plt.savefig(fname, dpi=300, format=fmt)
        print(f"Heat‑map saved to '{fname}'.")
    else:
        plt.show()

###############################################################################
# Explicit‑pairs helpers
###############################################################################

def read_pairs(filepath: str) -> List[Tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) < 2:
                print(f"Warning: line {lineno} in pairs file has <2 tokens, skipped.", file=sys.stderr)
                continue
            pairs.append((parts[0], parts[1]))
    if not pairs:
        raise ValueError("No valid pairs found in the file.")
    return pairs


def compute_similarity_and_distance(v1: np.ndarray, v2: np.ndarray) -> Tuple[float, float]:
    sim = float(cosine_similarity(v1.reshape(1, -1), v2.reshape(1, -1))[0][0])
    dist = float(euclidean_distances(v1.reshape(1, -1), v2.reshape(1, -1))[0][0])
    return sim, dist


def compare_entity_pairs(model, pairs: Iterable[Tuple[str, str]]) -> List[str]:
    results: list[str] = []
    for e1, e2 in pairs:
        try:
            sim, dist = compute_similarity_and_distance(model[e1], model[e2])
            line = f"Pair({e1}, {e2}): Cosine = {sim:.4f}, Euclidean = {dist:.4f}"
        except KeyError as ke:
            line = f"Missing vector for '{ke.args[0]}'"
        print(line)
        results.append(line)
    return results

###############################################################################
# Argument parsing (flags *after* the sub‑command)
###############################################################################

def build_parser() -> argparse.ArgumentParser:  # noqa: D401
    parser = argparse.ArgumentParser(
        prog="pairwise_similarity_tool.py",
        description="Analyse embedding spaces either randomly or for explicit pairs.",
    )

    # ---------------------------------------------------------------- sub‑parsers
    subparsers = parser.add_subparsers(dest="mode", metavar="{random,pairs}")

    # Common options for both modes
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--vec", required=True, help="Path to *.vec* file (text or binary).")
    common.add_argument("--binary", action="store_true", help="Treat --vec as binary word2vec.")

    # random ----------------------------------------------------------
    p_random = subparsers.add_parser(
        "random",
        help="Sample *k* random entities and plot a heat‑map.",
        parents=[common],
        add_help=True,
    )
    p_random.add_argument("-k", type=int, default=20, help="How many entities to sample (default 20).")
    p_random.add_argument("--output", help="Optional path to save the heat‑map image.")

    # pairs -----------------------------------------------------------
    p_pairs = subparsers.add_parser(
        "pairs",
        help="Compare explicit entity pairs from a file.",
        parents=[common],
        add_help=True,
    )
    p_pairs.add_argument("--pairs", required=True, help="Text file containing entity pairs.")
    p_pairs.add_argument("--output", help="Optional path to save the similarity results.")

    return parser


def parse_args() -> argparse.Namespace:  # noqa: D401
    parser = build_parser()
    args = parser.parse_args()

    # Manual enforcement for Python <3.7 (sub‑parser required flag missing)
    if args.mode is None:
        parser.error("please specify a sub‑command: 'random' or 'pairs'")
    return args

###############################################################################
# Main entry‑point
###############################################################################

def main() -> None:  # noqa: D401
    args = parse_args()

    print("Loading vectors…")
    model = load_vectors(args.vec, binary=args.binary)
    print(f"Loaded {len(model.key_to_index)} vectors.")

    if args.mode == "random":
        entities = sample_entities(model, k=args.k)
        sim_matrix = build_similarity_matrix(model, entities)
        plot_similarity(sim_matrix, entities, output=args.output)

    elif args.mode == "pairs":
        pairs = read_pairs(args.pairs)
        results = compare_entity_pairs(model, pairs)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("\n".join(results))
            print(f"Results written to '{args.output}'.")

    else:  # pragma: no cover
        raise RuntimeError("Unreachable: unknown mode.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("Interrupted by user.")
