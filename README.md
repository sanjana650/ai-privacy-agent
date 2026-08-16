# 🔐 AI Privacy Investigation & Remediation Agent

An LLM-powered backend agent that investigates application logs for privacy risks, retrieves relevant organizational policies, assesses risk, and automatically redacts exposed personally identifiable information (PII).

The project combines **agentic AI, tool calling, RAG, deterministic privacy detection, FastAPI, structured outputs, evaluation, testing, and Docker** into a small production-style AI engineering system.

---

## 📌 Overview

Application logs are essential for debugging and monitoring, but they can accidentally contain sensitive information such as:

- Singapore NRIC numbers
- Email addresses
- Phone numbers
- Credit card numbers

Simply detecting PII is not always enough.

A privacy investigation also needs to answer:

> What information was exposed?  
> Which organizational policies are relevant?  
> How serious is the exposure?  
> What should be done about it?

This project turns that process into an **AI-assisted investigation workflow**.

A user submits an application log through a REST API. An AI agent can then use specialized tools to investigate the log, retrieve relevant privacy policies, assess the risk, and produce a structured investigation report.

---

# 🏗️ System Architecture

```text
                    User
                     │
                     ▼
                  FastAPI
                     │
                     ▼
          AI Privacy Investigation Agent
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     detect_pii   search_policy  redact_log
          │          │          │
          ▼          ▼          ▼
       Regex     RAG / Vector   Deterministic
      Detection    Search       Redaction
          │          │          │
          └──────────┼──────────┘
                     ▼
                LLM Reasoning
                     │
                     ▼
            Risk Classification
            Policy Assessment
            Recommended Action
                     │
                     ▼
          Structured Pydantic Report
                     │
                     ▼
                API Response
```

---

# ✨ Features

## 1. PII Detection

The agent has access to a deterministic PII detection tool:

```python
detect_pii(log)
```

It detects sensitive information including:

| PII Type | Example |
|---|---|
| NRIC | `S1234567A` |
| Email | `alice@example.com` |
| Phone | `+65 9123 4567` |
| Credit Card | `4111 1111 1111 1111` |

PII detection is implemented deterministically rather than asking the LLM to guess whether a value is sensitive.

Example:

```text
Input:
Payment failed for customer S1234567A

Detected:
NRIC
```

---

## 2. Agentic Investigation

The LLM acts as an investigation and orchestration layer.

Instead of using the LLM for every operation, the agent has access to specialized tools:

```text
detect_pii_tool
search_policy_tool
redact_log_tool
```

The agent uses tool results as evidence when producing its investigation.

A typical workflow looks like:

```text
Application log
      ↓
PII detection
      ↓
Policy retrieval
      ↓
Privacy reasoning
      ↓
Risk classification
      ↓
Remediation
      ↓
Investigation report
```

This demonstrates concepts such as:

- LLM tool calling
- Agent orchestration
- Multi-step reasoning
- Agent state
- System prompting
- Structured outputs
- Tool-result grounding

---

## 3. Policy RAG

The project contains synthetic organizational privacy policies used to determine whether detected information violates company rules.

Example policy files:

```text
data/
├── pii_policy.txt
├── logging_policy.txt
├── incident_policy.txt
└── retention_policy.txt
```

The retrieval pipeline is:

```text
Policy Documents
      ↓
Text Chunking
      ↓
Embeddings
      ↓
Vector Store
      ↓
Similarity Search
      ↓
Relevant Policy Chunks
      ↓
AI Agent
```

The agent can call:

```python
search_policy(query)
```

to retrieve policies relevant to the current investigation.

For example:

```text
Detected:
NRIC

Retrieved policy:
"Highly sensitive personal information must not be exposed
in application logs."

Result:
HIGH privacy risk
```

This prevents the system from relying only on the LLM's internal knowledge when making policy-related conclusions.

---

## 4. Risk Classification

Investigations are classified into three levels:

```text
LOW
MEDIUM
HIGH
```

The prototype uses explicit risk rules:

| Finding | Risk |
|---|---|
| No PII | LOW |
| Email | MEDIUM |
| Phone number | MEDIUM |
| NRIC | HIGH |
| Credit card | HIGH |

When multiple types of PII are detected, the highest applicable risk level is used.

For example:

```text
EMAIL + PHONE
→ MEDIUM

EMAIL + NRIC
→ HIGH

NRIC + CREDIT_CARD
→ HIGH
```

---

## 5. Automated Remediation

The system does not only describe the problem.

It can also remediate the exposed log using:

```python
redact_log(log, findings)
```

Example:

```text
Before:

Payment failed for customer S1234567A
```

```text
After:

Payment failed for customer [REDACTED-NRIC]
```

Multiple PII types can also be redacted:

```text
Before:

Customer S1234567A can be reached at alice@example.com
```

