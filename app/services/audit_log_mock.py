"""
Serviço de auditoria mock para testes sem MongoDB
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuditLog:
    """Serviço de auditoria mock para testes sem MongoDB"""
    
    def __init__(self, uri: str = None, db: str = "techmatch", col: str = "audit_logs"):
        """
        Inicializa mock do audit log
        """
        logger.info("Usando AuditLog mock (sem MongoDB)")
        
    async def write_log(
        self, 
        request_id: str, 
        user_id: str, 
        query: Optional[str], 
        resultado: Dict[str, Any],
        processing_time: Optional[float] = None,
        error: Optional[str] = None
    ) -> str:
        """
        Mock do log de auditoria
        """
        log_entry = {
            "request_id": request_id,
            "user_id": user_id,
            "query": query,
            "resultado": resultado,
            "processing_time": processing_time,
            "error": error,
            "timestamp": datetime.utcnow()
        }
        
        logger.info(f"Mock audit log: {log_entry}")
        return f"mock_log_{request_id}"
        
    async def health_check(self) -> bool:
        """Mock health check - sempre retorna True"""
        return True
        
    async def get_stats(self) -> Dict[str, Any]:
        """Mock stats"""
        return {
            "total_requests": 0,
            "total_users": 0,
            "avg_processing_time": 0.0
        }
    
    async def get_logs(self, user_id: str = None, limit: int = 100, skip: int = 0) -> list:
        """Mock get logs"""
        return [
            {
                "request_id": "mock_request_1",
                "user_id": user_id or "test_user",
                "query": "test query",
                "resultado": {"status": "success"},
                "processing_time": 0.1,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

# Instância global
audit_log = AuditLog()