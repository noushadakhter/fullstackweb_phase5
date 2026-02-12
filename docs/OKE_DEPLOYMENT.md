# Oracle Container Engine (OKE) Deployment Guide for AI Todo Chatbot

Yeh guide aapko AI Todo Chatbot project ko Oracle Container Engine for Kubernetes (OKE) pe deploy karne mein madad karegi.

## 1. Prerequisites (Zaroori Tools)

Deploy karne se pehle, aapke paas yeh tools aur configurations honi chahiye:

-   **Oracle Cloud Infrastructure (OCI) CLI**: OCI resources ko manage karne ke liye.
    -   [Installation Guide](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/cliconcepts.htm)
-   **`kubectl`**: Kubernetes clusters ke saath interact karne ke liye.
    -   Agar aapke paas nahi hai, toh [yahan se install karein](https://kubernetes.io/docs/tasks/tools/install-kubectl/).
-   **`kubectl` configured for OKE**: Aapke OCI CLI aur `kubectl` ko OKE cluster ke saath communicate karne ke liye configure karna hoga.
    -   [Configuring `kubectl` for OKE](https://docs.oracle.com/en-us/iaas/Content/ContEng/Tasks/contengaccessingclustertutorial.htm)
-   **Helm**: Kubernetes applications ko deploy aur manage karne ke liye package manager.
    -   [Installation Guide](https://helm.sh/docs/intro/install/)
-   **Docker**: Docker images build karne ke liye.
    -   [Installation Guide](https://docs.docker.com/get-docker/)

## 2. OKE Cluster Setup (Agar Pehle Se Nahi Hai)

Agar aapke paas OKE cluster nahi hai, toh aapko pehle ek banana hoga.
-   [OKE Cluster Create karne ka official guide](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm)

## 3. Container Registry (Docker Images ke liye)

Aapko apne Docker images ko kisi container registry mein push karna hoga jahan se OKE unhe pull kar sake. Aap Oracle Container Registry (OCIR) ya Docker Hub jaisi koi public registry istemal kar sakte hain.

-   **Oracle Container Registry (OCIR)**: [Guide to use OCIR](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm)
-   **Docker Hub**: [Guide to use Docker Hub](https://docs.docker.com/docker-hub/)

## 4. Build aur Push Docker Images

Har microservice ke liye Docker images build karein aur unhe apni pasandida container registry pe push karein. `your-registry-username` aur `your-registry-url` ko apni information se badal dein.

```bash
# Example for Tasks Service
docker build -t your-registry-url/your-registry-username/tasks-service:latest -f services/tasks-service/Dockerfile .
docker push your-registry-url/your-registry-username/tasks-service:latest

# Example for API Gateway Service
docker build -t your-registry-url/your-registry-username/api-gateway:latest -f services/api-gateway/Dockerfile .
docker push your-registry-url/your-registry-username/api-gateway:latest

# Example for Frontend Service
docker build -t your-registry-url/your-registry-username/frontend-service:latest -f services/frontend/Dockerfile .
docker push your-registry-url/your-registry-username/frontend-service:latest

# Aur baaki sab services ke liye bhi aise hi karein
```

## 5. Helm Charts Configure Karein

Har service ke Helm chart (jo `helm/` directory mein hain) mein `values.yaml` file ko update karein. Ismein aapko apni Docker image ka naam aur tag provide karna hoga.

-   `helm/tasks-service/values.yaml` mein `image.repository` aur `image.tag` update karein.
-   `helm/api-gateway/values.yaml` mein `image.repository` aur `image.tag` update karein.
-   `helm/frontend/values.yaml` mein `image.repository` aur `image.tag` update karein.

**Example `helm/tasks-service/values.yaml` update:**

```yaml
image:
  repository: your-registry-url/your-registry-username/tasks-service
  tag: "latest"
```

## 6. Helm Se Deploy Karein

Ek baar jab aapne images build kar li hain aur Helm charts configure kar liye hain, toh ab aap services ko OKE pe deploy kar sakte hain.

```bash
# Tasks Service deploy karein
helm install tasks-service helm/tasks-service

# API Gateway Service deploy karein
helm install api-gateway helm/api-gateway

# Frontend Service deploy karein
helm install frontend-service helm/frontend

# Aur baaki sab services ke liye bhi install command run karein
```

## 7. Deployed Services Ko Access Karein

Services deploy hone ke baad, aap `kubectl get services` command se unki status dekh sakte hain. Frontend aur API Gateway jaise services ke liye LoadBalancer banaya jayega, jiske paas external IP address hoga jise aap web browser ya API client se access kar sakte hain.

```bash
kubectl get services -n default # Ya jis namespace mein deploy kiya hai
```

`EXTERNAL-IP` column mein aapko service ka IP address milega.

---
**Zaroori Note**: Yeh ek high-level guide hai. Har step mein aur bhi details ho sakti hain jo OCI aur Kubernetes ke official documentation mein milengi. Is constitution ko follow karte hue har service ko independently deploy karna hai.
