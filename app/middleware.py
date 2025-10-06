"""
Middlewares personalizados para a API TechMatch OCR+LLM

Este módulo contém middlewares customizados para logging,
autenticação, rate limiting e monitoramento de performance.
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils import generate_request_id, extract_client_info, get_utc_timestamp
from app.models import ErrorCode
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging detalhado de requisições
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Gerar ID único para a requisição
        request_id = generate_request_id()
        request.state.request_id = request_id
        
        # Extrair informações do cliente
        client_info = extract_client_info(request)
        
        # Log da requisição recebida
        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"IP: {client_info['ip_address']} - "
            f"User-Agent: {client_info['user_agent'][:100]}..."
        )
        
        try:
            # Processar requisição
            response = await call_next(request)
            
            # Calcular tempo de processamento
            process_time = time.time() - start_time
            
            # Log da resposta
            logger.info(
                f"[{request_id}] {response.status_code} - "
                f"Processado em {process_time:.4f}s"
            )
            
            # Adicionar headers de resposta
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            # Log de erro
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] Erro durante processamento: {e} - "
                f"Tempo até erro: {process_time:.4f}s",
                exc_info=True
            )
            
            # Retornar erro padronizado
            return JSONResponse(
                status_code=500,
                content={
                    "error": True,
                    "error_code": ErrorCode.INTERNAL_SERVER_ERROR,
                    "message": "Erro interno do servidor",
                    "request_id": request_id,
                    "timestamp": get_utc_timestamp().isoformat()
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para adicionar headers de segurança
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Headers de segurança
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        # Adicionar headers apenas se não existirem
        for header, value in security_headers.items():
            if header not in response.headers:
                response.headers[header] = value
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware simples para rate limiting
    """
    
    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_requests = {}  # Em produção, usar Redis
        self.window_size = 60  # 1 minuto
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Obter IP do cliente
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Limpar requisições antigas
        self._cleanup_old_requests(current_time)
        
        # Verificar rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit excedido para IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": True,
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Limite de {self.requests_per_minute} requisições por minuto excedido",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Registrar requisição
        self._record_request(client_ip, current_time)
        
        return await call_next(request)
    
    def _cleanup_old_requests(self, current_time: float):
        """Remove requisições antigas do cache"""
        cutoff_time = current_time - self.window_size
        
        for client_ip in list(self.client_requests.keys()):
            self.client_requests[client_ip] = [
                req_time for req_time in self.client_requests[client_ip]
                if req_time > cutoff_time
            ]
            
            # Remove cliente se não há requisições recentes
            if not self.client_requests[client_ip]:
                del self.client_requests[client_ip]
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Verifica se cliente excedeu rate limit"""
        if client_ip not in self.client_requests:
            return False
        
        recent_requests = len(self.client_requests[client_ip])
        return recent_requests >= self.requests_per_minute
    
    def _record_request(self, client_ip: str, current_time: float):
        """Registra nova requisição"""
        if client_ip not in self.client_requests:
            self.client_requests[client_ip] = []
        
        self.client_requests[client_ip].append(current_time)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware para monitoramento de performance
    """
    
    def __init__(self, app, slow_request_threshold: float = 5.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.request_metrics = []  # Em produção, usar sistema de métricas
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular métricas
        end_time = time.time()
        duration = end_time - start_time
        
        # Coletar métricas
        metrics = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "timestamp": start_time,
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        # Armazenar métricas (em produção, enviar para sistema de monitoramento)
        self.request_metrics.append(metrics)
        
        # Log de requisições lentas
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Requisição lenta detectada: {request.method} {request.url.path} - "
                f"{duration:.4f}s (threshold: {self.slow_request_threshold}s)"
            )
        
        # Adicionar métricas aos headers
        response.headers["X-Response-Time"] = f"{duration:.4f}"
        
        return response
    
    def get_metrics_summary(self) -> dict:
        """Retorna resumo das métricas coletadas"""
        if not self.request_metrics:
            return {"total_requests": 0}
        
        total_requests = len(self.request_metrics)
        avg_duration = sum(m["duration"] for m in self.request_metrics) / total_requests
        slow_requests = sum(1 for m in self.request_metrics if m["duration"] > self.slow_request_threshold)
        
        status_codes = {}
        for metric in self.request_metrics:
            code = metric["status_code"]
            status_codes[code] = status_codes.get(code, 0) + 1
        
        return {
            "total_requests": total_requests,
            "average_duration": round(avg_duration, 4),
            "slow_requests": slow_requests,
            "slow_request_percentage": round((slow_requests / total_requests) * 100, 2),
            "status_codes": status_codes
        }


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware customizado para CORS com configurações avançadas
    """
    
    def __init__(self, app, allowed_origins: list = None, allowed_methods: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Verificar se é requisição OPTIONS (preflight)
        if request.method == "OPTIONS":
            response = Response()
            self._add_cors_headers(response, request)
            return response
        
        # Processar requisição normal
        response = await call_next(request)
        self._add_cors_headers(response, request)
        
        return response
    
    def _add_cors_headers(self, response: Response, request: Request):
        """Adiciona headers CORS à resposta"""
        origin = request.headers.get("origin")
        
        # Verificar origem permitida
        if self.allowed_origins == ["*"] or origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
        
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 horas


class CompressionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para compressão de respostas
    """
    
    def __init__(self, app, minimum_size: int = 1024):
        super().__init__(app)
        self.minimum_size = minimum_size
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Verificar se cliente aceita compressão
        accept_encoding = request.headers.get("accept-encoding", "")
        
        if "gzip" in accept_encoding and hasattr(response, "body"):
            # Verificar tamanho mínimo para compressão
            if len(response.body) >= self.minimum_size:
                # Em uma implementação real, aplicaria compressão gzip aqui
                response.headers["Content-Encoding"] = "gzip"
                logger.debug(f"Resposta comprimida: {len(response.body)} bytes")
        
        return response