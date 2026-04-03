import imaplib
import email
from email.header import decode_header
import os
import requests
from pathlib import Path
from typing import Any, Dict


def _parse_env_file(env_file: Path) -> Dict[str, str]:
    """Parse KEY=VALUE lines from an env file."""
    values: Dict[str, str] = {}
    if not env_file.exists():
        return values

    for line in env_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue

        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def _load_config() -> Dict[str, Any]:
    """Load config once at startup from file then env vars. Fails if any required key is missing."""
    required_keys = [
        "IMAP_SERVER",
        "IMAP_PORT",
        "EMAIL_ADDRESS",
        "EMAIL_PASSWORD",
        "LLM_API_URL",
        "LLM_MODEL",
        "MAX_UNREAD_EMAILS",
        "USE_LLM",
    ]
    int_keys = {"IMAP_PORT", "MAX_UNREAD_EMAILS"}
    bool_keys = {"USE_LLM"}

    env_file_path = Path(os.getenv("TRIAGE_ENV_FILE", ".env"))
    file_values = _parse_env_file(env_file_path)
    config: Dict[str, Any] = {}
    missing = []

    for key in required_keys:
        value: Any = file_values.get(key)
        if value in (None, ""):
            value = os.getenv(key)
        if value in (None, ""):
            missing.append(key)
            continue

        if key in int_keys:
            try:
                value = int(value)
            except (TypeError, ValueError):
                raise ValueError(f"Config '{key}' must be an integer, got: {value!r}")
        
        if key in bool_keys:
            if isinstance(value, str):
                value = value.lower() in {"true", "yes", "1", "on"}
            else:
                value = bool(value)

        config[key] = value

    if missing:
        raise EnvironmentError(
            f"Missing required configuration key(s): {', '.join(missing)}. "
            f"Set them in '{env_file_path}' or as environment variables."
        )

    return config


CONFIG = _load_config()

# Configuration loaded at startup
IMAP_SERVER = CONFIG["IMAP_SERVER"]
IMAP_PORT = CONFIG["IMAP_PORT"]
EMAIL_ADDRESS = CONFIG["EMAIL_ADDRESS"]
EMAIL_PASSWORD = CONFIG["EMAIL_PASSWORD"]
LLM_API_URL = CONFIG["LLM_API_URL"]
LLM_MODEL = CONFIG["LLM_MODEL"]
MAX_UNREAD_EMAILS = CONFIG["MAX_UNREAD_EMAILS"]
USE_LLM = CONFIG["USE_LLM"]


def connect_to_mailbox() -> imaplib.IMAP4_SSL:
    """Connect to Gmail/Outlook mailbox."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        imap.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        print(f"Connected to {IMAP_SERVER}")
        return imap
    except Exception as e:
        print(f"Failed to connect: {e}")
        raise


def decode_email_header(header: str) -> str:
    """Decode email header."""
    decoded_parts = decode_header(header)
    decoded_str = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            decoded_str += part.decode(encoding or "utf-8", errors="ignore")
        else:
            decoded_str += part
    return decoded_str


def get_email_body(msg) -> str:
    """Extract email body text."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
                except Exception:
                    pass
    else:
        try:
            body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
        except Exception:
            body = msg.get_payload()
    return body[:500]  # Limit to 500 chars for LLM


def is_low_priority(sender: str) -> bool:
    """Local logic: Check if sender is 'noreply' or contains 'newsletter'."""
    sender_lower = sender.lower()
    return "noreply" in sender_lower or "newsletter" in sender_lower


def call_llm(email_body: str, subject: str = "") -> str:
    """Call LLM to summarize and classify email."""
    prompt = f"""Classify this email as ACTION_REQUIRED or FYI_ONLY based on these rules:

ACTION_REQUIRED if the email:
- Explicitly asks for a response or action from you
- Contains urgent language: "immediate", "urgent", "ASAP", "waiting for", "please respond"
- Requires you to do something: submit, approve, review, confirm, send
- Asks a direct question expecting a reply
- Contains a deadline or time constraint
- Needs your input or decision

Otherwise, respond with FYI_ONLY.

Respond with ONLY ONE line: either "ACTION_REQUIRED" or "FYI_ONLY"

Subject: {subject}
Email Body: {email_body}"""
    
    try:
        response = requests.post(
            LLM_API_URL,
            json={"prompt": prompt, "model": LLM_MODEL, "stream": False},
            timeout=30
        )
        response_json = response.json()
        raw = response_json.get("response")
        if raw is None:
            print("LLM response: (no 'response' key in reply, defaulting to ACTION_REQUIRED — email kept in inbox)")
            return "ACTION_REQUIRED"
        result = raw.strip().upper()
        print(f"LLM response: {result}")
        return "ACTION_REQUIRED" if "ACTION" in result else "FYI_ONLY"
    except Exception as e:
        print(f"LLM call failed: {e}, defaulting to ACTION_REQUIRED — email kept in inbox")
        return "ACTION_REQUIRED"


def create_archive_folder(imap: imaplib.IMAP4_SSL):
    """Create 'AI_Archive' folder if it doesn't exist."""
    try:
        imap.create("AI_Archive")
        print("Created 'AI_Archive' folder")
    except imaplib.IMAP4.error:
        print("'AI_Archive' folder already exists")


def move_email(imap: imaplib.IMAP4_SSL, email_id: bytes, destination: str):
    """Move email to destination folder."""
    try:
        imap.copy(email_id, destination)
        imap.store(email_id, "+FLAGS", "\\Deleted")
        print(f"Moved email {email_id} to {destination}")
    except Exception as e:
        print(f"Failed to move email: {e}")


def triage_emails():
    """Main function to triage unread emails."""
    imap = connect_to_mailbox()
    
    try:
        # Select INBOX
        imap.select("INBOX")
        
        # Fetch last N unread emails
        status, unread_ids = imap.search(None, "UNSEEN")
        email_ids = unread_ids[0].split()[-MAX_UNREAD_EMAILS:]
        
        if not email_ids:
            print("No unread emails found.")
            return
        
        print(f"Processing {len(email_ids)} unread emails...\n")
        
        for email_id in email_ids:
            try:
                status, msg_data = imap.fetch(email_id, "(RFC822)")
                if not msg_data or msg_data[0] is None:
                    print(f"Skipping email {email_id}: unable to fetch message data")
                    continue
                
                msg = email.message_from_bytes(msg_data[0][1])
            except Exception as e:
                print(f"Skipping email {email_id}: {e}")
                continue
            
            # Extract email details
            sender = decode_email_header(msg.get("From", "Unknown"))
            subject = decode_email_header(msg.get("Subject", "No Subject"))
            body = get_email_body(msg)
            
            # Local logic: Check for low priority
            priority = "Low Priority" if is_low_priority(sender) else "Standard"
            
            # LLM classification (only if enabled)
            classification = call_llm(body, subject) if USE_LLM else "NO_CLASSIFICATION"
            
            print(f"From: {sender}")
            print(f"Subject: {subject}")
            print(f"Priority: {priority}")
            print(f"Classification: {classification}")
            print("-" * 60)
        
        # Close connection without expunging (no emails were modified)
        imap.close()
        imap.logout()
        print("Done!")
        
    except Exception as e:
        print(f"Error during triage: {e}")
        imap.close()
        imap.logout()
        raise


if __name__ == "__main__":
    triage_emails()
