# Code Language Detector

Detects the programming language of a code snippet — paste it, upload a file,
or pipe it through the CLI. Built on a transparent, weighted pattern-matching
engine instead of a trained model: no dataset to collect, no GPU to train on,
no black box to explain in an interview.

**Live demo:** _add your deployed link here_

## Why a rule engine instead of machine learning

The first version of this project trained a CNN (MobileNet) to classify
*screenshots* of code as images. That approach works, but it's the wrong
tool for the job: it needs a labeled image dataset, a GPU-friendly training
loop, and it still can't explain *why* it thinks a snippet is Python. It also
never scaled past 3 languages.

Language detection is fundamentally a text problem — every language has
near-unique, cheap-to-check textual fingerprints (`<?php`, `public static
void main`, `fn main()`, `SELECT ... FROM`). So this version scores a
snippet's raw text against a table of weighted regex signatures per
language. The result:

- **16 languages**, with no retraining cost to add a 17th — just append rules.
- **Explainable output** — every prediction lists exactly which patterns fired.
- **Zero dependencies** for the detection logic itself (Flask is only needed for the web UI).
- **Microsecond latency**, deterministic and unit-testable.

## How it works

1. Each language owns a list of `(regex, weight, description)` rules — see
   [`detector/rules.py`](detector/rules.py). Stronger, less ambiguous signals
   (a `<?php` tag, a `public static void main` signature) carry more weight
   than common ones (a trailing semicolon).
2. [`detector/detector.py`](detector/detector.py) runs every rule against the
   input once, sums the weights per language, and optionally adds a small
   boost if the filename's extension agrees with the content.
3. The winner's confidence is its share of the total score across all
   languages that matched at all — so an unambiguous PHP file scores close to
   100%, while a five-line snippet that could plausibly be several languages
   reports a lower, honest confidence.

```python
from detector import LanguageDetector

result = LanguageDetector().detect("def add(a, b):\n    return a + b")
print(result.language, result.confidence)   # Python 83.3
print(result.matched_rules[result.language])
# ['function definition (def ...:)', 'colon-terminated block header']
```

## Supported languages

Python · JavaScript · TypeScript · Java · C · C++ · C# · Go · Ruby · PHP ·
Rust · HTML · CSS · SQL · Bash · JSON

## Project structure

```
.
├── app.py                  # Flask app: web UI + JSON API
├── detector/
│   ├── rules.py             # weighted regex signatures per language
│   ├── detector.py          # scoring engine
│   └── __main__.py          # CLI: python -m detector <file>
├── templates/index.html     # paste / upload UI
├── static/                  # CSS + progressive-enhancement JS
├── tests/test_detector.py   # one real-world snippet per language
└── requirements.txt
```

## Running it locally

```bash
git clone https://github.com/liyahayut/Code-Language-Detector.git
cd build
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
# -> http://127.0.0.1:5000
```

### CLI

```bash
python -m detector path/to/file.py another/file.js
```

### Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## API

```
POST /api/detect
Content-Type: application/json

{ "code": "console.log('hi')", "filename": "optional.js" }
```

Returns the detected language, a confidence score, per-language raw scores,
and the human-readable list of rules that matched.

## Deployment

A `Procfile` is included for Heroku-style platforms (`gunicorn app:app`).

## What changed from v1

- Replaced the image-classification pipeline (MobileNet + Keras, `.keras`
  model file, screenshot dataset) with the text-based rule engine above.
- Removed personal screenshots that had been committed to `uploads/` and
  added `uploads/` to `.gitignore` so user-submitted files are never
  version-controlled again.
- Replaced the unpinned, 50-plus-package `pip freeze` dump in
  `requirements.txt` with the two packages the app actually imports.
- Added a test suite, a CLI, a JSON API, and this README.

## License

MIT — see [LICENSE](LICENSE).
