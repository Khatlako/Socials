import PyPDF2
from docx import Document

class PortfolioService:
    """Handle portfolio document processing"""
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF"""
        try:
            text = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            return ' '.join(text)
        except Exception as e:
            raise Exception(f'Error extracting PDF text: {str(e)}')
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX"""
        try:
            doc = Document(file_path)
            text = [para.text for para in doc.paragraphs]
            return ' '.join(text)
        except Exception as e:
            raise Exception(f'Error extracting DOCX text: {str(e)}')
    
    @staticmethod
    def extract_text_from_file(file_path, file_type):
        """Extract text based on file type"""
        if file_type == 'pdf':
            return PortfolioService.extract_text_from_pdf(file_path)
        elif file_type in ['docx', 'doc']:
            return PortfolioService.extract_text_from_docx(file_path)
        elif file_type == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None

portfolio_service = PortfolioService()
