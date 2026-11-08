# Local AI Lab: Step-by-Step Plan

## Goal

Have back-and-forth text conversations with a local model on your Mac, with the features of ChatGPT
and Claude. Slower replies and lower answer quality are fine, since the model is smaller.

**Done means** you can open your own chat app in a browser, sign in, start and resume conversations,
watch replies stream in, stop, edit or regenerate a message, upload documents and ask about them,
and reach the same model through your own API with an API key. All of it runs on your Mac, with
Wi-Fi off.

## Decisions so far

| Decision | Choice |
|---|---|
| Hardware | Your M5 Mac (16GB) only. No Raspberry Pi, cloud GPUs, or new hardware |
| Network | Fully offline after downloads. Every service binds to `127.0.0.1` |
| How much to build | Almost everything yourself, including a tokenizer and a small inference engine |
| Languages | Python for the backend and AI parts; TypeScript and React for the web app |
| Features now | Text only |
| Features later | Image understanding, voice, code execution and tools, image generation |
| Dropped for now | CUDA (needs an NVIDIA GPU) and web search (needs internet) |
| Main model | Qwen3 8B, 4-bit (`Qwen3-8B-Q4_K_M.gguf`, 5.02GB) |
| Order | Bottom up, as written. Most time goes to theory and model internals (steps 3–7) |
| Web app | Keep it simple. It's needed for conversations, but it isn't the focus |
| Pace | 3–5 hours a week. Each step is split into sessions of about that size |
| Database | SQLite, a single file with no separate server. Needed from step 8 |

## How the finished system fits together

```text
Browser (your React chat app)
   │  your Mac only: http://127.0.0.1
   ▼
Chat backend (Python)            ← accounts, conversations, memory, documents, safety
   │
   ▼
Model gateway (Python)           ← your own "model API": API keys, streaming, queue, limits, logs
   │                    │
   ▼                    ▼
llama.cpp llama-server   Your own inference engine (learning; tiny model)
(Qwen3 8B, Metal GPU)
```

Each box is a separate program, the way large AI services split their work into separate services.

## Memory budget on your Mac

macOS lets the GPU use about 12GB of your 16GB. The 8B model takes about 5GB, plus room for
conversations. Close heavy apps while testing, and run one model at a time when you can.

---

## Stage A: Foundations

### Step 1: Decide the platform and the rules

- **What:** Commit to using your Mac only, offline, with every service on `127.0.0.1`. Write down
  what's in scope (text) and out of scope (image, voice, code, web search, CUDA).
- **Why:** Every later choice depends on these limits: model size, memory, tools, and security.
- **Skills you need:** None.
- **What you'll learn:** How hardware limits shape an AI system's design.
- **Done when:** This plan's decisions table is agreed. ✅ Done (2026-11-08).

### Step 2: Set up your development environment

- **What:** Install Python 3.12 with `uv` and llama.cpp from Homebrew. Create a git repository for
  the project, and set up formatting, linting, and a test runner. Node.js for the web app waits
  until step 11.
- **Why:** A repeatable setup means you can rebuild everything later, including offline, and the
  tests catch mistakes as the project grows.
- **Skills you need:** Terminal basics, git.
- **What you'll learn:** Python project setup, and keeping dependencies separate from your system's
  Python (yours is 3.9.6, which is too old).
- **Done when:** `uv run pytest` passes, `llama-server --version` works, and your first commit is made.

### Step 3: Learn how LLMs work

- **What:** First, build the maths and PyTorch basics through small exercises: vectors, dot
  products, matrix multiplication, softmax, gradients, and PyTorch tensors on your Mac's GPU. Then
  study the core LLM ideas: tokens, embeddings, attention, the transformer, sampling (temperature,
  top-p), the KV cache, context windows, and quantization. Write a short note in your own words for
  each one, and small code experiments where they help.
- **Why:** Steps 4–7 put these ideas into code. Understanding them first makes those steps much easier.
- **Skills you need:** Python, plus the linear algebra you already know. The exercises cover the
  rest.
- **What you'll learn:** What actually happens between sending a prompt and receiving a reply.
- **Done when:** You can explain, without notes, why replies arrive one token at a time and why long
  prompts take longer to start.

---

## Stage B: Build the model side yourself

### Step 4: Build a tokenizer

- **What:** Write a byte-pair encoding (BPE) tokenizer from scratch, and train it on some text. Then
  load Qwen3's real tokenizer, and compare how both split the same sentences. Implement Qwen3's chat
  template, which turns a conversation into the exact text the model expects.
- **Why:** Models read and write tokens, not characters. Token counts decide context limits, speed,
  and what usage costs on paid services.
- **Skills you need:** Python, dictionaries, and working with bytes and Unicode.
- **What you'll learn:** How text becomes numbers, why some languages and code use more tokens, and
  how chat templates mark roles like system, user, and assistant.
