import os
import json
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "feedbacks.json")

SEED_FEEDBACKS = [
    {
        "id": "FB-101",
        "timestamp": "2026-11-23T14:15:00",
        "nome": "Mariana Souza",
        "contato": "(14) 99781-4455",
        "pedido_id": "PED-7801",
        "comentario": "O Burger da Vila com bacon crocante e maionese verde artesanal estava espetacular! Chegou bem quentinho aqui no Jardim Ouro Verde em apenas 22 minutos. Parabéns!",
        "sentiment": "Positivo",
        "score": 0.98,
        "tags": ["Sabor", "Entrega", "Temperatura"],
        "resumo": "Elogio enfático ao sabor do lanche, crocância e agilidade na entrega.",
        "status": "lido",
        "alert_required": False,
        "treated_at": "2026-11-23T14:30:00"
    },
    {
        "id": "FB-102",
        "timestamp": "2026-11-23T14:40:00",
        "nome": "Lucas Ferreira",
        "contato": "(14) 99123-8877",
        "pedido_id": "PED-7815",
        "comentario": "Melhor smash burger de Ourinhos! Pão brioche macio, carne super suculenta e atendimento impecável no balcão da loja do Centro.",
        "sentiment": "Positivo",
        "score": 0.96,
        "tags": ["Sabor", "Atendimento"],
        "resumo": "Elogio ao hambúrguer smash e excelente atendimento no Centro.",
        "status": "lido",
        "alert_required": False,
        "treated_at": "2026-11-23T14:45:00"
    },
    {
        "id": "FB-103",
        "timestamp": "2026-11-23T15:05:00",
        "nome": "Beatriz Lima",
        "contato": "(14) 99654-1122",
        "pedido_id": "PED-7830",
        "comentario": "O lanche é bem saboroso, mas achei que a porção de batata rústica veio um pouco murcha pelo vapor na embalagem. Talvez um saquinho com respiro ajudaria.",
        "sentiment": "Neutro",
        "score": 0.55,
        "tags": ["Sabor", "Embalagem"],
        "resumo": "Lanche aprovado, porém batatas murchas devido à retenção de vapor na embalagem.",
        "status": "pendente",
        "alert_required": False,
        "treated_at": None
    },
    {
        "id": "FB-104",
        "timestamp": "2026-11-23T15:15:00",
        "nome": "Carlos Eduardo Silva",
        "contato": "(14) 99876-1234",
        "pedido_id": "PED-7842",
        "comentario": "Péssima experiência no pedido PED-7842! O pedido demorou quase 2 horas para entregar na Vila Odilon, o hambúrguer veio completamente gelado e a carne estava crua no meio. Exijo estorno ou providências urgentes!",
        "sentiment": "Crítico",
        "score": 0.10,
        "tags": ["Entrega", "Temperatura", "Sabor"],
        "resumo": "Crise de entrega com 2h de atraso, comida gelada e carne malpassada/crua.",
        "status": "pendente",
        "alert_required": True,
        "treated_at": None
    },
    {
        "id": "FB-105",
        "timestamp": "2026-11-23T15:20:00",
        "nome": "Patrícia Mendes",
        "contato": "(14) 99745-9900",
        "pedido_id": "PED-7850",
        "comentario": "Encontrei um cabelo grudado no queijo derretido do meu hambúrguer! Uma falta de higiene inaceitável. Quero o reembolso imediato via PIX.",
        "sentiment": "Crítico",
        "score": 0.08,
        "tags": ["Higiene", "Sabor"],
        "resumo": "Problema grave de higiene com presença de corpo estranho no produto.",
        "status": "pendente",
        "alert_required": True,
        "treated_at": None
    }
]

