#!/usr/bin/env python3
"""
Diagram Rendering Utility

This script can render Mermaid diagrams from the ARCHITECTURE.md file
to PNG/SVG images using mermaid-cli (mmdc).

Requirements:
    npm install -g @mermaid-js/mermaid-cli

Usage:
    python scripts/render_diagrams.py
    python scripts/render_diagrams.py --format svg
    python scripts/render_diagrams.py --output docs/diagrams/
"""

import re
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict


def extract_mermaid_diagrams(markdown_file: Path) -> List[Dict[str, str]]:
    """
    Extract Mermaid diagrams from markdown file.

    Args:
        markdown_file: Path to markdown file

    Returns:
        List of dictionaries with diagram info
    """
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all mermaid code blocks
    pattern = r'```mermaid\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)

    diagrams = []
    for idx, diagram_code in enumerate(matches, 1):
        # Try to find the heading before the diagram
        # Look for ### heading before the diagram
        heading_pattern = r'###\s+\d+\.\s+(.*?)\n\n```mermaid'
        heading_match = re.search(heading_pattern, content[:content.find(diagram_code)])

        if heading_match:
            # Find the last heading before this diagram
            all_headings = re.finditer(r'###\s+\d+\.\s+(.*?)\n', content[:content.find(diagram_code)])
            headings_list = list(all_headings)
            if headings_list:
                title = headings_list[-1].group(1).strip()
            else:
                title = f"Diagram {idx}"
        else:
            title = f"Diagram {idx}"

        # Create safe filename
        filename = re.sub(r'[^\w\s-]', '', title.lower())
        filename = re.sub(r'[-\s]+', '_', filename)

        diagrams.append({
            'id': idx,
            'title': title,
            'filename': filename,
            'code': diagram_code.strip()
        })

    return diagrams


def render_diagram(
    diagram_code: str,
    output_file: Path,
    format: str = 'png',
    theme: str = 'default'
) -> bool:
    """
    Render a Mermaid diagram to image file.

    Args:
        diagram_code: Mermaid diagram code
        output_file: Output file path
        format: Output format ('png' or 'svg')
        theme: Mermaid theme ('default', 'dark', 'forest', 'neutral')

    Returns:
        True if successful
    """
    # Create temporary mermaid file
    temp_file = Path('/tmp/temp_diagram.mmd')
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(diagram_code)

    # Check if mmdc is installed
    try:
        subprocess.run(['mmdc', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: mermaid-cli (mmdc) is not installed")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return False

    # Render diagram
    try:
        cmd = [
            'mmdc',
            '-i', str(temp_file),
            '-o', str(output_file),
            '-t', theme,
            '-b', 'transparent'
        ]

        if format == 'svg':
            cmd.extend(['-f', 'svg'])

        subprocess.run(cmd, check=True, capture_output=True)

        print(f"✓ Rendered: {output_file}")
        return True

    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to render {output_file}: {e}")
        return False
    finally:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Render Mermaid diagrams to images')
    parser.add_argument(
        '--format',
        choices=['png', 'svg'],
        default='png',
        help='Output format (default: png)'
    )
    parser.add_argument(
        '--theme',
        choices=['default', 'dark', 'forest', 'neutral'],
        default='default',
        help='Mermaid theme (default: default)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='docs/diagrams',
        help='Output directory (default: docs/diagrams)'
    )
    parser.add_argument(
        '--markdown',
        type=str,
        default='docs/ARCHITECTURE.md',
        help='Markdown file to process (default: docs/ARCHITECTURE.md)'
    )

    args = parser.parse_args()

    # Paths
    project_root = Path(__file__).parent.parent
    markdown_file = project_root / args.markdown
    output_dir = project_root / args.output

    # Check if markdown file exists
    if not markdown_file.exists():
        print(f"Error: Markdown file not found: {markdown_file}")
        return

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting diagrams from {markdown_file}")
    diagrams = extract_mermaid_diagrams(markdown_file)

    print(f"Found {len(diagrams)} diagrams")
    print(f"Output directory: {output_dir}")
    print(f"Format: {args.format}")
    print(f"Theme: {args.theme}")
    print()

    # Render each diagram
    success_count = 0
    for diagram in diagrams:
        output_file = output_dir / f"{diagram['filename']}.{args.format}"

        print(f"[{diagram['id']}/{len(diagrams)}] {diagram['title']}")

        if render_diagram(diagram['code'], output_file, args.format, args.theme):
            success_count += 1

    print()
    print(f"✓ Successfully rendered {success_count}/{len(diagrams)} diagrams")

    if success_count < len(diagrams):
        print(f"✗ Failed to render {len(diagrams) - success_count} diagrams")

    # Create index file
    index_file = output_dir / 'README.md'
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write('# Architecture Diagrams\n\n')
        f.write('This directory contains rendered architecture diagrams.\n\n')
        f.write('## Diagrams\n\n')

        for diagram in diagrams:
            filename = f"{diagram['filename']}.{args.format}"
            f.write(f"### {diagram['title']}\n\n")
            f.write(f"![{diagram['title']}]({filename})\n\n")

    print(f"\n✓ Created index: {index_file}")


if __name__ == '__main__':
    main()
