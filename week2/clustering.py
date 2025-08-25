#!/usr/bin/env python
"""
Two‑step pizza‑menu clustering (GPU‑ready) with *advanced* cluster naming
  1. Cluster menu items into pizza types.
  2. Build an ingredient hierarchy.
  3. Employ heuristics to name clusters:
     • Pizza‑type clusters → token‑salience scoring (cluster vs. global frequency)
     • Ingredient clusters → embedding‑centroid representative
  4. Store the results in JSON.
  5. (NEW) Visualize ingredient clusters using the already‑computed embeddings,
     with ingredient lists sorted by the plotted color.
"""

from __future__ import annotations
import re, json, os
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_distances
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import torch

# NEW: plotting + TSNE
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from matplotlib.colors import to_hex

# ─────────────────────── CONFIG ───────────────────────
HF_MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"  # 768‑d embeddings
FINE_THRESHOLD = 0.30  # distance cutoff for synonym merge
GENERIC_TOKENS = {"fresh", "dried"}
RANDOM_SEED = 42
OUTPUT_FILE = "cluster_labels.json"

# Basic stop‑words for token‑based labeling (can be expanded)
STOPWORDS = GENERIC_TOKENS | {
    "and", "with", "the", "of", "a", "al", "alla", "di", "la", "le",
    "con", "pizza", "in", "on"
}

# --‑‑‑‑‑ Manual base categories -------------------------------------------------
CATEGORY_KEYWORDS: Dict[str, Set[str]] = {
    "Pepper": {"pepper", "jalapeno", "chili", "bell"},
    "Tomato": {"tomato", "tomatoes"},
    "Nacho": {"tortilla", "nacho"},
    "Hard Cheese": {"parmesan", "romano", "pecorino", "grana"},
    "Soft Cheese": {"mozzarella", "feta", "ricotta", "gorgonzola", "chevre", "brie", "camembert", "cheese"},
    "Meat": {"ham", "salami", "bacon", "prosciutto", "sausage", "chorizo", "pepperoni", "meat"},
    "Sweet": {"pineapple", "apple", "pear", "fig", "honey", "jam", "fruit"},
    "Mushroom": {"mushroom", "portobello", "shiitake", "porcini"},
    "Sauce": {"pesto", "marinara", "salsa", "aioli", "ketchup", "dressing"},
}
UNKNOWN_CATEGORY = "Other"
# ------------------------------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# DEVICE = "cpu"
print(f"[INFO] Using {DEVICE.upper()} for embeddings")

menu_items = json.load(open("menu_items.json", "r", encoding="utf-8"))

# ──────────────────── HELPER FUNCTIONS ──────────────────────────

def normalize(term: str) -> str:
    """Lower‑case, strip punctuation, remove generic tokens."""
    term = re.sub(r"[^a-zA-Z\s]", " ", term.lower()).strip()
    return " ".join(w for w in term.split() if w not in GENERIC_TOKENS)

def tokenize(text: str) -> List[str]:
    """Simple word tokenizer returning lowercase tokens without punctuation."""
    return re.findall(r"[a-zA-Z]+", text.lower())

def embed(texts: List[str], model_name: str = HF_MODEL_NAME, device: str = DEVICE) -> np.ndarray:
    """Return embeddings from a Sentence‑Transformer model on the requested device."""
    model = SentenceTransformer(model_name, device=device)
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)

def assign_category(ingredient: str) -> str:
    for cat, vocab in CATEGORY_KEYWORDS.items():
        if any(tok in ingredient for tok in vocab):
            return cat
    return UNKNOWN_CATEGORY

# ───────────── GLOBAL TOKEN STATS (pizza names) ─────────────
pizza_names = [item["name"] for item in menu_items]
GLOBAL_PIZZA_TOKENS = Counter(tok for name in pizza_names for tok in tokenize(name))

# ───────────── PIZZA‑TYPE CLUSTERING ─────────────

