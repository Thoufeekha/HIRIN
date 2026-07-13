import pdfplumber
import re


class ResumeExtractor:
    """
    Extract text from PDF resumes and clean the output.
    """

    @staticmethod
    def extract_text(pdf_file):
        """
        Extract text from a PDF.

        Args:
            pdf_file: PDF path (string) or uploaded file object

        Returns:
            str: Cleaned resume text
        """

        extracted_pages = []

        try:
            with pdfplumber.open(pdf_file) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        extracted_pages.append(page_text)

            full_text = "\n\n".join(extracted_pages)

            return ResumeExtractor.clean_text(full_text)

        except FileNotFoundError:
            raise FileNotFoundError(
                f"PDF file not found: {pdf_file}"
            )

        except Exception as e:
            raise Exception(
                f"Error extracting PDF text: {str(e)}"
            )

    @staticmethod
    def clean_text(text):
        """
        Clean extracted text while preserving structure.
        """

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        text = re.sub(r"[\t ]+", " ", text)

        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    @staticmethod
    def get_basic_stats(text):
        """
        Return statistics about extracted text.
        """

        return {
            "characters": len(text),
            "words": len(text.split()),
            "lines": len(text.splitlines())
        }

    @staticmethod
    def preview(text, num_chars=1000):
        """
        Return preview of extracted text.
        """

        if len(text) <= num_chars:
            return text

        return text[:num_chars] + "\n\n...[TRUNCATED]..."