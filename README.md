# Feishu Work Records

[English](README.md) | [简体中文](README.zh-CN.md)

A Codex skill that turns task conversations into concise, table-first work records in Feishu **My Document Library** (`my_library`). Create the record once, then maintain the same document as the task progresses.

**Skill ID:** `work-record-to-feishu`

**Display name:** Feishu Work Records

Instructions and default record content are Chinese. The skill name and identifier are English.

## Behavior

| Area | Rule |
| --- | --- |
| Readability | Prefer native tables for each module, one item per row, short factual cells. Do not move whole paragraphs into cells. |
| Opening | Start the first module immediately after the document title. Omit creation-time, conversation-source, and scope preambles. |
| Current state | Put facts such as not developed, not deployed, unverified, or blocked in the relevant status row. Do not add future plans or a follow-up/to-do chapter. |
| Revision history | Keep important changes and valid historical evidence. The result column describes the current outcome, not future actions. |
| First use | Create `TaskSummary_YYYYMMDD` in My Document Library. The summary is at most 15 characters; the creation date uses `Asia/Shanghai`. |
| Later use | Locate and read the same task's existing record, update affected rows and actual revisions, and preserve its original title and date. |
| Skill development | Include each developed skill's complete current `SKILL.md`, including YAML frontmatter, in body code blocks and compare read-back text against saved snapshots. |

A short necessary explanation, image, or full source block can retain its natural format. Record only supported facts, distinguishing local tests, delivery, deployment, and acceptance.

## Requirements

- Codex with local skill loading and shell access.
- A separately installed, authenticated `lark-cli` with appropriate document permissions.
- Matching `lark-doc`, `lark-wiki`, and `lark-shared` skills; `lark-drive` is needed when an unbound existing record must be searched for. These dependencies are not bundled.
- CLI support for `docs +script`, `docs +create --parent-position my_library`, `docs +update`, `docs +fetch`, and `wiki +node-get`.
- Python 3.9+ for the bundled offline checker and regression tests (standard library only).

```bash
lark-cli docs +create --help
lark-cli docs +update --help
lark-cli docs +script --help
lark-cli wiki +node-get --help
```

Document operations use `--as user`. Configure authentication, scopes, and resource permissions for your own Feishu account. No credentials are included.

## Installation

Clone outside your skills directory, then link to the configured Codex skills directory. This example assumes the default path and no existing installation with this ID:

```bash
git clone https://github.com/zero-one-2024/work-record-to-feishu.git
mkdir -p ~/.codex/skills
ln -s "$(pwd)/work-record-to-feishu" ~/.codex/skills/work-record-to-feishu
```

If the target already exists, inspect and update your existing installation deliberately. Use your configured skill path if it differs from the example.

## Usage

In the task conversation:

```text
$work-record-to-feishu 编写工作记录
```

When the same task has new work:

```text
使用 $work-record-to-feishu 更新当前任务的工作记录。
```

The agent uses an explicitly provided record URL, a confirmed link in the current task conversation, or the task's saved binding. It reads the actual document before updating. Title equality alone does not establish identity. An inaccessible bound record must not be replaced by a new one; ambiguous candidates require clarification. If there is no binding and existence is uncertain, search and inspect candidates before deciding to create.

Confirmed first-time use creates the document and saves its URL, ID, original title/date, task identity, and last observed revision in the task workspace. With no new facts, return the existing link without duplicate rows. An explicit request for a separate snapshot creates another document while preserving the original task binding unless the user requests a switch. Asking only for a plan or local draft does not authorize cloud writes.

Updates preserve history, manual content, attachments, and references. When maintaining the task's older-format record, move relevant unfinished facts and unique evidence into the appropriate status tables before removing redundant opening text and future-action lists. Do not bulk-reformat unrelated old documents.

## Document format

Include only useful sections, with continuous native heading numbering:

```text
1 Task overview (optional field table)
2 Work performed
2.1 Actual modules (tables preferred)
3 Revision history (when actual revisions exist)
3.1 Revision details
4 Deliverables
4.1 Artifacts and validation (table)
5 Skill source (skill-development tasks only)
5.1 Skill ID / SKILL.md
```

Typical work tables use **Item / Work performed / Current outcome / Evidence**. Deliverables use **Artifact / Version or access / Validation**. Use the fewest suitable columns rather than forcing every module into the revision table.

| Version / round | Date | Triggering issue or requirement | Main changes | Validation | Current outcome | Evidence / attachments |
| --- | --- | --- | --- | --- | --- | --- |

Use actual versions and event dates. Keep past failures accurate when later results improve. Omit empty sections. The document ends after deliverables or full skill source, without a future-work chapter.

See [record format](references/record-format.md) and [document maintenance](references/document-maintenance.md) for the complete rules.

## Writing and verification

Use the installed `lark-doc` authoring workflow for creation and its observe/patch/read-back workflow for updates. A complete candidate is for validation, not permission to overwrite the whole cloud document. Use current block IDs and revisions for local patches; re-read concurrent changes before continuing.

The creation step targets the personal library:

```bash
lark-cli docs +create \
  --doc-format xml \
  --content '@./draft.xml' \
  --parent-position my_library \
  --as user \
  --format json
```

This command does not replace draft preparation and CLI checks. A timeout or partial result requires reading the existing target before retrying; do not create duplicates or append the same change twice.

Validate the complete candidate XML locally:

```bash
python3 scripts/validate_record.py /path/to/candidate.xml
```

For an update, pass the title actually read from the existing record. This checks that its name and original creation date are preserved, including legacy titles:

```bash
python3 scripts/validate_record.py /path/to/candidate.xml \
  --original-title 'OriginalTitle_20261103'
```

For skill-development records, use a saved source snapshot:

```bash
python3 scripts/validate_record.py /path/to/candidate.xml \
  --skill-source 'sample-skill=/path/to/SKILL-snapshot.md'
```

Use `caption="sample-skill/SKILL.md"` for source code blocks, repeating that caption for ordered split blocks. Repeat `--skill-source` for multiple skills. The checker verifies title/date shape, no preamble or follow-up headings, heading structure, simple table widths, and exact supplied source text. It requires a complete candidate, not an update fragment.

The checker does not judge factual accuracy, concision, target identity, preservation of user content, or successful cloud writes. Review these and read back the actual result. Source links and ZIP attachments do not replace the full source in the document body. Keep drafts, bindings, responses, and snapshots outside this repository.

## Tests and validation scope

```bash
python3 -m unittest discover -s tests -v
```

Offline tests cover structural rejection, original-title preservation, XML/source round-trips, split/multiple sources, missing or altered source, and CLI failure reporting. [Maintenance scenarios](tests/maintenance-scenarios.md) describe task-level cases for review; they are not proof of online behavior.

Historical checks on 2026-11-03 verified actual creation, library membership, native headings and revision table read-back, attachment upload/download with SHA-256 comparison, and complete source insertion/read-back. The 2026-11-13 revision adds table-first content rules, same-task maintenance, and offline validation. The new maintenance workflow has not been exercised against a live document as part of this update.

## Files

```text
work-record-to-feishu/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── record-format.md
│   └── document-maintenance.md
├── scripts/validate_record.py
├── tests/
│   ├── test_validate_record.py
│   └── maintenance-scenarios.md
├── README.md
├── README.zh-CN.md
└── .gitignore
```

This is an instruction-based skill with an offline checker, not a standalone Feishu application. No task transcripts, cloud responses, or credentials are distributed.
