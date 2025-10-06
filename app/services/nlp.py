"""
Serviço de NLP/LLM (Natural Language Processing / Large Language Model)
"""

import time
import re
from typing import List, Dict, Any, Optional
# from app.models import LLMAnalysis  # Modelo não existe, criar mock
from app.services.logging import get_logger

logger = get_logger(__name__)

class NLPService:
    """Serviço para análise de texto usando NLP/LLM"""
    
    def __init__(self):
        self.categories = [
            "Contrato", "Relatório", "Proposta", "Documentação Técnica",
            "Correspondência", "Formulário", "Certificado", "Outros"
        ]
        
    async def analyze_text(self, text: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analisa texto usando técnicas de NLP/LLM
        
        Args:
            text: Texto para análise
            options: Opções adicionais para análise
            
        Returns:
            LLMAnalysis com os resultados da análise
        """
        start_time = time.time()
        
        try:
            logger.info(f"Iniciando análise NLP de texto com {len(text)} caracteres")
            
            # Análise básica do texto
            summary = await self._generate_summary(text)
            key_points = await self._extract_key_points(text)
            sentiment = await self._analyze_sentiment(text)
            categories = await self._categorize_text(text)
            confidence = await self._calculate_confidence(text, summary, key_points)
            
            processing_time = time.time() - start_time
            
            logger.info(f"Análise NLP concluída em {processing_time:.2f}s")
            
            return {
                "summary": summary,
                "key_points": key_points,
                "sentiment": sentiment,
                "categories": categories,
                "confidence": confidence,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Erro na análise NLP: {str(e)}")
            processing_time = time.time() - start_time
            
            return {
                "summary": "Erro na análise do texto",
                "key_points": [],
                "sentiment": "neutro",
                "categories": ["Outros"],
                "confidence": 0.0,
                "processing_time": processing_time
            }
    
    def summarize_text(self, text: str) -> str:
        """Gera resumo do texto (método público)"""
        try:
            # Implementação simplificada - em produção usaria um modelo LLM real
            sentences = self._split_sentences(text)
            
            if len(sentences) <= 3:
                return text[:500] + "..." if len(text) > 500 else text
            
            # Selecionar primeiras e últimas frases como resumo básico
            summary_sentences = sentences[:2] + sentences[-1:]
            summary = " ".join(summary_sentences)
            
            return summary[:500] + "..." if len(summary) > 500 else summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extrai palavras-chave do texto"""
        try:
            # Implementação simplificada - em produção usaria TF-IDF ou modelos mais avançados
            import re
            from collections import Counter
            
            # Remover pontuação e converter para minúsculas
            words = re.findall(r'\b[a-záàâãéêíóôõúç]{3,}\b', text.lower())
            
            # Palavras comuns para filtrar (stop words básicas)
            stop_words = {'que', 'para', 'com', 'uma', 'por', 'são', 'dos', 'das', 'como', 'mais', 'foi', 'ser', 'tem', 'ter', 'seu', 'sua', 'seus', 'suas', 'este', 'esta', 'estes', 'estas', 'isso', 'isto', 'aqui', 'ali', 'onde', 'quando', 'como', 'porque', 'mas', 'também', 'ainda', 'apenas', 'muito', 'bem', 'todo', 'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras'}
            
            # Filtrar stop words e contar frequência
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            word_counts = Counter(filtered_words)
            
            # Retornar as palavras mais frequentes
            keywords = [word for word, count in word_counts.most_common(max_keywords)]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erro ao extrair palavras-chave: {str(e)}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analisa o sentimento do texto"""
        try:
            # Implementação simplificada - em produção usaria modelos de sentiment analysis
            positive_words = {'bom', 'ótimo', 'excelente', 'positivo', 'sucesso', 'qualidade', 'garantia', 'satisfação', 'aprovado', 'aceito', 'acordo', 'benefício', 'vantagem', 'lucro', 'ganho'}
            negative_words = {'ruim', 'péssimo', 'negativo', 'problema', 'erro', 'falha', 'defeito', 'reclamação', 'insatisfação', 'rejeitado', 'cancelado', 'perda', 'prejuízo', 'dano'}
            
            words = text.lower().split()
            positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
            negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))
            
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                sentiment = "neutral"
                confidence = 0.5
            elif positive_count > negative_count:
                sentiment = "positive"
                confidence = min(0.9, 0.5 + (positive_count - negative_count) / len(words))
            elif negative_count > positive_count:
                sentiment = "negative"
                confidence = min(0.9, 0.5 + (negative_count - positive_count) / len(words))
            else:
                sentiment = "neutral"
                confidence = 0.5
            
            return {
                "sentiment": sentiment,
                "confidence": round(confidence, 2),
                "positive_indicators": positive_count,
                "negative_indicators": negative_count
            }
            
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "positive_indicators": 0,
                "negative_indicators": 0
            }
    
    def categorize_text(self, text: str) -> List[Dict[str, Any]]:
        """Categoriza o texto em diferentes tipos de documento"""
        try:
            categories = []
            text_lower = text.lower()
            
            # Definir padrões para diferentes categorias
            category_patterns = {
                "contrato": ["contrato", "acordo", "prestação", "serviços", "cláusula", "prazo", "valor", "pagamento"],
                "relatório": ["relatório", "análise", "dados", "resultado", "conclusão", "período", "mensal", "anual"],
                "fatura": ["fatura", "nota fiscal", "cobrança", "vencimento", "total", "imposto", "desconto"],
                "correspondência": ["carta", "email", "comunicado", "informamos", "solicitamos", "atenciosamente"],
                "jurídico": ["processo", "tribunal", "advogado", "lei", "artigo", "código", "jurisprudência"],
                "técnico": ["especificação", "manual", "procedimento", "configuração", "sistema", "software"],
                "financeiro": ["balanço", "demonstrativo", "receita", "despesa", "lucro", "investimento"]
            }
            
            # Calcular score para cada categoria
            for category, keywords in category_patterns.items():
                matches = sum(1 for keyword in keywords if keyword in text_lower)
                if matches > 0:
                    confidence = min(0.95, matches / len(keywords))
                    categories.append({
                        "category": category,
                        "confidence": round(confidence, 2),
                        "matches": matches
                    })
            
            # Ordenar por confiança
            categories.sort(key=lambda x: x["confidence"], reverse=True)
            
            # Se nenhuma categoria foi identificada, retornar "geral"
            if not categories:
                return ["geral"]
            
            # Retornar apenas os nomes das categorias (top 3)
            return [cat["category"] for cat in categories[:3]]
            
        except Exception as e:
            logger.error(f"Erro ao categorizar texto: {str(e)}")
            return ["geral"]
    
    def calculate_similarity(self, query: str, texts: List[str]) -> List[float]:
        """Calcula similaridade entre query e textos"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Preparar todos os textos (query + textos para comparar)
            all_texts = [query] + texts
            
            # Criar vetorizador TF-IDF
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words=None,  # Não temos stop words em português no sklearn
                max_features=1000
            )
            
            # Vetorizar textos
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            
            # Calcular similaridade coseno entre query (primeiro item) e outros textos
            query_vector = tfidf_matrix[0:1]
            text_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(query_vector, text_vectors)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {str(e)}")
            # Retornar similaridade padrão baseada em palavras comuns
            similarities = []
            query_words = set(query.lower().split())
            
            for text in texts:
                text_words = set(text.lower().split())
                common_words = query_words.intersection(text_words)
                similarity = len(common_words) / max(len(query_words), len(text_words), 1)
                similarities.append(min(similarity, 1.0))
            
            return similarities
    
    def find_relevant_excerpts(self, query: str, text: str, max_excerpts: int = 3) -> List[str]:
        """Encontra trechos relevantes do texto baseado na query"""
        try:
            # Dividir texto em sentenças
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if not sentences:
                return []
            
            # Calcular similaridade de cada sentença com a query
            similarities = self.calculate_similarity(query, sentences)
            
            # Criar lista de sentenças com suas similaridades
            sentence_scores = list(zip(sentences, similarities))
            
            # Ordenar por similaridade (maior primeiro)
            sentence_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Retornar os trechos mais relevantes
            relevant_excerpts = []
            for sentence, score in sentence_scores[:max_excerpts]:
                if score > 0.1:  # Threshold mínimo de similaridade
                    relevant_excerpts.append(sentence.strip() + '.')
            
            return relevant_excerpts
            
        except Exception as e:
            logger.error(f"Erro ao encontrar trechos relevantes: {str(e)}")
            # Fallback: retornar primeiras sentenças que contenham palavras da query
            query_words = set(query.lower().split())
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            relevant = []
            for sentence in sentences[:10]:  # Verificar apenas primeiras 10 sentenças
                sentence_words = set(sentence.lower().split())
                if query_words.intersection(sentence_words):
                    relevant.append(sentence.strip() + '.')
                    if len(relevant) >= max_excerpts:
                        break
            
            return relevant
    
    async def _generate_summary(self, text: str) -> str:
        """Gera resumo do texto"""
        try:
            # Implementação simplificada - em produção usaria um modelo LLM real
            sentences = self._split_sentences(text)
            
            if len(sentences) <= 3:
                return text[:500] + "..." if len(text) > 500 else text
            
            # Selecionar primeiras e últimas frases como resumo básico
            summary_sentences = sentences[:2] + sentences[-1:]
            summary = " ".join(summary_sentences)
            
            return summary[:500] + "..." if len(summary) > 500 else summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo: {str(e)}")
            return text[:200] + "..." if len(text) > 200 else text
    
    async def _extract_key_points(self, text: str) -> List[str]:
        """Extrai pontos principais do texto"""
        try:
            key_points = []
            
            # Procurar por padrões que indicam pontos importantes
            patterns = [
                r'(?:importante|relevante|destaque|principal).*?[.!?]',
                r'(?:objetivo|meta|finalidade).*?[.!?]',
                r'(?:resultado|conclusão|resumo).*?[.!?]',
                r'(?:\d+[\.\)]\s+.*?[.!?])',  # Listas numeradas
                r'(?:•\s+.*?[.!?])',  # Listas com bullets
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
                for match in matches[:3]:  # Limitar a 3 matches por padrão
                    clean_match = re.sub(r'\s+', ' ', match.strip())
                    if len(clean_match) > 20 and clean_match not in key_points:
                        key_points.append(clean_match)
            
            # Se não encontrou pontos específicos, usar primeiras frases
            if not key_points:
                sentences = self._split_sentences(text)
                key_points = sentences[:3]
            
            return key_points[:5]  # Máximo 5 pontos principais
            
        except Exception as e:
            logger.error(f"Erro ao extrair pontos principais: {str(e)}")
            return []
    
    async def _analyze_sentiment(self, text: str) -> str:
        """Analisa sentimento do texto"""
        try:
            # Implementação simplificada - em produção usaria modelo de sentimento
            positive_words = [
                'bom', 'ótimo', 'excelente', 'positivo', 'sucesso', 'aprovado',
                'satisfatório', 'adequado', 'eficiente', 'qualidade'
            ]
            
            negative_words = [
                'ruim', 'péssimo', 'negativo', 'problema', 'erro', 'falha',
                'inadequado', 'insatisfatório', 'defeito', 'rejeitado'
            ]
            
            text_lower = text.lower()
            
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                return "positivo"
            elif negative_count > positive_count:
                return "negativo"
            else:
                return "neutro"
                
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {str(e)}")
            return "neutro"
    
    async def _categorize_text(self, text: str) -> List[str]:
        """Categoriza o texto"""
        try:
            text_lower = text.lower()
            detected_categories = []
            
            # Palavras-chave para cada categoria
            category_keywords = {
                "Contrato": ["contrato", "acordo", "cláusula", "termo", "condição"],
                "Relatório": ["relatório", "análise", "dados", "resultado", "estatística"],
                "Proposta": ["proposta", "orçamento", "cotação", "oferta", "projeto"],
                "Documentação Técnica": ["manual", "especificação", "técnico", "procedimento"],
                "Correspondência": ["carta", "email", "comunicado", "ofício", "memorando"],
                "Formulário": ["formulário", "cadastro", "inscrição", "solicitação"],
                "Certificado": ["certificado", "diploma", "atestado", "comprovante"]
            }
            
            for category, keywords in category_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    detected_categories.append(category)
            
            # Se nenhuma categoria foi detectada, usar "Outros"
            if not detected_categories:
                detected_categories.append("Outros")
            
            return detected_categories
            
        except Exception as e:
            logger.error(f"Erro na categorização: {str(e)}")
            return ["Outros"]
    
    async def _calculate_confidence(self, text: str, summary: str, key_points: List[str]) -> float:
        """Calcula confiança da análise"""
        try:
            confidence = 0.5  # Base
            
            # Aumentar confiança baseado no tamanho do texto
            if len(text) > 100:
                confidence += 0.2
            if len(text) > 500:
                confidence += 0.1
            
            # Aumentar confiança se conseguiu extrair informações
            if summary and len(summary) > 50:
                confidence += 0.1
            if key_points and len(key_points) > 0:
                confidence += 0.1
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.error(f"Erro ao calcular confiança: {str(e)}")
            return 0.5
    
    def _split_sentences(self, text: str) -> List[str]:
        """Divide texto em frases"""
        # Implementação simples de divisão de frases
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def get_supported_categories(self) -> List[str]:
        """Retorna categorias suportadas"""
        return self.categories.copy()

# Instância global do serviço
nlp_service = NLPService()