from urllib.parse import urlparse

import validators


class URLValidationError(Exception):
    """Raised when a submitted URL fails validation."""
    pass


MAX_URL_LENGTH = 2048  # Practical browser/server limit


def validate_url(raw_url: str) -> str:
    """
    Validates a raw user-submitted URL string.

    Returns the cleaned URL if valid, otherwise raises URLValidationError.
    This is the single entry point every URL must pass through before
    any feature extraction or analysis happens.
    """
    if not raw_url or not raw_url.strip():
        raise URLValidationError("URL cannot be empty.")

    url = raw_url.strip()

    if len(url) > MAX_URL_LENGTH:
        raise URLValidationError(f"URL exceeds maximum length of {MAX_URL_LENGTH} characters.")

    # Require an explicit scheme; default to https:// if missing so
    # "example.com" style input still works, without guessing http.
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    if not validators.url(url):
        raise URLValidationError("URL format is invalid.")

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise URLValidationError("Only http and https URLs are supported.")

    if not parsed.netloc:
        raise URLValidationError("URL is missing a valid host.")

    return url