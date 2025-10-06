"""
Configuração de logging para a aplicação
"""

import logging
import sys
from typing import Optional

def setup_logging(level: str = "INFO") -> None:
    """
    Configura o sistema de logging da aplicação
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configurar formato do log
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurar logging básico
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", encoding="utf-8")
        ]
    )
    
    # Configurar loggers específicos
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("pytesseract").setLevel(logging.WARNING)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Retorna um logger configurado
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name or __name__)