```text
After:

Customer [REDACTED-NRIC] can be reached at [REDACTED-EMAIL]
```

---

# 🧠 LLM vs Deterministic Components

A key design decision in this project is separating tasks that require **LLM reasoning** from tasks that should be **deterministic**.

### LLM responsibilities

The LLM is used for:

- Agent orchestration
- Tool selection
- Policy reasoning
- Explaining privacy risk
- Producing remediation recommendations
- Generating the structured investigation report

### Deterministic responsibilities

Python components are used for:

- Exact PII detection
- Exact redaction
- Policy-source extraction
- Validation

This avoids relying on an LLM for operations that can be performed more reliably with deterministic code.

For example, during early evaluation the LLM occasionally generated redactions such as:

```text
*********
```

instead of the required:

```text
[REDACTED-NRIC]
```

The architecture was therefore improved so the application layer enforces deterministic redaction.

Similarly, policy source filenames are extracted from actual retrieval tool results rather than trusting the LLM to reproduce them.

---

# 📦 Structured Outputs

Investigation results are validated using **Pydantic**.

A report contains fields such as:

```python
class InvestigationReport(BaseModel):
    risk_level: Literal["LOW", "MEDIUM", "HIGH"]

    pii_detected: list[str]

    policy_violations: list[str]

    policy_sources: list[str]

    explanation: str

    recommended_action: str

    redacted_log: str | None
```

This ensures the API returns a predictable schema instead of arbitrary LLM-generated text.

---

# 🌐 REST API

The application is exposed through FastAPI.

## Health Check

```http
GET /api/v1/health
```

Example response:

```json
{
  "status": "healthy"
}
```

---

## Create Investigation

```http
POST /api/v1/investigations
```

Example request:

```json
{
  "log": "Payment failed for customer S1234567A"
}
```

Example response:

```json
{
  "risk_level": "HIGH",
  "pii_detected": [
    "NRIC"
  ],
  "policy_violations": [
    "Exposure of highly sensitive personal information in application logs"
  ],
  "policy_sources": [
    "incident_policy.txt",
    "logging_policy.txt",
    "pii_policy.txt"
  ],
  "explanation": "The application log contains a Singapore NRIC, which is classified as highly sensitive personal information.",
  "recommended_action": "Redact NRIC from application logs and implement additional logging controls.",
  "redacted_log": "Payment failed for customer [REDACTED-NRIC]",
  "investigation_id": "c5efc5ca-ad8b-421f-bb04-6600fa7cae9e"
}
```

---

## Retrieve Investigation

```http
GET /api/v1/investigations/{investigation_id}
```

The prototype stores investigation results in memory and allows them to be retrieved using their generated ID.

---

# 🧪 Evaluation Framework

LLM applications require more than traditional unit tests because model behavior can vary between executions and models.

The project therefore contains a synthetic evaluation dataset covering:

- Individual PII types
- Multiple PII types
- Logs containing no PII
- False-positive scenarios
- Risk classification
- Policy retrieval
- Structured output generation
- Redaction

Example evaluation case:

```json
{
  "id": "case_01",
  "log": "Payment failed for customer S1234567A",
  "expected_pii": ["NRIC"],
  "expected_risk": "HIGH",
  "expected_policy_sources": [
    "pii_policy.txt",
    "incident_policy.txt"
  ],
  "expected_redacted_log": "Payment failed for customer [REDACTED-NRIC]"
}
```

The evaluation harness measures:

```text
PII accuracy
Risk accuracy
Policy grounding
Structured output success
Redaction accuracy
```

Run the evaluation with:

```bash
uv run python -m evaluation.evaluate
```

### Why evaluate the agent?

The evaluation suite helped identify real reliability issues during development.

For example, earlier versions occasionally:

- Generated inconsistent PII labels
- Produced incorrect risk classifications
- Invented policy source filenames
- Generated inconsistent redaction formats
- Failed structured tool calls with smaller LLMs

These failures informed changes to the system prompt and architecture.

This makes the evaluation framework part of the development process rather than only a final benchmark.

---

# 🧪 Testing

The project uses **pytest** for automated testing.

Tests cover components such as:

```text
tests/
├── test_api.py
├── test_pii.py
├── test_policy.py
└── test_remediation.py
```

### Unit tests

Unit tests verify:

- PII detection
- Redaction
- Policy retrieval
- Input validation

### API tests

FastAPI endpoints are tested using `TestClient`.

External LLM calls are mocked where appropriate so that automated tests do not depend on:

- Groq availability
- API rate limits
- Network connectivity
- Non-deterministic model responses

Run all tests:

```bash
uv run pytest -v
```

---

# 🐳 Docker

The complete backend can run inside a Docker container.

Build the image:

```bash
docker build -t ai-privacy-agent .
```

Run it:

