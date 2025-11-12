SHELL := /bin/bash
PY := python
VENV := .venv
ACT := source $(VENV)/bin/activate

export PYTHONPATH := $(PWD)

.PHONY: help venv install ingest-openai ingest-pdfs index query study-guide finetune coreml-export ui-streamlit ui-gradio clean

help:
	@echo "Targets:"
	@echo "  venv            - create local virtual environment"
	@echo "  install         - install Python deps into venv"
	@echo "  ingest-openai   - parse OpenAI export into artifacts/openai.parquet"
	@echo "  ingest-pdfs     - parse NIST/IAPP PDFs into artifacts/docs.parquet"
	@echo "  index           - build embeddings & Chroma index from artifacts/*.parquet"
	@echo "  query           - run a sample RAG query"
	@echo "  study-guide     - generate a short study guide for a topic"
	@echo "  finetune        - run MLX-LM LoRA on sft.jsonl (if present)"
	@echo "  coreml-export   - example Core ML export"
	@echo "  ui-streamlit    - run Streamlit UI"
	@echo "  ui-gradio       - run Gradio UI"
	@echo "  clean           - remove caches and temporary files"

venv:
	python3 -m venv $(VENV)

install: venv
	$(ACT) && pip install -U pip && pip install -r requirements.txt

ingest-openai:
	$(ACT) && $(PY) src/ingest/ingest_openai.py --in data/openai --out artifacts/openai.parquet

ingest-pdfs:
	$(ACT) && $(PY) src/ingest/ingest_pdfs.py --nist data/nist --iapp data/iapp --out artifacts/docs.parquet

index:
	$(ACT) && $(PY) src/rag/build_index.py --inputs artifacts/openai.parquet artifacts/docs.parquet --persist artifacts/index

query:
	$(ACT) && $(PY) src/rag/query.py --q "Summarize AC-2 in NIST 800-53r5 and list key controls." --topk 6

study-guide:
	$(ACT) && $(PY) src/rag/study_guide.py --topic "IAPP privacy principles vs. NIST access controls" --pages 2

finetune:
	$(ACT) && mlx_lm.finetune --model mlx-community/SmolLM2-1.7B-Instruct-4bit --train-data artifacts/sft.jsonl --lora-rank 8 --batch-size 8 --epochs 3 --lr 2e-4 --save-adapter artifacts/lora

coreml-export:
	$(ACT) && $(PY) src/llm/coreml_export.py --in artifacts/model --out artifacts/StudyKit-LLM.mlpackage

ui-streamlit:
	$(ACT) && streamlit run src/ui/streamlit_app.py

ui-gradio:
	$(ACT) && $(PY) src/ui/gradio_app.py

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache .mypy_cache .ruff_cache .ipynb_checkpoints
