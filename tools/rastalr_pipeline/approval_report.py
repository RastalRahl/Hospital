"""Idempotent presentation repair; never changes an approval decision."""
import re


def approved_markdown(markdown: str, qa: dict) -> str:
    if qa.get("status") != "approved" or qa.get("human_visual_review", {}).get("result") != "PASS":
        raise ValueError("An existing approved JSON record is required")
    # Keep all non-approval sections; raw pre-repair report is retained in D0 sources.
    markdown = re.sub(r"(?ms)^## Human visual approval\n.*?(?=^## |\Z)", "", markdown)
    markdown = re.sub(r"(?m)^Status:.*$", "Status: **APPROVED** — technical QA and human visual review complete.", markdown)
    review = qa["human_visual_review"]
    return (markdown.rstrip() + "\n\n## Human visual approval\n\n"
            f"Human visual review recorded `PASS` on `{review['reviewed_at']}` against `{review['reviewed_artifact']}`. "
            "All eight logical assets were promoted with their five implementation components; "
            "components remain non-logical and are absent from the catalog.\n")
