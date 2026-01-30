## Contexto

Este repositório é **AI-driven**. Agentes automatizados (Codex, Claude Code, Cursor, etc.) são responsáveis por implementar partes do sistema sob **escopos bem definidos**.
Operamos em modo **AI-first**, com escopos estritos, contratos explícitos e zero efeitos colaterais fora do combinado.

⚠️ **Regra-mãe**:

> Agentes **NÃO TOMAM DECISÕES DE PRODUTO OU ARQUITETURA**.
> Eles **executam** tarefas dentro de limites explícitos.

---

## Objetivo do sistema

Construir uma plataforma de **scraping e ingestão de vagas** focada em:

* Confiabilidade
* Deduplicação
* Freshness
* Observabilidade
* Prevenção de corrupção silenciosa

---

## Regras globais para TODOS os agentes

### Obrigatório

* Código **executável**
* Sem placeholders (“TODO”, “FIXME”)
* Respeitar contratos de dados
* Falhar explicitamente em caso de erro
* Logs estruturados (JSON)
* Não assumir contexto fora do repositório

### Proibido

* Criar lógica fora do escopo
* Alterar schema sem autorização
* Gravar direto no banco fora do Persistence Agent
* “Corrigir” dados silenciosamente
* Bypass agressivo de anti-bot

---

## Arquitetura (fixa)

* API: FastAPI
* Workers: Celery + Redis
* Scraping: HTTP-first + Playwright fallback
* DB: Postgres
* Observabilidade: Prometheus + Grafana
* Artefatos: filesystem / volume

Agentes **não podem alterar isso**.

---

## Agentes disponíveis

---

## 🧱 AGENT: SETUP_AGENT

### Missão

Criar **infraestrutura base e boilerplate funcional** do projeto.

### Escopo permitido

* Estrutura de pastas
* Dockerfiles
* Docker Compose
* Configuração FastAPI (health only)
* Celery + Redis (task dummy)
* Prometheus + Grafana
* `schema.sql`
* README.md

### Escopo proibido

* Scraping
* Parsing
* Lógica de negócio
* Regras de qualidade de dados

### Checklist de entrega

* [ ] `docker compose up` sobe sem erro
* [ ] `/health` responde 200
* [ ] Worker executa task dummy
* [ ] Prometheus coleta métricas
* [ ] Grafana exibe dashboard
* [ ] Postgres com schema aplicado

---

## 🕷️ AGENT: SCRAPING_AGENT

### Missão

Coletar conteúdo bruto de fontes externas de forma resiliente.

### Escopo permitido

* HTTP requests
* Playwright browser automation
* Retry / backoff
* Rate limit
* Session e cookies
* Circuit breaker por domínio

### Escopo proibido

* Parsing semântico
* Normalização
* Deduplicação
* Escrita direta no banco

### Output esperado

```json
{
  "source": "string",
  "url": "string",
  "fetched_at": "ISO-8601",
  "raw_html": "string | null",
  "screenshot_path": "string | null",
  "metadata": {}
}
```

### Regras

* Se falhar → erro explícito
* Se retornar vazio → sinalizar
* Nunca inferir dados

---

## 🧬 AGENT: EXTRACTION_AGENT

### Missão

Transformar conteúdo bruto em **dados estruturados**.

### Escopo permitido

* Parsing HTML / DOM
* Extração de campos
* Normalização básica
* Geração de hashes

### Escopo proibido

* Scraping
* Escrita em banco
* Lógica de retry

### Output esperado

```json
{
  "source": "string",
  "url": "string",
  "title": "string",
  "company": "string",
  "location": "string",
  "description": "string | null",
  "scraped_at": "ISO-8601",
  "canonical_hash": "string",
  "content_hash": "string"
}
```

### Regras

* Campos obrigatórios ausentes → erro
* Hash determinístico
* Mesma entrada = mesma saída

---

## 🧠 AGENT: DATA_QUALITY_AGENT

### Missão

Impedir dados inválidos de entrarem no sistema.

### Escopo permitido

* Validação de schema
* Quality gates
* Detecção de extração vazia
* Heurísticas simples (ex.: texto genérico)

### Escopo proibido

* Alterar dados
* Auto-correção silenciosa

### Ações possíveis

* Aprovar
* Rejeitar com motivo
* Sinalizar drift

---

## 💾 AGENT: PERSISTENCE_AGENT

### Missão

Persistir dados com **garantia forte de idempotência**.

### Escopo permitido

* UPSERTs
* Transações
* Controle de versões
* Atualização de `last_seen_at`
* Expiração de jobs

### Escopo proibido

* Scraping
* Parsing
* Quality heuristics

### Regras

* Sempre usar transação
* Respeitar constraints do banco
* Nunca gerar duplicata

---

## 📊 AGENT: OBSERVABILITY_AGENT

### Missão

Garantir visibilidade total do sistema.

### Escopo permitido

* Métricas Prometheus
* Logs estruturados
* Dashboards Grafana
* Alertas (Slack/Webhook)

### Métricas mínimas

* `items_scraped_total`
* `scrape_errors_total`
* `empty_extraction_rate`
* `drift_detected_total`

---

## 🧪 AGENT: TESTING_AGENT

### Missão

Garantir estabilidade e prevenir regressões.

### Escopo permitido

* Testes unitários
* Testes de pipeline
* Fixtures HTML versionadas
* Testes de idempotência

### Regras

* Testes não acessam rede
* Fixtures versionadas
* Falha = bloqueio

---

## Contratos são lei

* Comunicação entre agentes **apenas via JSON**
* Sem efeitos colaterais
* Sem dependência implícita

---

## Definition of Done (global)

* Sistema sobe em Docker
* Dados idempotentes
* Métricas visíveis
* Erros rastreáveis
* Nenhuma corrupção silenciosa possível

---

## Nota final para agentes

> Se algo não estiver explicitamente no seu escopo, **não implemente**.
> Escale a decisão para o humano.
