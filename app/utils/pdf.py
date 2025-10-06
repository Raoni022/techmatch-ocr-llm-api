"""
Utilitários para processamento de arquivos PDF
"""

import io
import base64
from typing import Optional, List, Tuple
import fitz  # PyMuPDF
from PIL import Image
from app.services.logging import get_logger

logger = get_logger(__name__)

class PDFUtils:
    """Utilitários para manipulação de arquivos PDF"""
    
    @staticmethod
    def validate_pdf(content: str) -> bool:
        """
        Valida se o conteúdo base64 é um PDF válido
        
        Args:
            content: Conteúdo do PDF em base64
            
        Returns:
            True se for um PDF válido
        """
        try:
            file_data = base64.b64decode(content)
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            page_count = pdf_document.page_count
            pdf_document.close()
            return page_count > 0
        except Exception as e:
            logger.error(f"Erro na validação do PDF: {str(e)}")
            return False
    
    @staticmethod
    def get_pdf_info(content: str) -> dict:
        """
        Extrai informações básicas do PDF
        
        Args:
            content: Conteúdo do PDF em base64
            
        Returns:
            Dicionário com informações do PDF
        """
        try:
            file_data = base64.b64decode(content)
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            
            info = {
                "page_count": pdf_document.page_count,
                "title": pdf_document.metadata.get("title", ""),
                "author": pdf_document.metadata.get("author", ""),
                "subject": pdf_document.metadata.get("subject", ""),
                "creator": pdf_document.metadata.get("creator", ""),
                "producer": pdf_document.metadata.get("producer", ""),
                "creation_date": pdf_document.metadata.get("creationDate", ""),
                "modification_date": pdf_document.metadata.get("modDate", ""),
                "encrypted": pdf_document.is_encrypted,
                "has_text": False,
                "has_images": False
            }
            
            # Verificar se há texto e imagens
            for page_num in range(min(3, pdf_document.page_count)):  # Verificar apenas primeiras 3 páginas
                page = pdf_document[page_num]
                
                if not info["has_text"] and page.get_text().strip():
                    info["has_text"] = True
                
                if not info["has_images"] and page.get_images():
                    info["has_images"] = True
                
                if info["has_text"] and info["has_images"]:
                    break
            
            pdf_document.close()
            return info
            
        except Exception as e:
            logger.error(f"Erro ao extrair informações do PDF: {str(e)}")
            return {
                "page_count": 0,
                "title": "",
                "author": "",
                "subject": "",
                "creator": "",
                "producer": "",
                "creation_date": "",
                "modification_date": "",
                "encrypted": False,
                "has_text": False,
                "has_images": False,
                "error": str(e)
            }
    
    @staticmethod
    def extract_text_from_pdf(content: str) -> List[str]:
        """
        Extrai texto de todas as páginas do PDF
        
        Args:
            content: Conteúdo do PDF em base64
            
        Returns:
            Lista com texto de cada página
        """
        try:
            file_data = base64.b64decode(content)
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            
            pages_text = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text = page.get_text()
                pages_text.append(text)
            
            pdf_document.close()
            return pages_text
            
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {str(e)}")
            return []
    
    @staticmethod
    def convert_pdf_pages_to_images(content: str, dpi: int = 150) -> List[str]:
        """
        Converte páginas do PDF em imagens base64
        
        Args:
            content: Conteúdo do PDF em base64
            dpi: Resolução das imagens
            
        Returns:
            Lista com imagens em base64
        """
        try:
            file_data = base64.b64decode(content)
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            
            images = []
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Converter página em imagem
                mat = fitz.Matrix(dpi/72, dpi/72)  # Matriz de transformação
                pix = page.get_pixmap(matrix=mat)
                
                # Converter para PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                
                # Converter para base64
                buffer = io.BytesIO()
                image.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                
                images.append(img_base64)
            
            pdf_document.close()
            return images
            
        except Exception as e:
            logger.error(f"Erro ao converter PDF em imagens: {str(e)}")
            return []
    
    @staticmethod
    def extract_images_from_pdf(content: str) -> List[dict]:
        """
        Extrai imagens do PDF
        
        Args:
            content: Conteúdo do PDF em base64
            
        Returns:
            Lista com informações das imagens extraídas
        """
        try:
            file_data = base64.b64decode(content)
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            
            extracted_images = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Extrair imagem
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY ou RGB
                            img_data = pix.tobytes("png")
                            img_base64 = base64.b64encode(img_data).decode()
                            
                            extracted_images.append({
                                "page": page_num + 1,
                                "index": img_index,
                                "width": pix.width,
                                "height": pix.height,
                                "colorspace": pix.colorspace.name if pix.colorspace else "unknown",
                                "content": img_base64
                            })
                        
                        pix = None  # Liberar memória
                        
                    except Exception as e:
                        logger.warning(f"Erro ao extrair imagem {img_index} da página {page_num}: {str(e)}")
                        continue
            
            pdf_document.close()
            return extracted_images
            
        except Exception as e:
            logger.error(f"Erro ao extrair imagens do PDF: {str(e)}")
            return []

# Instância global dos utilitários
pdf_utils = PDFUtils()