vocab: Set[str] = {normalize(ing) for item in menu_items for ing in item["ingredients"]}
vocab = sorted(vocab)

pizza_vecs, pizza_names = [], []
for item in menu_items:
    norm_set = {normalize(ing) for ing in item["ingredients"]}
    pizza_vecs.append([1 if v in norm_set else 0 for v in vocab])
    pizza_names.append(item["name"])
pizza_vecs = np.array(pizza_vecs, dtype=int)

# --- Drop rows that are all‑zero so cosine distance is well‑defined ----
non_zero_mask = pizza_vecs.sum(axis=1) != 0
X_nz = pizza_vecs[non_zero_mask]
names_nz = [n for n, keep in zip(pizza_names, non_zero_mask) if keep]
names_zero_rows = [n for n, keep in zip(pizza_names, non_zero_mask) if not keep]

pizza_clusterer = AgglomerativeClustering(
    linkage="average", metric="cosine", distance_threshold=1.1, n_clusters=None
).fit(X_nz)

pizza_types: Dict[int, List[str]] = defaultdict(list)
for n, lbl in zip(names_nz, pizza_clusterer.labels_):
    pizza_types[int(lbl)].append(n)

# Put zero‑ingredient pizzas in their own singleton cluster(s)
if names_zero_rows:
    next_lbl = max(pizza_types.keys(), default=-1) + 1
    for n in names_zero_rows:
        pizza_types[next_lbl].append(n)
        next_lbl += 1

# ───────────── INGREDIENT HIERARCHY ──────────────

ingredient_context: Dict[str, Set[str]] = defaultdict(set)
for item in menu_items:
    for ing in item["ingredients"]:
        ingredient_context[normalize(ing)].add(item["name"])

ing_keys: List[str] = sorted(ingredient_context)
sentences = [f"{ing} in {', '.join(sorted(ingredient_context[ing]))}" for ing in ing_keys]

embeddings = embed(sentences)  # <── already computed embeddings (we will reuse for viz)
distance = cosine_distances(embeddings)
similarity = 1 - distance

# clustering via tight agglomerative merge (to be named)
syn_clusterer = AgglomerativeClustering(
    linkage="average", metric="cosine", distance_threshold=FINE_THRESHOLD, n_clusters=None
).fit(embeddings)

level2: Dict[int, List[str]] = defaultdict(list)
for ing, lbl in zip(ing_keys, syn_clusterer.labels_):
    level2[int(lbl)].append(ing)

# ───────────── ADVANCED LABELERS ──────────────

ing_to_idx = {ing: idx for idx, ing in enumerate(ing_keys)}

# ---------- 2a. Bucket ingredients by base category -------------------
category_buckets: Dict[str, List[str]] = defaultdict(list)
for ing in ing_keys:
    category_buckets[assign_category(ing)].append(ing)

# ---------- 2b. Synonym merge *inside each bucket* --------------------
def label_ingredient_cluster(items: List[str]) -> str:
    idxs = [ing_to_idx[i] for i in items]
    vecs = embeddings[idxs]
    centroid = vecs.mean(axis=0, keepdims=True)
    sims = 1 - cosine_distances(vecs, centroid).flatten()
    return items[int(np.argmax(sims))]

def deduplicate(labels_to_items: Dict[str, List[str]]) -> Dict[str, List[str]]:
    used, out = set(), {}
    for lbl, items in labels_to_items.items():
        base, k = lbl, 2
        while lbl in used:
            lbl = f"{base}_{k}"
            k += 1
        used.add(lbl)
        out[lbl] = items
    return out

ingredient_level2_by_cat: Dict[str, Dict[str, List[str]]] = {}

