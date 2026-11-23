import os
import json
import re
import requests
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Modelos em ordem de prioridade conforme especificado e atualizado por self-annealing
PREFERRED_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest",
    "gemini-3.5-flash"
]

def analyze_feedback(comentario: str, nome: str = "", pedido_id: str = "") -> dict:
    """
    Analisa o feedback textual utilizando a API do Google Gemini.
    Retorna sentimento (Positivo, Neutro ou Crítico), tags associadas,
    resumo executivo e flag de alerta.
    Possui contingência determinística local de alta precisão (Self-Annealing).
    """
    if not comentario or not comentario.strip():
        return {
            "sentiment": "Neutro",
            "score": 0.5,
            "tags": ["Sem Comentário"],
            "resumo": "Avaliação enviada sem texto explicativo.",
            "alert_required": False,
            "engine": "local_empty"
        }

    # Tenta chamada à API do Gemini se a chave estiver configurada
    if GEMINI_API_KEY:
        for model in PREFERRED_MODELS:
            try:
                result = _call_gemini_api(model, comentario, nome, pedido_id)
                if result:
                    result["engine"] = f"gemini_api:{model}"
                    print(f"[SUCESSO] Analise realizada com sucesso via API Gemini ({model})")
                    return result
            except Exception as e:
                print(f"[AVISO] Falha ao consultar Gemini com o modelo {model}: {e}")

    # Fallback determinístico local (resiliência de cota/rede)
    print("[INFO] Acionando motor de analise deterministica local de contingencia.")
    return _local_deterministic_analysis(comentario)

def _call_gemini_api(model: str, comentario: str, nome: str, pedido_id: str) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
Você é o Analisador de Sentimentos e Feedbacks do BurgerSync para uma hamburgueria artesanal em Ourinhos.
Analise a avaliação do cliente abaixo com extremo rigor:

Cliente: {nome or 'Anônimo'}
Pedido: {pedido_id or 'Não informado'}
Comentário: "{comentario}"

Regras de Classificação:
1. Sentimento deve ser ESTRITAMENTE um dos seguintes:
   - "Positivo": Elogios, satisfação, comida saborosa, entrega pontual, recomendação.
   - "Neutro": Comentários mistos, dúvidas, sugestões leves sem irritação grave.
   - "Crítico": Reclamações severas, atrasos excessivos (+1h), comida fria ou estragada/crua, atendimento rude, pedidos de reembolso, problemas de higiene ou segurança alimentar.
2. Tags: extraia de 1 a 4 tags relevantes de temas como: "Sabor", "Entrega", "Atendimento", "Embalagem", "Preco", "Tempo de Espera", "Higiene", "Temperatura".
3. Alerta Gerencial: Se o sentimento for "Crítico", alert_required deve ser true.
4. Resumo: Uma frase curta em português resumindo o ponto principal.

Responda EXCLUSIVAMENTE em formato JSON puro, sem markdown, sem blocos de codigo adicionais:
{{
  "sentiment": "Positivo" | "Neutro" | "Crítico",
  "score": 0.95,
  "tags": ["Sabor", "Entrega"],
  "resumo": "Lanche saboroso e entrega rápida.",
  "alert_required": false,
  "urgency_reason": ""
}}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 400
        }
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=12)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}: {response.text[:200]}")

    data = response.json()
    candidates = data.get("candidates", [])
    if not candidates:
        raise Exception("Nenhum candidato retornado pelo Gemini.")

    text_resp = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
    
    # Limpeza de markdown se presente
    text_resp = re.sub(r"^```(json)?\s*", "", text_resp, flags=re.MULTILINE)
    text_resp = re.sub(r"\s*```$", "", text_resp, flags=re.MULTILINE).strip()

    parsed = json.loads(text_resp)
    
    # Sanitização e validação das chaves
    sentiment = parsed.get("sentiment", "Neutro")
    if sentiment not in ["Positivo", "Neutro", "Crítico"]:
        if "crit" in sentiment.lower() or "ruim" in sentiment.lower():
            sentiment = "Crítico"
        elif "pos" in sentiment.lower() or "bom" in sentiment.lower():
            sentiment = "Positivo"
        else:
            sentiment = "Neutro"

    return {
        "sentiment": sentiment,
        "score": float(parsed.get("score", 0.8 if sentiment == "Positivo" else (0.2 if sentiment == "Crítico" else 0.5))),
        "tags": parsed.get("tags", ["Geral"]),
        "resumo": parsed.get("resumo", "Avaliação processada pela IA."),
        "alert_required": sentiment == "Crítico",
        "urgency_reason": parsed.get("urgency_reason", "")
    }

