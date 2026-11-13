"""Offline regressions for generated records and full source read-back."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "validate_record", ROOT / "scripts" / "validate_record.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

TITLE = "<title>工作记录技能开发_20261113</title>"
HEADING = '<h1 seq="auto">工作内容</h1>'
TABLE = ("<table><thead><tr><th><p>事项</p></th><th><p>当前结果</p></th>"
         "</tr></thead><tbody><tr><td><p>方案</p></td><td><p>已确认；未部署</p>"
         "</td></tr></tbody></table>")


def source_block(label, text):
    return ('<pre lang="plaintext" caption="' + label + '/SKILL.md"><code>'
            + escape(text).replace("\r", "&#13;").replace("\n", "<br/>")
            + "</code></pre>")


class RecordValidationTests(unittest.TestCase):
    def codes(self, xml, sources=None):
        return {e["code"] for e in module.validate_record(xml, sources)}

    def test_concise_record_preserves_unfinished_fact(self):
        self.assertEqual(module.validate_record(TITLE + HEADING + TABLE), [])

    def test_redundant_intro_rejected(self):
        self.assertIn("preamble", self.codes(TITLE + "<p>记录创建时间：今日。</p>" + HEADING))

    def test_follow_up_chapters_rejected(self):
        for heading in ("后续事项", "5.1 待完成或待确认事项", "Next steps"):
            with self.subTest(heading=heading):
                xml = TITLE + HEADING + '<h2 seq="auto">' + heading + "</h2>"
                self.assertIn("follow_up", self.codes(xml))

    def test_source_with_forbidden_words_and_xml_is_unchanged(self):
        source = '---\nname: sample\n---\n# 后续事项\n<h1> & "示例"\n'
        xml = TITLE + HEADING + source_block("sample", source)
        self.assertEqual(module.validate_record(xml, {"sample": source}), [])

    def test_crlf_source_round_trip(self):
        source = "---\r\nname: sample\r\n---\r\n"
        self.assertEqual(module.validate_record(
            TITLE + HEADING + source_block("sample", source), {"sample": source}), [])

    def test_split_source_and_multiple_skills(self):
        source = "---\nname: sample\n---\n"
        xml = TITLE + HEADING + source_block("sample", source[:7])
        xml += source_block("sample", source[7:]) + source_block("another", "# Another\n")
        self.assertEqual(module.validate_record(
            xml, {"sample": source, "another": "# Another\n"}), [])

    def test_trimmed_source_and_missing_source_fail(self):
        source = "---\nname: sample\n---\n"
        xml = TITLE + HEADING + source_block("sample", source.rstrip())
        self.assertIn("source_mismatch", self.codes(xml, {"sample": source}))
        self.assertIn("source_missing", self.codes(TITLE + HEADING, {"sample": source}))

    def test_attachment_does_not_replace_source(self):
        xml = TITLE + HEADING + '<source token="example" name="skill.zip"/>'
        self.assertIn("source_missing", self.codes(xml, {"sample": "# Skill\n"}))

    def test_malformed_xml_and_patch_fragment_rejected(self):
        self.assertIn("xml", self.codes(TITLE + "<h1>"))
        self.assertIn("title", self.codes("<p>局部补丁不能冒充完整候选。</p>"))

    def test_invalid_name_date_and_heading_levels(self):
        for title in ("十六" * 8 + "_20261113", "任务_20260230"):
            self.assertIn("name", self.codes("<title>" + title + "</title>" + HEADING))
        self.assertIn("heading_level", self.codes(TITLE + HEADING + '<h3 seq="auto">模块</h3>'))

    def test_numbering_and_table_width(self):
        self.assertIn("numbering", self.codes(TITLE + "<h1>模块</h1>"))
        bad = TABLE.replace("<td><p>方案</p></td>", "")
        self.assertIn("table", self.codes(TITLE + HEADING + bad))

    def test_updates_keep_original_title_and_creation_date(self):
        original = "工作记录技能开发_20261103"
        same = "<title>" + original + "</title>" + HEADING + TABLE
        self.assertEqual(module.validate_record(same, original_title=original), [])
        changed = TITLE + HEADING + TABLE
        errors = module.validate_record(changed, original_title=original)
        self.assertIn("title_changed", {e["code"] for e in errors})

    def test_legacy_title_is_preserved_without_forced_renaming(self):
        original = "旧记录：此前人工确定的较长文档名称"
        xml = "<title>" + original + "</title>" + HEADING + TABLE
        self.assertEqual(module.validate_record(xml, original_title=original), [])

    def test_invalid_table_spans_report_errors(self):
        for span in ("wrong", "0", "-1"):
            bad = TABLE.replace("<th>", '<th colspan="' + span + '">', 1)
            self.assertIn("table", self.codes(TITLE + HEADING + bad))

    def test_actual_current_skill_source_can_be_archived_losslessly(self):
        source = (ROOT / "SKILL.md").read_bytes().decode("utf-8")
        xml = TITLE + HEADING + TABLE + source_block("work-record-to-feishu", source)
        self.assertEqual(module.validate_record(xml, {"work-record-to-feishu": source}), [])

    def test_cli_failure_has_nonzero_exit_status(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.xml"
            candidate.write_text(TITLE + "<p>冗余开场</p>" + HEADING, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_record.py"), str(candidate)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn('"status": "failed"', result.stdout)


if __name__ == "__main__":
    unittest.main()
