# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [1.2.0] - 2025-01-05

### Adicionado
- Documentação profissional completa com badges e índice
- Scripts de automação (`setup_local.sh` e `run.sh`)
- Arquivo `.editorconfig` para padronização de código
- Arquivo `LICENSE` (MIT)
- Arquivo `CHANGELOG.md` para controle de versões
- Arquivo `VERSION` para versionamento
- Arquivo `.env.example` com todas as variáveis de ambiente
- Estrutura de projeto limpa e organizada

### Melhorado
- README.md com documentação técnica profissional
- Estrutura de pastas mais limpa
- Docker Compose com configuração completa
- Documentação de API com exemplos práticos

### Removido
- Arquivos temporários e de cache
- Documentação redundante

## [1.1.0] - 2024-12-15

### Adicionado
- API completa para processamento de documentos
- Integração OCR com Tesseract
- Processamento NLP com Hugging Face
- Sistema de ranking e similaridade
- Suporte a múltiplos idiomas (PT, EN, ES)
- Documentação Swagger/OpenAPI
- Containerização com Docker
- Sistema de logs e auditoria

### Funcionalidades
- `/api/v1/health` - Health check da API
- `/api/v1/supported-languages` - Idiomas suportados
- `/api/v1/analyze-text` - Análise de texto
- `/api/v1/process-batch` - Processamento em lote
- `/api/v1/extract-info` - Extração de informações
- `/api/v1/audit-logs` - Logs de auditoria
- `/api/v1/stats` - Estatísticas do sistema