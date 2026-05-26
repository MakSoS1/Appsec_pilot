# Model Runtime

The MVP uses a local Qwen-family model through an OpenAI-compatible API. The default remote PC runtime is Ollama:

```env
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen35-hauhau-q4:latest
LLM_API_KEY=local-dev-key
```

The model is used for planning and explanation. It is not trusted as an executor. The backend normalizes model output, strips known template stop tokens, attempts JSON parsing, and falls back to deterministic safe planning when JSON is invalid or the model is unavailable.
