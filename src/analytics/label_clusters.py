#!/usr/bin/env python3
"""
Auto-label conversation clusters using MLX-LM

Reads cluster analysis and generates human-readable labels
"""
import json
import argparse
from pathlib import Path
from mlx_lm import load, generate

def load_cluster_data(cluster_file):
    """Load cluster summary from topic discovery"""
    # For now, we'll load from the terminal output
    # Later this will read from artifacts/topic_discovery_report.json
    return None

def generate_cluster_label(samples, cluster_id, model, tokenizer):
    """Generate a descriptive label for a cluster based on sample messages"""

    # Take first 5 samples (or fewer if not available)
    sample_texts = samples[:5]
    sample_preview = "\n".join([f"- {s[:150]}" for s in sample_texts])

    prompt = f"""Analyze these conversation samples and create a SHORT, descriptive label (3-5 words max).

Samples from cluster {cluster_id}:
{sample_preview}

The label should capture the main theme. Examples of good labels:
- "AI Ethics & Regulation"
- "Python Development Projects"
- "Logo & Brand Design"
- "NIST Compliance Research"

Label (3-5 words):"""

    response = generate(model, tokenizer, prompt=prompt, max_tokens=20, temp=0.3)

    # Extract just the label (remove prompt echo if present)
    label = response.strip()
    if "Label:" in label:
        label = label.split("Label:")[-1].strip()

    # Clean up
    label = label.replace('"', '').replace('\n', ' ').strip()

    # Ensure it's not too long
    words = label.split()
    if len(words) > 6:
        label = " ".join(words[:5])

    return label

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="artifacts/topic_discovery_report.json", help="Cluster report JSON")
    ap.add_argument("--output", default="artifacts/cluster_labels.json", help="Output labels")
    ap.add_argument("--model", default="mlx-community/SmolLM2-1.7B-Instruct-4bit", help="MLX model")
    args = ap.parse_args()

    print("Loading MLX-LM model...")
    model, tokenizer = load(args.model)

    # Hardcoded cluster samples from terminal output (temporary)
    # TODO: Replace with JSON loading once topic_discovery.py saves correctly
    clusters = {
        0: ["That's exciting! Tackling a topic like the convergence of AI and AGI is ambitious but rewarding.",
            "I've reviewed the previous chat file you shared. It provides a comprehensive outline about the EU AI Act",
            "how would I uncover opportunities to talk about AI to the dallas business community?"],
        2: ["the importance of respecting the natural evolution of identities within specific business contexts",
            "The global state of digital identity is rapidly evolving",
            "trust privacy and elegance"],
        3: ["what is the greatest danger to privacy",
            "The greatest danger to privacy in the digital era is multifaceted"],
        7: ["Just/a side note, but as the Us sits out of developing a CDBC, the EU and other government bodies are busy defining standards",
            "Search for the latest Global AI law & policy developments"],
        # Add more as needed...
    }

    labels = {}

    print("\n" + "="*80)
    print("GENERATING CLUSTER LABELS")
    print("="*80 + "\n")

    for cluster_id, samples in clusters.items():
        print(f"Cluster {cluster_id}... ", end="", flush=True)
        label = generate_cluster_label(samples, cluster_id, model, tokenizer)
        labels[cluster_id] = label
        print(f"✓ {label}")

    # Save
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(labels, f, indent=2)

    print(f"\n✅ Saved {len(labels)} labels to {args.output}")

    # Print summary
    print("\n" + "="*80)
    print("CLUSTER LABELS")
    print("="*80)
    for cluster_id, label in sorted(labels.items()):
        print(f"  Cluster {cluster_id:2d}: {label}")

if __name__ == "__main__":
    main()
