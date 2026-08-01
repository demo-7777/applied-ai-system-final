# 🎵 Music Recommender + Reliability System — Applied AI System

## Base Project (Module 3)

This project extends my **Module 3 "Music Recommender Simulation"** mini-project. The original was a small **content-based** recommender: it represented songs and a user "taste profile" as data, scored each song against the profile (genre +2, mood +1, energy similarity), and returned an explained, ranked top-*k* list. This applied-AI version keeps that engine and adds a **reliability/testing layer** — confidence scoring, guardrails, and an automated evaluation harness — so the system doesn't just produce recommendations, it *measures and defends how trustworthy they are*.

---

## Summary — What It Does & Why It Matters

Given a taste profile (`genre`, `mood`, `energy`), the system recommends the best-matching songs from its catalog, each with a plain-English reason **and a 0.0–1.0 confidence score**. When even the best match is weak (e.g. a genre the catalog doesn't cover), a **guardrail flags the result as low-confidence** instead of silently presenting a bad pick. An **evaluation harness** runs labeled profiles and reports accuracy + average confidence in a parseable format. This matters because a recommender that "feels" right but is never measured can quietly mislead — this version proves its behavior with tests and evidence.

**Chosen AI feature (required):** Reliability / Testing System — fully integrated into the recommend path (confidence changes what the system outputs and warns on), not a standalone script.

---

## Architecture Overview

Source diagram: [`diagrams/architecture.mmd`](diagrams/architecture.mmd) (Mermaid).

Data flows **input → process → output**, with a parallel reliability path:

1. **Input** — a taste profile plus the `songs.csv` catalog.
2. **Process** (`src/recommender.py`) — `load_songs` (guardrails: skip malformed rows, raise on empty catalog) → `score_song` → `recommend_songs` (rank top-*k* and attach a normalized **confidence**) → a **guardrail** that flags/logs low-confidence results.
3. **Output** — ranked recommendations with confidence + explanation, or a low-confidence warning.
4. **Reliability** — `src/evaluate.py` runs labeled cases into a markdown/JSON report; `pytest` unit-tests the functions; a human reviews the report and logs.

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux  (Windows: .venv\Scripts\activate)
pip install -r requirements.txt
```

Run the recommender:      `python -m src.main`
Run the evaluation harness: `python -m src.evaluate`
Run the tests:            `python -m pytest -q`

Committed output logs live in [`assets/`](assets/): `run_main.txt`, `run_evaluate.txt`, `run_tests.txt`.

---

## Sample Interactions (Reproducible Evidence)

### 1. End-to-end recommendation with confidence (`python -m src.main`)

Input profile: `{"genre": "pop", "mood": "happy", "energy": 0.8}`

```
INFO [recommender] Loaded 20 songs from data/songs.csv

=== High-Energy Pop: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8} ===

Sunrise City - Score: 3.98 - Confidence: 0.99
Because: genre match: pop (+2.0); mood match: happy (+1.0); energy close to 0.8 (+0.98)

Gym Hero - Score: 2.87 - Confidence: 0.72
Because: genre match: pop (+2.0); energy close to 0.8 (+0.87)

Rooftop Lights - Score: 1.96 - Confidence: 0.49
Because: mood match: happy (+1.0); energy close to 0.8 (+0.96)
```

### 2. Guardrail — low-confidence flag on an unknown genre

The evaluation harness includes an adversarial profile `{"genre": "polka", ...}`. No catalog song matches, so the guardrail fires:

```
WARNING [recommender] Low confidence (0.23) for prefs {'genre': 'polka', 'mood': 'party', 'energy': 0.5} — profile may not match the catalog
```

### 3. Reliability report (`python -m src.evaluate`)

```
| Case | Criterion | Top Pick | Confidence | Result |
|------|-----------|----------|------------|--------|
| High-Energy Pop | top pick genre == pop | Sunrise City (pop) | 0.99 | PASS |
| Deep Intense Rock | top pick genre == rock | Storm Runner (rock) | 0.98 | PASS |
| Chill Lofi | top pick genre == lofi | Library Rain (lofi) | 1.00 | PASS |
| Relaxed Jazz | top pick genre == jazz | Coffee Shop Stories (jazz) | 0.99 | PASS |
| Unknown Genre | flag low confidence (<0.4) | Midnight Coding (lofi) | 0.23 | PASS |

**5/5 cases passed; average confidence 0.84.**
```

(The harness also prints the same report as JSON for machine parsing.)

---

## Design Decisions & Trade-offs

- **Confidence = score / 4.0 (clamped 0–1).** The max achievable score is fixed (genre 2 + mood 1 + energy 1), so normalizing against it gives an intuitive, cheap confidence signal without a probabilistic model. Trade-off: it's a heuristic, not a calibrated probability — good enough to *rank trust*, not to quote as a real likelihood.
- **Guardrail threshold 0.4.** Below this, even a genre match plus partial energy can't be reached, so it reliably catches "nothing really fits." Trade-off: a fixed threshold is simple but not tuned per-profile.
- **Skip-and-log malformed rows instead of crashing.** A reproducible demo shouldn't die on one bad CSV line; the run continues and logs what it dropped. Trade-off: silent-ish data loss, mitigated by the warning log.
- **Kept the dual functional + OOP API** from the base project so existing tests still pass; the reliability layer was added *around* the core rather than rewriting it.

---

## Testing Summary

**10/10 automated tests pass** (`assets/run_tests.txt`). The suite covers confidence bounds/clamping, the low-confidence guardrail, the empty-catalog raise, malformed-row skipping, and the evaluation harness. The evaluation harness reports **5/5 labeled cases pass with average confidence 0.84**. What worked: exact-genre profiles produce high-confidence, correct top picks. What didn't / what I learned: the system has no partial-genre credit, so tastes between labels (e.g. `rock` vs `hard rock`) score no middle ground — the guardrail is what keeps those weak matches from being presented as confident answers.

---

## Reflection

The graded responsible-AI reflection (AI collaboration, biases, misuse, and reliability surprises) is in **[`model_card.md`](model_card.md)**.

What building this taught me: a recommendation is just *sort-by-a-number*, and the important engineering isn't the number — it's proving the number is trustworthy. Adding confidence + guardrails + an evaluation harness turned a prototype that "felt right" into a system that can *show* when it's right and flag when it isn't.
