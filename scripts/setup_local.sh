#!/bin/bash

# TechMatch OCR+LLM API - Setup Local
# Instala dependências e configura ambiente virtual

set -e

echo "🚀 TechMatch OCR+LLM API - Setup Local"
echo "======================================"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instalar dependências
echo "📚 Instalando dependências..."
pip install -r requirements.txt

# Verificar se Tesseract está instalado
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR não encontrado."
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-por tesseract-ocr-spa"
    echo "   macOS: brew install tesseract tesseract-lang"
    echo "   Windows: Baixe de https://github.com/UB-Mannheim/tesseract/wiki"
else
    echo "✅ Tesseract OCR encontrado"
fi

# Criar pasta de uploads
mkdir -p uploads

# Copiar arquivo de ambiente
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "   ⚠️  Configure as variáveis em .env conforme necessário"
fi

echo ""
echo "✅ Setup concluído com sucesso!"
echo ""
echo "Para executar a aplicação:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Ou use Docker:"
echo "  ./scripts/run.sh"
echo ""
echo "Acesse: http://localhost:8000/docs"