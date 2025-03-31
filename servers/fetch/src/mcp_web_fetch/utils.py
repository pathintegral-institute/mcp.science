import io

import markdownify
import pymupdf
import readabilipy


# handle html to markdown
def convert_html_to_markdown(html_text: str) -> str:
    simple_json_obj = readabilipy.simple_json.simple_json_from_html_string(
        html=html_text, use_readability=True
    )
    if not simple_json_obj["content"]:
        return ""

    return markdownify.markdownify(
        html=simple_json_obj["content"],
        heading_style=markdownify.ATX,
        strip=["script", "style", "iframe", "object", "embed"]
    )


# handle pdf to plain text
def convert_pdf_to_plain_text(pdf_bytes: bytes) -> str:
    """Convert pdf bytes to plain text
    """
    pdf_io = io.BytesIO(pdf_bytes)
    with pymupdf.open(stream=pdf_io) as pdf:
        text = chr(12).join([page.get_text() for page in pdf]) # type: ignore
    return text

# only get the media type
def extract_media_type(content_type_tag: str) -> str:
    if content_type_tag:
        return content_type_tag.split(";")[0]
    return ""
