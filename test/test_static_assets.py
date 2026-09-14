import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(ROOT, "templates")
STATIC = os.path.join(ROOT, "static")
STATIC_REF = re.compile(r"url_for\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*['\"]([^'\"]+)['\"]")


def _exists_with_exact_case(root, relative):
    current = root
    for part in relative.split("/"):
        if not os.path.isdir(current) or part not in os.listdir(current):
            return False
        current = os.path.join(current, part)
    return True


def _static_refs():
    refs = []
    for name in sorted(os.listdir(TEMPLATES)):
        if not name.endswith(".html"):
            continue
        with open(os.path.join(TEMPLATES, name), encoding="utf-8") as f:
            refs += [(name, ref) for ref in STATIC_REF.findall(f.read())]
    return refs


def test_templates_reference_static_files():
    assert _static_refs()


def test_static_references_match_file_names_exactly():
    broken = [template + ": " + ref for template, ref in _static_refs()
              if not _exists_with_exact_case(STATIC, ref)]
    assert broken == []
