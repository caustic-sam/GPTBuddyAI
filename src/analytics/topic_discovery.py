#!/usr/bin/env python3
"""
Topic Discovery & Categorization for OpenAI Chat History

Analyzes conversation data to discover:
1. Prime subjects/topics using clustering
2. Temporal patterns in your thinking
3. Knowledge domain taxonomy
"""
import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import Counter
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

def load_conversations(parquet_path):
    """Load and filter OpenAI conversation data"""
    df = pd.read_parquet(parquet_path)

    # Filter to user messages (your thoughts/questions)
    if 'author' in df.columns:
        user_df = df[df['author'] == 'user'].copy()
    else:
        # Fallback if no author column
        user_df = df.copy()

    print(f"Loaded {len(user_df)} messages from {len(df)} total")
    return user_df

def extract_embeddings(texts, model_name="all-MiniLM-L6-v2", max_texts=10000):
    """Generate embeddings for semantic clustering"""
    print(f"Generating embeddings for {len(texts)} texts...")

    # Sample if too many
    if len(texts) > max_texts:
        print(f"Sampling {max_texts} messages for topic discovery")
        import random
        random.seed(42)
        texts = random.sample(texts, max_texts)

    model = SentenceTransformer(model_name)
    embeddings = model.encode(texts, show_progress_bar=True)

    return embeddings, texts

def discover_topics_kmeans(embeddings, n_clusters=20):
    """Use K-Means clustering to discover topic groups"""
    print(f"Running K-Means clustering with {n_clusters} clusters...")

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings)

    return labels, kmeans

def discover_topics_dbscan(embeddings, eps=0.5, min_samples=5):
    """Use DBSCAN for density-based topic discovery"""
    print(f"Running DBSCAN clustering (eps={eps}, min_samples={min_samples})...")

    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    labels = dbscan.fit_predict(embeddings)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    print(f"Found {n_clusters} clusters + {n_noise} noise points")
    return labels

def visualize_topics_2d(embeddings, labels, output_path="artifacts/topic_clusters_2d.png"):
    """Create 2D visualization using PCA"""
    print("Generating 2D visualization...")

    # Reduce to 2D
    pca = PCA(n_components=2, random_state=42)
    coords_2d = pca.fit_transform(embeddings)

    # Plot
    plt.figure(figsize=(14, 10))
    scatter = plt.scatter(coords_2d[:, 0], coords_2d[:, 1], c=labels, cmap='tab20', alpha=0.6, s=20)
    plt.colorbar(scatter, label='Cluster ID')
    plt.title('Conversation Topics - 2D Projection (PCA)', fontsize=16)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Saved visualization to {output_path}")

def summarize_clusters(texts, labels, top_n=10):
    """Summarize each cluster with sample messages"""
    unique_labels = sorted(set(labels))

    cluster_summary = {}
    for label in unique_labels:
        if label == -1:  # Noise in DBSCAN
            continue

        cluster_texts = [t for t, l in zip(texts, labels) if l == label]
        cluster_summary[label] = {
            'count': len(cluster_texts),
            'samples': cluster_texts[:top_n]  # First N samples
        }

    return cluster_summary

def save_topic_report(cluster_summary, output_path="artifacts/topic_discovery_report.json"):
    """Save detailed topic report"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(cluster_summary, f, indent=2)

    print(f"Saved topic report to {output_path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="artifacts/openai.parquet", help="Input parquet file")
    ap.add_argument("--method", choices=['kmeans', 'dbscan'], default='kmeans', help="Clustering method")
    ap.add_argument("--n-clusters", type=int, default=20, help="Number of clusters (KMeans)")
    ap.add_argument("--eps", type=float, default=0.3, help="DBSCAN epsilon")
    ap.add_argument("--min-samples", type=int, default=10, help="DBSCAN min samples")
    ap.add_argument("--max-messages", type=int, default=10000, help="Max messages to analyze")
    args = ap.parse_args()

    # Load data
    df = load_conversations(args.input)

    # Extract text content
    if 'content' in df.columns:
        texts = df['content'].astype(str).tolist()
    elif 'text' in df.columns:
        texts = df['text'].astype(str).tolist()
    else:
        print("Error: No content/text column found")
        return

    # Filter out very short messages
    texts = [t for t in texts if len(t.strip()) > 20]
    print(f"Analyzing {len(texts)} messages (after filtering short ones)")

    # Generate embeddings
    embeddings, sampled_texts = extract_embeddings(texts, max_texts=args.max_messages)

    # Cluster
    if args.method == 'kmeans':
        labels, model = discover_topics_kmeans(embeddings, n_clusters=args.n_clusters)
    else:
        labels = discover_topics_dbscan(embeddings, eps=args.eps, min_samples=args.min_samples)

    # Visualize
    visualize_topics_2d(embeddings, labels)

    # Summarize
    cluster_summary = summarize_clusters(sampled_texts, labels, top_n=15)

    # Print summary
    print("\n" + "="*80)
    print("TOPIC DISCOVERY SUMMARY")
    print("="*80)
    for cluster_id in sorted(cluster_summary.keys()):
        info = cluster_summary[cluster_id]
        print(f"\nCluster {cluster_id}: {info['count']} messages")
        print("Sample messages:")
        for i, sample in enumerate(info['samples'][:3], 1):
            preview = sample[:150].replace('\n', ' ')
            print(f"  {i}. {preview}...")

    # Save report
    save_topic_report(cluster_summary)

    print("\n" + "="*80)
    print(f"Topic discovery complete! Found {len(cluster_summary)} distinct topics.")
    print("="*80)

if __name__ == "__main__":
    main()
