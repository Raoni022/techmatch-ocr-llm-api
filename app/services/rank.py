"""
Serviço de Ranking/Matching
"""

import time
from typing import List, Dict, Any, Optional
from app.models import MatchResult, LLMAnalysis, OCRResult
from app.services.logging import get_logger

logger = get_logger(__name__)

class RankingService:
    """Serviço para ranking e matching de documentos"""
    
    def __init__(self):
        self.similarity_threshold = 0.3
        
    async def calculate_matches(
        self, 
        ocr_result: OCRResult, 
        llm_analysis: LLMAnalysis,
        reference_documents: Optional[List[Dict[str, Any]]] = None
    ) -> MatchResult:
        """
        Calcula matches e ranking para um documento
        
        Args:
            ocr_result: Resultado do OCR
            llm_analysis: Análise do LLM
            reference_documents: Documentos de referência para comparação
            
        Returns:
            MatchResult com score e matches
        """
        start_time = time.time()
        
        try:
            logger.info("Iniciando cálculo de matches e ranking")
            
            # Se não há documentos de referência, usar dados mock
            if not reference_documents:
                reference_documents = self._get_mock_reference_documents()
            
            matches = []
            
            for ref_doc in reference_documents:
                similarity_score = await self._calculate_similarity(
                    ocr_result, llm_analysis, ref_doc
                )
                
                if similarity_score >= self.similarity_threshold:
                    matches.append({
                        "document_id": ref_doc.get("id", "unknown"),
                        "title": ref_doc.get("title", "Documento sem título"),
                        "similarity_score": similarity_score,
                        "matching_categories": self._find_matching_categories(
                            llm_analysis.categories, ref_doc.get("categories", [])
                        ),
                        "confidence": similarity_score * 0.9  # Ajustar confiança
                    })
            
            # Ordenar matches por score
            matches.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # Calcular score geral
            overall_score = await self._calculate_overall_score(matches, llm_analysis)
            
            # Criar ranking
            ranking = [match["document_id"] for match in matches]
            
            processing_time = time.time() - start_time
            logger.info(f"Matching concluído em {processing_time:.2f}s com {len(matches)} matches")
            
            return MatchResult(
                score=overall_score,
                matches=matches,
                ranking=ranking
            )
            
        except Exception as e:
            logger.error(f"Erro no cálculo de matches: {str(e)}")
            return MatchResult(
                score=0.0,
                matches=[],
                ranking=[]
            )
    
    async def _calculate_similarity(
        self, 
        ocr_result: OCRResult, 
        llm_analysis: LLMAnalysis, 
        reference_doc: Dict[str, Any]
    ) -> float:
        """Calcula similaridade entre documento atual e referência"""
        try:
            similarity_score = 0.0
            
            # Similaridade baseada em categorias (peso 40%)
            category_similarity = self._calculate_category_similarity(
                llm_analysis.categories, reference_doc.get("categories", [])
            )
            similarity_score += category_similarity * 0.4
            
            # Similaridade baseada em palavras-chave (peso 30%)
            keyword_similarity = self._calculate_keyword_similarity(
                ocr_result.text, reference_doc.get("content", "")
            )
            similarity_score += keyword_similarity * 0.3
            
            # Similaridade baseada em sentimento (peso 20%)
            sentiment_similarity = self._calculate_sentiment_similarity(
                llm_analysis.sentiment, reference_doc.get("sentiment", "neutro")
            )
            similarity_score += sentiment_similarity * 0.2
            
            # Bonus por confiança do OCR (peso 10%)
            confidence_bonus = ocr_result.confidence * 0.1
            similarity_score += confidence_bonus
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade: {str(e)}")
            return 0.0
    
    def _calculate_category_similarity(self, categories1: List[str], categories2: List[str]) -> float:
        """Calcula similaridade entre categorias"""
        if not categories1 or not categories2:
            return 0.0
        
        # Interseção das categorias
        common_categories = set(categories1) & set(categories2)
        total_categories = set(categories1) | set(categories2)
        
        if not total_categories:
            return 0.0
        
        return len(common_categories) / len(total_categories)
    
    def _calculate_keyword_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade baseada em palavras-chave"""
        try:
            # Implementação simplificada - em produção usaria TF-IDF ou embeddings
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            # Remover palavras muito comuns (stop words básicas)
            stop_words = {'o', 'a', 'de', 'da', 'do', 'e', 'em', 'um', 'uma', 'para', 'com', 'por'}
            words1 = words1 - stop_words
            words2 = words2 - stop_words
            
            if not words1 or not words2:
                return 0.0
            
            common_words = words1 & words2
            total_words = words1 | words2
            
            return len(common_words) / len(total_words)
            
        except Exception as e:
            logger.error(f"Erro ao calcular similaridade de palavras-chave: {str(e)}")
            return 0.0
    
    def _calculate_sentiment_similarity(self, sentiment1: str, sentiment2: str) -> float:
        """Calcula similaridade de sentimento"""
        if sentiment1 == sentiment2:
            return 1.0
        elif sentiment1 == "neutro" or sentiment2 == "neutro":
            return 0.5
        else:
            return 0.0
    
    def _find_matching_categories(self, categories1: List[str], categories2: List[str]) -> List[str]:
        """Encontra categorias em comum"""
        return list(set(categories1) & set(categories2))
    
    async def _calculate_overall_score(self, matches: List[Dict[str, Any]], llm_analysis: LLMAnalysis) -> float:
        """Calcula score geral do documento"""
        if not matches:
            return 0.0
        
        # Score baseado no melhor match
        best_match_score = matches[0]["similarity_score"] if matches else 0.0
        
        # Ajustar baseado na confiança da análise LLM
        adjusted_score = best_match_score * llm_analysis.confidence
        
        return min(1.0, adjusted_score)
    
    def _get_mock_reference_documents(self) -> List[Dict[str, Any]]:
        """Retorna documentos de referência mock para demonstração"""
        return [
            {
                "id": "doc_001",
                "title": "Contrato de Prestação de Serviços",
                "categories": ["Contrato"],
                "content": "contrato prestação serviços cláusulas condições pagamento",
                "sentiment": "neutro"
            },
            {
                "id": "doc_002", 
                "title": "Relatório Mensal de Vendas",
                "categories": ["Relatório"],
                "content": "relatório vendas mensal dados estatísticas resultado",
                "sentiment": "positivo"
            },
            {
                "id": "doc_003",
                "title": "Proposta Comercial",
                "categories": ["Proposta"],
                "content": "proposta comercial orçamento projeto desenvolvimento",
                "sentiment": "positivo"
            },
            {
                "id": "doc_004",
                "title": "Manual Técnico",
                "categories": ["Documentação Técnica"],
                "content": "manual técnico procedimentos especificação sistema",
                "sentiment": "neutro"
            }
        ]

# Instância global do serviço
ranking_service = RankingService()