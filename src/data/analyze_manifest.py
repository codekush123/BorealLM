import json

INPUT_PATH = (
    "src/data/manifests/"
    "lpbf_candidates_canonical.jsonl"
)

def load_records(path):
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            records.append(record)

    return records


def percentage(count, total):
    if total == 0:
        return 0

    return count / total * 100


def main():
    records = load_records(INPUT_PATH)

    total = len(records)

    with_abstract = sum(
        1 for record in records
        if record.get("abstract")
    )

    with_doi = sum(
        1 for record in records
        if record.get("doi")
    )

    with_pdf = sum(
        1 for record in records
        if record.get("pdf_url")
    )

    print("=" * 60)
    print("BOREALAM LPBF CANDIDATE REPORT")
    print("=" * 60)

    print("Total records:", total)

    print(
        f"With abstract: {with_abstract} "
        f"({percentage(with_abstract, total):.1f}%)"
    )

    print(
        f"With DOI: {with_doi} "
        f"({percentage(with_doi, total):.1f}%)"
    )

    print(
        f"With PDF URL: {with_pdf} "
        f"({percentage(with_pdf, total):.1f}%)"
    )

    license_counts = {}

    for record in records:
        license_name = record.get("license")

        if not license_name:
            license_name = "missing"

        license_counts[license_name] = (
            license_counts.get(license_name, 0) + 1
        )

    print("\nLicenses:")

    for license_name, count in license_counts.items():
        print(f"  {license_name}: {count}")

    title_counts = {}

    for record in records:
        title = record.get("title")

        if not title:
            continue

        normalized_title = title.strip().lower()

        title_counts[normalized_title] = (
            title_counts.get(normalized_title, 0) + 1
        )

    duplicate_titles = {
        title: count
        for title, count in title_counts.items()
        if count > 1
    }

    print(
        "\nDuplicate title groups:",
        len(duplicate_titles)
    )

    print("\n" + "=" * 60)
    print("DUPLICATE TITLE DETAILS")
    print("=" * 60)

    for duplicate_title in duplicate_titles:

        print(f"\nTitle: {duplicate_title}")

        for record in records:

            title = record.get("title")

            if not title:
                continue

            normalized_title = title.strip().lower()

            if normalized_title == duplicate_title:

                print("  OpenAlex ID:", record.get("openalex_id"))
                print("  DOI:", record.get("doi"))
                print("  Year:", record.get("year"))
                print("  Journal:", record.get("journal"))
                print()


if __name__ == "__main__":
    main()