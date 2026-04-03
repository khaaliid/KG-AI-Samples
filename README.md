# KG AI Samples

A collection of AI-powered tests, experiments, and samples exploring various applications of AI and machine learning.

## Overview

This repository serves as a sandbox for building, testing, and showcasing AI solutions across different domains. Each project demonstrates practical AI implementations, from email automation to Kubernetes management.

## Projects

### AI Inbox Pilot
Located in `ai-inbox-pilot/`

An intelligent email triage system that:
- Connects to IMAP mailboxes and analyzes unread messages
- Applies AI-powered rules to categorize and process emails
- Automatically archives messages based on intelligent filtering
- Supports Gmail and other standard email providers

**Tech Stack:** Python, IMAP, OpenAI (via `triage_llm.py`)

### Copilot Skills
Located in `copilot-skills/`

Custom skill documentation and samples for extending GitHub Copilot capabilities, including:
- Kubernetes management skills

## Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment manager (venv, conda, or similar)
- Git

### Installation

Each project has its own setup instructions. For the AI Inbox Pilot:

```bash
cd ai-inbox-pilot
python -m venv .venv
.venv\Scripts\Activate.ps1  # PowerShell on Windows
pip install -r requirements.txt
```

## Project Structure

```
KG-AI-Samples/
├── ai-inbox-pilot/          # Email triage and automation
│   ├── triage.py            # Main triage script
│   ├── triage_llm.py        # LLM integration
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Project-specific documentation
├── copilot-skills/          # GitHub Copilot skill definitions
└── README.md                # This file
```

## Contributing

This is a personal sandbox repository for AI experimentation. Feel free to add new samples and tests following these guidelines:
- Keep projects self-contained with their own README files
- Document dependencies clearly
- Include setup and usage instructions

## License

MIT

---

**Note:** Some projects require API keys or credentials. Create appropriate `.env` files with required configuration. See individual project READMEs for details.
