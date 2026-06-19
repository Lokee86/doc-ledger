from __future__ import annotations

import sys
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT))

from docs_index.readme_io import ensure_managed_sections
from docs_index.readme_io import make_readme_template
from docs_index.readme_io import managed_root_title
from docs_index.readme_io import replace_managed_block


def test_ensure_managed_sections_inserts_doc_ledger_markers() -> None:
    text = "# Title\n\n## Related Docs\n"

    result = ensure_managed_sections(text)

    assert "<!-- doc-ledger:files:start -->" in result
    assert "<!-- doc-ledger:stubs:start -->" in result
    assert "<!-- doc-ledger:folders:start -->" in result


def test_replace_managed_block_uses_doc_ledger_markers() -> None:
    text = """# Title

## Direct Files
<!-- doc-ledger:files:start -->
<!-- doc-ledger:files:end -->

## Stub Files
<!-- doc-ledger:stubs:start -->
<!-- doc-ledger:stubs:end -->

## Direct Folders
<!-- doc-ledger:folders:start -->
<!-- doc-ledger:folders:end -->
"""

    result = replace_managed_block(text, "files", ["- [guide.md](guide.md) - Guide documentation."])

    assert "<!-- doc-ledger:files:start -->" in result
    assert "- [guide.md](guide.md) - Guide documentation." in result


def test_make_readme_template_uses_doc_ledger_markers() -> None:
    folder = Path("/tmp/docs")

    result = make_readme_template(folder, folder, None)

    assert "<!-- doc-ledger:files:start -->" in result
    assert "<!-- doc-ledger:stubs:start -->" in result
    assert "<!-- doc-ledger:folders:start -->" in result


def test_ensure_managed_sections_migrates_top_level_headings() -> None:
    text = """# Docs

## Top-Level Files
<!-- doc-ledger:files:start -->
- [alpha.md](alpha.md) - Alpha description.
<!-- doc-ledger:files:end -->

## Rulebook
Keep this rulebook.

## Top-Level Folders
<!-- doc-ledger:folders:start -->
- [Guide](guide/!README.md) - Guide description.
<!-- doc-ledger:folders:end -->

## Related Docs
Still here.

## Notes
More notes.
"""

    result = ensure_managed_sections(text)

    assert "## Top-Level Files" not in result
    assert "## Top-Level Folders" not in result
    assert "## Direct Files" in result
    assert result.count("## Direct Files") == 1
    assert result.count("## Stub Files") == 1
    assert "## Direct Folders" in result
    assert result.count("## Direct Folders") == 1
    assert "- [alpha.md](alpha.md) - Alpha description." in result
    assert "- [Guide](guide/!README.md) - Guide description." in result
    assert "## Rulebook" in result
    assert "## Related Docs" in result
    assert "## Notes" in result


def test_managed_root_title_prefers_consistent_child_titles() -> None:
    root = Path("/tmp/docs")

    result = managed_root_title(root, "# Documentation\n", ["Docs", "Docs"])

    assert result == "Docs"


def test_managed_root_title_falls_back_to_root_heading_when_no_child_titles() -> None:
    root = Path("/tmp/docs")

    result = managed_root_title(root, "# Documentation\n", [])

    assert result == "Documentation"
