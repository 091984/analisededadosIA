"""Aplicativo Gradio inicial, sem integração com provedores de IA."""

import gradio as gr


def build_demo() -> gr.Blocks:
    """Cria a página temporária exibida enquanto o assistente é implementado."""
    with gr.Blocks(title="Assistente de Engenharia de Dados e IA") as interface:
        gr.Markdown("# Assistente de Engenharia de Dados e IA")
        gr.Markdown(
            "Estamos preparando este assistente para responder dúvidas sobre "
            "engenharia de dados e Inteligência Artificial."
        )
        gr.Info("A integração com IA será adicionada nas próximas tarefas.")
    return interface


demo = build_demo()
