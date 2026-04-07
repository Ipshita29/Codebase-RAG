"""
utils/filter.py
Smart file filtering — applies all rules to a raw list of files.
 
Rules:
  - Allowed extensions: .py .js .ts .css .html
  - Ignore folders: node_modules, .git, dist, build, __pycache__
  - Max file size: 100KB
  - Priority folders: src/, app/, backend/, frontend/, server/, client/
  - Remove duplicates (same path)
  - Return a FilterReport alongside filtered files
"""
 
# ─── Constants ──────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {".py", ".js", ".ts", ".css", ".html",".md"}
IGNORE_FOLDERS     = {"node_modules", ".git", "dist", "build", "__pycache__"}
PRIORITY_FOLDERS   = {"src", "app", "backend", "frontend", "server", "client"}
MAX_FILE_SIZE_KB   = 100
 
 
# ─── Internal Helpers ────────────────────────────────────────────────────────
 
def _get_extension(path: str) -> str:
    if "." in path:
        return "." + path.rsplit(".", 1)[-1].lower()
    return ""
 
 
def _in_ignored_folder(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in IGNORE_FOLDERS for part in parts)
 
 
def _is_priority(path: str) -> bool:
    parts = path.replace("\\", "/").split("/")
    return any(part in PRIORITY_FOLDERS for part in parts)
 
 
def _size_kb(content: str) -> float:
    return len(content.encode("utf-8")) / 1024
 
 
# ─── Main Filter Function ────────────────────────────────────────────────────
 
def filter_files(files: list[dict]) -> tuple[list[dict], dict]:
    """
    Filter a list of files using all system rules.
 
    Input:
        files = [{"path": str, "content": str}, ...]
 
    Returns:
        (filtered_files, report)
 
        filtered_files = [{"path": str, "content": str}, ...]
 
        report = {
            "total_input"      : int,
            "passed"           : int,
            "skipped_extension": int,
            "skipped_folder"   : int,
            "skipped_size"     : int,
            "skipped_duplicate": int,
            "priority_files"   : int,
            "by_extension"     : {"ext": count, ...},
        }
    """
    report = {
        "total_input"       : len(files),
        "passed"            : 0,
        "skipped_extension" : 0,
        "skipped_folder"    : 0,
        "skipped_size"      : 0,
        "skipped_duplicate" : 0,
        "priority_files"    : 0,
        "by_extension"      : {},
    }
 
    seen_paths = set()
    passed     = []
 
    for f in files:
        path    = f.get("path", "")
        content = f.get("content", "")
 
        # 1. Duplicate check
        if path in seen_paths:
            report["skipped_duplicate"] += 1
            continue
        seen_paths.add(path)
 
        # 2. Extension check
        ext = _get_extension(path)
        if ext not in ALLOWED_EXTENSIONS:
            report["skipped_extension"] += 1
            continue
 
        # 3. Ignored folder check
        if _in_ignored_folder(path):
            report["skipped_folder"] += 1
            continue
 
        # 4. File size check
        if _size_kb(content) > MAX_FILE_SIZE_KB:
            report["skipped_size"] += 1
            continue
 
        # ── Passed all filters ──
        is_p = _is_priority(path)
        if is_p:
            report["priority_files"] += 1
 
        report["by_extension"][ext] = report["by_extension"].get(ext, 0) + 1
 
        passed.append({
            "path"       : path,
            "content"    : content,
            "extension"  : ext,
            "size_kb"    : round(_size_kb(content), 2),
            "is_priority": is_p,
        })
 
    # 5. Sort: priority folders first, then alphabetically
    passed.sort(key=lambda x: (0 if x["is_priority"] else 1, x["path"]))
 
    report["passed"] = len(passed)
    return passed, report
 
 
# ─── Report Formatter ────────────────────────────────────────────────────────
 
def format_report(report: dict) -> str:
    """Return a human-readable summary of the filter report."""
    lines = [
        f"Total input files  : {report['total_input']}",
        f"Passed filtering   : {report['passed']}",
        f"Priority files     : {report['priority_files']}",
        f"Skipped (extension): {report['skipped_extension']}",
        f"Skipped (folder)   : {report['skipped_folder']}",
        f"Skipped (too large): {report['skipped_size']}",
        f"Skipped (duplicate): {report['skipped_duplicate']}",
        "",
        "By extension:",
    ]
    for ext, count in sorted(report["by_extension"].items()):
        lines.append(f"  {ext:<8} {count} file(s)")
    return "\n".join(lines)