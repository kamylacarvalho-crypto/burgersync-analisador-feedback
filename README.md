# 🍔 BurgerSync Ourinhos - Avaliador Inteligente de Feedback

> Sistema completo para coleta, análise de sentimentos com IA (Google Gemini) e gestão operacional de avaliações para uma hamburgueria artesanal em Ourinhos/SP.

---

## 🌟 Destaques do Projeto

* **Arquitetura em 3 Camadas:**
  * **Layer 1 (Diretiva):** `directive/projeto.md` especificando regras de negócio, critérios e self-annealing.
  * **Layer 2 (Orquestração):** Integração do fluxo de dados, IA, fallback de contingência e deploy.
  * **Layer 3 (Execução):** Scripts determinísticos em Python na pasta `execution/` (`analyzer.py`, `alert_service.py`, `db_handler.py`, `server.py`).
* **Análise de Sentimentos em Tempo Real com IA:**
  * Categorização em **Positivo**, **Neutro** ou **Crítico**.
  * Extração automática de tags (`Sabor`, `Entrega`, `Atendimento`, `Temperatura`, `Higiene`, `Embalagem`).
  * Mecanismo de **Self-Annealing** com resiliência e fallback determinístico local caso a API esteja temporariamente com alta demanda ou offline.
* **Sistema de Alerta Gerencial Imediato:**
  * Disparo automático para ocorrências críticas.
  * Integração com serviço SMTP e contingência estruturada em `.tmp/alerts.log`.
* **Painel Administrativo Interativo:**
  * Métricas em tempo real (Total, Taxa de Satisfação %, Críticos Pendentes).
  * Banner de crise pulsante para casos críticos não tratados.
  * Filtros dinâmicos por Sentimento, Tratativa (Pendente/Tratada) e Tags temáticas.
  * Busca instantânea por nome, pedido ou palavra-chave.
  * Checkboxes para marcar avaliações como tratadas.
  * Botão de contato direto via WhatsApp com o cliente insatisfeito.

---

## 🚀 Como Executar Localmente

### Pré-requisitos
* Python 3.10+ (instalável via `uv` ou instalador oficial)

### Instalação
```bash
# Clone o repositório
git clone https://github.com/kamylacarvalho-crypto/burgersync-analisador-feedback.git
cd burgersync-analisador-feedback

# Instale as dependências
pip install requests python-dotenv

# Configure suas credenciais
cp .env.example .env
# Edite o .env com sua GEMINI_API_KEY
```

### Inicialização do Servidor
```bash
python execution/server.py
```
Acesse no seu navegador:
* **Interface do Cliente:** `http://localhost:8000/`
* **Painel Administrativo:** `http://localhost:8000/admin`

---

## 🌐 Acesso em Nuvem (GitHub Pages)

* **Avaliação do Cliente:** [https://kamylacarvalho-crypto.github.io/burgersync-analisador-feedback/](https://kamylacarvalho-crypto.github.io/burgersync-analisador-feedback/)
* **Painel do Gerente:** [https://kamylacarvalho-crypto.github.io/burgersync-analisador-feedback/admin.html](https://kamylacarvalho-crypto.github.io/burgersync-analisador-feedback/admin.html)

---

## 📁 Estrutura de Arquivos

```text
├── directive/
│   └── projeto.md            # SOP e Diretrizes do Projeto
├── execution/
│   ├── analyzer.py           # Análise de IA (Gemini + Local Fallback)
│   ├── alert_service.py      # Gestor de Alertas Críticos (SMTP + Log)
│   ├── db_handler.py         # Manipulação do Banco de Dados JSON
│   └── server.py             # Servidor HTTP / API REST
├── data/
│   └── feedbacks.json        # Banco de dados estruturado
├── public/                   # Arquivos Frontend
│   ├── index.html            # Interface pública de avaliação
│   ├── admin.html            # Painel do gestor
│   ├── styles.css            # Estilos modernos e responsivos
│   ├── app.js                # Lógica da interface do cliente
│   └── admin.js              # Lógica do painel gerencial
├── .tmp/
│   └── alerts.log            # Log de contingência de alertas críticos
└── README.md
```
