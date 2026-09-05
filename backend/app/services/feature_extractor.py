import math
import re
from collections import Counter
from urllib.parse import urlparse

import tldextract

SUSPICIOUS_KEYWORDS = [
    "login", "signin", "verify", "account", "update", "secure",
    "banking", "confirm", "password", "webscr", "billing",
]

IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}"
    r"(?:25[0-5]|2[0-4]\d|[01]?\d?\d)$"
)


def _shannon_entropy(text: str) -> float:
    """
    Measures randomness of a string. High entropy hostnames
    (e.g. 'x7f2k9q.com') are a common phishing/DGA indicator.
    """
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def extract_features(url: str) -> dict:
    """
    Extracts lexical features from a validated URL.
    Assumes the URL has already passed validate_url().
    """
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    extracted = tldextract.extract(url)

    subdomain = extracted.subdomain
    subdomain_count = len(subdomain.split(".")) if subdomain else 0

    path = parsed.path or ""
    query = parsed.query or ""

    return {
        "url_length": len(url),
        "hostname_length": len(hostname),
        "path_length": len(path),
        "query_length": len(query),
        "has_fragment": bool(parsed.fragment),

        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_underscores": url.count("_"),
        "num_digits": sum(c.isdigit() for c in url),
        "num_special_chars": len(re.findall(r"[@%&=\$!\*]", url)),
        "num_query_params": query.count("&") + 1 if query else 0,

        "num_subdomains": subdomain_count,
        "is_ip_address": bool(IP_PATTERN.match(hostname)),
        "is_https": parsed.scheme == "https",

        "has_at_symbol": "@" in url,
        "has_double_slash_redirect": "//" in path,
        "has_encoded_chars": "%" in url,

        "has_suspicious_keyword": any(
            kw in url.lower() for kw in SUSPICIOUS_KEYWORDS
        ),

        "hostname_entropy": round(_shannon_entropy(hostname), 3),

        "tld": extracted.suffix,
    }