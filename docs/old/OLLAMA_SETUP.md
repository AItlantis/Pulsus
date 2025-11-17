# Ollama Setup for Pulsus MCP

Pulsus MCP uses a local LLM (via Ollama) to generate intelligent docstrings and documentation.

## Quick Start

### 1. Start Ollama

Open a **new terminal** and run:

```bash
ollama serve
```

You should see output like:
```
time=2024-01-XX msg="Ollama running on http://127.0.0.1:11434"
```

**Keep this terminal open** while using Pulsus.

### 2. Verify Ollama is Running

In another terminal:

```bash
curl http://localhost:11434/api/tags
```

You should see a list of installed models.

### 3. Pull the Model (if needed)

Pulsus is configured to use `qwen3-coder:30b` by default. Pull it with:

```bash
ollama pull qwen3-coder:30b
```

Or use a smaller/different model (see Configuration section below).

---

## Configuration

### Environment Variables

You can customize the LLM configuration with environment variables:

```bash
# Ollama host (default: http://localhost:11434)
export OLLAMA_HOST=http://localhost:11434

# Model name (default: qwen3-coder:30b)
export PULSUS_MODEL_NAME=qwen3-coder:30b

# Temperature (default: 0.2)
export PULSUS_TEMPERATURE=0.2

# Max tokens (default: 30720)
export PULSUS_MAX_TOKENS=30720

# Timeout in seconds (default: 60)
export PULSUS_TIMEOUT=60
```

### Recommended Models

**For Code Understanding & Documentation:**
- `qwen3-coder:30b` (default) - Best quality, requires ~20GB RAM
- `qwen3-coder:14b` - Good balance, requires ~10GB RAM
- `qwen3-coder:7b` - Lightweight, requires ~5GB RAM
- `codellama:13b` - Alternative, requires ~8GB RAM

**To change the model:**

```bash
export PULSUS_MODEL_NAME=qwen3-coder:14b
ollama pull qwen3-coder:14b
```

Then restart Pulsus.

---

## Troubleshooting

### "Cannot connect to Ollama"

**Symptom:**
```
[Error: Cannot connect to Ollama at http://localhost:11434]
```

**Solution:**
1. Check if Ollama is running: `netstat -an | findstr 11434`
2. If not, start it: `ollama serve`
3. Verify: `curl http://localhost:11434/api/tags`

### "LLM request failed with status 404"

**Symptom:**
```
[Error: LLM request failed with status 404]
```

**Possible Causes:**
1. **Model not installed** - Pull it: `ollama pull qwen3-coder:30b`
2. **Wrong model name** - Check installed models: `ollama list`
3. **Ollama not running** - Start it: `ollama serve`

**Solution:**
```bash
# List installed models
ollama list

# If your model is not listed, pull it
ollama pull qwen3-coder:30b

# Or use a different model
export PULSUS_MODEL_NAME=codellama:13b
ollama pull codellama:13b
```

### "Timeout" or Slow Generation

**Symptom:**
Generation takes a very long time or times out.

**Solution:**
1. Use a smaller model (e.g., `qwen3-coder:7b` instead of `30b`)
2. Increase timeout: `export PULSUS_TIMEOUT=120`
3. Reduce context: Ollama may be slow on first run (model loading)

---

## Fallback Mode

If Ollama is not available, Pulsus will automatically fall back to:

### For Documentation (`generate docs`)
- Creates basic documentation from AST analysis
- Lists all functions, classes, imports
- No LLM-generated descriptions (but still useful!)

### For Comments (`comment it`)
- Shows error message with instructions to start Ollama
- You'll need to start Ollama to use this feature

---

## Using Alternative LLM Providers

### OpenRouter / Anthropic / OpenAI

If you prefer a different LLM provider, you can modify `agents/pulsus/config/settings.py`:

```python
@dataclass
class ModelConfig:
    provider: str = "openrouter"  # Change this
    host: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")
    api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    # ... rest of config
```

Note: You'll need to update the request format in `script_ops.py` to match the provider's API.

---

## Performance Tips

1. **First run is slow** - Ollama loads the model into memory (can take 10-30 seconds)
2. **Keep Ollama running** - Subsequent requests are much faster
3. **Use GPU** - If available, Ollama will use it automatically (much faster)
4. **Monitor memory** - Large models (30b) need significant RAM

---

## Check Your Setup

Run this quick test:

```bash
# 1. Check Ollama is running
curl http://localhost:11434/api/tags

# 2. Check your model is installed
ollama list | grep qwen3-coder

# 3. Test generation
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3-coder:30b",
  "prompt": "Write a Python function docstring for: def add(a, b): return a + b",
  "stream": false
}'
```

If all three commands succeed, Pulsus MCP should work!

---

## Summary

**Minimum Steps to Get Started:**

1. `ollama serve` (in a separate terminal, keep it open)
2. `ollama pull qwen3-coder:30b` (one-time, or use a different model)
3. Use Pulsus: `@path/to/script.py` → `comment it`

That's it! The LLM will generate intelligent docstrings and documentation.
