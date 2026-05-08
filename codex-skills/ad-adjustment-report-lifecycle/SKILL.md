---
name: ad-adjustment-report-lifecycle
description: Generate advertising adjustment reports from rule documents and fresh ad data, then validate returned filled reports and import complete adjustment records into MySQL. Use when the user provides an ad rules document (.docx or .txt), an ad data spreadsheet (.xlsx), asks to create an adjustment report, or submits a filled adjustment report for completeness validation and database import. Supports Amazon-style Orders/Spend/CTR 30-day rules and generic ACoS 14-day rules. Enforce that source ad data is current through the report date or the immediately previous day before generating recommendations.
---

# Advertising Adjustment Report Lifecycle

Use this skill for the full adjustment-report lifecycle: generate the Excel report, stop for human completion, validate the returned report, and import records after validation passes when database configuration is available.

## Required Process

1. Confirm or infer the concrete inputs: platform, store, ad channel, rule document path, ad data workbook path, and report date.
2. Resolve relative report dates such as "today" using the current local date/timezone in the user or workspace context.
3. If the user explicitly says to assume or override the report date, use that date for Freshness Gate checks, file naming, and default adjustment time.
4. Save generated adjustment reports under `Z:\agent_data\广告\生成报告` by default. Keep only temporary exploration artifacts under `.codex-tmp/ad-adjustment-report/`.
5. Do not read project entry documents such as `AGENTS.md`, `PROJECT.md`, or `docs/*` during the normal report lifecycle unless the user explicitly asks for project integration or repository changes.

## Generate The Report

Prefer the bundled script:

```powershell
$env:PYTHONUTF8='1'
python "C:\Users\pc\.codex\skills\ad-adjustment-report-lifecycle\scripts\generate_ad_adjustment_report.py" `
  --rules "<rules.docx>" `
  --data "<ad-data.xlsx>" `
  --platform "<platform>" `
  --store "<store>" `
  --ad-channel "<ad channel>" `
  --report-date "<yyyy-mm-dd>"
```

The script defaults `--output-dir` to `Z:\agent_data\广告\生成报告`. Pass `--output-dir` only when the user explicitly requests a different destination.

Script behavior:

1. Parse `.docx` and `.txt` rule documents with structured libraries.
2. Accept rule lines such as `规则1：...` / `动作：...`, `Rule 1: ...` / `Action: ...`, and `1. ...` / `动作：...`.
3. Accept current Amazon-style source headers such as `店铺名称`, `国家`, `类型`, `广告组合`, `广告活动`, `有效状态`, `日期`, `曝光量`, `点击`, `花费-本币`, `广告销售额-本币`, and `广告订单`, plus canonical English headers.
4. Run the Freshness Gate before generating recommendations.
5. Infer the metric window from the rules: use 30 days for rules containing `30d` or `30天`; use 14 days for rules containing `14d` or `14天`; default to 14 days. Use `--window-days 14` or `--window-days 30` only when the user explicitly needs an override.
6. If source data is current through the day before the report date, use that latest source date as the metric window end date.
7. Ignore inactive ads whose status is paused, archived, disabled, or the Chinese equivalents.
8. For Amazon-style `Orders-30d` / `Spend-30d` / `CTR` rules, apply rules 1-14 from the document. Treat a parsed rule 15 cooldown/history rule as requiring external prior-adjustment history; do not invent history if no prior report or database records are available.
9. For generic 14-day ACoS rules, apply the bundled 1-9 ACoS decision tree.
10. Preserve the triggered rule as rule number plus complete condition and action text.
11. Include metric value columns used by the triggered rule. If an ACoS value is blank, include an ACoS blank-reason column.
12. Name the report as `<store>_<yyyy-mm-dd>_广告调整报告.xlsx`.
13. Print a JSON summary containing `report_date`, `data_period`, `latest_source_date`, `window_days`, `rule_engine`, `active_group_count`, `reported_row_count`, `action_counts`, and `output_path`.

## Freshness Gate

The generated report must not use stale decision data.

1. Inspect the ad workbook's date or period column and compute the latest parseable source data date.
2. The latest source data date must be either the report date or the day immediately before the report date.
3. If the latest source data date is older than `report_date - 1 day`, stop. Do not generate recommendations, do not backfill missing dates, and tell the user the report date, latest source data date, allowed latest dates, and that updated ad data is required.
4. If the workbook has no parseable source data date, stop and ask for a workbook with date or period fields.

