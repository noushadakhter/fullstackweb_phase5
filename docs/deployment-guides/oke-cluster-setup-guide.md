# Oracle Kubernetes Engine (OKE) Cluster Setup Guide

This guide provides a high-level overview of setting up an Oracle Kubernetes Engine (OKE) cluster. For detailed and up-to-date instructions, always refer to the official Oracle Cloud Infrastructure (OCI) documentation.

## Prerequisites

*   An Oracle Cloud Infrastructure (OCI) account.
*   Familiarity with OCI Console and basic networking concepts.
*   OCI CLI installed and configured locally (optional, but recommended for advanced users).

## High-Level Steps

1.  **Log in to OCI Console:**
    Access the OCI Console using your account credentials.

2.  **Create a Virtual Cloud Network (VCN):**
    OKE clusters require a VCN with subnets for worker nodes and load balancers.
    *   Navigate to **Networking -> Virtual Cloud Networks**.
    *   Click "Create VCN" and follow the wizard to set up a VCN with appropriate public and private subnets, routing tables, and security lists/network security groups.

3.  **Create an OKE Cluster:**
    *   Navigate to **Developer Services -> Kubernetes Clusters (OKE)**.
    *   Click "Create Cluster".
    *   **Choose "Quick Create"** for a simpler setup, or "Custom Create" for more control.
    *   **Cluster Name:** Provide a descriptive name for your cluster.
    *   **Kubernetes Version:** Select a supported Kubernetes version.
    *   **Node Pools:** Configure your worker nodes. For the "Always Free" tier, specify:
        *   **Node Shape:** Choose an appropriate VM.Standard.E2.1.Micro (for Always Free, if available for OKE).
        *   **Number of Nodes:** 1 (for Always Free).
        *   **Boot Volume Size:** Default or adjust as needed.
    *   **Networking:** Select your previously created VCN and appropriate subnets for worker nodes and load balancers.
    *   **Review and Create:** Review your configuration and click "Create Cluster".

4.  **Configure `kubectl` Access:**
    Once the cluster is provisioned (this can take several minutes):
    *   From the OKE cluster details page, click "Access Kubeconfig".
    *   Follow the instructions provided to download the kubeconfig file and merge it with your local `~/.kube/config` file.
    *   Test your `kubectl` connectivity:
        ```bash
        kubectl get nodes
        ```
        You should see your OKE worker node(s) listed.

## Next Steps

After setting up your OKE cluster and configuring `kubectl`, you can proceed with deploying Dapr and other infrastructure components, followed by your application services.
