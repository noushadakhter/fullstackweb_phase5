# Phase IV: Todo AI Chatbot with Local Kubernetes Deployment

This project implements an AI-powered chatbot that manages todo tasks through natural language, following a strict Spec-Driven Development and Agentic Dev Stack workflow. This phase focuses on containerization and local Kubernetes deployment using Minikube and Helm charts.

## Project Structure

```
.
├── backend/                  # FastAPI backend and SQLModel models
│   ├── app/                  # Application logic (database, auth, API endpoints)
│   ├── migrations/           # Alembic database migrations
│   ├── .env.example          # Example environment variables for backend
│   ├── requirements.txt      # Python dependencies for backend
│   ├── main.py               # Main FastAPI application
│   ├── models.py             # SQLModel database models
│   └── Dockerfile            # Dockerfile for backend application
├── frontend/                 # Next.js frontend (basic chat UI)
│   ├── public/
│   ├── src/
│   │   ├── app/              # Next.js App Router pages
│   │   └── styles/           # Global styles (Tailwind CSS)
│   ├── .env.local.example    # Example environment variables for frontend
│   ├── package.json          # Node.js dependencies for frontend
│   ├── Dockerfile            # Dockerfile for frontend application
│   └── ...                   # Other Next.js config files
├── helm/                     # Helm charts for Kubernetes deployment
│   ├── backend/              # Helm chart for the backend application
│   └── frontend/             # Helm chart for the frontend application
├── mcp_server/               # Model Context Protocol (MCP) server with tools
│   ├── requirements.txt      # Python dependencies for MCP server
│   ├── main.py               # FastMCP application to expose tools
│   └── tools.py              # Definitions of MCP tools (add_task, list_tasks, etc.)
├── specs/                    # Project specifications, architecture, and plan
│   ├── phase3-todo-chatbot/
│   │   ├── spec.md           # Detailed project specification
│   │   ├── architecture.md   # High-level architecture diagram
│   │   └── plan.md           # Implementation plan and task breakdown
│   ├── phase4-kubernetes-deployment/ # Specs for Kubernetes deployment
│   │   ├── plan.md           # Plan for Kubernetes deployment
│   │   └── tasks.md          # Tasks for Kubernetes deployment
│   └── ...
└── README.md                 # Project README (this file)
```

## Mandatory Tech Stack

*   **Frontend**: Next.js
*   **Backend**: Python FastAPI
*   **AI Framework**: OpenAI Agents SDK
*   **MCP Server**: Official MCP SDK (via `fastmcp`)
*   **ORM**: SQLModel
*   **Database**: Neon Serverless PostgreSQL
*   **Authentication**: Better Auth (stubbed)
*   **Containerization**: Docker (Docker Desktop)
*   **Orchestration**: Kubernetes (Minikube)
*   **Package Manager**: Helm Charts

## Setup and Running the Project (Kubernetes Deployment)

This section outlines how to deploy the Todo AI Chatbot on a local Kubernetes cluster using Minikube and Helm.

### 1. Prerequisites

*   Python 3.11+
*   Node.js (LTS recommended) & npm
*   A Neon PostgreSQL database instance.
*   An OpenAI API Key.
*   **Docker Desktop**: Required for building and managing Docker images.
*   **Minikube**: For running a local Kubernetes cluster.
    *   **Installation**: Follow the official Minikube installation guide: [https://minikube.sigs.k8s.io/docs/start/](https://minikube.sigs.k8s.io/docs/start/)
*   **kubectl**: Kubernetes command-line tool. (Usually installed with Minikube)
*   **Helm**: Kubernetes package manager.
    *   **Installation**: Follow the official Helm installation guide: [https://helm.sh/docs/intro/install/](https://helm.sh/docs/intro/install/)

### 2. Configure Environment Variables

Create `.env` files for your backend and frontend as specified in their respective directories (`backend/.env.example` and `frontend/.env.local.example`).

*   **`backend/.env` content**:
    ```
    DATABASE_URL="postgresql+psycopg2://[USER]:[PASSWORD]@[ENDPOINT_HOSTNAME]/[DATABASE_NAME]?sslmode=require"
    OPENAI_API_KEY="sk-your-openai-key"
    MCP_SERVER_URL="http://mcp-server-service:8001" # Internal Kubernetes Service URL
    ```
    *(Note: `MCP_SERVER_URL` is updated for internal Kubernetes communication)*

*   **`frontend/.env.local` content**:
    ```
    NEXT_PUBLIC_API_BASE_URL="http://backend-service:8000" # Internal Kubernetes Service URL
    ```
    *(Note: `NEXT_PUBLIC_API_BASE_URL` is updated for internal Kubernetes communication)*

### 3. Build and Push Docker Images

You need to build Docker images for both backend and frontend and push them to a container registry (e.g., Docker Hub, Google Container Registry, etc.). Replace `your-dockerhub-username` with your actual username.

1.  **Build Backend Image:**
    ```bash
    docker build -t your-dockerhub-username/todo-backend:latest -f backend/Dockerfile .
    ```
2.  **Push Backend Image:**
    ```bash
    docker push your-dockerhub-username/todo-backend:latest
    ```
3.  **Build Frontend Image:**
    ```bash
    docker build -t your-dockerhub-username/todo-frontend:latest -f frontend/Dockerfile .
    ```
4.  **Push Frontend Image:**
    ```bash
    docker push your-dockerhub-username/todo-frontend:latest
    ```

### 4. Start Minikube

Ensure Docker Desktop is running.
```bash
minikube start
```

### 5. Deploy with Helm

1.  **Update Helm `values.yaml`**:
    Before deploying, update the `image.repository` and `image.tag` fields in `helm/backend/values.yaml` and `helm/frontend/values.yaml` to point to your pushed Docker images.

    Example `helm/backend/values.yaml` update:
    ```yaml
    image:
      repository: your-dockerhub-username/todo-backend
      tag: "latest"
    ```
    Do the same for `helm/frontend/values.yaml`.

2.  **Install Backend Helm Chart:**
    ```bash
    helm install todo-backend helm/backend
    ```
3.  **Install Frontend Helm Chart:**
    ```bash
    helm install todo-frontend helm/frontend
    ```
    *(Note: You might need to adjust service types (e.g., `NodePort` or `LoadBalancer`) in `helm/frontend/values.yaml` and `helm/backend/values.yaml` to access the services from outside the cluster, or use `minikube service todo-frontend` to get the URL.)*

### 6. Access the Application

*   To get the URL of the frontend service in Minikube:
    ```bash
    minikube service todo-frontend
    ```
    This command will open the frontend in your browser or provide you with the access URL.

## Deliverables Completed

1.  System design (`specs/phase3-todo-chatbot/spec.md`, `architecture.md`)
2.  Detailed specs (`specs/phase3-todo-chatbot/spec.md`)
3.  Implementation plan (`specs/phase3-todo-chatbot/plan.md`)
4.  Backend code (`backend/`)
5.  MCP server code (`mcp_server/`)
6.  Frontend code (`frontend/`)
7.  SQLModel models (`backend/models.py`)
8.  Alembic migrations (`backend/migrations/`)
9.  Env examples (`backend/.env.example`, `frontend/.env.local.example`)
10. Backend Dockerfile (`backend/Dockerfile`)
11. Frontend Dockerfile (`frontend/Dockerfile`)
12. Backend Helm Chart (`helm/backend/`)
13. Frontend Helm Chart (`helm/frontend/`)
14. README (`README.md`)