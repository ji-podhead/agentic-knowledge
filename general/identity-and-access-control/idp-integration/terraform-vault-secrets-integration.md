---
okf_version: "1.0"
id: "okf-ide-idp-terraform-vault-secrets-integration"
title: "Zero-Trust Infrastructure Provisioning with Terraform & HashiCorp Vault AppRole Secrets Ingestion"
topic: "general/identity-and-access-control"
subtopic: "idp-integration"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - terraform
  - vault
  - approle
  - zero-trust
  - secrets-management
summary: "Technical guide for integrating Terraform with HashiCorp Vault via AppRole authentication, enabling dynamic secret generation and zero hardcoded credentials in IAC pipelines."
---

# Zero-Trust Infrastructure Provisioning with Terraform & HashiCorp Vault AppRole Secrets Ingestion

## Executive Summary

Hardcoding cloud provider API keys or database passwords in Terraform code or `.tfvars` files poses severe security risks. A Zero-Trust Infrastructure-as-Code (IaC) pipeline delegates credential issuance to a centralized secrets engine such as **HashiCorp Vault**.

This specification outlines the integration pattern where Terraform runners authenticate against Vault using **AppRole** authentication, fetch short-lived dynamic credentials (AWS STS tokens, PostgreSQL database leases, SSH certificates), and execute infrastructure changes without static secrets landing on developer workstations or CI/CD runners.

---

## 1. Authentication & Provisioning Flow

```
+------------------+     1. Auth (RoleID + SecretID)   +-------------------+
| Terraform Runner | --------------------------------> | HashiCorp Vault   |
| (CI/CD Pipeline) | <-------------------------------- | (AppRole Engine)  |
+--------+---------+          2. Vault Token           +---------+---------+
         |                                                       |
         | 3. Read Dynamic Credentials (KV v2 / AWS Engine)      |
         +------------------------------------------------------>|
         | <-----------------------------------------------------+
         | 4. Issue Short-Lived Token (TTL: 15m)
         |
+--------v---------+
| Cloud / Database |
| Infrastructure   |
+------------------+
```

---

## 2. Vault AppRole & Least-Privilege Policy Setup

### 2.1 Defining Least-Privilege Policy (`terraform-policy.hcl`)

```hcl
# Allow reading infrastructure dynamic credentials
path "secret/data/infrastructure/*" {
  capabilities = ["read"]
}

# Allow issuing dynamic short-lived database roles
path "database/creds/terraform-db-role" {
  capabilities = ["read"]
}
```

### 2.2 Provisioning the AppRole

```bash
# Enable AppRole engine
vault auth enable approle

# Mount policy and create role
vault policy write terraform-runner terraform-policy.hcl
vault write auth/approle/role/terraform-runner \
    secret_id_ttl=60m \
    token_ttl=15m \
    token_max_ttl=30m \
    policies="terraform-runner"

# Read Role ID and generate Secret ID
ROLE_ID=$(vault read -format=json auth/approle/role/terraform-runner/role-id | jq -r '.data.role_id')
SECRET_ID=$(vault write -f -format=json auth/approle/role/terraform-runner/secret-id | jq -r '.data.secret_id')
```

---

## 3. Terraform Vault Provider Integration

### 3.1 Provider Configuration (`providers.tf`)

```hcl
terraform {
  required_providers {
    vault = {
      source  = "hashicorp/vault"
      version = "~> 3.20.0"
    }
  }
}

provider "vault" {
  address = var.vault_address

  auth_login {
    path = "auth/approle/login"

    parameters = {
      role_id   = var.vault_role_id
      secret_id = var.vault_secret_id
    }
  }
}
```

### 3.2 Consuming Dynamic Secret Data (`main.tf`)

```hcl
data "vault_generic_secret" "db_credentials" {
  path = "secret/infrastructure/database"
}

resource "postgresql_role" "app_user" {
  name     = data.vault_generic_secret.db_credentials.data["username"]
  password = data.vault_generic_secret.db_credentials.data["password"]
  login    = true
}
```

---

## 4. Security Audit & Best Practices

- [x] **Zero Hardcoded Secrets**: Ensure `Gitleaks` or `Semgrep` static analysis scans verify no raw passwords or token strings exist in `.tf` files.
- [x] **Short-Lived Token Lease**: Set maximum TTL on AppRole tokens to <= 30 minutes.
- [x] **State File Encryption**: Configure encrypted S3/GCS backends with KMS server-side encryption since state files hold resolved dynamic secrets.
