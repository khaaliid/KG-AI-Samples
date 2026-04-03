# AI Inbox Pilot — Triage Script

Overview
- `triage.py` connects to an IMAP mailbox, inspects unread messages, applies simple local rules, and archives messages.
- Configuration is loaded at module startup from a `.env` file (or environment variables).

Requirements
- Python 3.8+
- Dependencies: `requests` (install with `pip install requests`)

Setup
1. Create and activate a Python virtual environment, then install dependencies.

```bash
# Create virtual environment
python -m venv .venv

# Activate (PowerShell)
.venv\Scripts\Activate.ps1

# Or activate (cmd.exe)
.venv\Scripts\activate.bat

# Or on macOS / Linux
source .venv/bin/activate

# Upgrade pip and install deps
pip install -U pip

# Install from requirements.txt (recommended)
pip install -r requirements.txt
```

2. Create a `.env` file in the `ai-inbox-pilot/` folder with required keys. Example:

```
IMAP_SERVER=imap.example.com
IMAP_PORT=993
SMTP_SERVER=smtp.example.com    # optional
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password
MAX_UNREAD_EMAILS=20
```

Notes:
- The script will fail early if any required key is missing.
- To use an alternate env file path set the environment variable `TRIAGE_ENV_FILE` to that file path.

Gmail setup (required for Gmail accounts)
If you plan to use a Gmail account, perform these steps to allow IMAP access from the script:

1. Enable IMAP in Gmail
  - In Gmail: Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP.

2. Use an App Password (recommended)
  - Ensure **2-Step Verification** is enabled for the Google account.
  - Visit Google Account → Security → App passwords.
  - Create a new app password (choose "Mail" and appropriate device), copy the generated password and put it into your `.env` as `EMAIL_PASSWORD=`.
  - Do not use your regular Google account password — app passwords are required for script access.

3. IMAP / SMTP host and ports
  - IMAP: `imap.gmail.com:993` (SSL)
  - SMTP: `smtp.gmail.com:587` (STARTTLS)

4. Google Workspace / OAuth notes
  - On Google Workspace accounts the administrator may block app passwords or IMAP access. If so, request your admin to enable IMAP or use OAuth2.
  - For production or multi-user setups prefer OAuth2 (no stored passwords). See Google Identity / Gmail IMAP XOAUTH2 docs for implementing OAuth2 tokens.

5. Security notes
  - "Less secure app access" is deprecated and should not be used.
  - Keep `.env` off version control (it's included in `.gitignore` already).

Example Gmail `.env` entries:

```
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=<your_app_password_here>
```

Run
From the `ai-inbox-pilot/` directory run:

```bash
python triage.py
```

Behavior
- Module-level config loading runs immediately on import. Missing required keys cause an `EnvironmentError` with a list of missing keys.
- The script selects `INBOX`, scans up to `MAX_UNREAD_EMAILS` most-recent unread messages, prints basic metadata, and moves processed messages into the `AI_Archive` mailbox.
- Local priority logic: senders containing `noreply` or `newsletter` are considered low priority.

Versions
- Simple (no LLM): `triage.py`
  - Connects to IMAP, applies local priority rules, and archives messages. No external LLM calls.

- LLM-enabled: `triage_llm.py` (or enable `USE_LLM` in a unified script)
  - Adds `call_llm()` to POST email text to an LLM endpoint and classify messages as `ACTION_REQUIRED` or `FYI_ONLY`.
  - Control with a boolean `USE_LLM` config key in `.env` (e.g. `USE_LLM=true`). When `false`, the script skips LLM calls.
  - Required additional env keys: `LLM_API_URL`, `LLM_MODEL`.

Notes on choosing a version:
- Use the simple version when you want minimal dependencies and no external API calls.
- Use the LLM-enabled version when you need automated classification/summarization; be mindful of API latency, costs, and privacy of email content.

If you add LLM support, ensure `requirements.txt` includes `requests` and add any client libs your LLM provider requires.

Prompt to generate this script
Use this prompt with an LLM to generate a similar `triage.py` script. Tweak provider-specific details (IMAP server names, LLM API schema) as needed.

```
Write a Python 3 script named `triage.py` that:
- Connects to an IMAP mailbox using `imaplib.IMAP4_SSL`.
- Loads configuration at module startup from a `.env` file (key=value lines) or environment variables. Required keys: `IMAP_SERVER`, `IMAP_PORT`, `EMAIL_ADDRESS`, `EMAIL_PASSWORD`, `MAX_UNREAD_EMAILS`.
- If any required key is missing, exit early with a clear error listing missing keys.
- Provides a `connect_to_mailbox()` function that logs into the IMAP server and reports connection failure.
- Provides helpers to decode email headers and extract the plain-text body (limit body to ~500 chars for processing).
- Implements a simple local priority heuristic: messages from addresses containing `noreply` or `newsletter` are low priority.
- Implements `triage_emails()` that:
  - Selects `INBOX`, creates `AI_Archive` if missing, fetches up to `MAX_UNREAD_EMAILS` unread messages, and for each message prints From/Subject/Priority.
  - Moves processed messages to `AI_Archive`.
- Add clear, minimal error handling and concise print statements for status.
- Keep dependencies minimal (`requests` permitted if LLM integration is added).

Return only a complete, well-formatted Python file as the answer (no extra commentary). Ensure the script follows best practices for config loading, input validation, and readable function decomposition.
```

Validation checklist
- Script syntax: checked (no syntax errors reported).
- Runtime: ensure `.env` contains required keys before running to avoid early failure.

Next steps (optional)
- Add unit tests for `decode_email_header`, `get_email_body`, and `_parse_env_file`.
- Add optional LLM classification with `USE_LLM` and safe timeouts/retries for the LLM call.

