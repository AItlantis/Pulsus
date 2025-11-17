"""
Documentation Scanner

Scans for existing documentation (.md files) and general docs in ../document directory.
"""

from pathlib import Path
from typing import Dict, Optional, List


def find_script_documentation(script_path: Path) -> Optional[Path]:
    """
    Find existing documentation for a script.

    Args:
        script_path: Path to the Python script

    Returns:
        Path to .md file if it exists, None otherwise
    """
    md_path = script_path.with_suffix('.md')
    if md_path.exists():
        return md_path
    return None


def find_document_directory(script_path: Path) -> Optional[Path]:
    """
    Find the ../document directory relative to the script.

    Args:
        script_path: Path to the Python script

    Returns:
        Path to document directory if it exists, None otherwise
    """
    # Try ../document from script's parent directory
    doc_dir = script_path.parent.parent / "document"
    if doc_dir.exists() and doc_dir.is_dir():
        return doc_dir

    # Try ../documents
    doc_dir = script_path.parent.parent / "documents"
    if doc_dir.exists() and doc_dir.is_dir():
        return doc_dir

    # Try ./document in same directory
    doc_dir = script_path.parent / "document"
    if doc_dir.exists() and doc_dir.is_dir():
        return doc_dir

    return None


def scan_related_documentation(script_path: Path) -> List[Dict[str, str]]:
    """
    Scan for related documentation files in ../document directory.

    Looks for files with similar names or general documentation.

    Args:
        script_path: Path to the Python script

    Returns:
        List of dictionaries with 'path' and 'content' keys
    """
    doc_dir = find_document_directory(script_path)
    if not doc_dir:
        return []

    related_docs = []
    script_name = script_path.stem

    # Look for markdown files
    for md_file in doc_dir.glob("**/*.md"):
        # Skip very large files
        if md_file.stat().st_size > 1024 * 1024:  # 1MB
            continue

        # Check if filename is related
        is_related = (
            script_name.lower() in md_file.stem.lower() or
            md_file.stem.lower() in script_name.lower() or
            md_file.stem.lower() in ['readme', 'overview', 'guide', 'documentation']
        )

        if is_related:
            try:
                content = md_file.read_text(encoding='utf-8')
                related_docs.append({
                    'path': str(md_file),
                    'name': md_file.name,
                    'content': content[:5000]  # Limit to 5000 chars
                })
            except Exception:
                pass

    return related_docs


def load_existing_documentation(script_path: Path) -> Optional[str]:
    """
    Load existing documentation for a script if available.

    Args:
        script_path: Path to the Python script

    Returns:
        Content of existing .md file, or None
    """
    md_path = find_script_documentation(script_path)
    if md_path:
        try:
            return md_path.read_text(encoding='utf-8')
        except Exception:
            return None
    return None


def has_documentation(script_path: Path) -> bool:
    """
    Check if script already has documentation.

    Args:
        script_path: Path to the Python script

    Returns:
        True if .md file exists
    """
    return find_script_documentation(script_path) is not None


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_path = Path(sys.argv[1])
        print(f"Testing documentation scanner for: {test_path}")
        print(f"Has docs: {has_documentation(test_path)}")
        print(f"Document dir: {find_document_directory(test_path)}")
        related = scan_related_documentation(test_path)
        print(f"Related docs found: {len(related)}")
        for doc in related:
            print(f"  - {doc['name']}")
