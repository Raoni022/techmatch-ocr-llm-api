"""
Utilitários para processamento de texto
"""

import re
import unicodedata
from typing import List, Dict, Optional, Tuple
from app.services.logging import get_logger

logger = get_logger(__name__)

class TextUtils:
    """Utilitários para manipulação e processamento de texto"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpa e normaliza texto
        
        Args:
            text: Texto para limpar
            
        Returns:
            Texto limpo e normalizado
        """
        try:
            if not text:
                return ""
            
            # Normalizar unicode
            text = unicodedata.normalize('NFKD', text)
            
            # Remover caracteres de controle
            text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
            
            # Normalizar espaços em branco
            text = re.sub(r'\s+', ' ', text)
            
            # Remover espaços no início e fim
            text = text.strip()
            
            return text
            
        except Exception as e:
            logger.error(f"Erro ao limpar texto: {str(e)}")
            return text or ""
    
    @staticmethod
    def extract_emails(text: str) -> List[str]:
        """
        Extrai endereços de email do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de emails encontrados
        """
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            return list(set(emails))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair emails: {str(e)}")
            return []
    
    @staticmethod
    def extract_phone_numbers(text: str) -> List[str]:
        """
        Extrai números de telefone do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de telefones encontrados
        """
        try:
            # Padrões para telefones brasileiros
            patterns = [
                r'\(\d{2}\)\s*\d{4,5}-?\d{4}',  # (11) 99999-9999
                r'\d{2}\s*\d{4,5}-?\d{4}',      # 11 99999-9999
                r'\+55\s*\d{2}\s*\d{4,5}-?\d{4}', # +55 11 99999-9999
            ]
            
            phones = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                phones.extend(matches)
            
            return list(set(phones))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair telefones: {str(e)}")
            return []
    
    @staticmethod
    def extract_cpf_cnpj(text: str) -> Dict[str, List[str]]:
        """
        Extrai CPFs e CNPJs do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Dicionário com CPFs e CNPJs encontrados
        """
        try:
            # Padrão para CPF
            cpf_pattern = r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}'
            cpfs = re.findall(cpf_pattern, text)
            
            # Padrão para CNPJ
            cnpj_pattern = r'\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}'
            cnpjs = re.findall(cnpj_pattern, text)
            
            return {
                "cpfs": list(set(cpfs)),
                "cnpjs": list(set(cnpjs))
            }
            
        except Exception as e:
            logger.error(f"Erro ao extrair CPF/CNPJ: {str(e)}")
            return {"cpfs": [], "cnpjs": []}
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extrai URLs do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de URLs encontradas
        """
        try:
            # Padrão para URLs
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            urls = re.findall(url_pattern, text)
            return list(set(urls))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair URLs: {str(e)}")
            return []
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        Extrai datas do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de datas encontradas
        """
        try:
            # Padrões para datas
            patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',      # DD/MM/YYYY
                r'\d{1,2}-\d{1,2}-\d{4}',      # DD-MM-YYYY
                r'\d{4}-\d{1,2}-\d{1,2}',      # YYYY-MM-DD
                r'\d{1,2}\s+de\s+\w+\s+de\s+\d{4}', # DD de mês de YYYY
            ]
            
            dates = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                dates.extend(matches)
            
            return list(set(dates))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair datas: {str(e)}")
            return []
    
    @staticmethod
    def extract_monetary_values(text: str) -> List[str]:
        """
        Extrai valores monetários do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Lista de valores encontrados
        """
        try:
            # Padrões para valores monetários
            patterns = [
                r'R\$\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',  # R$ 1.000,00
                r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*reais?', # 1.000,00 reais
                r'US\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # US$ 1,000.00
            ]
            
            values = []
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                values.extend(matches)
            
            return list(set(values))  # Remover duplicatas
            
        except Exception as e:
            logger.error(f"Erro ao extrair valores monetários: {str(e)}")
            return []
    
    @staticmethod
    def calculate_readability_score(text: str) -> Dict[str, float]:
        """
        Calcula métricas de legibilidade do texto
        
        Args:
            text: Texto para analisar
            
        Returns:
            Dicionário com métricas de legibilidade
        """
        try:
            if not text:
                return {"words": 0, "sentences": 0, "avg_words_per_sentence": 0, "complexity": 0}
            
            # Contar palavras
            words = len(text.split())
            
            # Contar frases
            sentences = len(re.split(r'[.!?]+', text))
            
            # Média de palavras por frase
            avg_words_per_sentence = words / sentences if sentences > 0 else 0
            
            # Calcular complexidade (baseado no tamanho médio das palavras)
            word_lengths = [len(word) for word in text.split()]
            avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
            
            # Score de complexidade (0-1, onde 1 é mais complexo)
            complexity = min(1.0, (avg_word_length - 3) / 7)  # Normalizar entre 3-10 caracteres
            
            return {
                "words": words,
                "sentences": sentences,
                "avg_words_per_sentence": round(avg_words_per_sentence, 2),
                "avg_word_length": round(avg_word_length, 2),
                "complexity": round(complexity, 2)
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular legibilidade: {str(e)}")
            return {"words": 0, "sentences": 0, "avg_words_per_sentence": 0, "complexity": 0}
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> List[Tuple[str, int]]:
        """
        Extrai palavras-chave mais frequentes do texto
        
        Args:
            text: Texto para analisar
            max_keywords: Número máximo de palavras-chave
            
        Returns:
            Lista de tuplas (palavra, frequência)
        """
        try:
            if not text:
                return []
            
            # Limpar e normalizar texto
            clean_text = TextUtils.clean_text(text.lower())
            
            # Remover pontuação e dividir em palavras
            words = re.findall(r'\b[a-záàâãéêíóôõúç]+\b', clean_text)
            
            # Stop words básicas em português
            stop_words = {
                'a', 'o', 'e', 'de', 'da', 'do', 'em', 'um', 'uma', 'para', 'com', 'por',
                'que', 'se', 'na', 'no', 'as', 'os', 'das', 'dos', 'ao', 'à', 'pelo',
                'pela', 'pelos', 'pelas', 'este', 'esta', 'estes', 'estas', 'esse',
                'essa', 'esses', 'essas', 'aquele', 'aquela', 'aqueles', 'aquelas',
                'seu', 'sua', 'seus', 'suas', 'meu', 'minha', 'meus', 'minhas',
                'nosso', 'nossa', 'nossos', 'nossas', 'vosso', 'vossa', 'vossos',
                'vossas', 'dele', 'dela', 'deles', 'delas', 'mais', 'menos', 'muito',
                'muita', 'muitos', 'muitas', 'pouco', 'pouca', 'poucos', 'poucas',
                'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras',
                'mesmo', 'mesma', 'mesmos', 'mesmas', 'também', 'ainda', 'já', 'só',
                'apenas', 'mas', 'porém', 'contudo', 'entretanto', 'todavia', 'quando',
                'onde', 'como', 'porque', 'porquê', 'qual', 'quais', 'quanto', 'quanta',
                'quantos', 'quantas', 'quem', 'ser', 'estar', 'ter', 'haver', 'fazer',
                'dizer', 'dar', 'ver', 'saber', 'poder', 'querer', 'ir', 'vir', 'ficar'
            }
            
            # Filtrar palavras muito curtas e stop words
            filtered_words = [
                word for word in words 
                if len(word) > 2 and word not in stop_words
            ]
            
            # Contar frequência
            word_freq = {}
            for word in filtered_words:
                word_freq[word] = word_freq.get(word, 0) + 1
            
            # Ordenar por frequência e retornar top keywords
            sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {str(e)}")
            return []

# Instância global dos utilitários
text_utils = TextUtils()