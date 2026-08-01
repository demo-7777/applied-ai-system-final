# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Stretch: Agentic Workflow Enhancement

I added an **agentic self-critique loop** ([`src/agent.py`](src/agent.py)) on top of the core recommender. It is a deterministic **plan → critique → act → re-check** decision chain: it produces a baseline recommendation, inspects its own output against reliability rules (weak-confidence picks and low artist diversity), revises the list to fix them, and loops until the list is clean or the revision stops changing (convergence).

**Committed reasoning traces:** [`assets/agent_trace.md`](assets/agent_trace.md) — the full multi-step trace for two profiles, regenerated with `python -m src.agent`.

**Before → after (Chill Lofi profile):** the baseline top-5 included *Catch the Rainbow*, a rock ballad that ranked only because its energy (0.35) matched the target — an "energy leak" across genres, flagged at confidence 0.25. The agent's CRITIQUE step caught it, and the ACT step dropped it, yielding a list where every pick clears the confidence floor.

**One flawed AI moment during this feature:** the first version of the loop kept re-flagging an unresolvable diversity issue (a strong-genre artist that legitimately survives the diversity penalty), churning identically until it hit `max_iters`. I added **convergence detection** — if an ACT step changes nothing, the remaining issues are best-effort and the loop stops — which fixed the wasted iterations.

---

## Agentic Workflow (SF8)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**Prompts used:**

<!-- Paste the key prompts you gave the agent -->

**What did the agent generate or change?**

<!-- List the files edited, code generated, or commands run -->

**What did you verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Design Pattern (SF10)

> Document how AI helped you choose or implement a design pattern.

**Which design pattern did you use?**

<!-- e.g., Strategy, Factory, Observer, etc. -->

**How did AI help you brainstorm or implement it?**

<!-- Describe the conversation or suggestions that led to your decision -->

**How does the pattern appear in your final code?**

<!-- Point to the relevant class or method -->
