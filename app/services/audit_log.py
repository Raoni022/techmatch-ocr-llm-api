"""
Serviço de auditoria para logs em MongoDB
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)

class AuditLog:
    """Serviço de auditoria para persistir logs de uso em MongoDB"""
    
    def __init__(self, uri: str = None, db: str = "techmatch", col: str = "audit_logs"):
        """
        Inicializa conexão com MongoDB
        
        Args:
            uri: URI de conexão MongoDB (padrão: mongodb://mongodb:27017)
            db: Nome do banco de dados
            col: Nome da coleção
        """
        if uri is None:
            uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
        
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db]
        self.collection = self.db[col]
        
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
        Persiste log de auditoria no MongoDB
        
        Args:
            request_id: ID único da requisição
            user_id: ID do usuário
            query: Query de busca (opcional)
            resultado: Resultado do processamento (sem conteúdo binário)
            processing_time: Tempo de processamento em segundos
            error: Mensagem de erro (se houver)
            
        Returns:
            ID do documento inserido
        """
        try:
            doc = {
                "request_id": request_id,
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "query": query,
                "resultado": resultado,  # Metadados apenas, não o documento completo
                "processing_time": processing_time,
                "error": error,
                "status": "error" if error else "success"
            }
            
            result = await self.collection.insert_one(doc)
            logger.info(f"Log de auditoria salvo: {request_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Erro ao salvar log de auditoria: {e}")
            raise
    
    async def get_logs(
        self, 
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> list:
        """
        Recupera logs de auditoria com filtros
        
        Args:
            user_id: Filtrar por usuário
            start_date: Data inicial
            end_date: Data final
            limit: Limite de resultados
            skip: Pular registros (paginação)
            
        Returns:
            Lista de logs
        """
        try:
            filter_query = {}
            
            if user_id:
                filter_query["user_id"] = user_id
                
            if start_date or end_date:
                filter_query["timestamp"] = {}
                if start_date:
                    filter_query["timestamp"]["$gte"] = start_date
                if end_date:
                    filter_query["timestamp"]["$lte"] = end_date
            
            cursor = self.collection.find(filter_query).sort("timestamp", -1).skip(skip).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            # Converter ObjectId para string
            for log in logs:
                log["_id"] = str(log["_id"])
                
            return logs
            
        except Exception as e:
            logger.error(f"Erro ao recuperar logs: {e}")
            raise
    
    async def get_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém estatísticas de uso
        
        Args:
            user_id: Filtrar por usuário
            
        Returns:
            Estatísticas de uso
        """
        try:
            match_filter = {}
            if user_id:
                match_filter["user_id"] = user_id
            
            pipeline = [
                {"$match": match_filter},
                {"$group": {
                    "_id": None,
                    "total_requests": {"$sum": 1},
                    "successful_requests": {"$sum": {"$cond": [{"$eq": ["$status", "success"]}, 1, 0]}},
                    "failed_requests": {"$sum": {"$cond": [{"$eq": ["$status", "error"]}, 1, 0]}},
                    "avg_processing_time": {"$avg": "$processing_time"},
                    "total_processing_time": {"$sum": "$processing_time"}
                }}
            ]
            
            result = await self.collection.aggregate(pipeline).to_list(length=1)
            
            if result:
                stats = result[0]
                del stats["_id"]
                return stats
            else:
                return {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "failed_requests": 0,
                    "avg_processing_time": 0,
                    "total_processing_time": 0
                }
                
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            raise
    
    async def health_check(self) -> bool:
        """
        Verifica se a conexão com MongoDB está funcionando
        
        Returns:
            True se conectado, False caso contrário
        """
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"MongoDB não está acessível: {e}")
            return False

# Instância global do serviço de auditoria
audit_log = AuditLog()