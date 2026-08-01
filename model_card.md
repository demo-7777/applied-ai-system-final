# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeMatch 1.0**

---

## 2. Intended Use  

VibeMatch takes a short "taste profile" (a favorite genre, a favorite mood, and a target energy level) and suggests the songs from its catalog that best fit that taste, each with a plain-English reason. It assumes the user can describe their taste with those three simple fields and that a single profile represents what they want right now. This is a **classroom learning tool** for exploring how content-based recommenders work — it is not built for real listeners or production use.

---

## 3. How the Model Works  

Think of it like a judge giving each song points. Every song has a genre, a mood, and an energy level (how calm or intense it feels). The user says what they like. A song earns 2 points if its genre matches, 1 point if its mood matches, and up to 1 more point for how close its energy is to what the user wants — the closer, the more points. Every song gets a total score, and the songs are lined up from highest score to lowest so the best matches sit on top. Compared to the starter code, which just returned the first few songs unchanged, I added the real point system, made it explain each score in words, and made it actually sort by score.

---

## 4. Data  

The catalog has **20 songs**. Ten came with the project (pop, lofi, rock, ambient, jazz, synthwave, indie pop) and I added ten additional tracks (rock and roll, soul, rock, metal, art rock, and hard rock). Moods range across happy, chill, intense, relaxed, moody, romantic, dreamy, and more. Each song also carries tempo, valence, danceability, and acousticness, though the current scoring only uses genre, mood, and energy. The dataset is tiny and skews toward rock, so whole areas of music (classical, hip hop, country, world music, and most non-English music) are missing, which limits how varied the recommendations can be.

---

## 5. Strengths  

The system works well for users whose taste lines up clearly with one of the well-represented genres — a rock fan or a lofi fan gets a top list that genuinely feels right, led by an exact genre-and-mood match. It correctly captures the idea that a matching genre matters most, a matching mood adds a little, and energy fine-tunes the order, so songs that hit all three (like Library Rain for the chill lofi profile, a perfect 4.0) rise to the very top. In every test the #1 pick matched my own intuition for that profile, which is a good sign the core logic is sound.

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

**What I found:** The scoring always awards energy points to *every* song, so a track with the wrong genre and wrong mood can still climb the list on energy alone. In the Chill Lofi test, *Catch the Rainbow* — a rock ballad — landed in the top 5 purely because its energy (0.35) exactly matched the target, despite having nothing to do with lofi. The catalog is also rock-heavy (5 of 20 songs are rock, hard rock, or metal) while genres like pop and jazz have only one or two entries, so genre-weighted profiles for the larger genres fill their whole top list with matches while smaller-genre fans run out of real matches quickly. Because the system only rewards *exact* genre and mood matches, closely related tastes (for example `rock` vs `hard rock`) get no partial credit, which unfairly penalizes users whose taste sits between the labels. Together these create a mild filter bubble that favors well-represented genres and lets raw energy leak across genre boundaries.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

**Profiles tested:** three distinct tastes — High-Energy Pop (pop / happy / 0.8), Deep Intense Rock (hard rock / intense / 0.85), and Chill Lofi (lofi / chill / 0.35). For each, I looked at whether the top 5 matched what a real fan of that style would actually want.

**What surprised me:** the biggest surprise was a rock ballad, *Catch the Rainbow*, showing up in the Chill Lofi list. It got there on energy alone, which taught me that a feature everyone always scores on (energy) can quietly pull in songs that don't fit the vibe at all.

**Profile comparisons (plain language):**

