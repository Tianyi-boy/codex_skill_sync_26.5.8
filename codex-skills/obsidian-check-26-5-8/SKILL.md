---
name: obsidian-check-26-5-8
description: Audit and govern the managed Obsidian vault through Obsidian MCP against the current `20_规范` standards. Use when the user asks to check vault folder structure, file placement, index coverage, frontmatter, tags, links, templates, plugin governance, security boundaries, or to write an audit record for the Obsidian vault.
---

# Obsidian_检查_26.5.8

Use this skill to inspect the managed Obsidian vault, compare it with the current governance notes, apply safe single-note fixes when authorized, and persist an audit record.

## Operating Rules

- Treat Obsidian MCP as the canonical interface for note operations.
- Use vault-relative paths for targets. When a typed target is required, use `{ "type": "path", "path": "..." }`.
- If Obsidian MCP is unavailable, report the blocker and do not edit a filesystem mirror.
- Resolve Chinese note paths through Obsidian MCP. Do not trust garbled terminal rendering as the source of truth.
- Use audit and restructuring records as evidence only. Do not treat old records as current rules unless a current governance note points to them.

## Read Current Rules First

Before judging the vault, read the current governance notes:

- `00_知识库管理/20_规范/规范适用顺序.md`
- `00_知识库管理/10_结构治理/知识库结构说明.md`
- `00_知识库管理/20_规范/命名规范.md`
- `00_知识库管理/20_规范/标签规范.md`
- `00_知识库管理/20_规范/链接规范.md`
- `00_知识库管理/20_规范/Frontmatter规范.md`
- `00_知识库管理/20_规范/索引与MOC规范.md`
- `00_知识库管理/20_规范/模板规范.md`
- `00_知识库管理/20_规范/插件治理规范.md`
- `00_知识库管理/20_规范/安全与密钥记录规范.md`
- `00_知识库管理/20_规范/审计规范.md`
- `00_知识库管理/20_规范/开源社区Obsidian实操规范.md`

Use this precedence:

1. Structure and placement: `知识库结构说明.md`.
2. Topic-specific checks: the matching specialized rule note.
3. Uncovered cases: `开源社区Obsidian实操规范.md`.
4. Audit records: evidence, not current rules.
5. Restructuring records: history, not current rules.

## Inspection Workflow

1. Inventory the vault with `obsidian_list_notes`.
   - Start with `depth=2`.
   - Narrow important folders with `depth=3` to `depth=6`.
   - For a full Markdown inventory, use `depth=10` and `extension=md`.
2. Check each top-level area against `知识库结构说明.md`:
   - `00_知识库管理`
   - `10_前沿技术调研`
   - `20_技术池`
   - `30_服务体系`
   - `50_项目管理`
   - `60_每日计划`
   - `70_经验池`
   - `90_系统配置`
3. For each area, inspect:
   - Whether folder purpose and note placement match the structure note.
   - Whether an index or MOC exists where the standards require one.
   - Whether durable notes are linked from the relevant index.
   - Whether frontmatter contains `title`, `created`, `updated`, `status`, and `tags`.
   - Whether names, tags, links, templates, and plugin records follow the standards.
   - Whether security-sensitive material is stored only as approved references, not real secrets.
4. Read key indexes with `format=full` and `includeLinks=true`.
5. Use `document-map` before targeted section edits.

## Validation Queries

Use `obsidian_list_tags` to review tag taxonomy drift.

Use JSONLogic searches for missing frontmatter:

```json
{"!":[{"var":"frontmatter.title"}]}
{"!":[{"var":"frontmatter.created"}]}
{"!":[{"var":"frontmatter.updated"}]}
{"!":[{"var":"frontmatter.status"}]}
{"!":[{"var":"frontmatter.tags"}]}
```

Search for generic or outdated project links:

- `[[项目总览]]`
- `[[路线图]]`
- `[[决策记录]]`
- `[[风险与问题]]`
- `[[会议与推进记录]]`
- `[[服务目录]]`
- `架构研究/`
- Any moved path named by the user.

Search for possible secret leakage:

- `api key`
- `token=`
- `AppSecret`
- `secret`
- `cookie`
- `password=`
- `client_secret`
- `refresh_token`

Treat placeholder, normative, or desensitized examples as non-leaks after inspection. Escalate real credentials with a rotation recommendation, but do not copy the secret into Obsidian.

If Dataview fails with `Cannot read properties of undefined (reading 'tryQuery')`, use JSONLogic searches and MCP reads instead, then record the Dataview issue as a low-priority tooling gap.

## Safe Fix Boundaries

Allowed without extra confirmation:

- Create or update the requested audit record.
- Add the audit record link to the knowledge-management index.
- Patch obvious index links or structure-note code blocks when the requested task is governance maintenance.
- Patch single-note generic links when the user has requested fixes for that issue.
- Fix obvious frontmatter mistakes in newly created notes.

Require explicit user confirmation before:

- Batch moving files.
- Batch deleting files.
- Batch renaming files or directories.
- Batch replacing tags across the vault.
- Merging or overwriting historical audit records.
- Changing notes that may contain sensitive source material.

## Audit Record

When the user asks to audit or check the vault, write an audit note under:

`00_知识库管理/80_审计记录/`

Use a title like:

- `规范符合性检查-YYYY-MM-DD` for ad-hoc checks.
- `每日规范审计-YYYY-MM-DD` for daily audits.

Include these sections:

- `结论`
- `检查依据`
- `检查范围`
- `符合项`
- `发现问题`
- `已自动处理` or `未自动处理`
- `建议处理顺序`
- `验证记录`

After creating the audit record, link it from:

`00_知识库管理/知识库管理索引.md`

Use the `历史与检查文档` section unless the current index has a more specific matching section.

Verify important writes with:

- `obsidian_get_note` using `document-map`.
- A targeted section read or `content` read.
- A search for the audit title.

## Current Known Conventions

- `20_规范` is the standards center.
- `60_每日计划/工作任务` is the company-level rolling task area, not only a project task list.
- Date notes belong under `60_每日计划/YYYY/YYYY-MM`.
- The canonical plugin governance inventory is `90_系统配置/Obsidian/插件治理清单.md`.
- The secret index is `90_系统配置/密钥与Token/密钥索引.md`.
- Generic short links inside project notes should usually be replaced with path-qualified links plus aliases when duplicate note titles exist.
- Mixed or non-recommended tags should be reported before bulk replacement.

## Response Format

Report:

- Note paths created or changed.
- MCP checks used to verify the result.
- Skipped checks or blockers.
- Confirmation items still unresolved.

Lead with P0 or P1 issues if any. Keep the response concise and path-specific.
