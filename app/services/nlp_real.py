"""
Serviço de NLP com LLM real usando Hugging Face
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline, AutoTokenizer, AutoModel
import torch
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

class RealNLPService:
    """Serviço de NLP com modelos reais do Hugging Face"""
    
    def __init__(self):
        """Inicializa os modelos de NLP"""
        self.sentence_model = None
        self.summarizer = None
        self.classifier = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa os modelos de forma lazy"""
        try:
            # Modelo para embeddings (leve e eficiente)
            logger.info("Carregando modelo de embeddings...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Pipeline de sumarização (modelo pequeno para CPU)
            logger.info("Carregando modelo de sumarização...")
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=-1  # CPU
            )
            
            # Pipeline de classificação de sentimento
            logger.info("Carregando modelo de classificação...")
            self.classifier = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                device=-1  # CPU
            )
            
            logger.info("Modelos NLP carregados com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos NLP: {e}")
            # Fallback para modelos mais simples se necessário
            self._initialize_fallback_models()
    
    def _initialize_fallback_models(self):
        """Inicializa modelos de fallback mais simples"""
        try:
            logger.info("Carregando modelos de fallback...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Usar modelo menor para sumarização
            self.summarizer = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-6-6",
                device=-1
            )
            
            # Modelo de sentimento mais simples
            self.classifier = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                device=-1
            )
            
        except Exception as e:
            logger.error(f"Erro ao carregar modelos de fallback: {e}")
            self.sentence_model = None
            self.summarizer = None
            self.classifier = None
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Gera embeddings para lista de textos
        
        Args:
            texts: Lista de textos
            
        Returns:
            Array numpy com embeddings
        """
        try:
            if self.sentence_model is None:
                raise ValueError("Modelo de embeddings não carregado")
            
            embeddings = self.sentence_model.encode(texts)
            return embeddings
            
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings: {e}")
            # Fallback para TF-IDF
            return self._fallback_embeddings(texts)
    
    def _fallback_embeddings(self, texts: List[str]) -> np.ndarray:
        """Fallback usando TF-IDF para embeddings"""
        try:
            vectorizer = TfidfVectorizer(max_features=384)  # Mesmo tamanho do sentence transformer
            embeddings = vectorizer.fit_transform(texts).toarray()
            return embeddings
        except Exception as e:
            logger.error(f"Erro no fallback de embeddings: {e}")
            # Retorna embeddings zeros como último recurso
            return np.zeros((len(texts), 384))
    
    def summarize_text(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """
        Gera resumo do texto usando modelo de sumarização
        
        Args:
            text: Texto para resumir
            max_length: Tamanho máximo do resumo
            min_length: Tamanho mínimo do resumo
            
        Returns:
            Resumo do texto
        """
        try:
            if self.summarizer is None:
                return self._extractive_summary(text, max_length)
            
            # Limitar tamanho do texto de entrada (BART tem limite)
            if len(text) > 1024:
                text = text[:1024]
            
            # Ajustar parâmetros baseado no tamanho do texto
            text_length = len(text.split())
            if text_length < 50:
                return text  # Texto muito pequeno, retorna original
            
            max_len = min(max_length, text_length // 2)
            min_len = min(min_length, max_len // 2)
            
            summary = self.summarizer(
                text,
                max_length=max_len,
                min_length=min_len,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            logger.error(f"Erro na sumarização: {e}")
            return self._extractive_summary(text, max_length)
    
    def _extractive_summary(self, text: str, max_length: int) -> str:
        """Sumarização extrativa simples como fallback"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if len(sentences) <= 3:
            return text
        
        # Pegar as primeiras sentenças até atingir o tamanho máximo
        summary_sentences = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > max_length * 5:  # Aproximadamente
                break
            summary_sentences.append(sentence)
            current_length += len(sentence)
        
        return '. '.join(summary_sentences[:3]) + '.'
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analisa sentimento do texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Dicionário com sentimento e score
        """
        try:
            if self.classifier is None:
                return {"sentiment": "neutral", "score": 0.5}
            
            # Limitar tamanho do texto
            if len(text) > 512:
                text = text[:512]
            
            result = self.classifier(text)
            
            return {
                "sentiment": result[0]['label'].lower(),
                "score": result[0]['score']
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de sentimento: {e}")
            return {"sentiment": "neutral", "score": 0.5}
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        Extrai palavras-chave do texto
        
        Args:
            text: Texto para análise
            top_k: Número de palavras-chave
            
        Returns:
            Lista de palavras-chave
        """
        try:
            # Usar TF-IDF para extração de palavras-chave
            vectorizer = TfidfVectorizer(
                max_features=top_k * 2,
                stop_words=None,  # Manter palavras em português
                ngram_range=(1, 2)
            )
            
            tfidf_matrix = vectorizer.fit_transform([text])
            feature_names = vectorizer.get_feature_names_out()
            tfidf_scores = tfidf_matrix.toarray()[0]
            
            # Pegar top-k palavras com maior score
            top_indices = np.argsort(tfidf_scores)[-top_k:][::-1]
            keywords = [feature_names[i] for i in top_indices if tfidf_scores[i] > 0]
            
            return keywords
            
        except Exception as e:
            logger.error(f"Erro na extração de palavras-chave: {e}")
            # Fallback simples
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 3:  # Ignorar palavras muito pequenas
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            return sorted(word_freq.keys(), key=word_freq.get, reverse=True)[:top_k]
    
    def calculate_similarity(self, query: str, documents: List[str]) -> List[float]:
        """
        Calcula similaridade entre query e documentos
        
        Args:
            query: Query de busca
            documents: Lista de documentos
            
        Returns:
            Lista de scores de similaridade
        """
        try:
            if not documents:
                return []
            
            # Gerar embeddings para query e documentos
            all_texts = [query] + documents
            embeddings = self.get_embeddings(all_texts)
            
            query_embedding = embeddings[0:1]
            doc_embeddings = embeddings[1:]
            
            # Calcular similaridade coseno
            similarities = cosine_similarity(query_embedding, doc_embeddings)[0]
            
            return similarities.tolist()
            
        except Exception as e:
            logger.error(f"Erro no cálculo de similaridade: {e}")
            # Fallback simples baseado em palavras comuns
            return self._simple_similarity(query, documents)
    
    def _simple_similarity(self, query: str, documents: List[str]) -> List[float]:
        """Cálculo de similaridade simples como fallback"""
        query_words = set(query.lower().split())
        similarities = []
        
        for doc in documents:
            doc_words = set(doc.lower().split())
            intersection = len(query_words.intersection(doc_words))
            union = len(query_words.union(doc_words))
            
            if union == 0:
                similarity = 0.0
            else:
                similarity = intersection / union
            
            similarities.append(similarity)
        
        return similarities
    
    def find_relevant_excerpts(self, query: str, text: str, max_excerpts: int = 3) -> List[str]:
        """
        Encontra trechos relevantes do texto para a query
        
        Args:
            query: Query de busca
            text: Texto completo
            max_excerpts: Número máximo de trechos
            
        Returns:
            Lista de trechos relevantes
        """
        try:
            # Dividir texto em sentenças
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            if not sentences:
                return []
            
            # Calcular similaridade de cada sentença com a query
            similarities = self.calculate_similarity(query, sentences)
            
            # Pegar as sentenças mais similares
            top_indices = np.argsort(similarities)[-max_excerpts:][::-1]
            relevant_excerpts = [sentences[i] for i in top_indices if similarities[i] > 0.1]
            
            return relevant_excerpts
            
        except Exception as e:
            logger.error(f"Erro ao encontrar trechos relevantes: {e}")
            # Fallback: procurar sentenças que contenham palavras da query
            query_words = query.lower().split()
            sentences = re.split(r'[.!?]+', text)
            relevant = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if any(word in sentence.lower() for word in query_words):
                    relevant.append(sentence)
                    if len(relevant) >= max_excerpts:
                        break
            
            return relevant
    
    def categorize_text(self, text: str) -> List[str]:
        """
        Categoriza o texto em categorias predefinidas
        
        Args:
            text: Texto para categorizar
            
        Returns:
            Lista de categorias
        """
        categories = []
        text_lower = text.lower()
        
        # Categorias baseadas em palavras-chave
        category_keywords = {
            "contrato": ["contrato", "acordo", "prestação", "serviços", "cláusula"],
            "jurídico": ["lei", "artigo", "código", "jurídico", "legal", "tribunal"],
            "financeiro": ["valor", "pagamento", "preço", "custo", "financeiro", "orçamento"],
            "técnico": ["sistema", "software", "tecnologia", "desenvolvimento", "técnico"],
            "comercial": ["venda", "compra", "produto", "cliente", "comercial", "negócio"],
            "administrativo": ["processo", "procedimento", "norma", "política", "gestão"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return categories if categories else ["geral"]

# Instância global do serviço NLP
nlp_service = RealNLPService()