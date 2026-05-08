# Business Intake Reference

Use this reference when a user asks to turn an unclear business process into a Codex skill.

## Minimum Viable Case

Capture one concrete example before designing the skill:

| Item | Question |
| --- | --- |
| Business owner | Who accepts the result? |
| Goal | What decision or action should the workflow support? |
| Input | Which file, table, API, or pasted text starts the process? |
| Output | What exact artifact or system change should be produced? |
| Frequency | One-time, daily, weekly, monthly, or event-driven? |
| Freshness | What is the latest required data date? |
| Acceptance | How does the user know the output is correct? |
| Failure mode | What should happen when data is missing or inconsistent? |

## Validation Evidence

Prefer evidence that another Codex instance can inspect:

- Command output with row counts or generated paths.
- A small anonymized sample input and expected output.
- Database record counts before and after import.
- Rendered document, spreadsheet, or screenshot for visual artifacts.
- A rejection list for records that could not be processed.

## Skill Scope Decision

Create one skill when the process has one stable input-output loop.

Split into multiple skills when:

- The same data feeds unrelated business decisions.
- One part creates records and another part audits or summarizes them.
- Different teams own different acceptance rules.
- Live operations require different approval or rollback expectations.

## Reference Placement

Use `SKILL.md` for the shortest reliable execution path.

Use `references/` for:

- Field mappings.
- Database schemas.
- Business rules.
- Examples.
- Troubleshooting tables.

Use `scripts/` for deterministic transformations, imports, exports, and validators.
