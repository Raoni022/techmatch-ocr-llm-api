"""
Endpoints da API TechMatch OCR+LLM - Versão Completa
"""

import uuid
import time
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse

from app.models import (
    BatchRequest, BatchResponse, DocumentResult, ProcessingStatus,
    TextAnalysisRequest, TextAnalysisResponse, HealthResponse,
    SupportedLanguagesResponse, InfoExtractionResponse, PDFInfoResponse,
    DocumentType,
    AuditLogResponse, StatsResponse
)
from app.services.ocr import ocr_service
# from app.services.nlp_real import nlp_service  # Comentado para teste sem dependências pesadas
from app.services.nlp import nlp_service  # Usar mock para teste
from app.services.audit_log_mock import audit_log
from app.utils.pdf import pdf_utils
from app.utils.text import text_utils
from app.services.logging import get_logger

logger = get_logger(__name__)

# Mapeamento de idiomas: API (pt/en/es) -> Tesseract (por/eng/spa)
LANG_MAP = {"pt": "por", "en": "eng", "es": "spa", "por": "por", "eng": "eng", "spa": "spa"}

# Criar router
router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Verifica saúde da API e serviços
    """
    try:
        # Verificar MongoDB
        mongo_status = "healthy" if await audit_log.health_check() else "unhealthy"
        
        # Verificar serviços NLP
        nlp_status = "healthy" if hasattr(nlp_service, 'analyze_text') else "unhealthy"
        
        # Status geral
        overall_status = "healthy" if mongo_status == "healthy" else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={
                "mongodb": mongo_status,
                "nlp": nlp_status,
                "ocr": "healthy"
            }
        )
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services={
                "mongodb": "unknown",
                "nlp": "unknown",
                "ocr": "unknown"
            }
        )

@router.get("/supported-languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    Retorna idiomas suportados pela API
    """
    languages = [
        {"code": "pt", "name": "Português"},
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Español"}
    ]
    
    return SupportedLanguagesResponse(languages=languages)

