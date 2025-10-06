"""
Configurações da aplicação TechMatch OCR+LLM API

Este módulo centraliza todas as configurações da aplicação,
incluindo variáveis de ambiente, configurações de serviços
e parâmetros de segurança.
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic BaseSettings
    
    Todas as configurações podem ser sobrescritas via variáveis de ambiente
    """
    
    # Configurações básicas da aplicação
    APP_NAME: str = Field(default="TechMatch OCR+LLM API", description="Nome da aplicação")
    VERSION: str = Field(default="1.0.0", description="Versão da aplicação")
    ENVIRONMENT: str = Field(default="development", description="Ambiente de execução")
    DEBUG: bool = Field(default=True, description="Modo debug")
    
    # Configurações do servidor
    HOST: str = Field(default="0.0.0.0", description="Host do servidor")
    PORT: int = Field(default=12000, description="Porta do servidor")
    LOG_LEVEL: str = Field(default="INFO", description="Nível de log")
    
    # Configurações de segurança
    ALLOWED_HOSTS: str = Field(
        default="*", 
        description="Hosts permitidos para TrustedHostMiddleware"
    )
    CORS_ORIGINS: str = Field(
        default="*", 
        description="Origens permitidas para CORS"
    )
    
    # Configurações do MongoDB
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017", 
        description="URI de conexão do MongoDB"
    )
    MONGODB_DATABASE: str = Field(
        default="techmatch", 
        description="Nome do banco de dados MongoDB"
    )
    
    # Configurações do OCR
    TESSERACT_CMD: Optional[str] = Field(
        default=None, 
        description="Caminho para o executável do Tesseract"
    )
    OCR_LANGUAGES: str = Field(
        default="por,eng,spa", 
        description="Idiomas suportados pelo OCR"
    )
    
    # Configurações do NLP
    NLP_MODEL_NAME: str = Field(
        default="neuralmind/bert-base-portuguese-cased", 
        description="Modelo NLP para análise de texto"
    )
    SENTIMENT_MODEL: str = Field(
        default="cardiffnlp/twitter-roberta-base-sentiment-latest",
        description="Modelo para análise de sentimento"
    )
    
    # Configurações de processamento
    MAX_FILE_SIZE: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Tamanho máximo de arquivo em bytes"
    )
    MAX_BATCH_SIZE: int = Field(
        default=50, 
        description="Número máximo de arquivos por lote"
    )
    PROCESSING_TIMEOUT: int = Field(
        default=300,  # 5 minutos
        description="Timeout para processamento em segundos"
    )
    
    # Configurações de cache
    CACHE_TTL: int = Field(
        default=3600,  # 1 hora
        description="TTL do cache em segundos"
    )
    
    # Configurações de auditoria
    ENABLE_AUDIT_LOG: bool = Field(
        default=True, 
        description="Habilitar logs de auditoria"
    )
    AUDIT_LOG_COLLECTION: str = Field(
        default="audit_logs", 
        description="Coleção para logs de auditoria"
    )
    
    # Configurações de rate limiting
    RATE_LIMIT_REQUESTS: int = Field(
        default=100, 
        description="Número de requests por minuto por IP"
    )
    
    class Config:
        """Configurações do Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignora campos extras do .env


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações
    
    Usa LRU cache para evitar recarregar as configurações
    a cada chamada.
    """
    return Settings()


# Configurações específicas por ambiente
ENVIRONMENT_CONFIGS = {
    "development": {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "CORS_ORIGINS": ["*"],
        "ALLOWED_HOSTS": ["*"]
    },
    "testing": {
        "DEBUG": True,
        "LOG_LEVEL": "DEBUG",
        "MONGODB_DATABASE": "techmatch_test"
    },
    "staging": {
        "DEBUG": False,
        "LOG_LEVEL": "INFO",
        "CORS_ORIGINS": ["https://staging.techmatch.com"],
        "ALLOWED_HOSTS": ["staging.techmatch.com"]
    },
    "production": {
        "DEBUG": False,
        "LOG_LEVEL": "WARNING",
        "CORS_ORIGINS": ["https://techmatch.com"],
        "ALLOWED_HOSTS": ["techmatch.com", "api.techmatch.com"]
    }
}


def get_environment_config(environment: str) -> dict:
    """
    Retorna configurações específicas do ambiente
    
    Args:
        environment: Nome do ambiente (development, testing, staging, production)
        
    Returns:
        Dicionário com configurações do ambiente
    """
    return ENVIRONMENT_CONFIGS.get(environment, ENVIRONMENT_CONFIGS["development"])