for cat, members in category_buckets.items():
    if len(members) == 1:  # singleton bucket
        ingredient_level2_by_cat[cat] = {members[0]: members}
        continue

    idxs = [ing_to_idx[m] for m in members]
    sub_vecs = embeddings[idxs]
    sub_lbls = AgglomerativeClustering(
        linkage="average", metric="cosine",
        distance_threshold=FINE_THRESHOLD, n_clusters=None
    ).fit_predict(sub_vecs)

    raw = defaultdict(list)
    for m, lbl in zip(members, sub_lbls):
        raw[int(lbl)].append(m)

    # Human‑readable labels + uniqueness inside the category
    labelled = deduplicate({label_ingredient_cluster(v): sorted(v) for v in raw.values()})
    ingredient_level2_by_cat[cat] = labelled

# ───────────── ADVANCED LABELER for pizza clusters ─────────────
def label_pizza_cluster(items: List[str]) -> str:
    local = Counter(tok for n in items for tok in tokenize(n) if tok not in STOPWORDS)
    if not local:
        return sorted(items, key=len)[0]
    sal = {t: local[t] / (GLOBAL_PIZZA_TOKENS[t] or 1) for t in local}
    best = max(sal, key=sal.get)
    return best.title()

pizza_type_labels = deduplicate({label_pizza_cluster(v): sorted(v) for v in pizza_types.values()})

# ───────────── WRITE RESULTS ─────────────
cluster_labels = {
    "pizza_type_clusters": pizza_type_labels,
    "ingredient_level2_clusters": ingredient_level2_by_cat,
}
with open(OUTPUT_FILE, "w", encoding="utf-8") as fp:
    json.dump(cluster_labels, fp, indent=2, ensure_ascii=False)

print(f"\n💾 Cluster labels written to {os.path.abspath(OUTPUT_FILE)}")

# ───────────── OPTIONAL DEBUG OUTPUT ─────────────
print("\n🍕 Pizza‑type clusters")
print(json.dumps(pizza_type_labels, indent=2, ensure_ascii=False))

print("\n🪢 Ingredient Level‑2 clusters by category (sample)")
for cat, clusters in list(ingredient_level2_by_cat.items())[:3]:
    print(f"\n▶ {cat}")
    print(json.dumps(clusters, indent=2, ensure_ascii=False))


# ╔══════════════════════════════════════════════════════════════════════╗
# ║     NEW: VISUALIZE (REUSE EMBEDDINGS) + INGREDIENT LIST BY COLOR    ║
# ╚══════════════════════════════════════════════════════════════════════╝

