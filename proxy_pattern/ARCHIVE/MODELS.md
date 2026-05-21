# OpenAI Models - 2026 Status

## ✅ Current Recommended Models

These are the latest OpenAI models available as of February 2026:

### GPT-5 Series (Flagship Models)

| Model | Best For | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| **gpt-5.2** | Coding, agents, complex tasks | 200K | Medium | High |
| **gpt-5-mini** | General tasks, well-defined problems | 128K | Fast | Medium |
| **gpt-5-nano** | Simple tasks, high-throughput | 128K | Fastest | Lowest |
| **gpt-5.2-pro** | Most precise responses | 200K | Slow | Highest |

### GPT-4.1 Series (Non-Reasoning)

| Model | Best For | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| **gpt-4.1** | Smart non-reasoning tasks | 128K | Fast | Medium |
| **gpt-4.1-mini** | Faster version of 4.1 | 128K | Faster | Lower |
| **gpt-4.1-nano** | Fastest 4.1 variant | 128K | Fastest | Lowest |

### Specialized Models

| Model | Purpose |
|-------|---------|
| **gpt-5.2-codex** | Long-horizon agentic coding |
| **gpt-5.1-codex** | Agentic coding in Codex |
| **o3-deep-research** | Most powerful research model |
| **o4-mini-deep-research** | Faster research model |

---

## ⚠️ Legacy Models (Still Available)

These models are still accessible via API but are considered legacy:

| Model | Status | Notes |
|-------|--------|-------|
| **gpt-4o** | Legacy | Retired from ChatGPT Feb 13, 2026 |
| **gpt-4o-mini** | Legacy | Retired from ChatGPT Feb 13, 2026 |
| **gpt-4** | Legacy | Old high-intelligence model |
| **gpt-4-turbo** | Legacy | Older fast model |
| **gpt-3.5-turbo** | Legacy | Old model for cheaper tasks |

**API Note**: These models continue to be available through the API with advance notice before any future retirement.

---

## 📊 Model Selection Guide

### For Development/Testing
**Recommended**: `gpt-5-nano`
- Fastest response time
- Lowest cost
- Good for iteration and testing

### For Production Applications
**Recommended**: `gpt-5-mini`
- Great balance of speed and capability
- Cost-efficient for scale
- Handles most real-world tasks

### For Complex Tasks
**Recommended**: `gpt-5.2`
- Best reasoning and problem-solving
- Superior for coding and agents
- Worth the extra cost for critical tasks

### For Maximum Quality
**Recommended**: `gpt-5.2-pro`
- Most precise and thoughtful responses
- Use when accuracy is paramount
- Higher cost, slower responses

### For Non-Reasoning Tasks
**Recommended**: `gpt-4.1`
- Fast and efficient
- When you don't need reasoning capabilities
- Good for classification, summarization, etc.

---

## 🔄 Migration Guide

If you're using legacy models, here's how to migrate:

### From GPT-4o → GPT-5.2
```yaml
# Before (legacy)
- model_name: gpt-4o
  litellm_params:
    model: openai/gpt-4o

# After (current)
- model_name: gpt-5.2
  litellm_params:
    model: openai/gpt-5.2
    timeout: 120  # Slightly longer for better responses
```

### From GPT-4o-mini → GPT-5-mini
```yaml
# Before (legacy)
- model_name: gpt-4o-mini
  litellm_params:
    model: openai/gpt-4o-mini

# After (current)
- model_name: gpt-5-mini
  litellm_params:
    model: openai/gpt-5-mini
```

### From GPT-3.5-turbo → GPT-5-nano
```yaml
# Before (legacy)
- model_name: gpt-3.5-turbo
  litellm_params:
    model: openai/gpt-3.5-turbo

# After (current)
- model_name: gpt-5-nano
  litellm_params:
    model: openai/gpt-5-nano
```

---

## 💰 Cost Comparison

Approximate pricing (per 1M tokens):

| Model | Input | Output | Notes |
|-------|-------|--------|-------|
| gpt-5.2 | $5.00 | $15.00 | Flagship pricing |
| gpt-5-mini | $0.40 | $1.60 | 90% cheaper than 5.2 |
| gpt-5-nano | $0.20 | $0.80 | 95% cheaper than 5.2 |
| gpt-4.1 | $3.00 | $12.00 | Non-reasoning option |
| gpt-4o (legacy) | $5.00 | $15.00 | Being phased out |
| gpt-3.5-turbo (legacy) | $0.50 | $1.50 | Old model |

*Prices are approximate and may vary. Check [OpenAI Pricing](https://openai.com/pricing) for current rates.*

---

## 🎯 Our Configuration

This proxy is pre-configured with:

1. **gpt-5.2** - For complex tasks
2. **gpt-5-mini** - For general use
3. **gpt-5-nano** - For high-throughput
4. **gpt-4.1** - For non-reasoning tasks

### Why These Models?

- ✅ **Latest technology** - GPT-5 series released in 2026
- ✅ **Future-proof** - Won't be deprecated soon
- ✅ **Cost-efficient** - Better price/performance ratio
- ✅ **Better capabilities** - Superior to GPT-4 series
- ✅ **Wide range** - From ultra-fast to most capable

---

## 📚 Additional Resources

- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [OpenAI Pricing](https://platform.openai.com/docs/pricing)
- [Model Comparison](https://platform.openai.com/docs/models/compare)
- [Deprecations Schedule](https://platform.openai.com/docs/deprecations)

---

## ⏰ Important Dates

- **February 13, 2026** - GPT-4o retired from ChatGPT
- **February 16, 2026** - chatgpt-4o-latest API endpoint discontinued
- **April 3, 2026** - GPT-4o fully retired from Business/Enterprise

**Action Required**: Migrate to GPT-5 series before these dates.

---

**Last Updated**: February 9, 2026  
**Source**: [OpenAI Platform Documentation](https://platform.openai.com/docs/models)
