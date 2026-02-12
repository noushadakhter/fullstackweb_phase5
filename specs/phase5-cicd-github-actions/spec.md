# Phase V: CI/CD Pipeline Specification using GitHub Actions

## 1. Introduction
This document specifies the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the Todo AI Chatbot project, leveraging GitHub Actions. The pipeline aims to automate the software delivery process, including building, testing, containerization, and deployment to Kubernetes environments (both local Minikube and production cloud clusters). Emphasis is placed on efficiency, reliability, security, and integration with Git workflows.

## 2. Build Workflow

-   **Trigger:** The CI workflow SHALL be triggered on:
    -   `push` events to `main` branch.
    -   `pull_request` events targeting `main` branch.
    -   Manual `workflow_dispatch` for specific scenarios.
-   **Steps:**
    1.  **Checkout Code:** Fetch the repository content.
    2.  **Setup Environment:** Install Python dependencies, Node.js dependencies (for frontend), and necessary tools (e.g., Helm, kubectl, Dapr CLI).
    3.  **Run Unit/Integration Tests:** Execute all unit and integration tests for backend and frontend services.
    4.  **Code Linting & Formatting:** Enforce code style guides (e.g., Black for Python, ESLint for JavaScript/TypeScript).
    5.  **Vulnerability Scanning:** Scan application dependencies and Docker images for known vulnerabilities.
    6.  **Build Artifacts:** Build distributable artifacts (e.g., Python packages, frontend bundles).

## 3. Docker Image Build & Push

-   **Trigger:** This workflow SHALL be triggered after a successful build workflow on `push` to `main` branch.
-   **Steps:**
    1.  **Login to Container Registry:** Authenticate with the target Container Registry (e.g., Docker Hub, Azure Container Registry, Google Container Registry).
    2.  **Build Docker Images:** Build Docker images for each microservice (backend, frontend, consumers/workers) based on their respective `Dockerfile`s.
        -   Images SHALL be tagged with `main-latest` and the GitHub `SHA` or a version number.
    3.  **Push Docker Images:** Push the built Docker images to the authenticated Container Registry.
    4.  **Image Scanning (Deep):** Perform a more comprehensive security scan on the pushed images.

## 4. Kubernetes Deployment Automation

-   **Trigger:** The CD workflow SHALL be triggered after a successful Docker image build & push to `main` branch.
-   **Deployment Strategy (GitOps):**
    -   The CD pipeline SHALL update the Helm chart `values.yaml` in a dedicated GitOps repository (or within the main repository) to reference the newly built Docker image tag.
    -   A GitOps operator (e.g., Argo CD, Flux CD) running in the Kubernetes cluster SHALL detect this change in the GitOps repository and automatically synchronize the deployment to the target environment.
-   **Environments:** Separate deployment pipelines for:
    -   `Staging` (optional, but recommended for pre-production testing).
    -   `Production` (targeting AKS/GKE/Oracle clusters).
-   **Deployment Steps:**
    1.  **Checkout GitOps Repository:** Fetch the GitOps repository.
    2.  **Update Image Tag:** Modify the relevant `values.yaml` file (e.g., `helm/backend/values-production.yaml`) to use the new Docker image tag.
    3.  **Commit & Push:** Commit the changes to the GitOps repository. The GitOps operator then handles the deployment.
    4.  **Post-Deployment Verification:** Run smoke tests or integration tests against the deployed application.

## 5. Environment Secrets Management

-   **GitHub Secrets:** Sensitive credentials required by GitHub Actions workflows (e.g., Container Registry credentials, Cloud provider service principal credentials, Kubernetes context credentials) SHALL be stored as GitHub Secrets.
-   **Environment-Specific Secrets:** For Kubernetes deployments, secrets SHALL be managed by:
    -   **Cloud Secrets Managers:** Using Dapr's Secrets building block to retrieve runtime secrets from cloud-managed solutions (Azure Key Vault, Google Secret Manager, OCI Vault).
    -   **Kubernetes Secrets:** Stored as Kubernetes Secrets and referenced by Dapr or directly mounted into pods for non-Dapr related secrets. These secrets SHALL be encrypted at rest and accessed with strict RBAC.
-   **Principle of Least Privilege:** GitHub Actions workflows SHALL only have the minimum necessary permissions to perform their tasks.

## 6. Branch Protection Rules

-   **`main` Branch:**
    -   **Require pull request reviews:** At least one approving review is required.
    -   **Require status checks to pass before merging:**
        -   `CI Build Workflow` (all tests, linting, scanning)
        -   `Docker Image Build & Push Workflow`
    -   **Require branches to be up to date before merging:** Ensures latest changes are always included.
    -   **Include administrators:** Enforce rules for all users, including administrators.
    -   **Require linear history:** Prevent merge commits.
-   **`feature/*` Branches:** No specific protection rules beyond default.
-   **`release/*` Branches:** Similar protection to `main` but with stricter checks for release candidate builds.

## 7. Next Steps

-   Create `.github/workflows/ci.yaml` for build and test.
-   Create `.github/workflows/docker-build-push.yaml` for image building.
-   Create `.github/workflows/cd-production.yaml` for GitOps-based deployment.
-   Configure GitHub Environments and associated secrets.
-   Set up branch protection rules in GitHub repository settings.
-   Ensure all Helm charts support dynamic image tags and environment-specific `values.yaml` overrides.