- **High-Energy Pop vs. Deep Intense Rock:** The pop profile floats bright, upbeat songs (Sunrise City, Gym Hero) to the top, while the rock profile pulls up loud, hard-hitting tracks (Civil War, Dirty Deeds, Ball Breaker). This makes sense — the two profiles ask for opposite moods (happy vs. intense) and different genres, so almost none of their top songs overlap.
- **Deep Intense Rock vs. Chill Lofi:** These are near opposites in energy (0.85 vs. 0.35). The rock list is full of fast, high-energy songs; the lofi list is full of slow, calm ones (Library Rain, Midnight Coding). The energy gap alone flips the whole ranking, which is exactly what you'd expect when one person wants a workout and the other wants to study.
- **High-Energy Pop vs. Chill Lofi:** Both can feel "pleasant," but pop wants high energy and happy mood while lofi wants low energy and chill mood. The pop list leans danceable and loud; the lofi list leans quiet and mellow. The only thing they share is that energy nudges a few unrelated songs onto both lists.

To put it simply: the reason "Gym Hero" keeps showing up for the Happy Pop fan is that it matches their exact genre *and* sits near their energy target — the system is rewarding the two things that person actually asked for, not judging the song's quality.

### Stress Test Output

Three diverse profiles were run against the 20-song catalog (top 5 each):

```
=== High-Energy Pop: {'genre': 'pop', 'mood': 'happy', 'energy': 0.8} ===
Sunrise City                 - 3.98  genre match: pop (+2.0); mood match: happy (+1.0); energy close to 0.8 (+0.98)
Gym Hero                     - 2.87  genre match: pop (+2.0); energy close to 0.8 (+0.87)
Rooftop Lights               - 1.96  mood match: happy (+1.0); energy close to 0.8 (+0.96)
Go Johnny Go                 - 1.95  mood match: happy (+1.0); energy close to 0.8 (+0.95)
Love Train                   - 1.90  mood match: happy (+1.0); energy close to 0.8 (+0.90)

=== Deep Intense Rock: {'genre': 'hard rock', 'mood': 'intense', 'energy': 0.85} ===
Civil War                    - 3.90  genre match: hard rock (+2.0); mood match: intense (+1.0); energy close to 0.85 (+0.90)
Dirty Deeds Done Dirt Cheap  - 3.00  genre match: hard rock (+2.0); energy close to 0.85 (+1.00)
Ball Breaker                 - 2.97  genre match: hard rock (+2.0); energy close to 0.85 (+0.97)
Rainbow in the Dark          - 1.95  mood match: intense (+1.0); energy close to 0.85 (+0.95)
Storm Runner                 - 1.94  mood match: intense (+1.0); energy close to 0.85 (+0.94)

=== Chill Lofi: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.35} ===
Library Rain                 - 4.00  genre match: lofi (+2.0); mood match: chill (+1.0); energy close to 0.35 (+1.00)
Midnight Coding              - 3.93  genre match: lofi (+2.0); mood match: chill (+1.0); energy close to 0.35 (+0.93)
Focus Flow                   - 2.95  genre match: lofi (+2.0); energy close to 0.35 (+0.95)
Spacewalk Thoughts           - 1.93  mood match: chill (+1.0); energy close to 0.35 (+0.93)
Catch the Rainbow            - 1.00  energy close to 0.35 (+1.00)
```

---

## 8. Future Work  

Ideas for how you would improve the model next:

