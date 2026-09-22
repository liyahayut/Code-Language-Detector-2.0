"""Command-line interface: python -m detector <file> [file ...]"""

from __future__ import annotations

import sys

from .detector import LanguageDetector


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: python -m detector <file> [file ...]")
        return 1

    detector = LanguageDetector()
    for path in argv:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                code = f.read()
        except OSError as exc:
            print(f"{path}: could not read file ({exc})")
            continue

        result = detector.detect(code, filename=path)
        if result.language:
            print(f"{path}: {result.language} ({result.confidence}% confidence)")
        else:
            print(f"{path}: unknown")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
