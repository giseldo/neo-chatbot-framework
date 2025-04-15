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
                entidades[nome] = match.group(1).strip()
    return entidades

def buscar_resposta(intencao):
    # Busca o vínculo entre intenção e resposta na chave "flow"
    if intencao and intencao in dados.get("flow", {}):
        response_key = dados["flow"][intencao]
        if response_key and response_key in dados.get("responses", {}):
            respostas = dados["responses"][response_key]
            if isinstance(respostas, list):
                return random.choice(respostas)
            return respostas
    return dados.get("resposta_padrao", "Desculpe, não entendi.")

def responder(mensagem, histórico):
    intencao = identificar_intencao(mensagem)
    resposta = buscar_resposta(intencao)
    entidades = extrair_entidades(mensagem, intencao)
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
