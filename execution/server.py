import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

# Garante que a pasta execution esteja no path de importação
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)

from analyzer import analyze_feedback
import db_handler
import alert_service

PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")

class BurgerSyncRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Endpoints da API REST
        if path == "/api/feedbacks":
            sentiment = query_params.get("sentiment", [None])[0]
            status = query_params.get("status", [None])[0]
            tag = query_params.get("tag", [None])[0]
            search = query_params.get("search", [None])[0]

            feedbacks = db_handler.get_all_feedbacks(sentiment, status, tag, search)
            self._send_json(200, feedbacks)
            return

        elif path == "/api/metrics":
            metrics = db_handler.get_metrics()
            self._send_json(200, metrics)
            return

        elif path == "/api/alerts":
            alerts = alert_service.read_recent_alerts()
            self._send_json(200, {"alerts": alerts})
            return

        # Roteamento de Arquivos Estáticos (Frontend)
        if path == "/" or path == "/index.html":
            self._serve_file(os.path.join(PUBLIC_DIR, "index.html"), "text/html")
        elif path == "/admin" or path == "/admin.html":
            self._serve_file(os.path.join(PUBLIC_DIR, "admin.html"), "text/html")
        else:
            # Remove a barra inicial e tenta buscar na pasta public
            rel_path = path.lstrip("/")
            file_path = os.path.join(PUBLIC_DIR, rel_path)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                ext = os.path.splitext(file_path)[1].lower()
                content_types = {
                    ".html": "text/html",
                    ".css": "text/css",
                    ".js": "application/javascript",
                    ".json": "application/json",
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".svg": "image/svg+xml",
                    ".ico": "image/x-icon"
                }
                ctype = content_types.get(ext, "application/octet-stream")
                self._serve_file(file_path, ctype)
            else:
                self._send_json(404, {"error": "Recurso não encontrado"})

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/feedback":
            body = self._read_json_body()
            if not body:
                self._send_json(400, {"error": "Corpo da requisição JSON inválido"})
                return

            nome = body.get("nome", "").strip()
            contato = body.get("contato", "").strip()
            pedido_id = body.get("pedido_id", "").strip()
            comentario = body.get("comentario", "").strip()

            if not comentario:
                self._send_json(400, {"error": "O campo 'comentario' é obrigatório."})
                return

            # 1. Análise com Gemini (ou fallback determinístico)
            analysis = analyze_feedback(comentario, nome, pedido_id)

            # 2. Consolidação e persistência no banco de dados JSON
            data_to_store = {
                "nome": nome,
                "contato": contato,
                "pedido_id": pedido_id,
                "comentario": comentario,
                "sentiment": analysis.get("sentiment"),
                "score": analysis.get("score"),
                "tags": analysis.get("tags"),
                "resumo": analysis.get("resumo"),
                "alert_required": analysis.get("alert_required"),
                "engine": analysis.get("engine")
            }
            stored_record = db_handler.add_feedback(data_to_store)

            # 3. Disparo de Alerta se for Crítico
            alert_dispatch_info = None
            if analysis.get("alert_required") or analysis.get("sentiment") == "Crítico":
                alert_dispatch_info = alert_service.dispatch_alert(stored_record)

            self._send_json(201, {
                "success": True,
                "feedback": stored_record,
                "alert": alert_dispatch_info
            })
            return

        self._send_json(404, {"error": "Endpoint não encontrado"})

    def do_PATCH(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        # Exemplo: /api/feedback/FB-104/status
        parts = [p for p in path.split("/") if p]
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "feedback" and parts[3] == "status":
            feedback_id = parts[2]
            body = self._read_json_body()
            new_status = body.get("status") if body else None

            if new_status not in ["lido", "pendente"]:
                self._send_json(400, {"error": "Status deve ser 'lido' ou 'pendente'"})
                return

            updated = db_handler.update_feedback_status(feedback_id, new_status)
            if "error" in updated:
                self._send_json(404, updated)
            else:
                self._send_json(200, updated)
            return

        self._send_json(404, {"error": "Endpoint não encontrado"})

    def _read_json_body(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            if content_length == 0:
                return {}
            post_data = self.rfile.read(content_length)
            return json.loads(post_data.decode("utf-8"))
        except Exception:
            return None

    def _send_json(self, status_code: int, data: any):
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.end_headers()
        self.wfile.write(response_bytes)

    def _serve_file(self, file_path: str, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self._send_cors_headers()
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self._send_json(500, {"error": f"Erro ao carregar arquivo: {e}"})

    def log_message(self, format, *args):
        # Log limpo
        sys.stdout.write(f"[HTTP] {self.address_string()} - {format % args}\n")
        sys.stdout.flush()

def run_server(port: int = 8000):
    db_handler.init_db()
    server_address = ("", port)
    httpd = HTTPServer(server_address, BurgerSyncRequestHandler)
    print(f"\n========================================================")
    print(f"🍔 BurgerSync Server Ativo!")
    print(f"👉 Cliente: http://localhost:{port}/")
    print(f"👉 Painel Admin: http://localhost:{port}/admin")
    print(f"========================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Servidor finalizado com sucesso.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    run_server(port)
