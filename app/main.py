"""
TechMatch OCR+LLM API - Arquivo principal

API empresarial para processamento inteligente de documentos com OCR e análise por LLM.
Oferece funcionalidades de extração de texto, análise de sentimento, categorização
e processamento em lote com auditoria completa.

Author: TechMatch Development Team
Version: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from app.api import router
from app.services.logging import setup_logging
from app.config import get_settings

# Configurar logging
logger = logging.getLogger(__name__)
setup_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    logger.info("🚀 Iniciando TechMatch OCR+LLM API...")
    logger.info(f"📊 Ambiente: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug mode: {settings.DEBUG}")
    
    yield
    
    logger.info("🛑 Encerrando TechMatch OCR+LLM API...")


# Criar instância do FastAPI com configurações empresariais
app = FastAPI(
    title="TechMatch OCR+LLM API",
    description="""
    ## API Empresarial para Processamento Inteligente de Documentos
    
    Esta API oferece funcionalidades avançadas de:
    
    * **OCR (Optical Character Recognition)** - Extração de texto de documentos
    * **Análise de Sentimento** - Classificação emocional do conteúdo
    * **Extração de Entidades** - Identificação de informações estruturadas
    * **Processamento em Lote** - Análise de múltiplos documentos
    * **Sistema de Auditoria** - Rastreamento completo de operações
    * **Estatísticas em Tempo Real** - Métricas de performance e uso
    
    ### Idiomas Suportados
    - Português (pt)
    - Inglês (en) 
    - Espanhol (es)
    
    ### Formatos Suportados
    - PDF, TXT, DOC, DOCX, JPG, PNG
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "TechMatch Support",
        "email": "support@techmatch.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configurar middlewares de segurança
if settings.ALLOWED_HOSTS != "*":
    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=[settings.ALLOWED_HOSTS]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else [settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções não tratadas"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Ocorreu um erro interno no servidor",
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


# Incluir rotas da API
app.include_router(router, prefix="/api/v1", tags=["API v1"])


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Endpoint raiz da API
    
    Retorna informações básicas sobre a API, incluindo versão,
    status e links para documentação.
    """
    return {
        "service": "TechMatch OCR+LLM API",
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.ENVIRONMENT,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json"
        },
        "endpoints": {
            "health_check": "/api/v1/health",
            "text_analysis": "/api/v1/analyze-text",
            "file_upload": "/api/v1/upload",
            "batch_processing": "/api/v1/process-batch",
            "audit_logs": "/api/v1/audit-logs",
            "statistics": "/api/v1/stats"
        },
        "supported_languages": ["pt", "en", "es"],
        "supported_formats": ["PDF", "TXT", "DOC", "DOCX", "JPG", "PNG"]
    }


def create_app() -> FastAPI:
    """Factory function para criar a aplicação FastAPI"""
    return app


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        server_header=False,
        date_header=False
    )