## Excel Contract

Build the workbook with five visible sections:

1. `广告基本信息`: include platform, store, channel, report date, data period, and available source ad identity fields. Never include ad status. Include country only when it is part of the source identity.
2. `根据规则调整的动作`: include the final recommended action.
3. `触发的规则`: include one field named `触发规则`.
4. `触发规则中指标的数值`: include relevant metric values and blank-reason columns.
5. `调整记录`: include `是否调整`, `调整方式`, `拒绝调整原因`, and `调整时间`.

Format requirements:

- Merge the first-row group headers for all five sections.
- Add borders to every used cell.
- Freeze the header rows, wrap text, and keep columns readable.
- Add a dropdown on `是否调整` with exactly `已调整` and `拒绝调整`.
- Default `调整时间` to the report date.

## Stop For Human Completion

After generating the report, stop and return the workbook path to the user. Do not import anything yet. The user must manually fill the `调整记录` section and return the completed workbook.

## Validate Returned Report

When the user returns a filled report, validate it first if the user asks only for validation. If the user asks to continue the lifecycle or import after validation, run the import script below because it validates before writing:

```powershell
$env:PYTHONUTF8='1'
python "C:\Users\pc\.codex\skills\ad-adjustment-report-lifecycle\scripts\validate_completed_report.py" `
  --report "<completed-report.xlsx>"
```

If validation fails, list the exact row numbers and fields, then ask the user to refill. Do not import partial or incomplete reports.

Required checks:

- `是否调整` must be `已调整` or `拒绝调整`.
- `调整方式` is required when `是否调整` is `已调整`.
- `拒绝调整原因` is required when `是否调整` is `拒绝调整`.
- `调整时间` is required and must be parseable as a date.
- Required identity fields, recommended action, triggered rule, and metric evidence must still be present.

## Import Records

Import is mandatory after validation passes when the user submitted a completed report for lifecycle continuation. The import target is the Docker-deployed MySQL service by default:

- Docker container: `agent-platform-mysql`
- Database: `agent_platform`
- User: `agent_app`
- Password: `change_me`
- Batch table: `ad_adjustment_import_batches`
- Record table: `ad_adjustment_records`

Use the bundled import script. It validates the report before opening a database transaction, writes an import batch, inserts one record per report row, and skips duplicate records by stable `record_id`.

```powershell
$env:PYTHONUTF8='1'
python "C:\Users\pc\.codex\skills\ad-adjustment-report-lifecycle\scripts\import_completed_report.py" `
  --report "<completed-report.xlsx>"
```

For a connection and parsing check without writing:

```powershell
$env:PYTHONUTF8='1'
python "C:\Users\pc\.codex\skills\ad-adjustment-report-lifecycle\scripts\import_completed_report.py" `
  --report "<completed-report.xlsx>" `
  --dry-run
```

Skip import only when validation fails, the Docker MySQL container is unavailable, the user explicitly says to validate only, or required credentials are changed and unavailable.

1. Use `docker exec -i agent-platform-mysql mysql ... agent_platform`; do not use a host MySQL instance for this lifecycle.
2. Keep the import transactional. If a database write fails, do not report partial success.
3. Preserve request, conversation, task, agent, skill, source report file, report date, store, row count, inserted count, skipped count, status, errors, and timestamps in the batch table.
4. Make the import idempotent for the same report rows and ad identity; skip duplicates instead of inserting them twice.
5. Return a structured summary with inserted count, skipped count, validation status, batch id, and any follow-up needs.

## Failure Rules

- If source ad data is not current through the report date or the immediately previous day, stop and require updated data before generating recommendations.
- If rule parsing fails, stop and report the missing or unparsed rule numbers. Do not silently invent default rules.
- If a rule requires prior adjustment history and no history source is available, state that cooldown suppression could not be applied.
- If the filled report is incomplete, say it is incomplete and require refilling before import.
- If MySQL is unavailable, report the connection failure and do not fake persistence.
- If source data ends before the adjustment time, do not claim adjustment effectiveness.
