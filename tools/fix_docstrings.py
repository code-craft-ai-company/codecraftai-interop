#!/usr/bin/env python3

"""Utility to fix documentation formatting in ccai source files."""

import sys
from pathlib import Path


def fix_file(path: Path) -> bool:
    """Fix documentation indentation and blank line rules for a file."""

    text = path.read_text().splitlines()

    changed = False

    # Fix module level docstring indentation
    start_idx = None
    for idx, line in enumerate(text):
        if line.strip().startswith('"""'):
            start_idx = idx
            break
        if line.strip() and not line.startswith('#'):
            # stop if actual code or comment before docstring
            break
    if start_idx is not None:
        # find closing triple quotes
        for j in range(start_idx + 1, len(text)):
            if '"""' in text[j]:
                end_idx = j
                break
        else:
            end_idx = None

        if end_idx is not None:
            for k in range(start_idx + 1, end_idx):
                desired = '    ' + text[k].lstrip()
                if text[k] != desired:
                    text[k] = desired
                    changed = True

    # Ensure blank line between parameter list and returns in docstrings
    for idx, line in enumerate(text[:-1]):
        if line.lstrip().startswith(':param'):
            nxt = text[idx + 1].lstrip()
            if nxt.startswith(':returns') or nxt.startswith(':return'):
                text.insert(idx + 1, '')
                changed = True

    if changed:
        path.write_text('\n'.join(text) + '\n')

    return changed


def main(argv: list[str]) -> int:
    root = Path('source/packages/ccai/interop')
    py_files = sorted(root.rglob('*.py'))

    any_changed = False
    for py in py_files:
        if fix_file(py):
            any_changed = True
    return 0 if any_changed else 1


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))

