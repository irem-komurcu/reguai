import re
import fitz
import pymupdf4llm

def load_pdf(data):
    pages = {}
    page = None
    pattern = "-----\n\n"
    with fitz.open(stream=data, filetype="pdf") as file:
        doc = pymupdf4llm.to_markdown(file, page_chunks=True)
        for pidx, p in enumerate(doc):
            text = p["text"]
            if text.endswith(pattern):
                text = text[:-len(pattern)]

            if page:
                bullet_pattern = r"^(?:\s*(?:[-*+]|\d+\.|[a-zA-Z]\.)\s+.*(?:\n|$))+"
                match = re.match(bullet_pattern, text, re.MULTILINE)
                
                if match:
                    to_prev_page = match.group(0)
                    text = text[len(to_prev_page):].strip()
                    pages[page] += f"\n{to_prev_page}"
            page = p["metadata"]["page"]
            pages[page] = text
    return pages
    