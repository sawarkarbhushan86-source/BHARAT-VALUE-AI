"""Security, input sanitation, path traversal protection, and prompt injection defense."""
import re
from pathlib import Path
from typing import Optional

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".json"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024 # 25MB

# Regex patterns for detecting prompt injection attempts in untrusted text
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s*prompt",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"jailbreak",
    r"act\s+as\s+(an\s+)?unrestricted",
    r"bypass\s+all\s+security\s+rules",
    r"output\s+the\s+hidden\s+system\s+key",
    r"print\s+environment\s+variables"
]

def sanitize_symbol(symbol: str) -> str:
    """Sanitize stock symbol to prevent query injection and invalid characters."""
    clean = re.sub(r"[^A-Za-z0-9_\-\.]", "", symbol.upper().strip())
    return clean[:20]

def validate_safe_path(base_dir: Path, target_path: str) -> Path:
    """
    Ensure the target path is strictly within the allowed base directory.
    Prevents path traversal attacks (e.g., ../../etc/passwd or C:\\Windows).
    """
    resolved_base = base_dir.resolve()
    resolved_target = (base_dir / target_path).resolve()
    if not str(resolved_target).startswith(str(resolved_base)):
        raise ValueError(f"Path traversal detected: {target_path} is outside allowed directory.")
    return resolved_target

def sanitize_untrusted_text(text: str) -> str:
    """
    Neutralize potential prompt injection attempts inside news articles or uploaded filings.
    The text is treated as passive untrusted data, never as system instructions.
    """
    if not text:
        return ""
    
    cleaned = text
    for pattern in PROMPT_INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[FILTERED_INSTRUCTION]", cleaned, flags=re.IGNORECASE)
        
    return cleaned

def is_safe_file_upload(filename: str, file_size: int) -> bool:
    """Validate file extension and size."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False
    if file_size > MAX_FILE_SIZE_BYTES:
        return False
    return True
