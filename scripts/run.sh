#!/bin/bash

# TechMatch OCR+LLM API - Run with Docker
# Executa a aplicação usando Docker Compose

set -e

echo "🐳 TechMatch OCR+LLM API - Docker Run"
echo "===================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale Docker"
    exit 1
fi

# Verificar se Docker Compose está disponível
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale Docker Compose"
    exit 1
fi

echo "✅ Docker encontrado"

# Criar pasta de uploads
mkdir -p uploads

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose down

# Construir e executar
echo "🔨 Construindo e executando containers..."
docker compose up --build

echo ""
echo "✅ Aplicação executando!"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   MongoDB: localhost:27017"
echo ""
echo "Para parar: Ctrl+C ou 'docker compose down'"