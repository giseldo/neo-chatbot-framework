import gradio as gr
import json
import os
import random
import re

# Carrega o arquivo de intenções
with open(os.path.join(os.path.dirname(__file__), "intencoes.json"), encoding="utf-8") as f:
    dados = json.load(f)

def identificar_intencao(mensagem):
    mensagem = mensagem.lower()
    for intencao, conteudo in dados["intencoes"].items():
        for utter in conteudo["utterances"]:
            if utter.lower() in mensagem:
                return intencao
    return None

def extrair_entidades(mensagem, intencao):
    entidades = {}
    intencoes_cfg = dados.get("intencoes", {})
    if intencao and intencao in intencoes_cfg:
        entidades_cfg = intencoes_cfg[intencao].get("entities", {})
        for nome, padrao in entidades_cfg.items():
            match = re.search(padrao, mensagem, re.IGNORECASE)
            if match:
                entidades[nome] = match.group(1).strip().lower()
    return entidades

def buscar_resposta(intencao, entidades=None):
    flow = dados.get("flow", {})
    responses = dados.get("responses", {})
    if not intencao or intencao not in flow:
        return dados.get("resposta_padrao", "Desculpe, não entendi.")

    next_step = flow[intencao].get("next")
    # Se for string simples, retorna resposta normalmente
    if isinstance(next_step, str):
        resposta_key = next_step
    # Se for dict, processa condições
    elif isinstance(next_step, dict):
        resposta_key = None
        # Verifica condição de entidade
        if "if_entidade_assunto" in next_step and entidades:
            assunto = entidades.get("assunto", "").lower()
            condicoes = next_step["if_entidade_assunto"]
            if assunto in condicoes:
                resposta_key = condicoes[assunto]
            else:
                resposta_key = condicoes.get("default")
        # Se não caiu em nenhuma condição, usa else
        if not resposta_key:
            resposta_key = next_step.get("else")
    else:
        return dados.get("resposta_padrao", "Desculpe, não entendi.")

    if resposta_key and resposta_key in responses:
        respostas = responses[resposta_key]
        if isinstance(respostas, list):
            return random.choice(respostas)
        return respostas
    return dados.get("resposta_padrao", "Desculpe, não entendi.")

def responder(mensagem, historico):
    intencao = identificar_intencao(mensagem)
    entidades = extrair_entidades(mensagem, intencao)
    resposta = buscar_resposta(intencao, entidades)
    if entidades:
        resposta += f"\n[Entidades extraídas: {entidades}]"
    return resposta

iface = gr.ChatInterface(
    fn=responder,
    title="Chatbot Simples com Gradio",
    description="Um chatbot básico usando Gradio."
)

if __name__ == "__main__":
    iface.launch()
