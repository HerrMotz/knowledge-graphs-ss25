#!/usr/bin/env python3
"""pairwise_similarity_tool.py

A unified utility that can either:
  • SAMPLE *k* random entities from an embedding model, build a full cosine‑similarity
    matrix and (optionally) save a heat‑map.
  • COMPARE an arbitrary list of entity pairs (provided in a plain‑text file) and
    print/save their individual cosine similarities.

The script supports both binary and text Word2Vec‑style *.vec* files produced by
OWL2Vec*, Onto2Vec, etc.  The text loader is tolerant of header lines and minor
format issues.

Usage examples
--------------
Random heat‑map of 30 entities and save as PNG::

    python pairwise_similarity_tool.py random --vec model.vec -k 30 \
        --output heatmap.png

Compare explicit pairs listed in *pairs.txt* and write results::

    python pairwise_similarity_tool.py pairs --vec model.vec \
        --pairs pairs.txt --output similarities.txt

pairs.txt should contain ONE pair per line, separated by whitespace, e.g.::

    margherita pizza
    mozzarella kaese
    zutat tomatensauce
"""
from __future__ import annotations

import argparse
import os
import random
from typing import Iterable, List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
from gensim.models import KeyedVectors
from sklearn.metrics.pairwise import cosine_similarity

###############################################################################
# Loading helpers
###############################################################################

def load_vectors_binary(filepath: str) -> KeyedVectors:  # noqa: D401
    """Load **binary** Word2Vec vectors with *gensim*."""
    return KeyedVectors.load_word2vec_format(filepath, binary=True)


def load_vectors_text(filepath: str) -> "TextModel":  # noqa: D401
    """Load a **text** Word2Vec/*.vec* file into a lightweight mapping.

    The implementation is defensive: it gracefully skips header lines such as
    ``"1000000 300"`` as well as malformed entries.
    """

    vectors: dict[str, np.ndarray] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) < 2:
                continue  # blank or garbage line

            # Detect common header line ("num_vectors dim")
            if len(parts) == 2 and all(p.isdigit() for p in parts):
                continue

            entity = parts[0]
            try:
                vector = np.array([float(x) for x in parts[1:]], dtype=np.float32)
            except ValueError:
                print(
                    f"Warning: Skipping line {lineno} – could not parse vector for '{entity}'."
                )
                continue
            vectors[entity] = vector

    class TextModel(dict):
        """Minimal dict‑like wrapper mimicking *KeyedVectors* where needed."""

        # gensim models expose *key_to_index*
        @property
        def key_to_index(self):  # type: ignore[override]
            return {k: i for i, k in enumerate(self.keys())}

        def __getitem__(self, key):  # type: ignore[override]
            if key not in self:
                raise KeyError(key)
            return super().__getitem__(key)

    return TextModel(vectors)  # type: ignore[return-value]


def load_vectors(filepath: str, binary: bool) -> "KeyedVectors | TextModel":
    """Dispatcher picking the right loader based on *binary* flag."""
    if binary:
        return load_vectors_binary(filepath)
    return load_vectors_text(filepath)

###############################################################################
# Random‑sampling functionality
###############################################################################

def sample_entities(model: "KeyedVectors | TextModel", k: int) -> List[str]:
    """Return *k* distinct random entity IDs from the model vocabulary."""
    vocab = list(model.key_to_index.keys())
    if k > len(vocab):
        raise ValueError(f"Model contains only {len(vocab)} entities; cannot sample {k}.")
    return random.sample(vocab, k)


def build_similarity_matrix(model: "KeyedVectors | TextModel", entities: Sequence[str]) -> np.ndarray:
    """Stack the vectors & compute a square cosine‑similarity matrix."""
    matrix = np.vstack([model[e] for e in entities])  # shape: (k, dim)
    return cosine_similarity(matrix)


def plot_similarity(sim_matrix: np.ndarray, entities: Sequence[str], output: str | None = None) -> None:
    """Render a heat‑map of *sim_matrix*; save to *output* if provided."""
    # Determine output filename & format
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
            print(f"Warning: Unknown image extension '.{ext}' – saving as PNG to '{fname}'.")

    plt.figure(figsize=(10, 8))
    im = plt.imshow(sim_matrix, vmin=-1, vmax=1, cmap="coolwarm")
    plt.colorbar(im, label="Cosine similarity")
    plt.xticks(range(len(entities)), entities, rotation=90, fontsize=8)
    plt.yticks(range(len(entities)), entities, fontsize=8)
    plt.title(f"Pairwise Cosine Similarity (n={len(entities)})")
    plt.tight_layout()

    if fname:  # save silently
        plt.savefig(fname, dpi=300, format=fmt)
        print(f"Saved heat‑map to '{fname}'.")
    else:  # interactive
        plt.show()