def _auto_perplexity(n: int) -> int:
    """
    Choose a safe t‑SNE perplexity for sample count n.
    Must satisfy 5 ≤ perplexity < n. Uses a conservative heuristic.
    """
    if n <= 6:
        return max(2, n - 1)  # allow tiny sets
    return min(30, max(5, n // 3, 10), n - 1)

def _collect_points_for_category(
    category: str,
    ingredient_level2_by_cat: Dict[str, Dict[str, List[str]]],
    ing_to_idx: Dict[str, int],
) -> Tuple[List[int], List[str], List[str]]:
    """
    Returns:
      idxs: embedding indices of ingredients in this category
      labels: per‑ingredient automatic cluster label (the dict keys)
      names: ingredient strings
    """
    if category not in ingredient_level2_by_cat:
        raise ValueError(f"Category '{category}' not found. Available: {sorted(ingredient_level2_by_cat)}")

    idxs, labels, names = [], [], []
    for cluster_label, members in ingredient_level2_by_cat[category].items():
        for ing in members:
            if ing not in ing_to_idx:
                continue
            idxs.append(ing_to_idx[ing])
            labels.append(cluster_label)
            names.append(ing)
    return idxs, labels, names

def visualize_ingredient_clusters_tsne(
    category: str = "Other",
    annotate: bool = True,
    save_png: str | None = None,
    save_csv: str | None = None,
    export_sorted_txt: str | None = None,
):
    """
    Create a 2D t‑SNE visualization for one expert category using the
    ALREADY computed 'embeddings'.

    - Colors are assigned per automatic cluster using a stable palette (tab20).
    - The ingredient list (CSV/TXT) is **sorted by color** (cluster color index),
      then by cluster label, then ingredient name.
    """
    idxs, labels, names = _collect_points_for_category(category, ingredient_level2_by_cat, ing_to_idx)
    if not idxs:
        print(f"[WARN] No points to visualize for category '{category}'.")
        return

    V = embeddings[idxs]  # reuse existing embeddings
    n = V.shape[0]
    perp = _auto_perplexity(n)
    print(f"[INFO] Visualizing category='{category}' with n={n}, t‑SNE perplexity={perp}")

    tsne = TSNE(n_components=2, random_state=RANDOM_SEED, perplexity=perp)
    XY = tsne.fit_transform(V)

    # ── Stable palette and sorted legend/color order ────────────────────
    # Sort clusters alphabetically for determinism, then map to palette indices.
    unique_clusters = sorted(set(labels))
    palette = list(plt.get_cmap('tab20').colors)
    cluster_to_color_idx = {c: i % len(palette) for i, c in enumerate(unique_clusters)}
    cluster_to_color = {c: palette[idx] for c, idx in cluster_to_color_idx.items()}

    # ── Scatter plot ────────────────────────────────────────────────────
    plt.figure(figsize=(12, 8))
    # Plot clusters in color order for a legend that matches the sorted list
    for c in sorted(unique_clusters, key=lambda x: cluster_to_color_idx[x]):
        mask = [lbl == c for lbl in labels]
        xs = XY[mask, 0]
        ys = XY[mask, 1]
        plt.scatter(xs, ys, label=c, s=60, color=cluster_to_color[c])

    if annotate:
        for (x, y), name in zip(XY, names):
            plt.annotate(name, (x, y), fontsize=8)

    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title=f"{category} clusters")
    plt.title(f"t‑SNE Visualization of Ingredient Clusters — {category}")
    plt.tight_layout()
    plt.grid(True)

    # ── Build a table for exports (sorted by color) ─────────────────────
    rows = []
    for (x, y), ing, lbl in zip(XY, names, labels):
        color_idx = cluster_to_color_idx[lbl]
        color_hex = to_hex(cluster_to_color[lbl])
        rows.append({
            "ingredient": ing,
            "cluster_label": lbl,
            "x": float(x),
            "y": float(y),
            "category": category,
            "color_index": int(color_idx),
            "color_hex": color_hex,
        })

    rows.sort(key=lambda r: (r["color_index"], r["cluster_label"].lower(), r["ingredient"].lower()))

    # Optional CSV export (sorted by color)
    if save_csv:
        import csv
        with open(save_csv, "w", encoding="utf-8", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=["ingredient","cluster_label","x","y","category","color_index","color_hex"])
            w.writeheader()
            w.writerows(rows)
        print(f"[INFO] Saved points CSV (sorted by color) → {os.path.abspath(save_csv)}")

    # Optional plain‑text export: a human‑readable list grouped by color
    if export_sorted_txt:
        with open(export_sorted_txt, "w", encoding="utf-8") as fp:
            current_idx = None
            for r in rows:
                if r["color_index"] != current_idx:
                    current_idx = r["color_index"]
                    fp.write(f"\n=== Color {current_idx:02d} ({r['color_hex']}) ===\n")
                fp.write(f"- [{r['cluster_label']}] {r['ingredient']}\n")
        print(f"[INFO] Saved ingredient list by color → {os.path.abspath(export_sorted_txt)}")

    if save_png:
        plt.savefig(save_png, dpi=150)
        print(f"[INFO] Saved figure → {os.path.abspath(save_png)}")

    plt.show()


if __name__ == "__main__":
    # Example: visualize the "Other" expert category (matches your JSON sample)
    visualize_ingredient_clusters_tsne(
        category="Other",
        annotate=True,
        save_png="ingredient_clusters_Other_tsne.png",
        save_csv="ingredient_clusters_Other_points.csv",          # CSV sorted by color
        export_sorted_txt="ingredient_list_Other_by_color.txt",   # TXT grouped+sorted by color
    )
