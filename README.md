---
title: Assistente de Engenharia de Dados e IA
emoji: "🎓"
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
---

# Assistente de Engenharia de Dados e IA

Base inicial de um chat público e didático para dúvidas sobre engenharia de
dados e Inteligência Artificial. O projeto será publicado no Hugging Face
Spaces e configurado gradualmente conforme a
[spec da Parte 1](SPEC-parte1-cicd-deploy.md).

## Estado atual

Esta é somente a **tarefa 1** da spec: a estrutura Python/Gradio está pronta e
o aplicativo exibe uma página temporária de preparação. Ainda não há
configuração por YAML, chamadas a modelos, chaves de API ou deploy automático.

## Executar localmente

Requer Python 3.10 ou mais recente.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Depois, abra o endereço local mostrado no terminal, normalmente
`http://127.0.0.1:7860`.

Para encerrar o servidor, use `Ctrl+C`.

## Segurança

Não coloque chaves de API neste repositório, no README ou em arquivos de
configuração versionados. Quando a integração com IA for implementada, as chaves
serão cadastradas exclusivamente como *Secrets* do Hugging Face Space.
