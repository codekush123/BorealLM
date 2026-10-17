import xml.etree.ElementTree as ET
from pathlib import Path
import re


XML_PATH = Path(
    "data/raw/xml/W2942539847.tei.xml"
)

OUTPUT_PATH = Path(
    "data/processed/debug/W2942539847_body_citation_aware_v1.txt"
)

FIGURE_OUTPUT_PATH = Path(
    "data/processed/debug/W2942539847_figure_captions.txt"
)

NS = {
    "tei": "http://www.tei-c.org/ns/1.0"
}

def extract_element_text(element):

    if element is None:
        return ""

    raw_text = "".join(element.itertext())

    normalized_text = " ".join(
        raw_text.split()
    )

    return normalized_text

def extract_abstract_text(abstract_element):

    if abstract_element is None:
        return ""

    fragments = [
        fragment.strip()
        for fragment in abstract_element.itertext()
        if fragment.strip()
    ]

    return " ".join(fragments)

def element_name(element):
    return element.tag.split("}")[-1]

def normalize_spacing(text):

    text = " ".join(text.split())

    text = re.sub(
        r"\s+([.,;:!?])",
        r"\1",
        text,
    )

    return text

def render_inline(element):

    parts = [element.text or ""]

    for child in element:

        tag = element_name(child)

        is_bibliographic_reference = (
            tag == "ref"
            and child.get("type") == "bibr"
        )

        if not is_bibliographic_reference:
            parts.append(render_inline(child))

        # Preserve text following the inline element.
        parts.append(child.tail or "")

    return "".join(parts)

def extract_paragraph_text(paragraph):

    sentences = [
        child
        for child in paragraph
        if element_name(child) == "s"
    ]

    if not sentences:
        return normalize_spacing(
            render_inline(paragraph)
        )

    parts = []

    if paragraph.text and paragraph.text.strip():
        parts.append(
            normalize_spacing(paragraph.text)
        )

    for child in paragraph:

        tag = element_name(child)

        if tag == "ref" and child.get("type") == "bibr":
            pass
        else:
            text = normalize_spacing(
                render_inline(child)
            )

            if text:
                parts.append(text)

        if child.tail and child.tail.strip():
            parts.append(
                normalize_spacing(child.tail)
            )

    return " ".join(parts)

def inside_figure(element, parent_map):

    parent = parent_map.get(element)

    while parent is not None:

        if element_name(parent) == "figure":
            return True

        parent = parent_map.get(parent)

    return False

def extract_article(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    abstract_element = root.find(
        ".//tei:abstract", NS
    )

    body_element = root.find(
        ".//tei:body", NS
    )

    if body_element is None:
        raise ValueError("No TEI body found.")

    parent_map = {
        child: parent
        for parent in body_element.iter()
        for child in parent
    }

    body_parts = []
    figure_parts = []

    heading_count = 0
    paragraph_count = 0
    figure_count = 0

    abstract = extract_abstract_text(abstract_element)

    if abstract:
        body_parts.extend(["ABSTRACT", abstract])

    body_parts.append("BODY")

    for element in body_element.iter():

        tag = element_name(element)

        if tag == "figure":

            figure_count += 1

            figure_text = extract_element_text(
                element
            )

            figure_parts.append(
                f"FIGURE ELEMENT {figure_count}\n"
                f"{figure_text}"
            )

        elif tag == "head":

            parent = parent_map.get(element)

            if (
                parent is not None
                and element_name(parent) == "div"
                and not inside_figure(element, parent_map)
            ):

                heading = extract_element_text(
                    element
                )

                if heading:
                    body_parts.append(f"## {heading}")
                    heading_count += 1

        elif tag == "p":

            if inside_figure(element, parent_map):
                continue

            paragraph = extract_paragraph_text(element)

            if paragraph:
                body_parts.append(paragraph)
                paragraph_count += 1

    body_text = "\n\n".join(body_parts)

    figure_text = "\n\n".join(figure_parts)

    return (
        body_text,
        figure_text,
        heading_count,
        paragraph_count,
        figure_count,
    )


def main():

    (
        body_text,
        figure_text,
        headings,
        paragraphs,
        figures,
    ) = extract_article(XML_PATH)

    print("\nABSTRACT VERIFICATION")

    print(
        "Missing sentence space:",
        "components.Widespread" in body_text
    )

    print(
        "Existing joined-word issue:",
        "liquidsolid" in body_text
    )

    print("\nFirst 700 characters:")
    print(body_text[:700])

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        body_text,
        encoding="utf-8",
    )

    FIGURE_OUTPUT_PATH.write_text(
        figure_text,
        encoding="utf-8",
    )

    print("=" * 60)
    print("BOREALAM STRUCTURED EXTRACTION")
    print("=" * 60)

    print("Scientific headings:", headings)
    print("Body paragraphs:", paragraphs)
    print("Figure elements:", figures)

    print("Body characters:", len(body_text))
    print("Figure characters:", len(figure_text))

    print("\nBody file:", OUTPUT_PATH)
    print("Figure file:", FIGURE_OUTPUT_PATH)


if __name__ == "__main__":
    main()