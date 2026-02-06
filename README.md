# Sagi Lab - AI-Powered Automated Malware Triage

**Sagi Lab** is an intelligent security operations platform designed to automate the triage, investigation, and analysis of security alerts. By combining the reasoning capabilities of Large Language Models (LLMs) with authoritative Threat Intelligence (VirusTotal), Sagi Lab reduces alert fatigue and provides actionable investigations in seconds.

## 🚀 Key Features

*   **Automated Triage Workflow**: A robust graph-based workflow (LangGraph) that orchestrates the entire analysis process:
    1.  **Classification**: Determines alert type and category (e.g., Ransomware, C2).
    2.  **MITRE ATT&CK Mapping**: Maps activity to specific Tactics and Techniques.
    3.  **Entity Extraction**: Identifies IPs, Domains, URLs, Hashes, and Accounts.
    4.  **Threat Intelligence**: Automatically queries VirusTotal to validate IOCs.
    5.  **AI Analysis**: Synthesizes all data to generate a final verdict and investigation steps.
*   **Interactive Dashboard**: Real-time visualization of alert volume, severity, and threat landscape.
*   **Deep Analysis**: "Thinking" models (e.g., Qwen-QwQ) provide transparent reasoning for every decision.
*   **Modern Stack**: Built for performance and developer experience.

## 🛠 Technology Stack

### Backend
*   **Framework**: FastAPI (Python 3.10+)
*   **Database**: PostgreSQL
*   **ORM**: SQLAlchemy (Async)
*   **AI Orchestration**: LangChain & LangGraph
*   **LLM Provider**: Qwen / DeepSeek (via OpenAI-compatible API)
*   **Threat Intel**: VirusTotal API

### Frontend
*   **Framework**: React 18 (Vite)
*   **Language**: TypeScript
*   **Styling**: TailwindCSS
*   **Visualizations**: Recharts
*   **Markdown**: React-Markdown (for analysis reports)

### Infrastructure
*   **Containerization**: Docker & Docker Compose
*   **Reverse Proxy**: Nginx (Production)

## 🏁 Getting Started

### Prerequisites
*   Docker & Docker Compose
*   VirusTotal API Key
*   LLM API Key (e.g., DeepSeek, Qwen, or OpenAI)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-org/sagi-lab.git
    cd sagi-lab
    ```

2.  **Configure Environment Variables**
    Create a `.env` file in the root directory:
    ```ini
    # Database
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your_secure_password
    POSTGRES_DB=sagi_db

    # AI / LLM
    LLM_API_BASE=https://api.your-llm-provider.com/v1
    LLM_API_KEY=sk-your-api-key
    LLM_MODEL=qwq-32b
    LLM_ENABLE_THINKING=true

    # Threat Intelligence
    VIRUSTOTAL_API_KEY=your-virustotal-api-key
    ```

3.  **Start the Application**
    ```bash
    docker-compose up --build
    ```

4.  **Access the Platform**
    *   **Frontend**: http://localhost:5173
    *   **Backend API**: http://localhost:8081/docs

## 🧪 Development Workflow

*   **Frontend**: The Docker container runs in `dev` mode with hot-reloading enabled. Edits to `frontend/src` will reflect immediately.
*   **Backend**: The backend API is available at `http://localhost:8081`. The Swagger UI (`/docs`) is great for testing endpoints manually.

## 📂 Project Structure

```
sagi-lab/
├── backend/            # FastAPI Application
│   ├── app/
│   │   ├── api/        # API Endpoints
│   │   ├── core/       # Config & Security
│   │   ├── db/         # Database Models & Session
│   │   ├── models/     # SQLAlchemy Models
│   │   ├── pkg/        # Utilities (Logger, VT Client)
│   │   ├── schemas/    # Pydantic Schemas
│   │   ├── services/   # Business Logic
│   │   └── triage/     # LangGraph Triage Workflow
│   │       ├── nodes/  # Workflow Steps (Classify, Analyze...)
│   │       └── prompts/# System Prompts
├── frontend/           # React Application
│   ├── src/
│   │   ├── components/ # UI Components
│   │   ├── services/   # API Client
│   │   └── types/      # TypeScript Definitions
├── docker-compose.yml  # Container Orchestration
└── .env                # Environment Config
```

## 🛡 License

[MIT](LICENSE)
