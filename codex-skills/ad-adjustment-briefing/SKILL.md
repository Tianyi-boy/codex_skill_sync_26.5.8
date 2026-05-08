---
name: ad-adjustment-briefing
description: Generate daily advertising adjustment briefings strictly from Docker MySQL database records, including generated report evidence, submitted/imported adjustment records, audit-like persisted records, and recent ad performance data. Use when the user asks which platform/store/channel got or submitted adjustment reports, how many ads need adjustment or continued observation, how many were completed or rejected, or how recent ad adjustments performed.
---

# Advertising Adjustment Briefing

Use this skill to produce a factual daily briefing after advertising adjustment reports have been generated or submitted.

This skill is database-only. Do not use local adjustment report files, generated workbook files, temporary JSON exports, spreadsheet filenames, or filesystem timestamps as evidence for report acquisition, report submission, daily counts, or recent adjustment effects.

## Required Process

1. Use the requested date; if absent, use the current local date.
2. Query real database evidence only from the MySQL database running inside Docker containers.
3. Prefer the repository/API layer when it exposes the required records. If it does not, use a read-only SQL query against Docker MySQL through `docker exec` or the project's Docker Compose service.
4. Do not query host-local MySQL unless the user explicitly says the Docker database is exposed there and should be queried through the host port.
5. Do not infer that a store/channel got a report from local files. A store/channel counts as having got a report only when the database has persisted evidence for that store/channel/date.
6. Do not infer that a store/channel submitted a report unless a completed report was validated and imported or an equivalent successful submission record exists in the database.

## Docker Database Discovery

When the database connection is not already known:

1. Run `docker ps` and identify the MySQL container.
2. Inspect container environment variables such as `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `MYSQL_ROOT_PASSWORD`.
3. Query through the container, for example `docker exec <mysql-container> mysql -u<user> -p<password> <database> -e "<SQL>"`.
4. Use `--default-character-set=utf8mb4` when reading Chinese text.
5. Keep queries read-only.

For the current agent-platform schema, the expected Docker MySQL database is usually `agent_platform`, but always verify it from Docker/container metadata before querying.

## Data Tables

Include the relevant data tables and fields in the skill. This is intentional: the briefing depends on persisted evidence, and explicit table guidance prevents accidentally using local report files or the wrong MySQL instance.

Primary tables in the current schema:

- `ad_adjustment_import_batches`: evidence that a submitted adjustment report was validated/imported. Important fields: `batch_id`, `report_date`, `store`, `status`, `record_count`, `inserted_count`, `created_at`, `source_report_file`.
- `ad_adjustment_records`: imported adjustment rows and daily counts. Important fields: `report_date`, `store`, `recommended_action`, `adjustment_status`, `adjustment_time`, `campaign`, `ad_type`, `raw_report_row`, `created_at`, `updated_at`.
- `generated_files`: evidence that a report or generated artifact was persisted. Important fields: `filename`, `status`, `created_at`, `storage_path`, `content_type`, `request_id`, `conversation_id`.
- `ad_metrics`: ad performance data for recent effect evaluation. Important fields: `date`, `marketplace`, `store`, `campaign`, `ad_group`, `impressions`, `clicks`, `spend`, `sales`, `orders`, `ctr`, `cvr`, `acos`, `roas`.
- Audit-like or workflow tables such as `skill_runs`, `agent_runs`, `messages`, and `attachments` may be used only as supporting persisted evidence when they clearly identify the same report date, store, platform/channel, and successful workflow status.

If the schema evolves, discover fields from `information_schema.COLUMNS` and keep the same evidence rules. Do not silently substitute local files for missing database tables.

## Evidence Rules

For each platform + store + ad-channel row:

1. `今天获取调整报告`: yes only when the database contains a report-generation record, generated-file record, audit/workflow record, successful import batch, imported adjustment record, or equivalent persisted database record for that report date.
2. `今天提交调整报告`: yes only when a validated successful submission/import exists in the database for that report date. In the current schema, this normally means a successful `ad_adjustment_import_batches` row or imported rows in `ad_adjustment_records`.
3. A successful submission/import is also sufficient evidence that the store/channel got the report. Do not output `提交=是` and `获取=否` for the same store/channel/date.
4. Normalize known store aliases only when they appear in database values, such as `kaguyasu-US -> kagu` and `genji furniture-US -> genji`.
5. Determine ad channel from an explicit database column when available. In the current schema, if no dedicated `ad_channel` column exists, read it from persisted `raw_report_row` JSON or other persisted database evidence. Do not use the local workbook path as evidence.
6. Always emit all required platform/store/channel rows, including zero rows with no database evidence.

## Platform And Channel Rows

Always report at platform + store + ad-channel level.

- Amazon stores: `kagu`, `genji`, `senyu`, `zhongcheng`; channel `Amazon Ads`.
- Wayfair store: `linhe`; channel `Wayfair Ads`.
- Shopify stores: `anzhap`, `kagu`, `zima`; split into three rows per store: `Google Ads`, `Pinterest Ads`, and `Facebook Ads`.

Never merge Shopify channels into `Google / Pinterest / Facebook`.

## Daily Counts

For each row, include:

- `今天获取调整报告`: yes/no.
- `今天提交调整报告`: yes/no.
- `提交报告条数`: imported database row count for that store/channel/date.
- `需要调整`: rows whose `recommended_action` does not contain `持续观察`.
- `持续观察`: rows whose `recommended_action` contains `持续观察`.
- `已完成调整`: among `需要调整`, rows whose `adjustment_status` is `已调整`.
- `拒绝调整`: among `需要调整`, rows whose `adjustment_status` is `拒绝调整`.

Use zeroes and `否` for stores/channels with no database evidence that day.

## Recent Adjustment Effect

Evaluate recent performance only when there is post-adjustment ad performance data in the database.

1. Find database adjustments whose `adjustment_time` falls in the last 14 days.
2. Match adjusted ads to `ad_metrics` by the strongest available persisted identifiers, usually store + campaign and, when present, ad group or SKU.
3. Compare the pre-adjustment window with the post-adjustment window when both are available.
4. Prefer a 14-day pre window and a 7-day or 14-day post window, depending on available data.
5. Compare Spend, Sales, Orders, ACoS, CTR, CVR, CPA, and ROAS when the database source has those metrics. If CPA is not stored, compute it as Spend / Orders when Orders > 0.
6. Compute the latest available performance date only from database performance records.
7. If adjustment times are after the latest database ad data date, or `ad_metrics` is empty, state that the effect cannot yet be evaluated and give the exact missing data window.

Do not claim an adjustment worked or failed without post-adjustment database evidence.

## Required Briefing Shape

Produce:

1. A short title with the briefing date.
2. A table with columns: `平台`, `店铺`, `投放渠道`, `今天获取调整报告`, `今天提交调整报告`, `提交报告条数`, `需要调整`, `持续观察`, `已完成调整`, `拒绝调整`.
3. A one-paragraph total summary.
4. A recent adjustment-effect section.
5. A short口径说明 when helpful, naming the database/tables used and any missing evidence.

After generating the briefing, the final assistant answer must display the full briefing content directly in chat. Do not return only file paths, JSON paths, SQL snippets, or a summary. If artifacts are written, mention their paths only after the full briefing has been shown.

## Output Rules

- Keep the briefing concise and decision-ready.
- Separate facts from assumptions.
- Use exact dates when explaining missing data windows.
- Include platform/store/channel rows even when no database record exists, so the user can see coverage gaps.
- If a table exists but has no rows, say so plainly rather than treating it as missing.
- File paths are optional supporting details and must not replace the visible briefing.
