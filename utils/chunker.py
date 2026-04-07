"""
utils/chunker.py
Code-aware chunking system.

Rules:
  - Python  : split by def / class
  - JS / TS : split by function / arrow functions
  - CSS/HTML: split by fixed line windows
  - Max 200 chunks total across all files
  - Each chunk carries metadata (file, type, index)
"""

import re

# ─── Constants ───────────────────────────────────────────────────────────────
MAX_TOTAL_CHUNKS  = 200
FALLBACK_LINES    = 50      # lines per chunk for CSS / HTML


# ─── Language Routers ────────────────────────────────────────────────────────

def chunk_file(file: dict) -> list[dict]:
    """
    Chunk a single file dict: {"path", "content", "extension", ...}
    Returns list of chunk dicts.
    """
    path    = file["path"]
    content = file["content"]
    ext     = file.get("extension", "." + path.rsplit(".", 1)[-1].lower())

    if ext == ".py":
        raw_chunks = _chunk_python(content)
    elif ext in {".js", ".ts"}:
        raw_chunks = _chunk_js(content)
    else:
        raw_chunks = _chunk_by_lines(content, FALLBACK_LINES)

    # Build chunk dicts with metadata
    chunks = []
    for i, text in enumerate(raw_chunks):
        text = text.strip()
        if not text:
            continue
        chunks.append({
            "chunk_id"  : f"{path}::chunk_{i}",
            "file_path" : path,
            "extension" : ext,
            "chunk_index": i,
            "content"   : text,
            "line_count": len(text.splitlines()),
        })

    return chunks


# ─── Python Chunker ──────────────────────────────────────────────────────────

def _chunk_python(content: str) -> list[str]:
    """Split Python source by top-level def / class boundaries."""
    lines   = content.splitlines(keepends=True)
    chunks  = []
    current = []

    # Pattern: line that starts a new top-level def or class
    boundary = re.compile(r'^(def |class |\basync\s+def )')

    for line in lines:
        if boundary.match(line) and current:
            chunks.append("".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("".join(current))

    # If no boundaries found, fall back to line windows
    if len(chunks) <= 1 and len(lines) > FALLBACK_LINES:
        return _chunk_by_lines(content, FALLBACK_LINES)

    return chunks


# ─── JS / TS Chunker ─────────────────────────────────────────────────────────

def _chunk_js(content: str) -> list[str]:
    """
    Split JS/TS by function declarations, arrow functions, and class declarations.
    Splits on lines that look like the START of a new top-level function/class.
    """
    lines   = content.splitlines(keepends=True)
    chunks  = []
    current = []

    # Matches:  function foo(  |  const foo = (  |  class Foo  |  export function
    boundary = re.compile(
        r'^\s*(export\s+)?(default\s+)?(async\s+)?'
        r'(function[\s*]|class\s+\w|const\s+\w+\s*=\s*(async\s*)?\(|'
        r'const\s+\w+\s*=\s*(async\s*)?function)'
    )

    for line in lines:
        if boundary.match(line) and current:
            chunks.append("".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        chunks.append("".join(current))

    if len(chunks) <= 1 and len(lines) > FALLBACK_LINES:
        return _chunk_by_lines(content, FALLBACK_LINES)

    return chunks


# ─── Fallback: Fixed Line Windows ────────────────────────────────────────────

def _chunk_by_lines(content: str, window: int) -> list[str]:
    """Split content into fixed-size line windows."""
    lines  = content.splitlines()
    chunks = []
    for i in range(0, len(lines), window):
        chunk = "\n".join(lines[i : i + window])
        if chunk.strip():
            chunks.append(chunk)
    return chunks if chunks else [content]


# ─── Batch Chunker ───────────────────────────────────────────────────────────

def chunk_all_files(files: list[dict]) -> tuple[list[dict], dict]:
    """
    Chunk all files and enforce the MAX_TOTAL_CHUNKS cap.

    Returns:
        (chunks, report)
        chunks = [{"chunk_id", "file_path", "extension",
                   "chunk_index", "content", "line_count"}, ...]
        report = {"total_chunks", "files_chunked", "capped", "by_extension"}
    """
    all_chunks = []

    for f in files:
        file_chunks = chunk_file(f)
        all_chunks.extend(file_chunks)

    capped = len(all_chunks) > MAX_TOTAL_CHUNKS
    if capped:
        all_chunks = all_chunks[:MAX_TOTAL_CHUNKS]

    # Build report
    by_ext = {}
    for c in all_chunks:
        ext = c["extension"]
        by_ext[ext] = by_ext.get(ext, 0) + 1

    report = {
        "total_chunks" : len(all_chunks),
        "files_chunked": len({c["file_path"] for c in all_chunks}),
        "capped"       : capped,
        "by_extension" : by_ext,
    }

    return all_chunks, report