###############################################################################
# Explicit‑pairs functionality
###############################################################################

def read_pairs(filepath: str) -> List[Tuple[str, str]]:
    """Read whitespace‑separated entity pairs from *filepath*."""
    pairs: list[tuple[str, str]] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            parts = line.strip().split()
            if len(parts) < 2:
                print(f"Warning: Line {lineno} in pairs file has <2 tokens – skipped.")
                continue
            pairs.append((parts[0], parts[1]))
    if not pairs:
        raise ValueError("Pairs file contained no valid pairs.")
    return pairs


def compute_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    return float(cosine_similarity(v1.reshape(1, -1), v2.reshape(1, -1))[0][0])


def compare_entity_pairs(model: "KeyedVectors | TextModel", pairs: Iterable[Tuple[str, str]]) -> List[str]:
    """Compute similarities for each *(e1, e2)*; return pretty strings."""
    results: list[str] = []
    for e1, e2 in pairs:
        try:
            v1 = model[e1]
            v2 = model[e2]
            sim = compute_similarity(v1, v2)
            line = f"Similarity({e1}, {e2}) = {sim:.4f}"
        except KeyError as ke:
            missing = ke.args[0]
            line = f"Missing vector for '{missing}'."
        print(line)
        results.append(line)
    return results

###############################################################################
# Main CLI
###############################################################################

def parse_args() -> argparse.Namespace:  # noqa: D401
    parser = argparse.ArgumentParser(
        description="Compare OWL2Vec* embeddings either randomly or for explicit pairs.",
    )

    # Global / shared options
    parser.add_argument("--vec", required=True, help="Path to *.vec* file (text or binary).")
    parser.add_argument(
        "--binary",
        action="store_true",
        help="Treat --vec as binary word2vec format (default: text).",
    )

    sub = parser.add_subparsers(dest="mode", required=True, help="Select operation mode.")

    # RANDOM MODE ----------------------------------------------------------------
    p_random = sub.add_parser("random", help="Sample *k* random entities & plot heat‑map.")
    p_random.add_argument("-k", type=int, default=20, help="Number of entities to sample (default: 20).")
    p_random.add_argument(
        "--output",
        help="Optional path to save the heat‑map. If omitted the plot pops up interactively.",
    )

    # PAIRS MODE ------------------------------------------------------------------
    p_pairs = sub.add_parser("pairs", help="Compare specific entity pairs from a file.")
    p_pairs.add_argument("--pairs", required=True, help="Text file containing entity pairs.")
    p_pairs.add_argument(
        "--output",
        help="Optional file to write the similarity results (one line per pair).",
    )

    return parser.parse_args()


def main() -> None:  # noqa: D401
    args = parse_args()

    # ------------------------ load embedding model ---------------------------
    print("Loading vectors…")
    model = load_vectors(args.vec, binary=args.binary)
    print(f"Loaded {len(model.key_to_index)} vectors.")

    # ------------------------ RANDOM MODE ------------------------------------
    if args.mode == "random":
        print(f"Sampling {args.k} entities at random…")
        entities = sample_entities(model, k=args.k)
        print("Entities:", ", ".join(entities))

        print("Computing similarity matrix…")
        sim_matrix = build_similarity_matrix(model, entities)

        print("Plotting heat‑map…")
        plot_similarity(sim_matrix, entities, output=args.output)

    # ------------------------ PAIRS MODE -------------------------------------
    elif args.mode == "pairs":
        print(f"Reading pairs from '{args.pairs}'…")
        pairs = read_pairs(args.pairs)
        print(f"{len(pairs)} pairs loaded. Computing similarities…")

        results = compare_entity_pairs(model, pairs)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write("\n".join(results))
            print(f"Results written to '{args.output}'.")

    else:  # pragma: no cover
        raise RuntimeError("Unknown mode – this should be unreachable.")


if __name__ == "__main__":
    main()