@router.get("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(text: str, language: str = "pt"):
    """
    Analisa texto fornecido
    """
    try:
        start_time = time.time()
        
        # Análise básica
        word_count = len(text.split())
        char_count = len(text)
        
        # Usar NLP real
        summary = nlp_service.summarize_text(text)
        keywords = nlp_service.extract_keywords(text)
        sentiment_result = nlp_service.analyze_sentiment(text)
        categories = nlp_service.categorize_text(text)
        
        processing_time = time.time() - start_time
        
        # Log de auditoria (opcional)
        try:
            await audit_log.write_log(
                request_id=str(uuid.uuid4()),
                user_id="anonymous",
                query=None,
                resultado={
                    "type": "text_analysis",
                    "word_count": word_count,
                    "char_count": char_count,
                    "categories": categories
                },
                processing_time=processing_time
            )
        except Exception as e:
            logger.warning(f"Não foi possível salvar log de auditoria: {e}")
        
        return TextAnalysisResponse(
            original_text=text,
            language=language,
            word_count=word_count,
            char_count=char_count,
            summary=summary,
            keywords=keywords,
            sentiment=sentiment_result["sentiment"],
            categories=categories
        )
        
    except Exception as e:
        logger.error(f"Erro na análise de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/extract-info", response_model=InfoExtractionResponse)
async def extract_info(text: str):
    """
    Extrai informações estruturadas do texto
    """
    try:
        emails = text_utils.extract_emails(text)
        phones = text_utils.extract_phone_numbers(text)
        dates = text_utils.extract_dates(text)
        urls = text_utils.extract_urls(text)
        entities = []  # Implementar extração de entidades se necessário
        
        return InfoExtractionResponse(
            emails=emails,
            phones=phones,
            dates=dates,
            urls=urls,
            entities=entities
        )
        
    except Exception as e:
        logger.error(f"Erro na extração de informações: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-batch", 
    response_model=BatchResponse,
    responses={
        200: {
            "description": "Processamento concluído com sucesso",
            "content": {
                "application/json": {
                    "examples": {
                        "com_query": {
                            "summary": "Processamento com query - retorna ranking",
                            "description": "Quando uma query é fornecida, o sistema calcula scores de similaridade e ordena os documentos por relevância",
                            "value": {
                                "request_id": "req-123",
                                "user_id": "user-456", 
                                "query": "contratos de trabalho",
                                "total_documents": 2,
                                "successful_documents": 2,
                                "failed_documents": 0,
                                "results": [
                                    {
                                        "document_id": "doc-1",
                                        "filename": "contrato.pdf",
                                        "status": "completed",
                                        "extracted_text": "Contrato de trabalho...",
                                        "summary": "Documento sobre contrato de trabalho...",
                                        "similarity_score": 0.85,
                                        "justification": "Documento altamente relevante (score: 0.85) - contém informações relacionadas à query",
                                        "relevant_excerpts": ["contrato de trabalho", "cláusulas trabalhistas"],
                                        "processing_time": 2.1
                                    }
                                ],
                                "total_processing_time": 4.2,
                                "timestamp": "2024-01-15T10:30:00Z"
                            }
                        },
                        "sem_query": {
                            "summary": "Processamento sem query - apenas sumários",
                            "description": "Quando nenhuma query é fornecida, o sistema retorna apenas os sumários dos documentos sem scores de similaridade",
                            "value": {
                                "request_id": "req-789",
                                "user_id": "user-456",
                                "query": None,
                                "total_documents": 2,
                                "successful_documents": 2,
                                "failed_documents": 0,
                                "results": [
                                    {
                                        "document_id": "doc-2",
                                        "filename": "relatorio.pdf",
                                        "status": "completed",
                                        "extracted_text": "Relatório mensal...",
                                        "summary": "Relatório contendo dados mensais...",
                                        "similarity_score": None,
                                        "justification": None,
                                        "relevant_excerpts": None,
                                        "processing_time": 1.8
                                    }
                                ],
                                "total_processing_time": 3.6,
                                "timestamp": "2024-01-15T10:35:00Z"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def process_batch(
    request_id: str = Form(...),
    user_id: str = Form(...),
    query: Optional[str] = Form(None),
    language: str = Form("por"),
    files: List[UploadFile] = File(...)
):
    """
    Processa múltiplos documentos em lote
    
    **Dois modos de operação:**
    
    1. **Com query**: Retorna ranking com scores de similaridade
       - Calcula similaridade entre query e cada documento
       - Ordena resultados por relevância (maior score primeiro)
       - Inclui justificativas e trechos relevantes
    
    2. **Sem query**: Retorna apenas sumários dos documentos
       - Extrai texto e gera sumários
       - Não calcula scores de similaridade
       - Processamento mais rápido
    
    **Parâmetros:**
    - request_id: Identificador único da requisição
    - user_id: Identificador do usuário
    - query: Texto de busca (opcional)
    - language: Idioma para OCR (pt/en/es, padrão: por)
    - files: Lista de arquivos (PDF, imagens ou texto)
    """
    try:
        start_time = time.time()
        logger.info(f"Iniciando processamento em lote - Request: {request_id}, User: {user_id}")
        
        # Mapear idioma da API para Tesseract
        lang_param = str(language or "por").lower()
        tess_lang = LANG_MAP.get(lang_param, "por")
        
        # Determinar modo de processamento
        has_query = bool(query and query.strip())
        processing_mode = "ranking" if has_query else "summary_only"
        logger.info(f"Modo de processamento: {processing_mode}")
        
        results = []
        successful_docs = 0
        failed_docs = 0
        
        # Processar cada arquivo
        for file in files:
            doc_start_time = time.time()
            document_id = str(uuid.uuid4())
            
            try:
                # Ler conteúdo do arquivo
                content = await file.read()
                
                # Extrair texto via OCR
                extracted_text = ""
                
                if file.content_type == "application/pdf":
                    # Converter para base64 e usar o método assíncrono correto
                    b64_content = base64.b64encode(content).decode("utf-8")
                    ocr_result = await ocr_service.extract_text_from_document(
                        content=b64_content,
                        document_type=DocumentType.PDF,
                        language=tess_lang
                    )
                    extracted_text = ocr_result.text or ""
                elif file.content_type.startswith("image/"):
                    # Converter para base64 e usar o método assíncrono correto
                    b64_content = base64.b64encode(content).decode("utf-8")
                    ocr_result = await ocr_service.extract_text_from_document(
                        content=b64_content,
                        document_type=DocumentType.IMAGE,
                        language=tess_lang
                    )
                    extracted_text = ocr_result.text or ""
                else:
                    # Texto puro
                    extracted_text = content.decode('utf-8', errors="ignore")
                
                # Gerar resumo
                summary = nlp_service.summarize_text(extracted_text)
                
                # Calcular similaridade e justificativa APENAS se query fornecida
                similarity_score = None
                justification = None
                relevant_excerpts = None
                
                if has_query:
                    # Calcular similaridade
                    similarities = nlp_service.calculate_similarity(query, [extracted_text])
                    similarity_score = similarities[0] if similarities else 0.0
                    
                    # Encontrar trechos relevantes
                    relevant_excerpts = nlp_service.find_relevant_excerpts(query, extracted_text)
                    
                    # Gerar justificativa
                    if similarity_score > 0.7:
                        justification = f"Documento altamente relevante (score: {similarity_score:.2f}) - contém informações relacionadas à query"
                    elif similarity_score > 0.4:
                        justification = f"Documento moderadamente relevante (score: {similarity_score:.2f}) - possui algumas informações relacionadas"
                    else:
                        justification = f"Documento pouco relevante (score: {similarity_score:.2f}) - poucas informações relacionadas à query"
                
                doc_processing_time = time.time() - doc_start_time
                
                # Criar resultado do documento
                doc_result = DocumentResult(
                    document_id=document_id,
                    filename=file.filename,
                    status=ProcessingStatus.COMPLETED,
                    extracted_text=extracted_text,
                    summary=summary,
                    similarity_score=similarity_score,
                    justification=justification,
                    relevant_excerpts=relevant_excerpts,
                    processing_time=doc_processing_time,
                    error_message=None
                )
                
                results.append(doc_result)
                successful_docs += 1
                
                logger.info(f"Documento processado com sucesso: {file.filename}")
                
            except Exception as e:
                logger.error(f"Erro ao processar documento {file.filename}: {e}")
                
                doc_result = DocumentResult(
                    document_id=document_id,
                    filename=file.filename,
                    status=ProcessingStatus.FAILED,
                    extracted_text=None,
                    summary=None,
                    similarity_score=None,
                    justification=None,
                    relevant_excerpts=None,
                    processing_time=time.time() - doc_start_time,
                    error_message=str(e)
                )
                
                results.append(doc_result)
                failed_docs += 1
        
        # Ordenar resultados por similaridade APENAS se query fornecida
        if has_query:
            results.sort(key=lambda x: x.similarity_score or 0, reverse=True)
        
        total_processing_time = time.time() - start_time
        
        # Criar resposta
        batch_response = BatchResponse(
            request_id=request_id,
            user_id=user_id,
            query=query if has_query else None,
            total_documents=len(files),
            successful_documents=successful_docs,
            failed_documents=failed_docs,
            results=results,
            total_processing_time=total_processing_time,
            timestamp=datetime.utcnow()
        )
        
        # Log de auditoria (opcional)
        try:
            await audit_log.write_log(
                request_id=request_id,
                user_id=user_id,
                query=query if has_query else None,
                resultado={
                    "type": "batch_processing",
                    "total_documents": len(files),
                    "successful_documents": successful_docs,
                    "failed_documents": failed_docs,
                    "has_query": has_query,
                    "processing_mode": processing_mode
                },
                processing_time=total_processing_time
            )
        except Exception as e:
            logger.warning(f"Não foi possível salvar log de auditoria: {e}")
        
        logger.info(f"Processamento em lote concluído - Request: {request_id}")
        
        return batch_response
        
    except Exception as e:
        logger.error(f"Erro no processamento em lote: {e}")
        
        # Log de erro (opcional)
        try:
            await audit_log.write_log(
                request_id=request_id,
                user_id=user_id,
                query=query,
                resultado={},
                error=str(e)
            )
        except Exception as log_error:
            logger.warning(f"Não foi possível salvar log de erro: {log_error}")
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit-logs", response_model=AuditLogResponse)
async def get_audit_logs(
    user_id: Optional[str] = None,
    page: int = 1,
    per_page: int = 50
):
    """
    Recupera logs de auditoria
    """
    try:
        skip = (page - 1) * per_page
        logs = await audit_log.get_logs(
            user_id=user_id,
            limit=per_page,
            skip=skip
        )
        
        return AuditLogResponse(
            logs=logs,
            total=len(logs),
            page=page,
            per_page=per_page
        )
        
    except Exception as e:
        logger.error(f"Erro ao recuperar logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=StatsResponse)
async def get_stats(user_id: Optional[str] = None):
    """
    Obtém estatísticas de uso
    """
    try:
        stats = await audit_log.get_stats()
        
        return StatsResponse(
            total_requests=stats.get("total_requests", 0),
            successful_requests=stats.get("successful_requests", 0),
            failed_requests=stats.get("failed_requests", 0),
            avg_processing_time=stats.get("avg_processing_time", 0.0),
            total_processing_time=stats.get("total_processing_time", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf-info/{document_id}", response_model=PDFInfoResponse)
async def get_pdf_info(document_id: str):
    """
    Obtém informações de um PDF (placeholder - implementar se necessário)
    """
    # Esta rota seria implementada se houvesse necessidade de armazenar PDFs
    raise HTTPException(status_code=501, detail="Funcionalidade não implementada")

# Manter compatibilidade com rotas antigas
@router.post("/upload")
async def upload_file_legacy(
    file: UploadFile = File(...),
    enable_ocr: bool = Form(True),
    enable_llm: bool = Form(True)
):
    """
    Upload de arquivo individual (compatibilidade)
    """
    try:
        # Processar como batch de um único arquivo
        request_id = str(uuid.uuid4())
        user_id = "legacy_user"
        
        response = await process_batch(
            request_id=request_id,
            user_id=user_id,
            query=None,
            files=[file]
        )
        
        # Retornar resultado do primeiro (e único) documento
        if response.results:
            result = response.results[0]
            return {
                "success": True,
                "message": "Arquivo processado com sucesso",
                "data": {
                    "document_id": result.document_id,
                    "filename": result.filename,
                    "status": result.status,
                    "extracted_text": result.extracted_text,
                    "summary": result.summary,
                    "processing_time": result.processing_time
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Erro no processamento")
            
    except Exception as e:
        logger.error(f"Erro no upload legacy: {e}")
        raise HTTPException(status_code=500, detail=str(e))