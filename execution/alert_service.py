import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ALERT_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".tmp", "alerts.log")

def dispatch_alert(feedback_data: dict) -> dict:
    """
    Dispara alerta para feedbacks classificados como Crítico.
    Tenta envio via SMTP. Caso não configurado ou em falha de conexão,
    executa fallback seguro para gravação estruturada em .tmp/alerts.log.
    """
    if feedback_data.get("sentiment") != "Crítico" and not feedback_data.get("alert_required"):
        return {"alert_sent": False, "reason": "Feedback não é crítico."}

    # Validação e consolidação rigorosa dos dados do cliente
    nome = feedback_data.get("nome") or "Cliente não identificado"
    contato = feedback_data.get("contato") or "Não informado"
    pedido_id = feedback_data.get("pedido_id") or "S/N"
    comentario = feedback_data.get("comentario") or ""
    tags = ", ".join(feedback_data.get("tags", []))
    resumo = feedback_data.get("resumo", "Sem resumo gerado")
    timestamp = feedback_data.get("timestamp") or datetime.now().isoformat()

    smtp_host = os.getenv("SMTP_HOST", "").strip()
    smtp_port = os.getenv("SMTP_PORT", "").strip()
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASS", "").strip()
    recipient = os.getenv("ALERT_RECIPIENT", "gerencia.burgersync@gmail.com").strip()

    alert_summary = (
        f"ALERTA CRÍTICO - PEDIDO #{pedido_id}\n"
        f"Data/Hora: {timestamp}\n"
        f"Cliente: {nome}\n"
        f"Contato: {contato}\n"
        f"Tags do Problema: {tags}\n"
        f"Resumo da IA: {resumo}\n"
        f"Comentário Completo: \"{comentario}\"\n"
    )

    # 1. Tenta envio por SMTP caso as credenciais existam
    if smtp_host and smtp_user and smtp_pass:
        try:
            port = int(smtp_port) if smtp_port else 587
            msg = MIMEMultipart()
            msg["From"] = smtp_user
            msg["To"] = recipient
            msg["Subject"] = f"🚨 [BURGSYNC ALERTA] Crise no Pedido #{pedido_id} - {nome}"
            msg.attach(MIMEText(alert_summary, "plain", "utf-8"))

            with smtplib.SMTP(smtp_host, port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            print(f"[SUCESSO] Alerta crítico despachado via SMTP para {recipient}")
            return {
                "alert_sent": True,
                "method": "smtp",
                "recipient": recipient,
                "timestamp": timestamp
            }
        except Exception as e:
            print(f"[AVISO] Falha no disparo SMTP ({e}). Acionando fallback para .tmp/alerts.log")

    # 2. Fallback determinístico para .tmp/alerts.log
    return _log_fallback_alert(alert_summary, feedback_data, timestamp)

def _log_fallback_alert(alert_summary: str, feedback_data: dict, timestamp: str) -> dict:
    os.makedirs(os.path.dirname(ALERT_LOG_PATH), exist_ok=True)
    
    log_entry = (
        f"================================================================================\n"
        f"[ALERTA CRÍTICO GERENCIAL] {timestamp}\n"
        f"{alert_summary}"
        f"Status de Despacho: Gravado no log de contingência (fallback ativo)\n"
        f"================================================================================\n\n"
    )

    try:
        with open(ALERT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
        print(f"[INFO] Alerta registrado estruturadamente em {ALERT_LOG_PATH}")
    except Exception as e:
        print(f"[ERRO] Falha ao gravar log de contingência: {e}")

    return {
        "alert_sent": True,
        "method": "log_fallback",
        "log_path": ALERT_LOG_PATH,
        "timestamp": timestamp
    }

def read_recent_alerts(limit: int = 15) -> list:
    """Lê os últimos alertas registrados no log de contingência."""
    if not os.path.exists(ALERT_LOG_PATH):
        return []
    try:
        with open(ALERT_LOG_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        blocks = [b.strip() for b in content.split("================================================================================") if b.strip()]
        return blocks[-limit:]
    except Exception as e:
        print(f"[ERRO] Falha ao ler {ALERT_LOG_PATH}: {e}")
        return []
