# PDF Support

This document outlines the PDF support feature of the Text-to-Speech Generator application.

## Overview

The application now supports direct PDF file uploads, automatically extracting text content and converting it to speech. This feature is available through both the web interface and the API.

## How It Works

1. **Text Extraction**: When a PDF file is uploaded, the application uses the PyPDF2 library to extract text content from all pages.
2. **Processing**: The extracted text is processed in the same way as direct text input, including chunking for large documents.
3. **Storage**: In the history, PDF-sourced audio files are marked accordingly and display the original PDF filename.

## Usage

### Web Interface

1. Navigate to the main page of the application
2. Either:
   - Enter text in the text area, OR
   - Click the "Upload a PDF File" button and select a PDF document
3. Select your preferred voice and model
4. Click "Generate Speech"

### API

The API supports PDF uploads in two ways:

#### Multipart Form Data

```bash
curl -X POST -F "pdf_file=@document.pdf" \
     -F "voice=alloy" \
     -F "model=tts-1" \
     http://localhost:5001/api/generate
```

#### JSON with Base64-encoded PDF

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{
        "pdf_base64": "BASE64_ENCODED_PDF_DATA",
        "voice": "alloy",
        "model": "tts-1",
        "filename": "document.pdf"
     }' \
     http://localhost:5001/api/generate
```

## Limitations

- The maximum PDF file size is 20MB
- PDF files that are scanned images without proper OCR may not extract properly
- Password-protected PDFs are not supported
- Complex formatting from PDFs may not be preserved
- Maximum of 25,000 characters can be processed (same as direct text input)

## Implementation Details

### Backend

The PDF support is implemented using the PyPDF2 library, which provides Python functions for reading and manipulating PDF files. The main extraction function is `extract_text_from_pdf()`, which:

1. Creates a PdfReader object from the uploaded file
2. Iterates through all pages
3. Extracts text from each page
4. Combines the text with appropriate spacing
5. Returns the extracted text

### Frontend

The frontend includes:

1. A file input field for PDF uploads
2. Client-side validation ensuring at least text or PDF is provided
3. A "clear file" button to remove the selected PDF
4. Display of the source type and original filename in the results page
5. PDF badges in the history view to identify PDF-sourced audio

## Testing

The PDF feature includes comprehensive tests:

### Server-side Tests

- Unit tests for the extraction functionality
- Integration tests for the web interface and API endpoints
- Error handling tests for various PDF processing scenarios

### Client-side Tests

- UI interaction tests for the PDF upload field
- Form validation tests for PDF submissions
- API integration tests with PDF data

## Future Improvements

Potential future enhancements to the PDF support feature:

1. OCR support for image-based PDFs
2. Password protection handling
3. Table and form extraction improvements
4. Extraction preview before processing
5. Partial PDF processing (selecting specific pages)
6. Extraction of document metadata (title, author, etc.) 