def init_db():
    """Garante a existência do arquivo JSON do banco de dados e dados iniciais."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH) or os.path.getsize(DB_PATH) == 0:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(SEED_FEEDBACKS, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Banco de dados JSON inicializado com {len(SEED_FEEDBACKS)} avaliacoes de exemplo em {DB_PATH}")

def get_all_feedbacks(sentiment: str = None, status: str = None, tag: str = None, search: str = None) -> list:
    init_db()
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            feedbacks = json.load(f)
    except Exception as e:
        print(f"[ERRO] Falha ao ler {DB_PATH}: {e}")
        return []

    # Aplicação de filtros
    filtered = feedbacks
    if sentiment and sentiment.lower() != "todos":
        filtered = [fb for fb in filtered if fb.get("sentiment", "").lower() == sentiment.lower()]

    if status and status.lower() != "todos":
        filtered = [fb for fb in filtered if fb.get("status", "").lower() == status.lower()]

    if tag and tag.lower() != "todas":
        filtered = [fb for fb in filtered if any(t.lower() == tag.lower() for t in fb.get("tags", []))]

    if search:
        s_lower = search.lower()
        filtered = [
            fb for fb in filtered
            if s_lower in fb.get("nome", "").lower()
            or s_lower in fb.get("pedido_id", "").lower()
            or s_lower in fb.get("comentario", "").lower()
            or s_lower in fb.get("contato", "").lower()
        ]

    # Ordenação decrescente por timestamp (mais recentes primeiro)
    filtered.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return filtered

def add_feedback(data: dict) -> dict:
    init_db()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    new_id = f"FB-{len(feedbacks) + 101}"
    record = {
        "id": new_id,
        "timestamp": data.get("timestamp") or datetime.now().isoformat(),
        "nome": data.get("nome", "").strip() or "Cliente Anônimo",
        "contato": data.get("contato", "").strip() or "Não informado",
        "pedido_id": data.get("pedido_id", "").strip() or f"PED-{uuid.uuid4().hex[:6].upper()}",
        "comentario": data.get("comentario", "").strip(),
        "sentiment": data.get("sentiment", "Neutro"),
        "score": float(data.get("score", 0.5)),
        "tags": data.get("tags", ["Geral"]),
        "resumo": data.get("resumo", ""),
        "status": "pendente",
        "alert_required": bool(data.get("alert_required", False)),
        "treated_at": None,
        "engine": data.get("engine", "gemini_api")
    }

    feedbacks.append(record)

    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, indent=2, ensure_ascii=False)

    print(f"[SUCESSO] Feedback gravado com ID {new_id} ({record['sentiment']})")
    return record

def update_feedback_status(feedback_id: str, new_status: str) -> dict:
    init_db()
    with open(DB_PATH, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)

    updated_record = None
    for fb in feedbacks:
        if fb.get("id") == feedback_id:
            fb["status"] = new_status
            fb["treated_at"] = datetime.now().isoformat() if new_status == "lido" else None
            updated_record = fb
            break

    if updated_record:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(feedbacks, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Status do feedback {feedback_id} alterado para '{new_status}'")
        return updated_record

    return {"error": f"Feedback com ID {feedback_id} não encontrado."}

def get_metrics() -> dict:
    feedbacks = get_all_feedbacks()
    total = len(feedbacks)
    if total == 0:
        return {
            "total": 0,
            "positivos": 0,
            "neutros": 0,
            "criticos": 0,
            "criticos_pendentes": 0,
            "taxa_satisfacao": 0.0
        }

    positivos = sum(1 for fb in feedbacks if fb.get("sentiment") == "Positivo")
    neutros = sum(1 for fb in feedbacks if fb.get("sentiment") == "Neutro")
    criticos = sum(1 for fb in feedbacks if fb.get("sentiment") == "Crítico")
    criticos_pendentes = sum(1 for fb in feedbacks if fb.get("sentiment") == "Crítico" and fb.get("status") == "pendente")

    return {
        "total": total,
        "positivos": positivos,
        "neutros": neutros,
        "criticos": criticos,
        "criticos_pendentes": criticos_pendentes,
        "taxa_satisfacao": round((positivos / total) * 100, 1)
    }

if __name__ == "__main__":
    init_db()
    print("Métricas Atuais:", json.dumps(get_metrics(), indent=2))
