import PyPDF2
import io

def test_pdf():
    """Test PDF extraction functionality"""
    try:
        # Open the PDF file
        with open("test.pdf", "rb") as f:
            pdf_content = f.read()
        
        print(f"PDF content length: {len(pdf_content)}")
        
        # Create a BytesIO object with the content
        pdf_file_io = io.BytesIO(pdf_content)
        
        # Use PyPDF2 to read the PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file_io)
        num_pages = len(pdf_reader.pages)
        print(f"Number of pages: {num_pages}")
        
        pdf_text = ""
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            print(f"Page {page_num+1} text length: {len(page_text) if page_text else 0}")
            print(f"Page {page_num+1} text: {page_text}")
            if page_text:  # Only add if text was extracted
                pdf_text += page_text + "\n\n"
        
        print(f"Total extracted text length: {len(pdf_text.strip())}")
        print(f"Extracted text: {pdf_text.strip()}")
        
        return pdf_text.strip()
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    test_pdf() 