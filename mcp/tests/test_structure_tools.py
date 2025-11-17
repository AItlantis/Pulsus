"""
Test script for new MCP structure tools (format_script and scan_structure).

This script demonstrates and tests:
1. mcp_format_script() - Auto-format Python scripts
2. mcp_scan_structure() - Scan directory structure and build dependency map
"""

import sys
import json
from pathlib import Path

# Add parent directories to path
testudo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(testudo_root))

from agents.mcp.helpers.script_ops import ScriptOps


def test_format_script():
    """Test mcp_format_script() functionality."""
    print("=" * 70)
    print("TEST: mcp_format_script()")
    print("=" * 70)

    script_ops = ScriptOps()

    # Test with this file
    test_file = Path(__file__)

    print(f"\nTesting format check on: {test_file.name}")
    print("-" * 70)

    # Check only (don't modify)
    result = script_ops.format_script(str(test_file), check_only=True)

    print(f"Success: {result['success']}")
    print(f"Would be formatted: {result['formatted']}")
    print(f"Changes detected: {len(result.get('changes', []))}")

    if result.get('changes'):
        print("\nChanges:")
        for change in result['changes']:
            print(f"  - {change}")

    print(f"\nMessage: {result.get('message', 'N/A')}")

    if result.get('error'):
        print(f"Error: {result['error']}")

    print("\n" + "=" * 70)
    print("[OK] Format script test completed")
    print("=" * 70)


def test_scan_structure():
    """Test mcp_scan_structure() functionality."""
    print("\n" + "=" * 70)
    print("TEST: mcp_scan_structure()")
    print("=" * 70)

    script_ops = ScriptOps()

    # Scan the agents/mcp directory
    base_dir = Path(__file__).parent

    print(f"\nScanning directory: {base_dir}")
    print("-" * 70)

    result = script_ops.scan_structure(
        str(base_dir),
        include_patterns=['*.py'],
        exclude_patterns=['__pycache__', '*.pyc']
    )

    if result['success']:
        stats = result['statistics']

        print("\n[STATISTICS]")
        print("-" * 70)
        print(f"Total files:       {stats['total_files']}")
        print(f"Total directories: {stats['total_directories']}")
        print(f"Total lines:       {stats['total_lines']}")
        print(f"Total imports:     {stats['total_imports']}")
        print(f"Files with errors: {stats['files_with_errors']}")

        if stats.get('top_imports'):
            print(f"\n[TOP IMPORTED MODULES]")
            print("-" * 70)
            for imp in stats['top_imports'][:5]:
                print(f"  {imp['module']:30s} ({imp['count']} files)")

        # Show dependency map for a few files
        dep_map = result['dependency_map']
        print(f"\n[DEPENDENCY MAP] ({len(dep_map)} files)")
        print("-" * 70)

        for i, (file_path, info) in enumerate(list(dep_map.items())[:3]):
            if 'error' in info:
                print(f"\n{file_path}:")
                print(f"  [ERROR] {info['error']}")
            else:
                print(f"\n{file_path}:")
                print(f"  Lines: {info['lines']}")
                print(f"  Imports: {info['num_imports']}")
                if info['imports']:
                    print(f"  Dependencies:")
                    for imp in info['imports'][:3]:
                        if imp['type'] == 'import':
                            print(f"    - import {imp['module']}")
                        else:
                            print(f"    - from {imp['module']} import {imp['name']}")
                    if len(info['imports']) > 3:
                        print(f"    ... and {len(info['imports']) - 3} more")

        if len(dep_map) > 3:
            print(f"\n  ... and {len(dep_map) - 3} more files")

        # Show directory tree structure
        structure = result['structure']
        print(f"\n[DIRECTORY STRUCTURE]")
        print("-" * 70)
        print_tree(structure, indent=0, max_depth=2)

    else:
        print(f"[ERROR] {result['error']}")

    print("\n" + "=" * 70)
    print("[OK] Structure scan test completed")
    print("=" * 70)


def print_tree(node, indent=0, max_depth=3):
    """Print directory tree recursively."""
    if indent > max_depth:
        return

    prefix = "  " * indent

    if node['type'] == 'directory':
        print(f"{prefix}[DIR] {node['name']}/")
        for child in node.get('children', []):
            print_tree(child, indent + 1, max_depth)
    else:
        size_kb = node.get('size', 0) / 1024
        print(f"{prefix}[FILE] {node['name']} ({size_kb:.1f} KB)")


def test_format_with_sample_code():
    """Test formatting with a sample unformatted code."""
    print("\n" + "=" * 70)
    print("TEST: Format sample unformatted code")
    print("=" * 70)

    # Create a temporary file with poorly formatted code
    import tempfile

    unformatted_code = '''
import os,sys
import json
from pathlib import Path
import re

unused_import = "test"

def test_function(  a,b,c  ):
    result=a+b+c
    return result

class TestClass:
    def __init__(self,value):
        self.value=value

    def get_value( self ):
        return self.value
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(unformatted_code)
        temp_file = f.name

    try:
        script_ops = ScriptOps()

        print(f"\nOriginal code:")
        print("-" * 70)
        print(unformatted_code)

        # Check formatting
        result = script_ops.format_script(temp_file, check_only=True)

        print("\nFormatting check results:")
        print("-" * 70)
        print(f"Needs formatting: {result['formatted']}")
        print(f"Changes:")
        for change in result.get('changes', []):
            print(f"  - {change}")

    finally:
        # Clean up
        Path(temp_file).unlink(missing_ok=True)

    print("\n" + "=" * 70)
    print("[OK] Sample code formatting test completed")
    print("=" * 70)


if __name__ == "__main__":
    print("\nMCP STRUCTURE TOOLS TEST SUITE")
    print("=" * 70)

    try:
        # Test 1: Format script
        test_format_script()

        # Test 2: Scan structure
        test_scan_structure()

        # Test 3: Format sample code
        test_format_with_sample_code()

        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70)

    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