- **Done when:** Your Qwen3 template turns a sample conversation into exactly the same tokens as the
  reference library.

### Step 5: Train a tiny language model from scratch

- **What:** Build a small GPT-style model in PyTorch, using your Mac's GPU, and train it on a small
  text dataset. Its output will be poor, and that's expected.
- **Why:** Training shows how a model's weights come to exist, and why models like Claude need far
  more data and computing power than any home machine has.
- **Skills you need:** Python, PyTorch basics (which you'll learn in this step), and step 3's concepts.
- **What you'll learn:** Training loops, loss, learning rates, overfitting, and how model size
  affects quality.
- **Done when:** The loss falls steadily, and the model produces text that resembles its training data.

### Step 6: Build your own inference engine for a real model

- **What:** Load the real weights of a small model, Qwen3 0.6B, and write its forward pass yourself:
  RMSNorm, rotary position embeddings (RoPE), grouped-query attention, and the SwiGLU feed-forward
  layers. Add sampling, stop tokens, streaming, and a KV cache. Then try 8-bit quantization yourself.
- **Why:** This is what llama.cpp does internally. Building it yourself turns the model server from a
  black box into something you understand.
- **Skills you need:** PyTorch and step 3's concepts. This is the hardest step in the plan.
- **What you'll learn:** Exactly how a model turns your prompt into a reply, why the KV cache matters
  so much for speed, and what quantization gives up.
- **Done when:** For the same prompt with greedy sampling, your engine produces the same tokens as a
  reference implementation, and the KV cache makes it measurably faster.

### Step 7: Run and measure a production model server

- **What:** Run llama.cpp's `llama-server` with Qwen3 8B on `127.0.0.1`, using your Mac's GPU. Measure
  time to first token, reading speed (prefill), generation speed (decode), and memory use. Compare
  4-bit with 5-bit and 8-bit, short with long contexts, and your own engine with llama.cpp.
- **Why:** Your own engine is for learning, while llama.cpp is fast enough for daily use. Measuring
  them shows where your engine is slower and why.
- **Skills you need:** Terminal, `curl`, and simple Python scripts.
- **What you'll learn:** The GGUF file format, quantization trade-offs, Metal GPU use, context-size
  limits, and OpenAI-compatible APIs.
- **Done when:** You have a benchmark table in `notes/`, and a script that starts the server the same
  way every time.

---

## Stage C: Build the service around the model

### Step 8: Build your own model gateway

- **What:** Write a Python service (FastAPI) that sits in front of the model servers, like
  `api.openai.com` or `api.anthropic.com`. It will offer a chat endpoint with streaming over
  server-sent events, API keys stored as hashes, rate limits, timeouts, cancellation, a request
  queue, request logs, and clear error responses. It routes each request to llama.cpp or your own
  engine.
- **Why:** Apps should never talk to the model server directly, since the model server has no
  security. The gateway is where access control, fairness, and monitoring live.
- **Skills you need:** Python web APIs, async programming (you'll learn some here), and HTTP.
- **What you'll learn:** API design, streaming, backpressure, queueing when requests arrive at the
  same time, and API-key security.
- **Done when:** A request with a valid key streams a reply, an invalid key is rejected, closing the
  connection stops generation, and two requests sent together are handled in order.

### Step 9: Build the conversation backend

- **What:** Store users, conversations, and messages in a database (SQLite). Messages are stored as a
  tree, so editing a message or regenerating a reply creates a new branch instead of overwriting.
  Add automatic titles, custom instructions, a thinking-mode switch (Qwen3 can show its reasoning,
  like Claude), and context-window management that trims or summarizes long conversations.
- **Why:** The model remembers nothing between requests. The backend sends the right history every
  time, which is what makes it feel like a conversation.
- **Skills you need:** SQL, data modelling, and Python.
- **What you'll learn:** How chat products manage context, what happens when a conversation outgrows
  the context window, and how editing and regenerating work.
- **Done when:** Long conversations keep working, edits create branches you can switch between, and
  titles appear automatically.

### Step 10: Add accounts and security

- **What:** Add sign-up and sign-in with hashed passwords (Argon2), secure session cookies,
  protection against cross-site requests (CSRF), and checks that users only see their own
  conversations. Add an admin role.
- **Why:** Every real AI service has accounts, and conversations are private data.
- **Skills you need:** Web security basics, which this step teaches.
- **What you'll learn:** Authentication, authorization, password storage, and common web attacks
  and how to prevent them.
- **Done when:** A test proves one user can't read another user's conversations, even by guessing
  their IDs.

### Step 11: Build the chat web app

- **What:** Install Node.js, then build a simple React and TypeScript app. The core features are a
  conversation sidebar, streaming replies, Markdown and code formatting, stop, regenerate, and edit.
  Branch switching, a collapsible thinking section, search, settings, and dark mode are optional
  extras. Keep this step short, since the internals are the focus.
- **Why:** This is the part you see and use, like the ChatGPT and Claude websites.
- **Skills you need:** TypeScript and React, which you can learn as you go.
- **What you'll learn:** Rendering streamed text smoothly, managing app state, and handling errors
  and slow replies.
- **Done when:** You can hold a full conversation in the browser with the core features working.

---

## Stage D: Product features

### Step 12: Add file uploads and document questions (RAG)

- **What:** Accept text, Markdown, and PDF files. Split them into chunks, turn the chunks into
  embeddings with a small local embedding model, and write your own vector search (start simple,
  then make it faster). Add citations showing which part of a file an answer came from, and
  "projects" that keep documents together for related chats.
- **Why:** Small models know little and can't read long files at once. Retrieval finds the relevant
  parts and gives just those to the model.
- **Skills you need:** Python, and basic vector maths (cosine similarity).
- **What you'll learn:** Embeddings, chunking, retrieval quality, citations, and why RAG sometimes
  finds the wrong passages.
- **Done when:** Questions about an uploaded document return answers with correct citations, and a
  small retrieval test set passes.

### Step 13: Add memory across conversations

- **What:** Let the assistant save useful facts about you (with your approval), use them in new
  chats, and let you view, edit, and delete them. This works like ChatGPT's memory feature.
- **Why:** This is how assistants seem to remember you between conversations.
- **Skills you need:** Everything from steps 9 and 12.
- **What you'll learn:** Deciding what to remember, keeping memory relevant, and giving users
  control over their data.
- **Done when:** A fact saved in one chat is used correctly in a new one, and deleting it removes it
  everywhere.

### Step 14: Add safety and reliability

- **What:** Add limits on request size and reply length, a simple check for harmful requests and
  replies, protection against instructions hidden in uploaded documents, and graceful handling of
  timeouts and crashes.
- **Why:** Real services must handle misuse and failures, not just normal use.
- **Skills you need:** Everything so far.
- **What you'll learn:** Guardrails, prompt injection, and designing for failure.
- **Done when:** A set of misuse tests produces safe responses, and killing the model server shows a
  clear error instead of breaking the app.

---

## Stage E: Run it like a real service

### Step 15: Measure quality with tests (evals)

- **What:** Build a set of test prompts with expected behaviour, and score answers automatically,
  including using the model to grade answers. Rerun them whenever you change the model, compression,
  prompts, or retrieval.
- **Why:** AI services test model behaviour constantly, so changes don't quietly make answers worse.
- **Skills you need:** Python and testing.
- **What you'll learn:** How to measure answer quality, and the limits of automated grading.
- **Done when:** One command runs your eval set, and you can compare scores between two setups.

### Step 16: Add monitoring and load testing

- **What:** Track time to first token, tokens per second, queue length, errors, and memory use, and
  show them on a simple local dashboard. Simulate several users chatting at once, and try
  llama.cpp's parallel request setting.
- **Why:** You can't improve what you can't see, and serving several users at once is one of the
  hardest parts of real AI services.
- **Skills you need:** Python, plus metrics and logging basics.
- **What you'll learn:** Monitoring, bottlenecks, queueing, and how batching affects speed.
- **Done when:** Your dashboard shows what happens when three simulated users chat at the same time.

### Step 17: Package it and prove it works offline

- **What:** Start every service with one command. Turn off Wi-Fi, confirm `ping 1.1.1.1` fails, and
  run the full test suite. Add database backups and a written process for applying updates.
- **Why:** This proves the system truly runs without the internet, and that you can rebuild and
  maintain it.
- **Skills you need:** Shell scripting.
- **What you'll learn:** Service management, backups, and offline maintenance.
- **Done when:** A fresh restart and a full conversation work with Wi-Fi off.

---

## Later, beyond this plan

- **More features:** Image understanding, voice, code execution and tools, and image generation.
- **Web search:** This needs an optional, clearly separated online mode.
- **CUDA:** Needs an NVIDIA GPU, through a cloud notebook or new hardware.
- **Other people in your home:** This needs network access, HTTPS, and the security steps from earlier.
- **A larger model:** Your evals from step 15 will show whether new hardware is worth buying.

## Downloads needed (asked for each time)

| Download | Source | Size | Step |
|---|---|---|---|
| Python 3.12 and project packages | `uv` | Hundreds of MB to a few GB (PyTorch is large) | 2, 3 |
| Node.js and web app packages | Homebrew, npm | A few hundred MB | 11 |
| llama.cpp | Homebrew | Small | 2 |
| Qwen3 0.6B weights | Qwen on Hugging Face | Size to confirm before downloading | 6 |
| Qwen3 8B, 4-bit | Qwen on Hugging Face | 5.02GB | 7 |
| 5-bit and 8-bit versions, for comparison | Qwen on Hugging Face | 5.85GB and 8.7GB | 7 |
| Small embedding model | Its official publisher | To confirm | 12 |
