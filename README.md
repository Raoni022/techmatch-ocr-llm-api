# TechMatch OCR+LLM API

## 🚀 API Empresarial para Processamento Inteligente de Documentos

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118.0-green.svg)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen.svg)](VERSION)

> **API robusta e escalável que combina tecnologias de OCR e NLP para análise inteligente de documentos**

Uma solução empresarial completa que integra reconhecimento óptico de caracteres (OCR) com processamento de linguagem natural (NLP) para extrair, analisar e classificar informações de documentos de forma inteligente e automatizada.

---

## 📋 Sumário

- [🎯 Visão Geral](#-visão-geral)
- [✨ Funcionalidades](#-funcionalidades)
- [🏗️ Arquitetura](#️-arquitetura)
- [🚀 Instalação](#-instalação)
  - [🐳 Docker (Recomendado)](#-docker-recomendado)
  - [💻 Instalação Local](#-instalação-local)
- [📖 Uso da API](#-uso-da-api)
- [🔧 Configuração](#-configuração)
- [📚 Exemplos](#-exemplos)
- [🧪 Testes](#-testes)
- [🏛️ Decisões de Design](#️-decisões-de-design)
- [🤝 Contribuição](#-contribuição)
- [📄 Licença](#-licença)

---

## 🎯 Visão Geral

O **TechMatch OCR+LLM API** é uma solução robusta para processamento automatizado de documentos que integra:

- **OCR Multilíngue**: Extração de texto usando Tesseract (Português, Inglês, Espanhol)
- **Análise NLP**: Processamento com modelos Hugging Face para sentiment analysis e classificação
- **Sistema de Ranking**: Algoritmos de similaridade e relevância
- **API RESTful**: Interface moderna com FastAPI e documentação automática
- **Containerização**: Deploy simplificado com Docker

### 🔄 Fluxo de Processamento

```
📄 Documento → 🔍 OCR → 📝 Texto → 🧠 NLP → 📊 Análise → 🎯 Resultado
```

1. **Upload**: Recebe documentos (PDF, imagens)
2. **OCR**: Extrai texto usando Tesseract
3. **NLP**: Analisa sentimento, extrai palavras-chave
4. **Classificação**: Categoriza e calcula relevância
5. **Ranking**: Ordena por similaridade e importância

---

## ✨ Funcionalidades

### 🔌 Endpoints Principais

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/v1/health` | GET | Status da API e serviços |
| `/api/v1/supported-languages` | GET | Idiomas suportados |
| `/api/v1/analyze-text` | POST | Análise de texto direto |
| `/api/v1/process-batch` | POST | Processamento de documentos |
| `/api/v1/extract-info` | POST | Extração de informações |
| `/api/v1/audit-logs` | GET | Logs de auditoria |
| `/api/v1/stats` | GET | Estatísticas do sistema |

### 🎛️ Recursos Avançados

- ✅ **Processamento Assíncrono**: Suporte a operações não-bloqueantes
- ✅ **Validação Robusta**: Modelos Pydantic para entrada e saída
- ✅ **Logs Estruturados**: Sistema completo de auditoria
- ✅ **CORS Configurado**: Pronto para integração frontend
- ✅ **Documentação Interativa**: Swagger UI automático
- ✅ **Containerização**: Docker e Docker Compose
- ✅ **Configuração Flexível**: Variáveis de ambiente

---

## 🏗️ Arquitetura

```
techmatch-ocr-llm-api/
├── app/                    # Código fonte principal
│   ├── main.py            # Aplicação FastAPI
│   ├── api.py             # Endpoints da API
│   ├── models.py          # Modelos Pydantic
│   └── services/          # Serviços de negócio
│       ├── ocr_service.py
│       ├── nlp_service.py
│       ├── ranking_service.py
│       └── logging_service.py
├── scripts/               # Scripts de automação
│   ├── setup_local.sh     # Setup ambiente local
│   └── run.sh             # Execução com Docker
├── Dockerfile             # Imagem Docker
├── compose.yml            # Docker Compose
├── requirements.txt       # Dependências Python
└── .env.example          # Variáveis de ambiente
```

---

## 🚀 Instalação

### 🐳 Docker (Recomendado)

**Pré-requisitos**: Docker e Docker Compose

```bash
# 1. Clone/extraia o projeto
cd techmatch-ocr-llm-api

# 2. Execute com Docker
./scripts/run.sh

# Ou manualmente:
docker compose up --build
```

### 💻 Instalação Local

**Pré-requisitos**: Python 3.8+, Tesseract OCR

```bash
# 1. Setup automático
./scripts/setup_local.sh

# 2. Ativação manual do ambiente
source venv/bin/activate

# 3. Execução
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 📦 Instalação do Tesseract

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-spa
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- Baixe de: https://github.com/UB-Mannheim/tesseract/wiki

---

## 📖 Uso da API

### 🌐 Acesso

- **API Base**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### 🔍 Health Check

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-05T10:30:00Z",
  "services": {
    "ocr": "operational",
    "nlp": "operational",
    "database": "operational"
  },
  "version": "1.2.0"
}
```

---

## 🔧 Configuração

### 🌍 Variáveis de Ambiente

Copie `.env.example` para `.env` e configure:

```bash
# Aplicação
APP_NAME=TechMatch OCR+LLM API
APP_VERSION=1.2.0
DEBUG=false

# Banco de Dados
MONGO_URI=mongodb://localhost:27017/techmatch

# Serviços
USE_MOCK_AUDIT=true          # true para mock, false para MongoDB
USE_REAL_NLP=true            # true para Hugging Face, false para mock

# OCR
TESSERACT_CMD=tesseract
OCR_LANGUAGES=por+eng+spa    # Idiomas suportados

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=*               # Configurar para produção

# Logs
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### ⚙️ Configurações Importantes

- **USE_MOCK_AUDIT**: `true` para desenvolvimento, `false` para produção com MongoDB
- **USE_REAL_NLP**: `true` para usar modelos reais, `false` para respostas mock
- **OCR_LANGUAGES**: Idiomas do Tesseract (por+eng+spa)
- **CORS_ORIGINS**: Configure domínios específicos em produção

---

## 📚 Exemplos

### 📝 Análise de Texto

```bash
curl -X POST "http://localhost:8000/api/v1/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Este é um excelente produto que recomendo!",
    "language": "pt"
  }'
```

**Resposta:**
```json
{
  "sentiment": {
    "label": "POSITIVE",
    "score": 0.9234
  },
  "keywords": ["excelente", "produto", "recomendo"],
  "category": "review",
  "confidence": 0.87,
  "language_detected": "pt"
}
```

### 📄 Processamento de Documento

```bash
curl -X POST "http://localhost:8000/api/v1/process-batch" \
  -F "files=@documento.pdf" \
  -F "target_text=tecnologia inovação"
```

**Resposta:**
```json
{
  "results": [
    {
      "filename": "documento.pdf",
      "extracted_text": "Texto extraído do documento...",
      "analysis": {
        "sentiment": {"label": "NEUTRAL", "score": 0.6},
        "keywords": ["tecnologia", "inovação", "desenvolvimento"],
        "category": "technical"
      },
      "similarity_score": 0.78,
      "ranking_position": 1
    }
  ],
  "processing_time": 2.34,
  "total_files": 1
}
```

### 📊 Idiomas Suportados

```bash
curl -X GET "http://localhost:8000/api/v1/supported-languages"
```

**Resposta:**
```json
{
  "languages": [
    {"code": "pt", "name": "Português"},
    {"code": "en", "name": "English"},
    {"code": "es", "name": "Español"}
  ],
  "default": "pt"
}
```

---

## 🧪 Testes

### 🔍 Casos de Teste Manuais

1. **Health Check**
   ```bash
   curl http://localhost:8000/api/v1/health
   # Esperado: Status 200, todos serviços "operational"
   ```

2. **Upload e OCR**
   ```bash
   curl -X POST -F "files=@test.pdf" \
     http://localhost:8000/api/v1/process-batch
   # Esperado: Texto extraído e análise completa
   ```

3. **Análise de Sentimento**
   ```bash
   curl -X POST -H "Content-Type: application/json" \
     -d '{"text":"Produto ruim","language":"pt"}' \
     http://localhost:8000/api/v1/analyze-text
   # Esperado: Sentiment "NEGATIVE"
   ```

### 🐛 Troubleshooting

**Problema**: Tesseract não encontrado
```bash
# Solução Ubuntu/Debian:
sudo apt-get install tesseract-ocr tesseract-ocr-por

# Verificar instalação:
tesseract --version
```

**Problema**: Erro de dependências Python
```bash
# Solução:
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🏛️ Decisões de Design

### 🎯 Arquitetura

- **FastAPI**: Escolhido por performance, documentação automática e type hints
- **Pydantic**: Validação robusta e serialização automática
- **Tesseract**: OCR maduro com suporte multilíngue
- **Hugging Face**: Modelos NLP state-of-the-art
- **Docker**: Containerização para deploy consistente

### 🔒 Segurança

- **CORS**: Configurado para desenvolvimento, restringir em produção
- **Validação**: Todos inputs validados com Pydantic
- **Logs**: Sistema completo de auditoria
- **Variáveis**: Configuração via environment variables

### 📈 Performance

- **Assíncrono**: FastAPI com suporte async/await
- **Caching**: Modelos NLP carregados uma vez
- **Streaming**: Upload de arquivos otimizado
- **Logs**: Estruturados para análise

### 🔧 Manutenibilidade

- **Modular**: Serviços separados por responsabilidade
- **Tipagem**: Type hints em todo código
- **Documentação**: Swagger automático
- **Testes**: Estrutura preparada para testes automatizados

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

### 📋 Padrões

- **Código**: Seguir PEP 8
- **Commits**: Mensagens descritivas
- **Documentação**: Atualizar README quando necessário
- **Testes**: Incluir testes para novas funcionalidades

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**Desenvolvido por Raoni Medeiros • v1.2.0**

[![GitHub](https://img.shields.io/badge/GitHub-Profile-black.svg)](https://github.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue.svg)](https://linkedin.com)

</div>