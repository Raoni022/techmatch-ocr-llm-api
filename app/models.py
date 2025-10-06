"""
Modelos de dados para a API TechMatch OCR+LLM

Este módulo define todos os modelos Pydantic utilizados pela API,
incluindo modelos de requisição, resposta e entidades de domínio.
Todos os modelos incluem validações, documentação e exemplos.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, Field, validator
from pydantic.types import PositiveFloat, PositiveInt
from typing import Annotated

# Type aliases para validações
constr = Annotated[str, Field()]
conint = Annotated[int, Field()]

class DocumentType(str, Enum):
    """Tipos de documento suportados pela API"""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    DOCX = "docx"
    DOC = "doc"


class ProcessingStatus(str, Enum):
    """Status de processamento de documentos"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class SentimentType(str, Enum):
    """Tipos de sentimento detectados"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class LanguageCode(str, Enum):
    """Códigos de idioma suportados"""
    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"


class ErrorCode(str, Enum):
    """Códigos de erro padronizados"""
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    OCR_PROCESSING_ERROR = "OCR_PROCESSING_ERROR"
    NLP_PROCESSING_ERROR = "NLP_PROCESSING_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"

class DocumentUploadRequest(BaseModel):
    """Modelo para requisição de upload de documento"""
    filename: str = Field(..., description="Nome do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "contrato.pdf",
                "content_type": "application/pdf",
                "size": 1024000
            }
        }
    }

class BatchRequest(BaseModel):
    """Modelo para requisição de processamento em lote"""
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID único da requisição")
    user_id: str = Field(..., description="ID do usuário")
    query: Optional[str] = Field(None, description="Query de busca (opcional - se não fornecida, retorna sumários)")
    documents: List[DocumentUploadRequest] = Field(..., description="Lista de documentos para processar")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "example_with_query": {
                        "summary": "Batch com query específica",
                        "value": {
                            "request_id": "req_123456",
                            "user_id": "user_789",
                            "query": "contratos de prestação de serviços",
                            "documents": [
                                {
                                    "filename": "contrato1.pdf",
                                    "content_type": "application/pdf",
                                    "size": 1024000
                                },
                                {
                                    "filename": "contrato2.pdf", 
                                    "content_type": "application/pdf",
                                    "size": 2048000
                                }
                            ]
                        }
                    }
                },
                {
                    "example_without_query": {
                        "summary": "Batch apenas para sumários",
                        "value": {
                            "request_id": "req_654321",
                            "user_id": "user_456",
                            "query": None,
                            "documents": [
                                {
                                    "filename": "documento1.pdf",
                                    "content_type": "application/pdf",
                                    "size": 512000
                                },
                                {
                                    "filename": "imagem1.jpg",
                                    "content_type": "image/jpeg", 
                                    "size": 256000
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }

class DocumentResult(BaseModel):
    """Resultado do processamento de um documento"""
    document_id: str = Field(..., description="ID do documento")
    filename: str = Field(..., description="Nome do arquivo")
    status: ProcessingStatus = Field(..., description="Status do processamento")
    extracted_text: Optional[str] = Field(None, description="Texto extraído")
    summary: Optional[str] = Field(None, description="Resumo do documento")
    similarity_score: Optional[float] = Field(None, description="Score de similaridade com a query")
    justification: Optional[str] = Field(None, description="Justificativa do match")
    relevant_excerpts: Optional[List[str]] = Field(None, description="Trechos relevantes")
    processing_time: float = Field(..., description="Tempo de processamento")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")

class BatchResponse(BaseModel):
    """Resposta do processamento em lote"""
    request_id: str = Field(..., description="ID da requisição")
    user_id: str = Field(..., description="ID do usuário")
    query: Optional[str] = Field(None, description="Query utilizada")
    total_documents: int = Field(..., description="Total de documentos processados")
    successful_documents: int = Field(..., description="Documentos processados com sucesso")
    failed_documents: int = Field(..., description="Documentos que falharam")
    results: List[DocumentResult] = Field(..., description="Resultados por documento")
    total_processing_time: float = Field(..., description="Tempo total de processamento")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do processamento")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "req_123456",
                "user_id": "user_789", 
                "query": "contratos de prestação de serviços",
                "total_documents": 2,
                "successful_documents": 2,
                "failed_documents": 0,
                "results": [
                    {
                        "document_id": "doc_001",
                        "filename": "contrato1.pdf",
                        "status": "completed",
                        "extracted_text": "Contrato de prestação de serviços...",
                        "summary": "Contrato entre empresa A e B para serviços de consultoria",
                        "similarity_score": 0.95,
                        "justification": "Documento altamente relevante - contém termos 'contrato' e 'prestação de serviços'",
                        "relevant_excerpts": ["prestação de serviços de consultoria", "contrato firmado entre as partes"],
                        "processing_time": 2.5,
                        "error_message": None
                    }
                ],
                "total_processing_time": 5.2,
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    }

class DocumentUploadResponse(BaseModel):
    """Modelo para resposta de upload de documento"""
    document_id: str = Field(..., description="ID único do documento")
    filename: str = Field(..., description="Nome do arquivo")
    status: ProcessingStatus = Field(..., description="Status do processamento")
    upload_timestamp: datetime = Field(..., description="Timestamp do upload")

class TextAnalysisRequest(BaseModel):
    """Modelo para requisição de análise de texto"""
    text: str = Field(..., description="Texto para análise", min_length=1)
    language: Optional[str] = Field("pt", description="Idioma do texto (pt, en, es)")
    
class TextAnalysisResponse(BaseModel):
    """Modelo para resposta de análise de texto"""
    original_text: str = Field(..., description="Texto original")
    language: str = Field(..., description="Idioma detectado")
    word_count: int = Field(..., description="Número de palavras")
    char_count: int = Field(..., description="Número de caracteres")
    summary: str = Field(..., description="Resumo do texto")
    keywords: List[str] = Field(..., description="Palavras-chave extraídas")
    sentiment: str = Field(..., description="Sentimento do texto")
    categories: List[str] = Field(..., description="Categorias identificadas")

class DocumentProcessingRequest(BaseModel):
    """Modelo para requisição de processamento de documento"""
    document_id: str = Field(..., description="ID do documento")
    extract_text: bool = Field(True, description="Extrair texto via OCR")
    analyze_content: bool = Field(True, description="Analisar conteúdo com NLP")
    language: Optional[str] = Field("pt", description="Idioma esperado")

class DocumentProcessingResponse(BaseModel):
    """Modelo para resposta de processamento de documento"""
    document_id: str = Field(..., description="ID do documento")
    status: ProcessingStatus = Field(..., description="Status do processamento")
    extracted_text: Optional[str] = Field(None, description="Texto extraído")
    analysis: Optional[TextAnalysisResponse] = Field(None, description="Análise do texto")
    processing_time: float = Field(..., description="Tempo de processamento em segundos")
    error_message: Optional[str] = Field(None, description="Mensagem de erro, se houver")

class HealthResponse(BaseModel):
    """Modelo para resposta de health check"""
    status: str = Field(..., description="Status da API")
    timestamp: datetime = Field(..., description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    services: Dict[str, str] = Field(..., description="Status dos serviços")

class SupportedLanguagesResponse(BaseModel):
    """Modelo para resposta de idiomas suportados"""
    languages: List[Dict[str, str]] = Field(..., description="Lista de idiomas suportados")

class InfoExtractionResponse(BaseModel):
    """Modelo para resposta de extração de informações"""
    emails: List[str] = Field(..., description="E-mails encontrados")
    phones: List[str] = Field(..., description="Telefones encontrados")
    dates: List[str] = Field(..., description="Datas encontradas")
    urls: List[str] = Field(..., description="URLs encontradas")
    entities: List[Dict[str, Any]] = Field(..., description="Entidades nomeadas")

class PDFInfoResponse(BaseModel):
    """Modelo para resposta de informações de PDF"""
    pages: int = Field(..., description="Número de páginas")
    title: Optional[str] = Field(None, description="Título do documento")
    author: Optional[str] = Field(None, description="Autor do documento")
    subject: Optional[str] = Field(None, description="Assunto do documento")
    creator: Optional[str] = Field(None, description="Criador do documento")
    creation_date: Optional[datetime] = Field(None, description="Data de criação")
    modification_date: Optional[datetime] = Field(None, description="Data de modificação")
    file_size: int = Field(..., description="Tamanho do arquivo em bytes")

class AuditLogResponse(BaseModel):
    """Modelo para resposta de logs de auditoria"""
    logs: List[Dict[str, Any]] = Field(..., description="Lista de logs")
    total: int = Field(..., description="Total de logs")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Logs por página")

class StatsResponse(BaseModel):
    """Modelo para resposta de estatísticas"""
    total_requests: int = Field(..., description="Total de requisições")
    successful_requests: int = Field(..., description="Requisições bem-sucedidas")
    failed_requests: int = Field(..., description="Requisições falhadas")
    avg_processing_time: float = Field(..., description="Tempo médio de processamento")
    total_processing_time: float = Field(..., description="Tempo total de processamento")

# Modelos para compatibilidade com serviços existentes
class OCRResult(BaseModel):
    """Resultado do processamento OCR"""
    text: str = Field(..., description="Texto extraído")
    confidence: float = Field(..., description="Confiança do OCR")
    processing_time: float = Field(..., description="Tempo de processamento")
    page_count: Optional[int] = Field(None, description="Número de páginas processadas")

class ProcessingRequest(BaseModel):
    """Requisição de processamento (compatibilidade)"""
    document: Dict[str, Any] = Field(..., description="Dados do documento")
    enable_ocr: bool = Field(True, description="Habilitar OCR")
    enable_llm: bool = Field(True, description="Habilitar LLM")
    enable_matching: bool = Field(True, description="Habilitar matching")
    options: Optional[Dict[str, Any]] = Field(None, description="Opções adicionais")

class DocumentProcessingResult(BaseModel):
    """Resultado do processamento de documento (compatibilidade)"""
    document_id: str = Field(..., description="ID do documento")
    status: ProcessingStatus = Field(..., description="Status do processamento")
    ocr_result: Optional[OCRResult] = Field(None, description="Resultado do OCR")
    llm_analysis: Optional[Dict[str, Any]] = Field(None, description="Análise LLM")
    match_result: Optional[Dict[str, Any]] = Field(None, description="Resultado do matching")
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Data de atualização")

class APIResponse(BaseModel):
    """Resposta padrão da API (compatibilidade)"""
    success: bool = Field(..., description="Sucesso da operação")
    message: str = Field(..., description="Mensagem")
    data: Optional[Any] = Field(None, description="Dados da resposta")


# Novos modelos com validações mais robustas
class EnhancedTextAnalysisRequest(BaseModel):
    """Modelo aprimorado para análise de texto com validações robustas"""
    text: str = Field(
        ..., 
        min_length=1,
        max_length=50000,
        description="Texto para análise (1-50000 caracteres)"
    )
    language: Optional[LanguageCode] = Field(
        LanguageCode.PORTUGUESE, 
        description="Idioma do texto"
    )
    include_sentiment: bool = Field(True, description="Incluir análise de sentimento")
    include_keywords: bool = Field(True, description="Incluir extração de palavras-chave")
    include_entities: bool = Field(False, description="Incluir reconhecimento de entidades")
    max_keywords: int = Field(10, ge=1, le=50, description="Número máximo de palavras-chave")
    
    @validator('text')
    def validate_text_content(cls, v):
        """Valida se o texto não está vazio após limpeza"""
        if not v.strip():
            raise ValueError('Texto não pode estar vazio')
        return v.strip()


class EnhancedTextAnalysisResponse(BaseModel):
    """Resposta aprimorada para análise de texto"""
    original_text: str = Field(..., description="Texto original")
    language: LanguageCode = Field(..., description="Idioma detectado")
    word_count: PositiveInt = Field(..., description="Número de palavras")
    char_count: PositiveInt = Field(..., description="Número de caracteres")
    sentence_count: PositiveInt = Field(..., description="Número de sentenças")
    paragraph_count: PositiveInt = Field(..., description="Número de parágrafos")
    
    # Análise de sentimento
    sentiment: Optional[SentimentType] = Field(None, description="Sentimento detectado")
    sentiment_confidence: Optional[PositiveFloat] = Field(None, description="Confiança do sentimento")
    
    # Palavras-chave e entidades
    keywords: List[str] = Field(default_factory=list, description="Palavras-chave extraídas")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Entidades nomeadas")
    
    # Resumo e categorização
    summary: Optional[str] = Field(None, description="Resumo automático")
    categories: List[str] = Field(default_factory=list, description="Categorias identificadas")
    
    # Métricas de processamento
    processing_time: PositiveFloat = Field(..., description="Tempo de processamento em segundos")
    model_version: str = Field(..., description="Versão do modelo utilizado")
    
    class Config:
        """Configuração do modelo"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponse(BaseModel):
    """Modelo padronizado para respostas de erro"""
    error: bool = Field(True, description="Indica que é uma resposta de erro")
    error_code: ErrorCode = Field(..., description="Código do erro")
    message: str = Field(..., description="Mensagem de erro legível")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais do erro")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp do erro")
    request_id: Optional[str] = Field(None, description="ID da requisição para rastreamento")
    
    class Config:
        """Configuração do modelo"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FileUploadRequest(BaseModel):
    """Modelo para requisição de upload de arquivo com validações"""
    filename: str = Field(..., min_length=1, max_length=255, description="Nome do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    file_size: int = Field(..., ge=1, le=10*1024*1024, description="Tamanho em bytes (max 10MB)")
    enable_ocr: bool = Field(True, description="Habilitar processamento OCR")
    enable_nlp: bool = Field(True, description="Habilitar análise NLP")
    language_hint: Optional[LanguageCode] = Field(None, description="Dica de idioma do documento")
    
    @validator('filename')
    def validate_filename(cls, v):
        """Valida extensão do arquivo"""
        allowed_extensions = {'.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
        if not any(v.lower().endswith(ext) for ext in allowed_extensions):
            raise ValueError(f'Extensão não suportada. Permitidas: {", ".join(allowed_extensions)}')
        return v
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Valida tipo MIME"""
        allowed_types = {
            'application/pdf', 'text/plain', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/jpeg', 'image/png', 'image/jpg'
        }
        if v not in allowed_types:
            raise ValueError(f'Tipo MIME não suportado: {v}')
        return v


class SystemHealthResponse(BaseModel):
    """Resposta detalhada de health check do sistema"""
    status: str = Field(..., description="Status geral do sistema")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp da verificação")
    version: str = Field(..., description="Versão da API")
    environment: str = Field(..., description="Ambiente de execução")
    uptime_seconds: PositiveFloat = Field(..., description="Tempo de atividade em segundos")
    
    # Status dos serviços
    services: Dict[str, Dict[str, Any]] = Field(..., description="Status detalhado dos serviços")
    
    # Métricas do sistema
    system_metrics: Dict[str, Any] = Field(default_factory=dict, description="Métricas do sistema")
    
    class Config:
        """Configuração do modelo"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }