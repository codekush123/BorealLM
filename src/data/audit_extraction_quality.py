import re
from pathlib import Path
import json
import hashlib

TEXT_PATH = Path(
    "data/processed/debug/"
    "W2942539847_body_citation_aware_v1.txt"
)

WORK_ID = "W2942539847"

REPORT_PATH = Path(
    "data/reviews/W2942539847_extraction_audit_v1.json"
)

ISSUE_PATTERNS = {
    "joined_words": (
        r"\b(liquidsolid|LPBFproduced|laserinduced)\b"
    ),
    "split_word": r"\bL aser-based\b",
    "plot_text": r"0 10 600 mm s -1",
    "embedded_caption": (
        r"Fig\. 7 Quality of LPBF-AM tracks"
    ),
    "missing_equation": (
        r"is equal to\s*,\s*where"
    ),
    "publisher_footer": (
        r"NATURE COMMUNICATIONS\s*\|"
    ),
}

def audit_text(text):

    issues = []

    for issue_type, pattern in ISSUE_PATTERNS.items():

        matches = list(
            re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        )

        print(f"\n{issue_type}: {len(matches)}")

        for match in matches:

            start = max(0, match.start() - 90)
            end = min(len(text), match.end() + 90)

            context = " ".join(
                text[start:end].split()
            )

            issue = {
                "issue_id": f"{WORK_ID}-{len(issues) + 1:03d}",
                "issue_type": issue_type,
                "start_char": match.start(),
                "end_char": match.end(),
                "original_text": match.group(),
                "context": context,
                "status": "pending_verification",
                "pdf_page": None,
                "corrected_text": None,
                "resolution": None,
            }

            issues.append(issue)

            print("  ID:", issue["issue_id"])
            print("  Position:", match.start())
            print("  Context:", context)

    return issues

def main():

    text = TEXT_PATH.read_text(
        encoding="utf-8"
    )

    print("=" * 60)
    print("BOREALAM EXTRACTION QUALITY AUDIT")
    print("=" * 60)

    print("Characters:", len(text))

    issues = audit_text(text)

    report = {
        "openalex_id": (
            f"https://openalex.org/{WORK_ID}"
        ),
        "source_text": str(TEXT_PATH),
        "source_sha256": hashlib.sha256(
            TEXT_PATH.read_bytes()
        ).hexdigest(),
        "issue_count": len(issues),
        "review_status": "pending",
        "issues": issues,
    }

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if REPORT_PATH.exists():
        raise FileExistsError(
            f"Review report already exists: {REPORT_PATH}"
        )

    REPORT_PATH.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nTOTAL FLAGGED OCCURRENCES:", len(issues))
    print("Review report:", REPORT_PATH)
    print("Status: REQUIRES MANUAL REVIEW")


if __name__ == "__main__":
    main()