- **Partial genre/mood credit.** Give some points for related tastes (e.g. `rock` vs `hard rock`) instead of only exact matches, so users whose taste sits between labels aren't penalized.
- **Use the unused features.** Fold tempo, valence, danceability, and acousticness into the score (respecting the profile's `likes_acoustic` flag) for finer matches.
- **A diversity rule.** Add a small penalty when the same artist or genre already appears in the top list, so results aren't dominated by one cluster (the rock-heavy filter-bubble effect).
- **A bigger, more balanced catalog.** Add songs across the genres currently missing (classical, hip hop, country, world music) so every profile has real matches to draw from.

---

## 9. Personal Reflection  

My biggest learning moment was realizing that a "recommendation" is really just sorting a list by a number I chose how to calculate. Once I saw that the whole system was a scoring rule plus a sort, recommenders stopped feeling like magic. AI helped most when I was expanding the dataset and shaping the scoring logic quickly, but I had to double-check it constantly — for example, when song data came in with genre and mood fields as messy semicolon lists, they would have broken the exact-match scoring, so I cleaned them to single values.

What surprised me was how convincing the results feel even with only three features. Giving genre the most weight, mood a little, and energy as a tiebreaker was enough to make the top picks "feel right" for each profile — but it also surprised me how a low-energy rock ballad could sneak into a chill lofi list purely on energy, which showed me how easily a simple rule can produce a hidden bias. This changed how I think about real apps like Spotify: their suggestions are not mysterious taste-readers, just much larger versions of the same idea, and the same risks of filter bubbles and over-favored genres exist at that scale. If I extended this, I would add partial credit for related genres, use the features I left unused, and add a diversity rule so one genre can't dominate the list.

---

# Responsible AI Reflection (Final Project)

*These sections answer the required Step 5 reflection prompts for the Applied AI System project. They build on the reliability/testing feature added in this version (confidence scoring, guardrails, and the `src/evaluate.py` harness).*

## What are the limitations or biases in your system?

The core bias is a **catalog / weighting filter bubble**: genre carries the most weight (+2.0) and the 20-song catalog is rock-heavy (rock / hard rock / metal), so rock-leaning profiles fill their whole top list with matches while thinly-represented genres run out of real matches fast. The scoring only rewards **exact** genre and mood matches, so related tastes (`rock` vs `hard rock`) get zero partial credit, unfairly penalizing users whose taste sits between labels. Energy points are awarded to *every* song, so a wrong-genre track can still climb on energy alone. The new **confidence score is a heuristic, not a calibrated probability** — it reliably *ranks* trust but should not be quoted as a real likelihood. The system also understands nothing about lyrics, language, or artist, and whole genres (classical, hip hop, country, most non-English music) are absent.

## Could your AI be misused, and how would you prevent that?

Two realistic misuses. First, the **confidence number could be presented as objective certainty** ("0.99 = the perfect song for you") to nudge users or justify decisions the data can't support. Prevention: the confidence is documented here and in the README as a bounded heuristic, and the low-confidence **guardrail** actively flags weak matches rather than hiding them. Second, a rigged or imbalanced catalog could be used to **manipulate what surfaces** (e.g. stacking one label/artist to dominate every list) — a real risk in commercial recommenders. Prevention: the evaluation harness makes catalog skew visible and measurable, and future work adds a diversity penalty so one cluster can't monopolize results. Because the system is a transparent, explainable scoring rule (every pick shows its reasons), manipulation is auditable rather than black-box.

## What surprised you while testing your AI's reliability?

The biggest surprise was that the **adversarial case was the most useful test**. Feeding an out-of-catalog genre (`polka`) produced a normal-looking top pick — the system *always* returns something — but the confidence dropped to ~0.23 and the guardrail fired. This showed me that a recommender's real failure mode isn't crashing; it's **confidently returning a plausible-but-wrong answer**. Adding a confidence floor changed a silent failure into a visible, logged warning. I was also surprised how cleanly a fixed `score / 4.0` normalization separated strong matches (0.98–1.00) from weak ones (~0.2), which made the 0.4 threshold an obvious dividing line without any tuning.

## Describe your collaboration with AI during this project.

I used an AI assistant to help extend the base recommender into this reliability system. **Helpful suggestion:** it proposed normalizing the raw score against the fixed maximum (4.0) to derive confidence, and reusing that same value both for the low-confidence guardrail *and* as the pass criterion for the adversarial evaluation case — one consistent signal wired through the whole system instead of three ad-hoc thresholds. **Flawed suggestion:** an early evaluation case labeled a profile with the expected genre `"acoustic"`, but no song in the catalog actually has that genre, so the test could *never* pass — it looked like a recommender bug when it was really a bad test label. I caught it by checking the catalog's real genres and replaced the case with `jazz` (which exists), which fixed the harness to 5/5. The lesson: AI is fast at scaffolding logic but will confidently invent data/labels that don't exist, so every generated test needs to be checked against the real inputs.
