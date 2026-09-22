"""
Core detection engine.

The detector scores a code snippet against every language's rule set and
turns the raw scores into a ranked, human-explainable result. It is pure
Python, has zero third-party dependencies, and runs in microseconds even on
large files, since it never touches the network or loads a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .rules import LANGUAGE_RULES

# Optional signal: a matching file extension gives a language a head start,
# but content is always re-checked, so a mislabeled or extension-less file
# still gets classified correctly from its content.
EXTENSION_HINTS: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".c": "C",
    ".h": "C",
    ".cs": "C#",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP",
    ".rs": "Rust",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".sql": "SQL",
    ".sh": "Bash",
    ".bash": "Bash",
    ".json": "JSON",
}

EXTENSION_HINT_WEIGHT = 2.0


@dataclass
class DetectionResult:
    language: str | None
    confidence: float  # 0-100, share of total score captured by the winner
    scores: dict[str, float] = field(default_factory=dict)
    matched_rules: dict[str, list[str]] = field(default_factory=dict)

    def ranked(self) -> list[tuple[str, float]]:
        """Languages sorted by score, highest first."""
        return sorted(self.scores.items(), key=lambda kv: kv[1], reverse=True)


class LanguageDetector:
    """Detects the programming language of a source-code snippet."""

    def __init__(self, rules: dict = LANGUAGE_RULES) -> None:
        self._rules = rules

    def detect(self, code: str, filename: str | None = None) -> DetectionResult:
        if not code or not code.strip():
            return DetectionResult(language=None, confidence=0.0)

        scores: dict[str, float] = {lang: 0.0 for lang in self._rules}
        matched: dict[str, list[str]] = {lang: [] for lang in self._rules}

        for language, rules in self._rules.items():
            for rule in rules:
                if rule.pattern.search(code):
                    scores[language] += rule.weight
                    matched[language].append(rule.description)

        if filename:
            ext = _extract_extension(filename)
            hinted = EXTENSION_HINTS.get(ext)
            if hinted and hinted in scores:
                scores[hinted] += EXTENSION_HINT_WEIGHT
                matched[hinted].append(f"filename extension '{ext}'")

        total = sum(scores.values())
        # drop languages with no evidence at all, to keep the result readable
        scores = {lang: s for lang, s in scores.items() if s > 0}
        matched = {lang: reasons for lang, reasons in matched.items() if lang in scores}

        if not scores:
            return DetectionResult(language=None, confidence=0.0)

        best_lang, best_score = max(scores.items(), key=lambda kv: kv[1])
        confidence = round((best_score / total) * 100, 1) if total else 0.0

        return DetectionResult(
            language=best_lang,
            confidence=confidence,
            scores=scores,
            matched_rules=matched,
        )


def _extract_extension(filename: str) -> str:
    idx = filename.rfind(".")
    return filename[idx:].lower() if idx != -1 else ""
