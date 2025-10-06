"""
Serviço de OCR (Optical Character Recognition)
"""

import time
import base64
import io
from typing import Optional, Tuple
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from app.models import OCRResult, DocumentType
from app.services.logging import get_logger

logger = get_logger(__name__)

class OCRService:
    """Serviço para processamento de OCR"""
    
    def __init__(self):
        self.supported_languages = ['por', 'eng', 'spa']
        
    async def extract_text_from_document(
        self, 
        content: str, 
        document_type: DocumentType,
        language: str = 'por'
    ) -> OCRResult:
        """
        Extrai texto de um documento usando OCR
        
        Args:
            content: Conteúdo do documento em base64
            document_type: Tipo do documento
            language: Idioma para OCR
            
        Returns:
            OCRResult com o texto extraído
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando OCR para documento tipo {document_type}")
            
            # Decodificar conteúdo base64
            file_data = base64.b64decode(content)
            
            if document_type == DocumentType.PDF:
                text, confidence = await self._extract_from_pdf(file_data, language)
            elif document_type == DocumentType.IMAGE:
                text, confidence = await self._extract_from_image(file_data, language)
            else:
                # Para texto simples, apenas decodificar
                text = file_data.decode('utf-8')
                confidence = 1.0
                
            processing_time = time.time() - start_time
            
            logger.info(f"OCR concluído em {processing_time:.2f}s com confiança {confidence:.2f}")
            
            return OCRResult(
                text=text,
                confidence=confidence,
                language=language,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Erro no OCR: {str(e)}")
            processing_time = time.time() - start_time
            
            return OCRResult(
                text="",
                confidence=0.0,
                language=language,
                processing_time=processing_time
            )
    
    async def _extract_from_pdf(self, file_data: bytes, language: str) -> Tuple[str, float]:
        """Extrai texto de PDF usando OCR"""
        try:
            # Abrir PDF
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            
            all_text = []
            total_confidence = 0.0
            page_count = 0
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Tentar extrair texto diretamente primeiro
                direct_text = page.get_text()
                
                if direct_text.strip():
                    # Se há texto extraível diretamente, usar
                    all_text.append(direct_text)
                    total_confidence += 0.95  # Alta confiança para texto direto
                else:
                    # Caso contrário, usar OCR na imagem da página
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    
                    # Converter para PIL Image
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Aplicar OCR
                    ocr_text = pytesseract.image_to_string(image, lang=language)
                    all_text.append(ocr_text)
                    
                    # Estimar confiança baseada na quantidade de texto
                    confidence = min(0.8, len(ocr_text.strip()) / 1000)
                    total_confidence += confidence
                
                page_count += 1
            
            pdf_document.close()
            
            final_text = "\n\n".join(all_text)
            avg_confidence = total_confidence / page_count if page_count > 0 else 0.0
            
            return final_text, min(1.0, avg_confidence)
            
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {str(e)}")
            return "", 0.0
    
    async def _extract_from_image(self, file_data: bytes, language: str) -> Tuple[str, float]:
        """Extrai texto de imagem usando OCR"""
        try:
            # Abrir imagem
            image = Image.open(io.BytesIO(file_data))
            
            # Aplicar OCR
            text = pytesseract.image_to_string(image, lang=language)
            
            # Estimar confiança baseada na quantidade de texto extraído
            confidence = min(0.9, len(text.strip()) / 500)
            
            return text, confidence
            
        except Exception as e:
            logger.error(f"Erro ao processar imagem: {str(e)}")
            return "", 0.0
    
    def get_supported_languages(self) -> list:
        """Retorna lista de idiomas suportados"""
        return self.supported_languages.copy()

# Instância global do serviço
ocr_service = OCRService()