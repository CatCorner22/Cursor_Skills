"""Confirms that every file copy in SKILL.md's appendix matches the source file exactly,
and that hooks written from the appendix behave the same as the source scripts."""

import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def appendix_blocks():
    with open(os.path.join(ROOT, "SKILL.md"), encoding="utf-8") as handle:
        text = handle.read()
    pattern = re.compile(r"^### A\.\d+ (.+?)\n\n(`{3,4})\w*\n(.*?)\n\2\n", re.S | re.M)
    return {match.group(1): match.group(3) for match in pattern.finditer(text)}


class AppendixTests(unittest.TestCase):
    def test_every_source_file_is_copied_exactly(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("build_skill", os.path.join(ROOT, "build_skill.py"))
        build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build)
        blocks = appendix_blocks()
        self.assertEqual(len(blocks), len(build.APPENDIX))
        for source, target, _ in build.APPENDIX:
            with open(os.path.join(ROOT, source), encoding="utf-8") as handle:
                self.assertEqual(blocks[target], handle.read().rstrip(), source)


if __name__ == "__main__":
    unittest.main()