def _local_deterministic_analysis(comentario: str) -> dict:
    """Motor determinístico local com dicionário semântico ponderado para hambúrgueres."""
    text_lower = comentario.lower()

    # Dicionário crítico
    crit_words = [
        "pessimo", "péssimo", "horrivel", "horrível", "frio", "gelado", "cru", "crua",
        "estragad", "podre", "demorou", "demora", "atraso", "atrasado", "1h", "2h",
        "reembolso", "dinheiro de volta", "nojo", "barata", "cabelo", "sujo", "sujeira",
        "nunca mais", "vergonha", "falta de respeito", "desrespeito", "pior", "intragavel",
        "intragável", "cancelar", "cancelamento", "odiei", "lixo", "estragou"
    ]

    # Dicionário positivo
    pos_words = [
        "excelente", "maravilhos", "delicia", "delícia", "otimo", "ótimo", "perfeito",
        "incrivel", "incrível", "suculento", "muito bom", "gostoso", "parabens", "parabéns",
        "rapido", "rápido", "quentinho", "quente", "adorei", "amei", "recomendo",
        "top", "show", "melhor burger", "melhor lanche", "10/10", "sensacional"
    ]

    crit_matches = [w for w in crit_words if w in text_lower]
    pos_matches = [w for w in pos_words if w in text_lower]

    if crit_matches and len(crit_matches) >= len(pos_matches):
        sentiment = "Crítico"
        score = 0.15
        alert = True
        resumo = f"Reclamação severa identificada: {', '.join(crit_matches[:2])}."
    elif pos_matches:
        sentiment = "Positivo"
        score = 0.92
        alert = False
        resumo = f"Elogio ao produto/serviço: {', '.join(pos_matches[:2])}."
    else:
        sentiment = "Neutro"
        score = 0.50
        alert = False
        resumo = "Avaliação neutra ou moderada sem fortes termos avaliativos."

    # Extração de tags
    tags = []
    if any(k in text_lower for k in ["sabor", "gosto", "carne", "lanche", "burger", "hamburguer", "maionese", "ponto", "molho", "queijo", "bacon", "salgado", "tempero"]):
        tags.append("Sabor")
    if any(k in text_lower for k in ["entrega", "motoboy", "chegou", "demora", "espera", "tempo", "rapido", "atraso", "minuto", "hora"]):
        tags.append("Entrega")
    if any(k in text_lower for k in ["atendimento", "atendente", "educacao", "educação", "garcom", "garçom", "whatsapp", "suporte", "grosseria"]):
        tags.append("Atendimento")
    if any(k in text_lower for k in ["embalagem", "amassado", "virado", "vazou", "sacola", "lacre"]):
        tags.append("Embalagem")
    if any(k in text_lower for k in ["preco", "preço", "caro", "barato", "custo", "beneficio", "valor"]):
        tags.append("Preço")
    if any(k in text_lower for k in ["frio", "gelado", "quentinho", "quente", "temperatura"]):
        tags.append("Temperatura")
    if any(k in text_lower for k in ["cabelo", "sujo", "estragado", "higiene", "nojo"]):
        tags.append("Higiene")

    if not tags:
        tags.append("Geral")

    return {
        "sentiment": sentiment,
        "score": score,
        "tags": tags,
        "resumo": resumo,
        "alert_required": alert,
        "urgency_reason": "Identificado termos de alta insatisfação no comentário." if alert else "",
        "engine": "deterministic_local"
    }

if __name__ == "__main__":
    test_comment = "O lanche Burger da Vila chegou completamente frio após 1h30 de espera e a carne estava crua!"
    res = analyze_feedback(test_comment, "Carlos", "PED-102")
    print("\nResultado do Teste:")
    print(json.dumps(res, indent=2, ensure_ascii=False))
