#!/usr/bin/env python3
"""
BOS Bible Chapter Reformatter
Reusable helper script for the Grok BOS Chapter Reformatting Prompt series.

This script performs precise, rule-based transformations while guaranteeing
zero unintended changes to whitespace, markup, footnotes, or any other content.

Usage examples:
    # Apply Prompt #8 rules and print result
    python bos_reformatter.py "chapter.txt" --mode verse-list-numbering

    # Apply Prompt #8 rules and save to file
    python bos_reformatter.py "chapter.txt" "chapter_reformatted.txt" --mode verse-list-numbering

Supported modes (extendable for future prompts):
    verse-list-numbering   → Exactly the three changes from Prompt #8
"""

import re
import argparse
from pathlib import Path


def apply_verse_numbering_and_list_conversion(content: str) -> str:
    """
    Applies exactly the three required changes from BOS Prompt #8:
    1. Add bold verse numbers at the start of every <li> verse content
       (with exactly one space after </strong>)
    2. Convert all <ol start="N"> to <ul class="verse-list">
    3. Convert all </ol> to </ul>
    No other modifications are made.
    """
    # Change 2 + 3: Convert ordered lists to unordered lists with the verse-list class
    # Remove any start="X" attribute in the process
    content = re.sub(r'<ol start="\d+">', '<ul class="verse-list">', content)
    content = content.replace('</ol>', '</ul>')

    # Change 1: Add verse numbers
    verse_counter = [1]   # list so it is mutable inside the nested function

    def insert_verse_number(match: re.Match) -> str:
        num = verse_counter[0]
        verse_counter[0] += 1
        # Insert exactly: <strong>N</strong> + one space + original content
        return f"{match.group(1)}<strong>{num}</strong> {match.group(2)}{match.group(3)}"

    # Match every <li>...</li> and number its content
    # Using DOTALL in case any future verse spans lines (current files are single-line)
    content = re.sub(
        r'(<li>)(.*?)(</li>)',
        insert_verse_number,
        content,
        flags=re.DOTALL
    )

    return content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reusable BOS Bible Chapter Reformatter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python bos_reformatter.py input.txt --mode verse-list-numbering
  python bos_reformatter.py input.txt output.txt --mode verse-list-numbering
        """
    )
    parser.add_argument(
        "input_file",
        help="Path to the original chapter file (the one with <ol> lists)"
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default=None,
        help="Optional output path. If omitted, result is printed to stdout."
    )
    parser.add_argument(
        "--mode",
        choices=["verse-list-numbering"],
        default="verse-list-numbering",
        help="Which set of reformatting rules to apply (default: verse-list-numbering)"
    )

    args = parser.parse_args()

    # Read input
    input_path = Path(args.input_file)
    if not input_path.exists():
        parser.error(f"Input file not found: {input_path}")

    content = input_path.read_text(encoding="utf-8")

    # Apply the requested transformation
    if args.mode == "verse-list-numbering":
        result = apply_verse_numbering_and_list_conversion(content)
    else:
        result = content   # fallback (should not happen with current choices)

    # Write or print result
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.write_text(result, encoding="utf-8")
        print(f"✅ Reformatted file written to: {output_path.resolve()}")
    else:
        print(result)


if __name__ == "__main__":
    main()
