"""
Weighted, regex-based language signatures.

Each language maps to a list of Rule objects. A Rule is a compiled regex
paired with a weight and a short human-readable description. Higher weight
means the pattern is a stronger, less ambiguous signal for that language
(e.g. `<?php` is worth far more than a lone semicolon).

Adding a new language is a matter of appending an entry to LANGUAGE_RULES —
no retraining, no dataset needed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    pattern: re.Pattern
    weight: float
    description: str


def _rule(pattern: str, weight: float, description: str, flags: int = re.MULTILINE) -> Rule:
    return Rule(re.compile(pattern, flags), weight, description)


LANGUAGE_RULES: dict[str, list[Rule]] = {
    "Python": [
        _rule(r"^\s*def\s+\w+\s*\(.*\)\s*:", 3, "function definition (def ...:)"),
        _rule(r"^\s*class\s+\w+.*:\s*$", 3, "class definition"),
        _rule(r"^\s*(import|from)\s+[\w.]+", 2.5, "import statement"),
        _rule(r"\bself\.\w+", 2.5, "self.attribute reference"),
        _rule(r"^\s*elif\s+.*:", 2, "elif clause"),
        _rule(r"__init__|__main__|__name__", 2.5, "python dunder"),
        _rule(r"\bprint\(", 1.5, "print() call"),
        _rule(r"^\s*#(?!\!).*$", 0.5, "hash comment"),
        _rule(r":\s*$", 0.5, "colon-terminated block header"),
    ],
    "JavaScript": [
        _rule(r"\bconsole\.(log|error|warn)\(", 3, "console.log/error/warn"),
        _rule(r"=>\s*\{?", 2.5, "arrow function"),
        _rule(r"\b(const|let|var)\s+\w+\s*=", 2, "variable declaration"),
        _rule(r"\bfunction\s*\w*\s*\(.*\)\s*\{", 2.5, "function declaration"),
        _rule(r"\bdocument\.(getElementById|querySelector)", 3, "DOM access"),
        _rule(r"\brequire\(['\"]", 1.5, "CommonJS require"),
        _rule(r"\bexport\s+(default\s+)?(function|const|class)", 2, "ES module export"),
        _rule(r";\s*$", 0.3, "semicolon-terminated statement"),
    ],
    "TypeScript": [
        _rule(r"\binterface\s+\w+\s*\{", 4, "interface declaration"),
        _rule(r":\s*(string|number|boolean|void|any|unknown)\b", 3, "type annotation"),
        _rule(r"\bexport\s+(type|enum)\s+\w+", 3.5, "type/enum export"),
        _rule(r"<\w+>\s*\(", 1.5, "generic type parameter"),
        _rule(r"\bimplements\s+\w+", 3, "implements clause"),
        _rule(r"\bas\s+\w+;", 2, "type assertion"),
    ],
    "Java": [
        _rule(r"\bpublic\s+static\s+void\s+main\s*\(", 5, "main method signature"),
        _rule(r"\bSystem\.out\.println\(", 4, "System.out.println"),
        _rule(r"^\s*(public|private|protected)\s+(static\s+)?(final\s+)?class\s+\w+", 4, "class declaration"),
        _rule(r"\bimport\s+java\.", 3.5, "java.* import"),
        _rule(r"^\s*(public|private|protected)\s+[\w<>\[\]]+\s+\w+\s*\(.*\)\s*\{", 1.5, "typed method signature"),
        _rule(r"\bnew\s+\w+<.*>\(\)", 2, "generic instantiation"),
    ],
    "C++": [
        _rule(r"#include\s*<\w+>", 2, "angle-bracket include"),
        _rule(r"\bstd::\w+", 4, "std:: namespace usage"),
        _rule(r"\b(cout|cin)\s*(<<|>>)", 4, "cout/cin stream operator"),
        _rule(r"\busing\s+namespace\s+std;", 4, "using namespace std"),
        _rule(r"^\s*(template|class)\s*<?\w*>?\s*\{?", 1.5, "template/class"),
        _rule(r"\bnullptr\b", 2, "nullptr keyword"),
    ],
    "C": [
        _rule(r"#include\s*<\w+\.h>", 3.5, "C-style .h include"),
        _rule(r"\bprintf\(|\bscanf\(", 3, "printf/scanf"),
        _rule(r"\bint\s+main\s*\(\s*(void|int argc)?", 2.5, "int main(...)"),
        _rule(r"\bmalloc\(|\bfree\(", 2.5, "manual memory management"),
        _rule(r"->\w+", 1, "struct pointer access"),
        _rule(r"\btypedef\s+struct\b", 2.5, "typedef struct"),
    ],
    "C#": [
        _rule(r"\bConsole\.WriteLine\(", 4, "Console.WriteLine"),
        _rule(r"^\s*using\s+System(\.\w+)*;", 3.5, "using System;"),
        _rule(r"\bnamespace\s+[\w.]+", 3, "namespace declaration"),
        _rule(r"^\s*(public|private|protected)\s+(static\s+)?(async\s+)?\w+\s+\w+\s*\(.*\)\s*\{", 1.5, "typed method signature"),
        _rule(r"\bGet;\s*set;", 3, "auto property"),
    ],
    "Go": [
        _rule(r"^\s*package\s+main", 4, "package main"),
        _rule(r"\bfunc\s+\w+\s*\(", 3, "func declaration"),
        _rule(r"\bfmt\.(Println|Printf|Sprintf)\(", 4, "fmt.Print*"),
        _rule(r":=", 2, "short variable declaration"),
        _rule(r"^\s*import\s*\(", 2, "grouped import block"),
    ],
    "Ruby": [
        _rule(r"^\s*def\s+\w+.*$", 2, "method definition"),
        _rule(r"^\s*end\s*$", 2, "end keyword"),
        _rule(r"\bputs\s+", 3, "puts statement"),
        _rule(r"\brequire(_relative)?\s+['\"]", 1.5, "require"),
        _rule(r"@\w+", 1.5, "instance variable"),
        _rule(r"\bdo\s*\|.*\|", 2.5, "block with parameters"),
    ],
    "PHP": [
        _rule(r"<\?php", 5, "<?php opening tag"),
        _rule(r"\$\w+\s*=", 2, "variable assignment ($var =)"),
        _rule(r"\becho\s+", 1.5, "echo statement"),
        _rule(r"->\w+\(", 1, "method call on object"),
        _rule(r"\bfunction\s+\w+\s*\(.*\)\s*\{", 1.5, "function declaration"),
    ],
    "Rust": [
        _rule(r"\bfn\s+\w+\s*\(", 3, "fn declaration"),
        _rule(r"\blet\s+mut\s+\w+", 3.5, "let mut binding"),
        _rule(r"\bprintln!\(", 4, "println! macro"),
        _rule(r"\buse\s+std::", 3, "use std::"),
        _rule(r"->\s*\w+(<.*>)?\s*\{", 1.5, "typed return arrow"),
        _rule(r"\bimpl\s+\w+", 3, "impl block"),
    ],
    "HTML": [
        _rule(r"<!DOCTYPE\s+html>", 5, "DOCTYPE declaration"),
        _rule(r"</?(html|head|body|div|span)\b", 2, "structural tag"),
        _rule(r"<meta\s+", 1.5, "meta tag"),
        _rule(r"</?\w+[^>]*>", 0.4, "generic tag"),
    ],
    "CSS": [
        _rule(r"[.#]?[\w-]+\s*\{[^}]*:[^}]*;[^}]*\}", 3, "selector { property: value; }"),
        _rule(r"@media\s*\(", 3.5, "@media query"),
        _rule(r"^\s*[.#][\w-]+\s*\{", 2, "class/id selector"),
        _rule(r":\s*(hover|focus|active)\b", 2, "pseudo-class"),
    ],
    "SQL": [
        _rule(r"\bSELECT\b.*\bFROM\b", 5, "SELECT ... FROM", re.IGNORECASE | re.DOTALL),
        _rule(r"\bINSERT\s+INTO\b", 4.5, "INSERT INTO", re.IGNORECASE),
        _rule(r"\bCREATE\s+TABLE\b", 4.5, "CREATE TABLE", re.IGNORECASE),
        _rule(r"\bWHERE\b", 1.5, "WHERE clause", re.IGNORECASE),
        _rule(r"\bJOIN\b", 2, "JOIN clause", re.IGNORECASE),
    ],
    "Bash": [
        _rule(r"^#!.*\b(bash|sh)\b", 5, "shebang"),
        _rule(r"^\s*if\s*\[\s*.*\]\s*;\s*then", 3, "if [ ]; then"),
        _rule(r"\becho\s+", 1, "echo"),
        _rule(r"^\s*fi\s*$|^\s*done\s*$", 2, "fi/done terminator"),
        _rule(r"\$\{?\w+\}?", 0.5, "shell variable"),
    ],
    "JSON": [
        _rule(r'^\s*[{\[]', 1, "starts with { or ["),
        _rule(r'"\w+"\s*:\s*("|\d|\{|\[|true|false|null)', 2, "quoted key: value pair"),
        _rule(r"[{\[][\s\S]*[}\]]\s*$", 1, "balanced braces/brackets"),
    ],
}
