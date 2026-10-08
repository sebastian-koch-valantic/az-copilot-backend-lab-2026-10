# .agents

Agent-neutral location for skills, read by GitHub Copilot in VS Code (and other agent tools).
Each skill is a folder `skills/<name>/SKILL.md`. Skills load on demand, the instructions in
`AGENTS.md` load on every request.

## Skills in this repo
- **grill-me**: interviews you about a ticket or plan in rounds. Adapted from https://github.com/mattpocock/skills (MIT, `skills/LICENSE-mattpocock-skills`). Used in Part 1 of the lab (ticket DWH-101).
- **test-driven-development**: no production code without a failing test first. From https://github.com/obra/superpowers (MIT, `skills/LICENSE-superpowers`). Used in Follow-up A (ticket DWH-103).
- **systematic-debugging**, **verification-before-completion**: from https://github.com/obra/superpowers (MIT). Optional.
- **ticket-to-spec**: not included. You write it in Part 2.

## Adding a skill
Create `.agents/skills/<name>/SKILL.md` with `name` (equal to the folder) and `description`
(says when to use it). Keep it short, one job per skill.
