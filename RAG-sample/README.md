# Simple RAG Client

A Python script that queries AnythingLLM using the Retrieval-Augmented Generation (RAG) approach. This client sends user messages to an AnythingLLM workspace and retrieves AI-powered responses based on indexed documents.

## Overview

This script demonstrates how to:
- Connect to a running AnythingLLM instance via its REST API
- Query a specific workspace with RAG (Retrieval-Augmented Generation) mode
- Get AI responses based on documents indexed in your workspace
- Work with both AnythingLLM and Ollama (local LLM) for completely local AI processing

## Prerequisites

1. **AnythingLLM** installed and running
   - Download from: https://www.anythingllm.com/
   - Default API endpoint: `http://localhost:3001/api/v1`

2. **Ollama** (optional, for local models)
   - Download from: https://ollama.ai/
   - Pull a model: `ollama pull llama3.1:8b`

3. **Python 3.8+** with `requests` library
   ```bash
   pip install requests
   ```

## Configuration

### Step 1: Get Your API Key from AnythingLLM

1. Open AnythingLLM in your browser (default: `http://localhost:3001`)
2. Go to **Settings** (gear icon in the top-right)
3. Navigate to **API Keys** section
4. Click **Generate New API Key**
5. Copy the generated API key

### Step 2: Update the Script

Edit `simple-RAG-client.py` and update these variables:

```python
API_KEY = "your_api_key_here"  # Paste your API key here
BASE_URL = "http://localhost:3001/api/v1"  # AnythingLLM API endpoint
WORKSPACE_SLUG = "my-workspace"  # Your workspace name (lowercase, with hyphens)
```

**Finding your workspace slug:**
- In AnythingLLM, go to your workspace
- The workspace slug appears in the URL: `http://localhost:3001/workspace/{WORKSPACE_SLUG}`
- Example: `company-docs`, `my-workspace`, etc.

## Usage

1. Make sure AnythingLLM is running and has documents indexed in your workspace
2. Run the script:
   ```bash
   python simple-RAG-client.py
   ```
3. Enter your question when prompted:
   ```
   Write your message: What is the deployment process?
   ```
4. The script returns:
   - `[DEBUG] Complete response:` - Full API response JSON
   - `AI answer:` - The extracted text response from the AI

## Script Behavior

- **Mode:** `query` - Searches only within indexed documents in your workspace
- **Response:** Returns both the complete API response and the extracted text answer
- **User Input:** Each run prompts for a new message

## API Response Structure

The complete response includes metadata about the query, sources used, and the AI response. Example:

```json
{
  "textResponse": "Based on your documents, the deployment process...",
  "sources": ["document1.pdf", "document2.txt"],
  "vectorDbId": "...",
  ...
}
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Ensure AnythingLLM is running on `http://localhost:3001` |
| Invalid API key | Generate a new API key in AnythingLLM Settings → API Keys |
| Workspace not found | Check the workspace slug matches your workspace name (case-sensitive) |
| No documents indexed | Add documents to your workspace first via the AnythingLLM UI |
| Using Ollama models | Configure Ollama as the LLM provider in AnythingLLM Settings |

## Integration with Ollama

To use local Ollama models with AnythingLLM:

1. Start Ollama:
   ```bash
   ollama serve
   ```

2. Pull a model:
   ```bash
   ollama pull llama3.1:8b
   ```

3. In AnythingLLM Settings → LLM Provider:
   - Select **Ollama**
   - Set base URL to `http://localhost:11434`
   - Choose your model (e.g., `llama3.1:8b`)

4. Run this script - it will use the Ollama model configured in AnythingLLM

## Files

- `simple-RAG-client.py` - Main script that queries AnythingLLM
- `data/sample-README.md` - Example document that can be indexed in AnythingLLM

## License

MIT
