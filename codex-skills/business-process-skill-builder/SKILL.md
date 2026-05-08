---
name: business-process-skill-builder
description: Turn an internal business need into a verified Codex skill. Use when Codex must clarify a business requirement, run the workflow on real or sample inputs, verify outputs and failure cases, then freeze the repeatable process as a SKILL.md with scripts, references, assets, and validation checks. Trigger for requests to convert a business workflow, current project, operational playbook, data process, reporting process, or repeated team procedure into a reusable Codex skill after validation.
---

# Business Process Skill Builder

## Core Rule

Do not write the final skill first. First make the business workflow executable, run it at least once, verify the result, then convert only the stable parts into the skill.

Keep each skill narrow enough that another Codex instance can use it without rediscovering the business process.

## Workflow

1. Define the business boundary.
   - Identify the business user, goal, input files or systems, output artifact, and decision owner.
   - Capture the smallest successful example, using real data when available and safe.
   - Record non-goals so the first skill does not become an oversized platform plan.

2. Run the process manually or with existing scripts.
   - Prefer existing project scripts and database schemas over new abstractions.
   - If files are involved, inspect headers, sheet names, encodings, required columns, and sample rows before processing.
   - If the process touches production systems, require an explicit dry-run or staging path unless the user has clearly asked for live changes.

3. Verify the workflow.
   - Check that the output matches the business objective, not only that commands exit successfully.
   - Validate required inputs, row counts, date ranges, duplicate handling, and idempotency where relevant.
   - Save concise evidence: command output, generated file path, row counts, screenshots, or before/after examples.

4. Choose the skill shape.
   - Put stable step-by-step instructions in `SKILL.md`.
   - Put deterministic operations in `scripts/`.
   - Put schemas, field mappings, examples, and longer business rules in `references/`.
   - Put reusable templates or boilerplate files in `assets/`.

5. Write the skill.
   - Use a precise `description` that includes both capability and trigger scenarios.
   - Keep `SKILL.md` short and procedural.
   - Link only the reference files that Codex should load when that specific detail is needed.
   - Include a validation section that tells Codex how to prove the skill worked.

6. Validate and iterate.
   - Run the structural validator:
     `python C:\Users\pc\.codex\skills\.system\skill-creator\scripts\quick_validate.py <skill-folder>`
   - Run any bundled scripts on a sample or real dry-run input.
   - Use `scripts\validate_business_skill.py <skill-folder>` from this skill for project-level completeness checks.
   - If a test exposes ambiguity, update the skill or references before treating it as finalized.

## Business Intake

When the requirement is vague, gather only the facts needed to run one representative case:

- Trigger phrase users will type.
- Input source: file path, database, API, web page, or manual pasted text.
- Output: report, database import, spreadsheet, document, UI change, or operational action.
- Freshness rule: required date range or latest acceptable data date.
- Validation rule: what must be true for the business user to accept the result.
- Exception handling: missing data, rejected records, partial completion, and rollback expectations.

For a reusable intake checklist, read `references/business-intake.md`.

## Skill Freezing Checklist

A business skill is ready to use when all items are true:

- `SKILL.md` has valid frontmatter with `name` and `description`.
- The description contains concrete trigger contexts, not only a generic summary.
- The workflow has been run once on realistic input.
- Verification evidence exists in the conversation, logs, generated output, or a referenced artifact.
- Required input fields and freshness rules are documented.
- Failure handling is documented for the most likely bad input.
- Scripts, if present, have been run successfully after being added.
- `quick_validate.py` passes.

## Output Standard

When finishing a business-skill conversion, report:

- Skill folder path.
- What workflow was verified.
- What validation commands passed.
- Any remaining operational risk or user decision still outside the skill.
