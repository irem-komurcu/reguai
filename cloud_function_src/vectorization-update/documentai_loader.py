from google.cloud import documentai_v1 as documentai

processor_name = "projects/qwiklabs-gcp-02-53d3959153c2/locations/us/processors/2284c80bd7a1f4a8"

def load_pdf(data):
    client = documentai.DocumentProcessorServiceClient()
    document_content = data

    raw_document = documentai.RawDocument(content=document_content, mime_type="application/pdf")
    request = documentai.ProcessRequest(name=processor_name, raw_document=raw_document)

    try:
        response = client.process_document(request=request)
        full_text = response.document.text
        page_texts = {}
        
        for page in response.document.pages:
            page_number = page.page_number
            text = ""
            for segment in page.layout.text_anchor.text_segments:
                start_index = segment.start_index if segment.start_index else 0
                end_index = segment.end_index if segment.end_index else len(full_text)
                text += full_text[start_index:end_index]
            
            page_texts[page_number] = text
        return page_texts
    except Exception as e:
        raise Exception("Error during processing:", e)