```bash
docker run --env-file .env -p 8000:8000 ai-privacy-agent
```

The API will then be available at:

```text
http://localhost:8000
```

Interactive FastAPI documentation:

```text
http://localhost:8000/docs
```

---

# ⚙️ Running Locally

## 1. Clone the repository

```bash
git clone <repository-url>

cd ai-privacy-agent
```

## 2. Install dependencies

This project uses **uv** for Python dependency management.

```bash
uv sync
```

## 3. Configure environment variables

Create:

```text
.env
```

Add:

```env
GROQ_API_KEY=your_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
```

Never commit `.env` or API keys to source control.

## 4. Start the API

```bash
uv run uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# 📁 Project Structure

```text
ai-privacy-agent/
│
├── app/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── prompts.py
│   │   └── tools.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── rag/
│   │   └── retriever.py
│   │
│   ├── tools/
│   │   ├── pii.py
│   │   ├── policy.py
│   │   └── remediation.py
│   │
│   ├── config.py
│   └── main.py
│
├── data/
│   ├── pii_policy.txt
│   ├── logging_policy.txt
│   ├── incident_policy.txt
│   └── retention_policy.txt
│
├── evaluation/
│   ├── cases.json
│   └── evaluate.py
│
├── tests/
│   ├── test_api.py
│   ├── test_pii.py
│   ├── test_policy.py
│   └── test_remediation.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── Dockerfile
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core backend |
| FastAPI | REST API |
| Pydantic | Validation and structured outputs |
| LangChain | Agent orchestration and tool calling |
| Groq | LLM inference |
| ChromaDB | Vector storage / similarity retrieval |
| Hugging Face Embeddings | Policy embeddings |
| pytest | Automated testing |
| uv | Dependency management |
| Docker | Containerization |
| GitHub Actions | Continuous integration |

---

# 🔄 CI Pipeline

GitHub Actions automatically validates the project when code is pushed.

```text
Git Push
   ↓
GitHub Actions
   ↓
Install Python + dependencies
   ↓
Run pytest
   ↓
Build Docker image
   ↓
Pass / Fail
```

This ensures changes do not silently break the application.

---

# 💡 Key Engineering Decisions

### Why not use the LLM to detect PII?

PII such as NRICs, emails, phone numbers, and credit card numbers can be detected reliably using deterministic techniques.

Using an LLM for these cases would introduce unnecessary cost and non-determinism.

The LLM is instead used where contextual reasoning provides more value.

### Why use an agent?

Privacy investigation involves multiple capabilities:

```text
detect
→ retrieve evidence
→ reason
→ remediate
→ report
```

Tool calling allows the LLM to orchestrate these capabilities while keeping the individual operations modular.

### Why use RAG?

The LLM should not invent organizational privacy rules.

RAG allows the system to retrieve relevant policy information and ground its conclusions in external documents.

### Why combine AI and deterministic code?

Production AI systems should not use an LLM for every operation.

This project uses:

```text
LLM
→ reasoning and orchestration

Python
→ deterministic operations

RAG
→ external evidence

Pydantic
→ output validation

pytest + evaluation
→ reliability measurement
```

The result is a hybrid architecture that uses each component where it is most appropriate.

---

# ⚠️ Limitations

This project is a prototype built using synthetic data and synthetic organizational policies.

Current limitations include:

- Regex-based PII detection supports a limited number of entity types.
- Investigation storage is in-memory rather than persistent.
- Policy documents are synthetic.
- The evaluation dataset is intentionally small.
- LLM behavior can still vary between models and runs.
- API rate limits can interrupt large evaluation runs.
- The system is not intended for production security or compliance use.

---

# 🚀 Future Improvements

Potential extensions include:

- spaCy or transformer-based named entity recognition
- Database-backed investigation history
- Authentication and authorization
- More comprehensive privacy policies
- Larger evaluation datasets
- Agent tracing and observability
- Retrieval quality metrics
- Prompt/model comparison experiments
- Asynchronous investigation jobs
- Cloud deployment

---

# 🎯 What I Learned

This project explored how to move from a traditional ML/NLP pipeline toward a production-style AI engineering architecture.

Key areas included:

- Designing LLM agents
- Implementing tool calling
- Building RAG pipelines
- Working with embeddings and vector databases
- Designing structured LLM outputs
- Separating deterministic logic from LLM reasoning
- Evaluating non-deterministic AI systems
- Testing AI-backed APIs without making real LLM calls
- Building REST APIs with FastAPI
- Containerizing Python applications
- Setting up automated CI

One of the main lessons from the project was that building reliable AI systems is not simply about adding an LLM. It requires deciding **where an LLM is useful, where deterministic software is more appropriate, and how the two can work together reliably.**

---

## Disclaimer

This project uses **synthetic application logs and synthetic organizational policies only**.

