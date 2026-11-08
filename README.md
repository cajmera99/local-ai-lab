# Local AI Lab

Building a ChatGPT-style AI system from the ground up, running fully offline on a laptop.

This project rebuilds the main parts of an LLM service myself, one layer at a time, to understand
how products like ChatGPT and Claude actually work: the tokenizer, the model's forward pass,
inference, the serving API, conversation management, document retrieval, and evaluation.

The focus is on the internals rather than the interface. Where a production tool exists
(llama.cpp), I use it as a reference and benchmark against my own implementation.

## Status

🚧 In progress: **step 2 of 17 complete.** See [PLAN.md](PLAN.md) for every step, including why it
matters and what it teaches.

| Stage | Steps | Status |
|---|---|---|
| **A. Foundations** | 1. Platform and constraints · 2. Dev environment · 3. Maths, PyTorch and LLM theory | 2 of 3 done |
| **B. The model** | 4. BPE tokenizer · 5. Train a tiny GPT · 6. Own inference engine for Qwen3 0.6B · 7. llama.cpp benchmarks | Not started |
| **C. The service** | 8. Model gateway API · 9. Conversation backend · 10. Accounts and security · 11. Chat web app | Not started |
| **D. Features** | 12. Document Q&A (RAG) · 13. Memory · 14. Safety | Not started |
| **E. Operations** | 15. Evals · 16. Monitoring and load tests · 17. Offline packaging | Not started |

## Architecture (target)

```text
Browser (React chat app)
   │  localhost only: http://127.0.0.1
   ▼
Chat backend (Python)            ← accounts, conversations, memory, documents, safety
   │
   ▼
Model gateway (Python)           ← API keys, streaming, queueing, rate limits, logs
   │                    │
   ▼                    ▼
llama.cpp llama-server   Own inference engine (PyTorch, Qwen3 0.6B)
(Qwen3 8B, Metal GPU)
```

## Constraints

- **Hardware:** An Apple M5 laptop with 16GB of unified memory. No dedicated GPU or cloud compute.
- **Offline:** Everything runs locally after models are downloaded, and every service binds to
  `127.0.0.1`.
- **Scope:** Text conversations first. Images, voice, and tool use come later.

These limits are deliberate: they force decisions about model size, quantization, memory, and
latency that real AI services also have to make.

## Tech stack

| Area | Tools |
|---|---|
| Language and tooling | Python 3.12, uv, pytest, Ruff |
| Model internals | PyTorch on Apple's Metal GPU (planned) |
| Inference | llama.cpp with GGUF models; own engine (planned) |
| Services | FastAPI and SQLite (planned) |
| Web app | TypeScript and React (planned) |

## Getting started

Requires macOS on Apple silicon, [uv](https://docs.astral.sh/uv/), and
[Homebrew](https://brew.sh/).

```bash
uv python install 3.12
brew install llama.cpp
uv sync
uv run pytest
```

## Project layout

```text
src/local_ai_lab/   source code
tests/              tests
notes/              measurements and findings for each step
scripts/            start, test and benchmark scripts
models/             model files (not tracked; large)
```

## Learning notes

Each step ends with a write-up in [`notes/`](notes/) covering what I measured, what went wrong,
and what I learned.

## License

[MIT](LICENSE)
