from pathlib import Path

import pymupdf


PDF_PATH = Path(
    "data/raw/pdf/W2942539847.pdf"
)

OUTPUT_PATH = Path(
    "data/processed/debug/W2942539847_pymupdf_raw.txt"
)

def inspect_pdf(pdf_path):

    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    with pymupdf.open(pdf_path) as document:

        if document.needs_pass:
            raise ValueError("PDF requires a password.")

        print("=" * 60)
        print("BOREALAM PDF STRUCTURE REPORT")
        print("=" * 60)

        print("Pages:", document.page_count)
        print("Metadata title:", document.metadata.get("title"))
        print("PDF format:", document.metadata.get("format"))

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            text = page.get_text("text")

            print(
                f"Page {page_number}: "
                f"{len(text)} characters"
            )

def extract_pdf_text(pdf_path, output_path):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    extracted_pages = []

    with pymupdf.open(pdf_path) as document:

        if document.needs_pass:
            raise ValueError("PDF requires a password.")

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            text = page.get_text(
                "text",
                sort=True,
            )

            page_content = (
                f"\n===== PAGE {page_number} =====\n"
                + text
            )

            extracted_pages.append(page_content)

    full_text = "\n".join(extracted_pages)

    if not full_text.strip():
        raise ValueError("No text extracted.")

    output_path.write_text(
        full_text,
        encoding="utf-8",
    )

    return full_text

def compare_reading_order(pdf_path, page_number=2):

    output_dir = Path("data/processed/debug")
    output_dir.mkdir(parents=True, exist_ok=True)

    with pymupdf.open(pdf_path) as document:
        page = document[page_number - 1]

        unsorted_text = page.get_text(
            "text",
            sort=False,
        )

        sorted_text = page.get_text(
            "text",
            sort=True,
        )

    versions = {
        "unsorted": unsorted_text,
        "sorted": sorted_text,
    }

    for name, text in versions.items():

        output_path = (
            output_dir
            / f"W2942539847_page{page_number}_{name}.txt"
        )

        output_path.write_text(
            text,
            encoding="utf-8",
        )

        visible_characters = sum(
            not character.isspace()
            for character in text
        )

        print(f"\n{name.upper()}")
        print("Total characters:", len(text))
        print("Non-whitespace characters:", visible_characters)
        print("Output:", output_path)

def main():

    inspect_pdf(PDF_PATH)

    print("\nExtracting PDF text...")

    full_text = extract_pdf_text(
        PDF_PATH,
        OUTPUT_PATH,
    )

    print("\nEXTRACTION COMPLETE")
    print("Characters:", len(full_text))
    print("Output:", OUTPUT_PATH)

    print("\nTEXT PREVIEW")
    print("-" * 60)
    print(full_text[:1500])

    print("\nCOMPARING READING ORDER")

    compare_reading_order(
        PDF_PATH,
        page_number=2,
    )


if __name__ == "__main__":
    main()