import os, gradio as gr
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from mlx_lm import load, generate

client = PersistentClient(path="artifacts/index")
coll = client.get_collection("studykit")
embed = SentenceTransformer("all-MiniLM-L6-v2")
model_id = os.getenv("LM_MODEL", "mlx-community/SmolLM2-1.7B-Instruct-4bit")
model, tok = load(model_id)

def ask(q, topk=6, max_tokens=400):
    qv = embed.encode([q])[0].tolist()
    r = coll.query(query_embeddings=[qv], n_results=topk)
    chunks = r["documents"][0]
    metas = r["metadatas"][0]

    context = ""
    cites = []
    for i, (c, m) in enumerate(zip(chunks, metas), start=1):
        cite = f"[{i}] source={m.get('source')} page={m.get('page')}"
        context += f"{cite}\n{c}\n\n"
        cites.append(f"[{i}] {m.get('source')} (page {m.get('page')})")

    prompt = f"Use the CONTEXT to answer with inline citations like [1], [2].\n\nCONTEXT:\n{context}\nQ: {q}\nA:"
    out = generate(model, tok, prompt, max_tokens=max_tokens)
    return out, "\n".join(cites)

with gr.Blocks(title="GPTBuddyAI RAG") as demo:
    gr.Markdown("# GPTBuddyAI — Multi-Corpus RAG")
    with gr.Row():
        q = gr.Textbox(label="Question", placeholder="e.g., Summarize AC-2 in NIST 800-53r5")
    with gr.Row():
        topk = gr.Slider(3, 12, value=6, step=1, label="Top-k passages")
        max_toks = gr.Slider(200, 1600, value=int(os.getenv('LM_MAX_TOKENS', '400')), step=50, label="Max tokens")
    with gr.Row():
        btn = gr.Button("Answer")
    with gr.Row():
        ans = gr.Markdown()
    with gr.Accordion("Citations", open=False):
        cites = gr.Markdown()

    btn.click(ask, inputs=[q, topk, max_toks], outputs=[ans, cites])

if __name__ == "__main__":
    demo.launch()
