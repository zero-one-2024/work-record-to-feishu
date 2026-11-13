# Feishu Work Records

[English](README.md) | [简体中文](README.zh-CN.md)

将任务会话整理为简洁、表格优先的工作记录，保存到飞书**我的文档库**（`my_library`）。首次创建，工作有更新时维护同一篇文档。

**技能标识：** `work-record-to-feishu`

**显示名称：** Feishu Work Records

技能说明和默认记录内容使用中文，技能名称与标识使用英文。

## 行为规则

| 方面 | 规则 |
| --- | --- |
| 易读性 | 各模块能用原生表格就用表格，一行一个事项，单元格只写关键事实，不整段搬运文字。 |
| 开头 | 标题后直接进入第一个模块，省略创建时间、会话来源、记录范围等开场说明。 |
| 当前状态 | 未开发、未部署、未验证、受阻等事实放在对应状态行，不编写未来计划或后续／待办章节。 |
| 版本迭代 | 保留重要变更与有效历史证据，结果列写当前结果，不写未来行动。 |
| 首次调用 | 在我的文档库创建“任务摘要_YYYYMMDD”，摘要不超过15个字符，创建日期采用北京时间。 |
| 后续调用 | 定位并读取同一任务的原记录，更新相关行与真实迭代，保留原名称及首次创建日期。 |
| 技能开发 | 正文完整收录所开发技能的当前SKILL.md，包含YAML元数据；回读与源文件快照比对。 |

必要的一句说明、图片和完整原文可保留适合的表达形式。只记录有依据的事实，分别表达本地测试、交付、部署和验收。

## 使用要求

- 能加载本地技能并运行命令的 Codex 环境。
- 单独安装并完成登录授权的 `lark-cli`，具备所需文档权限。
- 配套的 `lark-doc`、`lark-wiki`、`lark-shared` 技能；没有绑定且需搜索旧记录时，还需 `lark-drive`。本仓库不附带这些依赖。
- CLI 支持 `docs +script`、`docs +create --parent-position my_library`、`docs +update`、`docs +fetch` 和 `wiki +node-get`。
- Python 3.9+，用于附带的离线检查器及回归测试，仅使用标准库。

```bash
lark-cli docs +create --help
lark-cli docs +update --help
lark-cli docs +script --help
lark-cli wiki +node-get --help
```

文档操作使用 `--as user`。按自己的飞书账号配置登录、接口权限和资源权限；仓库不包含账号凭据。

## 安装

将仓库克隆到技能目录之外，再链接到实际配置的 Codex 技能目录。以下示例使用默认位置，并假设尚未安装同名技能：

```bash
git clone https://github.com/zero-one-2024/work-record-to-feishu.git
mkdir -p ~/.codex/skills
ln -s "$(pwd)/work-record-to-feishu" ~/.codex/skills/work-record-to-feishu
```

安装位置已存在时，先检查再更新原安装。使用其他技能目录时替换为实际配置的位置。

## 调用方式

在任务会话中调用：

```text
$work-record-to-feishu 编写工作记录
```

同一任务有新工作时调用：

```text
使用 $work-record-to-feishu 更新当前任务的工作记录。
```

智能体优先使用用户指定的记录链接、当前任务会话中确认过的链接或任务绑定信息，更新前读取实际文档。不能仅凭同名认定对应关系。原绑定文档无权限时不能另建替代；多个候选无法区分时需明确目标。没有绑定且不确定是否已有记录时，先搜索并核对内容，再决定是否创建。

确认首次记录后创建文档，在任务工作区保存URL、ID、原名称日期、任务标识和观察到的revision。没有新事实时返回原链接，不重复追加。用户明确另建独立快照时保留原任务绑定，除非指定切换。只讨论方案或只要求本地草稿时不写入云文档。

更新保留历史、人工内容、图片附件与引用。维护本任务的旧格式记录时，先把相关未完成事实和独有证据迁入对应状态表，再移除冗余开场与未来行动清单。不批量整理其他历史文档。

## 文档格式

只保留有用的章节，使用连续的原生标题编号：

```text
1 任务概述（必要时，用字段表）
2 工作内容
2.1 实际模块（优先表格）
3 版本迭代记录（存在真实迭代时）
3.1 迭代明细
4 工作成果
4.1 交付与验证（表格）
5 技能文件原文（仅技能开发类）
5.1 技能标识／SKILL.md
```

工作内容通常使用“事项／处理内容／当前结果／证据”，成果通常使用“成果／版本或位置／验证结果”。根据内容选择最少且足够的列，不将所有模块强行套入迭代表。

| 版本／轮次 | 日期 | 触发问题或需求 | 主要修改内容 | 验证记录 | 当前结果 | 证据／附件 |
| --- | --- | --- | --- | --- | --- | --- |

保留真实版本和事件日期。后续验证通过，也不能改写当时失败的历史事实。省略空节，文档在成果或完整技能原文后结束，不设置未来工作章节。

完整规则见 [工作记录格式](references/record-format.md) 和 [文档维护](references/document-maintenance.md)。

## 写入与验证

创建遵循 `lark-doc` 创作工作流，更新遵循先读现状、局部修改、回读的流程。完整候选文档用于检查，不代表允许整篇覆盖；局部修改使用最新block ID和revision，遇到并发变化先重读。

首次创建指定个人文档库：

```bash
lark-cli docs +create \
  --doc-format xml \
  --content '@./draft.xml' \
  --parent-position my_library \
  --as user \
  --format json
```

该命令不能替代草稿准备和CLI检查。超时或部分成功时，先回读目标确认实际结果，再决定是否重试，避免重复创建或重复追加。

本地检查完整候选XML：

```bash
python3 scripts/validate_record.py /path/to/candidate.xml
```

更新时传入实际读取到的原文档名，检查名称及首次创建日期得到保留，旧格式标题也不强行改名：

```bash
python3 scripts/validate_record.py /path/to/candidate.xml \
  --original-title 'OriginalTitle_20261103'
```

技能开发类记录指定保存的源文件快照：

```bash
python3 scripts/validate_record.py /path/to/candidate.xml \
  --skill-source 'sample-skill=/path/to/SKILL-snapshot.md'
```

源码代码块使用 `caption="sample-skill/SKILL.md"`，拆分片段保持同一caption并按顺序排列。多个技能重复传入 `--skill-source`。检查器验证名称日期格式、无开场和后续标题、标题结构、简单表格列数及指定原文一致性；必须传入完整候选，不能用局部更新片段代替。

检查器不判断事实准确性、文字是否精炼、文档目标是否正确、人工内容是否保留或线上写入是否成功，这些仍需审阅并实际回读。源码链接与ZIP不能替代正文完整原文。草稿、绑定信息、响应和源码快照保留在本仓库之外。

## 测试与验证范围

```bash
python3 -m unittest discover -s tests -v
```

离线测试覆盖结构拒绝、原名称保留、XML与源码往返还原、多片段及多技能、缺失或改变的原文、CLI失败报告。[维护场景](tests/maintenance-scenarios.md)提供任务级审阅用例，不代表线上行为已验证。

2026年11月3日曾验证实际创建、个人文档库归属、原生标题及迭代表回读、附件上传下载与SHA-256一致性、完整源码插入回读。2026年11月13日修改加入表格优先、同一任务维护及离线检查；本次修改没有对真实云文档执行新的维护验证。

## 文件结构

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

本项目是附带离线检查器的指令型技能，不是独立飞书应用；仓库不包含任务会话、云端响应或账号凭据。
