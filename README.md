# Feishu Work Records

[English](README.md) | [简体中文](README.zh-CN.md)

A Codex skill that turns the current task conversation into a structured work record and creates a Feishu cloud document in **My Document Library** (`my_library`).

**Skill ID:** `work-record-to-feishu`

**Display name:** Feishu Work Records

The skill supports development, design, research, documentation, and testing tasks. Its instructions and default document content are written in Chinese; its name and identifier are English.

## What it does

- Summarizes the task's requirements, completed work, key decisions, deliverables, validation results, and remaining work.
- Names each document `TaskSummary_YYYYMMDD`, with a summary of at most 15 characters and a creation date in `Asia/Shanghai`.
- Uses native headings with continuous numbering such as `1`, `1.1`, `2`, and `2.1`.
- Records version or revision history in a native seven-column table.
- For skill-development tasks, includes the developed skill's complete current `SKILL.md` in the document body, including YAML frontmatter, and compares the read-back text with the saved source snapshot.
- Creates each record in the authenticated user's personal document library and verifies its location after creation.
- Creates a new document on each invocation. It does not automatically update an earlier work record.

## Requirements

- A Codex environment that can load local skills and run shell commands.
- A separately installed and authenticated `lark-cli` with permission to create, read, and, when needed, repair documents in your Feishu personal document library.
- The matching `lark-doc`, `lark-wiki`, and `lark-shared` skills provided by your CLI setup. This repository does not bundle those skills or the CLI.
- A CLI version supporting `docs +script`, `docs +create --parent-position my_library`, `docs +fetch`, and `wiki +node-get`.
- Python 3.9+ if using the documented `zoneinfo` date example or local snapshot/checksum helpers.

Check the capabilities of your installed CLI before using the skill:

```bash
lark-cli docs +create --help
lark-cli docs +script --help
lark-cli wiki +node-get --help
```

Document operations use `--as user`. Authentication, resource permissions, and scope configuration remain specific to your Feishu account; no credentials are included in this repository.

## Installation

Clone the repository outside your skills directory, then link it into your configured Codex skills directory. The example below assumes the default `~/.codex/skills` path and that no skill with this ID is already installed:

```bash
git clone https://github.com/zero-one-2024/work-record-to-feishu.git
mkdir -p ~/.codex/skills
ln -s "$(pwd)/work-record-to-feishu" ~/.codex/skills/work-record-to-feishu
```

If the installation path already exists, inspect it first and update your existing checkout or installation deliberately. Do not replace an existing installation blindly. If your Codex environment uses a different skills directory, use that configured location instead.

## Usage

In the conversation for the task you want to document, invoke:

```text
$work-record-to-feishu 编写工作记录
```

For example:

```text
使用 $work-record-to-feishu 整理当前任务的开发过程，保存到飞书我的文档库。
```

The agent gathers the current conversation's supported facts, prepares and checks an XML draft, creates the document, reads it back, and returns its Feishu link. Asking only for a plan or local draft does not authorize document creation.

For skill-development records, the source included is the skill actually developed or modified in that task, rather than unrelated helper skills used to write the record. Multiple delivered skills receive separate source sections.

## Document format

The default outline adapts to the work actually performed. Empty sections are omitted.

```text
1 Task overview
1.1 Background
1.2 Objectives and requirements

2 Work performed
2.1 Completed work
2.2 Key decisions

3 Revision history
3.1 Revision details

4 Deliverables
4.1 Artifacts and access
4.2 Validation and current status

5 Follow-up work
5.1 Open items

6 Skill source (skill-development tasks only)
6.1 SKILL.md
```

Revision-history columns:

| Version / round | Date | Triggering issue or requirement | Main changes | Validation | Outcome and follow-up | Evidence / attachments |
| --- | --- | --- | --- | --- | --- | --- |

The skill preserves actual version identifiers and event dates. It uses descriptive rounds when no version was assigned, and explicitly identifies missing evidence. Building an artifact, passing local tests, deployment, and acceptance are recorded as separate states.

For the complete Chinese formatting specification, see [record-format.md](references/record-format.md).

## Creation and verification

The document creation step uses the CLI authoring workflow and this destination:

```bash
lark-cli docs +create \
  --doc-format xml \
  --content '@./draft.xml' \
  --parent-position my_library \
  --as user \
  --format json
```

This is the creation step within the workflow, not a standalone replacement for draft preparation and checks. Follow the installed `lark-doc` instructions for the current CLI version.

After creation, the agent checks the title, heading numbers, table structure, relevant attachments, and personal-library membership. For skill source sections, it restores XML-escaped text and line breaks and compares the content against the saved snapshot. A ZIP attachment or source link does not replace the full source in the document body.

If an attachment fails after document creation, the agent repairs only the document created by that invocation. If a creation request times out with an unknown result, it checks the known response and document state before attempting another creation.

## Validation status

Verified during development on 2026-11-03:

- Skill metadata and local reference checks.
- Local XML draft parsing and creation-command dry run.
- Actual document creation in My Document Library and membership verification.
- Read-back of five first-level headings, nine second-level headings, and a seven-column table with five revision rows.
- ZIP attachment upload, download, and SHA-256 comparison.
- Full `SKILL.md` source insertion and exact read-back comparison.

The source-inclusion rule was subsequently incorporated into the skill. Its application across other task types and error-recovery scenarios has not been exhaustively tested. No automated test suite is bundled; CLI checks and read-back verification are used for actual records.

## Files

```text
work-record-to-feishu/
├── SKILL.md                     # Agent workflow and rules
├── agents/openai.yaml           # Display name and default invocation
├── references/record-format.md  # Document format and source-inclusion rules
├── README.md
├── README.zh-CN.md
└── .gitignore
```

This is an instruction-based skill, not a standalone application. Task transcripts, generated records, source snapshots, Feishu response files, and credentials are not distributed with it.
