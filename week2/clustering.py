#!/usr/bin/env python
"""
Two‑step pizza‑menu clustering
  1. Cluster menu items into pizza types.
  2. Build a 2‑level ingredient hierarchy.
Embedding backend: Hugging Face Sentence‑Transformers only.
"""

from __future__ import annotations
import re, itertools, json
from collections import defaultdict
from typing import List, Dict, Set

import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer

# ─────────────────────── CONFIG ───────────────────────
HF_MODEL_NAME      = "sentence-transformers/all-mpnet-base-v2"      # 768‑d embeddings
COARSE_THRESHOLD   = 0.55   # similarity edge cutoff for Level‑1 graph
FINE_THRESHOLD     = 0.25   # distance cutoff for synonym merge (Level‑2)
GENERIC_TOKENS     = {"cheese", "sauce", "fresh", "dried"}          # adjust for your data
RANDOM_SEED        = 42

# ───────────────────── SAMPLE DATA ─────────────────────
menu_items = [
    {"name": "Pizza Margherita",       "ingredients": ["mozzarella cheese", "tomato", "basil"]},
    {"name": "Pizza Margherita XL",    "ingredients": ["mozzarella", "tomato sauce", "basil"]},
    {"name": "Pepperoni Pizza",        "ingredients": ["pepperoni", "mozzarella", "tomato sauce"]},
    {"name": "Sun‑Dried Tomato Pizza", "ingredients": ["sun dried tomato", "mozzarella", "oregano"]},
]

# ──────────────────── HELPERS ──────────────────────────
def normalize(term: str) -> str:
    """Lower‑case, strip punctuation, remove generic tokens."""
    term = re.sub(r"[^a-zA-Z\s]", " ", term.lower()).strip()
    return " ".join(w for w in term.split() if w not in GENERIC_TOKENS)

def embed(texts: List[str], model_name: str = HF_MODEL_NAME) -> np.ndarray:
    """Return embeddings from a Sentence‑Transformer model."""
    model = SentenceTransformer(model_name, device="cpu")
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

# ───────────── PIZZA‑TYPE CLUSTERING ─────────────
# Build vocabulary and binary vectors
vocab: Set[str] = {normalize(ing) for item in menu_items for ing in item["ingredients"]}
vocab = sorted(vocab)

pizza_vecs, pizza_names = [], []
for item in menu_items:
    norm_set = {normalize(ing) for ing in item["ingredients"]}
    pizza_vecs.append([1 if v in norm_set else 0 for v in vocab])
    pizza_names.append(item["name"])
pizza_vecs = np.array(pizza_vecs, dtype=int)

pizza_clusterer = AgglomerativeClustering(
    linkage="average", metric="cosine",
    distance_threshold=1.1, n_clusters=None
).fit(pizza_vecs)

pizza_types: Dict[int, List[str]] = defaultdict(list)
for n, lbl in zip(pizza_names, pizza_clusterer.labels_):
    pizza_types[lbl].append(n)

# ───────────── INGREDIENT HIERARCHY ──────────────
# 2‑a. Contextual sentences
ingredient_context: Dict[str, Set[str]] = defaultdict(set)
for item in menu_items:
    for ing in item["ingredients"]:
        ingredient_context[normalize(ing)].add(item["name"])

ing_keys: List[str] = sorted(ingredient_context)
sentences = [
    f"{ing} in {', '.join(sorted(ingredient_context[ing]))}" for ing in ing_keys
]

embeddings = embed(sentences)
distance = cosine_distances(embeddings)
similarity = 1 - distance

# 2‑b. Level‑1 categories via Louvain on similarity graph
G = nx.Graph()
for i, j in itertools.combinations(range(len(ing_keys)), 2):
    if similarity[i, j] >= (1 - COARSE_THRESHOLD):
        G.add_edge(i, j, weight=float(similarity[i, j]))

communities = nx.algorithms.community.louvain.louvain_communities(
    G, weight="weight", seed=RANDOM_SEED
)
level1: Dict[int, List[str]] = {
    idx: [ing_keys[i] for i in sorted(c)] for idx, c in enumerate(communities)
}

# 2‑c. Level‑2 synonym clusters (tight merge)
syn_clusterer = AgglomerativeClustering(
    linkage="average", metric="cosine",
    distance_threshold=FINE_THRESHOLD, n_clusters=None
).fit(embeddings)

level2: Dict[int, List[str]] = defaultdict(list)
for ing, lbl in zip(ing_keys, syn_clusterer.labels_):
    level2[lbl].append(ing)

# Canonical spellings: choose shortest form in each Level‑2 cluster
canonical_map = {ing: min(group, key=len) for group in level2.values() for ing in group}

# ───────────── OUTPUT ──────────────
print("\n🍕 Pizza‑type clusters")
print(json.dumps(pizza_types, indent=2, ensure_ascii=False))

print("\n🌳 Ingredient hierarchy – Level 1 (broad categories)")
print(json.dumps(level1, indent=2, ensure_ascii=False))

print("\n🪢 Ingredient hierarchy – Level 2 (synonyms)")
print(json.dumps(level2, indent=2, ensure_ascii=False))

print("\n✅ Canonical ingredient mapping (sample)")
for k, v in list(canonical_map.items())[:10]:
    print(f"{k:<25} → {v}")
