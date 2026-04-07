"""
utils/file_handler.py
Handles:
  - Fetching files from a public GitHub repo
  - Extracting files from an uploaded ZIP
Strategy: Download the repo as a ZIP via GitHub (no API token needed),
then extract it in-memory — avoids rate limits entirely.
"""

import io
import os
import zipfile
import requests

# ─── Constants ──────────────────────────────────────────────────────────────
GITHUB_MAX_FILES = 150
ZIP_MAX_FILES    = 50
ZIP_MAX_SIZE_MB  = 5
MAX_FILE_SIZE_KB = 100

ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".css", ".html",".md"}
IGNORE_FOLDERS     = {"node_modules", ".git", "dist", "build", "__pycache__"}
PRIORITY_FOLDERS   = {"src", "app", "backend", "frontend", "server", "client"}


# ─── Helpers ────────────────────────────────────────────────────────────────

def _is_allowed(filename: str) -> bool:
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)


def _in_ignored_folder(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in IGNORE_FOLDERS for part in parts)


def _is_priority(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in PRIORITY_FOLDERS for part in parts)


def _parse_github_url(url: str):
    """Return (owner, repo) from a GitHub URL."""
    url = url.strip().rstrip("/")
    # Remove trailing .git if present
    if url.endswith(".git"):
        url = url[:-4]
    try:
        parts = url.split("github.com/")[1].split("/")
        return parts[0], parts[1]
    except (IndexError, AttributeError):
        return None, None


def _get_headers() -> dict:
    """
    Build request headers.
    If a GitHub token is set (via env var GITHUB_TOKEN), include it.
    This is optional — the main fetch strategy doesn't need it.
    """
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


# ─── GitHub Fetcher (ZIP download strategy — no rate limit) ─────────────────

def fetch_github_files(github_url: str):
    """
    Download the repo as a ZIP archive from GitHub.
    This uses the /zipball endpoint which does NOT count against
    the 60 req/hour unauthenticated API rate limit.

    Returns: (files list, error string)
    files = [{"path": str, "content": str}, ...]
    """
    owner, repo = _parse_github_url(github_url)
    if not owner or not repo:
        return [], "Invalid GitHub URL. Format: https://github.com/owner/repo"

    # GitHub's zipball endpoint — downloads the whole repo as a zip
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

    try:
        resp = requests.get(zip_url, timeout=30, allow_redirects=True)

        # If 'main' branch doesn't exist, try 'master'
        if resp.status_code == 404:
            zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/master.zip"
            resp = requests.get(zip_url, timeout=30, allow_redirects=True)

        if resp.status_code == 404:
            return [], f"Repo not found or is private: github.com/{owner}/{repo}"

        if resp.status_code != 200:
            return [], f"Failed to download repo (HTTP {resp.status_code}). Check the URL."

    except requests.exceptions.ConnectionError:
        return [], "Network error. Could not reach GitHub. Check your internet connection."
    except requests.exceptions.Timeout:
        return [], "Request timed out. The repo may be too large. Try a smaller repo."

    # Now extract from the in-memory ZIP
    try:
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
    except zipfile.BadZipFile:
        return [], "Downloaded file was not a valid ZIP. Try again."

    all_names = zf.namelist()

    # GitHub ZIPs have a root folder like "repo-main/" — strip it
    candidates = []
    for name in all_names:
        # Skip directories
        if name.endswith("/"):
            continue
        # Strip the root folder prefix (e.g. "myrepo-main/src/app.py" → "src/app.py")
        parts = name.split("/", 1)
        relative_path = parts[1] if len(parts) > 1 else name

        if not relative_path:
            continue
        if not _is_allowed(relative_path):
            continue
        if _in_ignored_folder(relative_path):
            continue

        candidates.append((name, relative_path))   # (zip_name, display_path)

    # Sort: priority folders first
    candidates.sort(key=lambda x: (0 if _is_priority(x[1]) else 1, x[1]))
    candidates = candidates[:GITHUB_MAX_FILES]

    files = []
    for zip_name, relative_path in candidates:
        try:
            data = zf.read(zip_name)
            if len(data) > MAX_FILE_SIZE_KB * 1024:
                continue    # skip files > 100KB
            content = data.decode("utf-8", errors="ignore")
            files.append({"path": relative_path, "content": content})
        except Exception:
            continue

    if not files:
        return [], "No supported code files found (.py, .js, .ts, .css, .html)."

    return files, ""


# ─── ZIP Extractor ──────────────────────────────────────────────────────────

def extract_zip_files(zip_bytes: bytes):
    """
    Extract code files from an uploaded ZIP (bytes).
    Returns: (files list, error string)
    """
    size_mb = len(zip_bytes) / (1024 * 1024)
    if size_mb > ZIP_MAX_SIZE_MB:
        return [], f"ZIP too large: {size_mb:.1f}MB. Max allowed is {ZIP_MAX_SIZE_MB}MB."

    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return [], "Invalid ZIP file. Please upload a valid .zip archive."

    all_names = zf.namelist()

    candidates = [
        name for name in all_names
        if not name.endswith("/")
        and _is_allowed(name)
        and not _in_ignored_folder(name)
    ]

    candidates.sort(key=lambda x: (0 if _is_priority(x) else 1, x))
    candidates = candidates[:ZIP_MAX_FILES]

    files = []
    for name in candidates:
        try:
            data = zf.read(name)
            if len(data) > MAX_FILE_SIZE_KB * 1024:
                continue
            files.append({"path": name, "content": data.decode("utf-8", errors="ignore")})
        except Exception:
            continue

    if not files:
        return [], "No supported code files found in the ZIP."

    return files, ""