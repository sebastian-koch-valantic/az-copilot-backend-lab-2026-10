---
name: grill-me
description: Interview the user relentlessly about a plan, ticket or design until nothing is silently assumed. Use when the user says "grill me" or wants to stress-test a plan before building.
disable-model-invocation: true
---

<!-- Adapted from github.com/mattpocock/skills (MIT). -->

Interview the user until you reach a shared understanding. Map the topic as a design tree:
every decision branches into the decisions that hang off it.

Work in rounds. The frontier is every decision whose prerequisites are already settled.
Ask the whole frontier in one round: number each question and give your recommended answer.
Then wait for the answers before the next round.

Format of a round:

Q1 - <question title>: <question, with options if useful>
Recommended: <your answer>

Rules:
- Facts are your job, not the user's. Look them up in the repo with your read and search tools
  instead of asking.
- Decisions are the user's. Put each to them and wait.
- Done when the frontier is empty: every branch visited, nothing silently assumed.
- Do not act on the result until the user confirms the shared understanding.
