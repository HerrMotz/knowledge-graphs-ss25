import json
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from itertools import cycle

# Replace this with your full JSON structure
with open("cluster_labels.json") as f:
    ingredient_clusters = json.load(f)["ingredient_level2_clusters"]

# Extract and flatten the data: (ingredient, cluster_label)
data = []
for expert_cat, clusters in ingredient_clusters["ingredient_level2_clusters"].items():
    for cluster_label, ingredients in clusters.items():
        for ingredient in ingredients:
            data.append((ingredient, cluster_label))

# Create a DataFrame
df = pd.DataFrame(data, columns=["ingredient", "cluster"])

# TF-IDF vectorization of ingredient names
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df["ingredient"])

# Apply t-SNE dimensionality reduction
tsne = TSNE(n_components=2, random_state=42, perplexity=5)
X_embedded = tsne.fit_transform(X.toarray())

# Plotting
plt.figure(figsize=(12, 8))
colors = cycle(plt.cm.tab20.colors)
cluster_colors = {cluster: color for cluster, color in zip(df["cluster"].unique(), colors)}

# Scatter plot with color per cluster
for cluster in df["cluster"].unique():
    indices = df["cluster"] == cluster
    plt.scatter(X_embedded[indices, 0], X_embedded[indices, 1],
                label=cluster, color=cluster_colors[cluster], s=60)

# Annotate ingredient names
for i, txt in enumerate(df["ingredient"]):
    plt.annotate(txt, (X_embedded[i, 0], X_embedded[i, 1]), fontsize=8)

# Final layout
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Clusters")
plt.title("t-SNE Visualization of Ingredient Clusters")
plt.tight_layout()
plt.grid(True)
plt.show()
