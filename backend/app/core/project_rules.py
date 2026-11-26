"""Rules shared by project schemas and services."""
import re

MIN_DOCUMENTATION_CHARS = {"build": 200, "architecture": 600, "code_review": 500}
MIN_REFLECTION_CHARS = 100
MAX_DOCUMENTATION_CHARS = 20_000
MAX_REFLECTION_CHARS = 5_000
RUBRIC_CRITERIA = ("understanding", "implementation", "verification", "ownership")
MIN_APPROVAL_SCORE = 2

_REPO = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]{1,100})/([A-Za-z0-9_.-]{1,100})$")


def normalize_repo_url(value: str | None) -> str | None:
    """Return a clean GitHub repository URL, None for blank input, or raise ValueError.
    The URL is checked by format only. The server never fetches it."""
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    cleaned = cleaned.rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    match = _REPO.fullmatch(cleaned)
    if not match or any(part in (".", "..") for part in match.groups()):
        raise ValueError("Use a GitHub repository link such as https://github.com/yourname/your-project")
    return cleaned
