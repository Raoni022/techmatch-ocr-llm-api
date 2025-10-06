"""
Utilitários e funções auxiliares para a API TechMatch OCR+LLM

Este módulo contém funções utilitárias, decoradores e helpers
utilizados em toda a aplicação.
"""

import asyncio
import functools
import hashlib
import logging
import time
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from uuid import uuid4

import aiofiles
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.models import ErrorCode, ErrorResponse

logger = logging.getLogger(__name__)

# Type variables para funções genéricas
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


def generate_request_id() -> str:
    """
    Gera um ID único para requisições
    
    Returns:
        String com ID único baseado em timestamp e UUID
    """
    timestamp = int(time.time() * 1000)
    unique_id = str(uuid4())[:8]
    return f"req_{timestamp}_{unique_id}"


def generate_document_id() -> str:
    """
    Gera um ID único para documentos
    
    Returns:
        String com ID único para documento
    """
    return str(uuid4())


def calculate_file_hash(file_content: bytes) -> str:
    """
    Calcula hash SHA-256 do conteúdo do arquivo
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        
    Returns:
        Hash SHA-256 em formato hexadecimal
    """
    return hashlib.sha256(file_content).hexdigest()


def get_utc_timestamp() -> datetime:
    """
    Retorna timestamp UTC atual
    
    Returns:
        Datetime object com timezone UTC
    """
    return datetime.now(timezone.utc)


def format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho de arquivo em formato legível
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        String formatada (ex: "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Valida se a extensão do arquivo é permitida
    
    Args:
        filename: Nome do arquivo
        allowed_extensions: Lista de extensões permitidas
        
    Returns:
        True se extensão é válida, False caso contrário
    """
    if not filename:
        return False
    
    file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
    return f".{file_ext}" in [ext.lower() for ext in allowed_extensions]


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza nome de arquivo removendo caracteres perigosos
    
    Args:
        filename: Nome original do arquivo
        
    Returns:
        Nome sanitizado do arquivo
    """
    import re
    
    # Remove caracteres perigosos
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove espaços múltiplos e substitui por underscore
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Remove pontos no início/fim
    sanitized = sanitized.strip('.')
    
    # Limita tamanho
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_len = 255 - len(ext) - 1 if ext else 255
        sanitized = f"{name[:max_name_len]}.{ext}" if ext else name[:255]
    
    return sanitized or "unnamed_file"


def timing_decorator(func: F) -> F:
    """
    Decorator para medir tempo de execução de funções
    
    Args:
        func: Função a ser decorada
        
    Returns:
        Função decorada que loga tempo de execução
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executada em {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falhou após {execution_time:.4f}s: {e}")
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executada em {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} falhou após {execution_time:.4f}s: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def retry_decorator(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator para retry automático de funções
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay inicial entre tentativas
        backoff: Multiplicador do delay a cada tentativa
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} falhou após {max_retries} tentativas: {e}")
                        break
                    
                    logger.warning(f"{func.__name__} falhou (tentativa {attempt + 1}/{max_retries + 1}): {e}")
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} falhou após {max_retries} tentativas: {e}")
                        break
                    
                    logger.warning(f"{func.__name__} falhou (tentativa {attempt + 1}/{max_retries + 1}): {e}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


async def safe_file_write(filepath: str, content: Union[str, bytes], mode: str = 'w') -> bool:
    """
    Escreve arquivo de forma segura com tratamento de erros
    
    Args:
        filepath: Caminho do arquivo
        content: Conteúdo a ser escrito
        mode: Modo de abertura do arquivo
        
    Returns:
        True se sucesso, False caso contrário
    """
    try:
        async with aiofiles.open(filepath, mode) as f:
            await f.write(content)
        return True
    except Exception as e:
        logger.error(f"Erro ao escrever arquivo {filepath}: {e}")
        return False


async def safe_file_read(filepath: str, mode: str = 'r') -> Optional[Union[str, bytes]]:
    """
    Lê arquivo de forma segura com tratamento de erros
    
    Args:
        filepath: Caminho do arquivo
        mode: Modo de abertura do arquivo
        
    Returns:
        Conteúdo do arquivo ou None se erro
    """
    try:
        async with aiofiles.open(filepath, mode) as f:
            return await f.read()
    except Exception as e:
        logger.error(f"Erro ao ler arquivo {filepath}: {e}")
        return None


def create_error_response(
    error_code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Cria resposta de erro padronizada
    
    Args:
        error_code: Código do erro
        message: Mensagem de erro
        details: Detalhes adicionais
        status_code: Código HTTP
        request_id: ID da requisição
        
    Returns:
        JSONResponse com erro formatado
    """
    error_response = ErrorResponse(
        error_code=error_code,
        message=message,
        details=details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=status_code,
        content=error_response.dict()
    )


def extract_client_info(request: Request) -> Dict[str, Any]:
    """
    Extrai informações do cliente da requisição
    
    Args:
        request: Objeto Request do FastAPI
        
    Returns:
        Dicionário com informações do cliente
    """
    return {
        "ip_address": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
        "referer": request.headers.get("referer"),
        "accept_language": request.headers.get("accept-language"),
        "content_type": request.headers.get("content-type"),
        "content_length": request.headers.get("content-length"),
        "method": request.method,
        "url": str(request.url),
        "query_params": dict(request.query_params)
    }


class PerformanceMonitor:
    """
    Monitor de performance para operações
    """
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.metrics = {}
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Iniciando operação: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type is None:
            logger.info(f"Operação {self.operation_name} concluída em {duration:.4f}s")
        else:
            logger.error(f"Operação {self.operation_name} falhou após {duration:.4f}s: {exc_val}")
        
        self.metrics['duration'] = duration
        self.metrics['success'] = exc_type is None
    
    def add_metric(self, key: str, value: Any):
        """Adiciona métrica customizada"""
        self.metrics[key] = value
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas coletadas"""
        return self.metrics.copy()


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    Divide lista em chunks menores
    
    Args:
        lst: Lista a ser dividida
        chunk_size: Tamanho de cada chunk
        
    Returns:
        Lista de chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge múltiplos dicionários de forma segura
    
    Args:
        *dicts: Dicionários a serem merged
        
    Returns:
        Dicionário merged
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result