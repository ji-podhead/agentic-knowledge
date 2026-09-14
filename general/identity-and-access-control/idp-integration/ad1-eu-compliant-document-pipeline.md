---
okf_version: "1.0"
id: "okf-ide-idp-ad1-eu-compliant-document-pipeline"
title: "ad1 Platform: EU GDPR-Compliant Automated Email & Document Processing Architecture"
topic: "general/identity-and-access-control"
subtopic: "idp-integration"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - ad1
  - gdpr
  - eu-compliance
  - postgresql
  - mcp-tools
  - document-processing
summary: "Technical architectural specification for ad1, an EU GDPR-compliant platform for automated email ingestion, document extraction, and PostgreSQL storage."
---

# ad1 Platform: EU GDPR-Compliant Automated Email & Document Processing Architecture

## Executive Summary

Automated enterprise document extraction and email processing within the EU requires strict adherence to data protection regulations (GDPR / DSGVO), credential isolation, and auditable data retention policies.

The **ad1 platform** delivers a modular, containerized architecture combining OAuth2 Gmail/IMAP ingestion, PostgreSQL relational storage, and Model Context Protocol (MCP) tool integrations for secure AI-driven email and attachment processing.

---

## 1. System Architecture & Flow

```
Email Source (Gmail API / IMAP)
             |
             v OAuth2 Authentication Layer
+-------------------------------------------------------------------+
| ad1 Ingestion & Session Manager                                   |
| (Encrypted OAuth Tokens, GAIA Service Account Isolation)          |
+-----------------------------------+-------------------------------+
                                    | Raw Payload Stream
                                    v
+-------------------------------------------------------------------+
| ad1 Backend Processing Core                                       |
|  1. HTML Sanitization & Body Text Normalization                   |
|  2. Attachment Extraction & Virus Scanning                        |
|  3. PostgreSQL Relational Persistence                             |
+-----------------------------------+-------------------------------+
                                    | MCP JSON-RPC
                                    v
+-------------------------------------------------------------------+
| MCP AI Agent Layer                                                |
| (Exposes send_email, list_unprocessed, extract_document_data)    |
+-------------------------------------------------------------------+
```

---

## 2. PostgreSQL Relational Schema Definition

```sql
-- Enforce strict email processing state
CREATE TYPE processing_status_enum AS ENUM ('UNPROCESSED', 'PROCESSING', 'COMPLETED', 'FAILED');

CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    sender VARCHAR(320) NOT NULL,
    recipient VARCHAR(320) NOT NULL,
    subject TEXT,
    body_text TEXT,
    received_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status processing_status_enum DEFAULT 'UNPROCESSED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attachments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID REFERENCES emails(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    content_type VARCHAR(100),
    file_size_bytes BIGINT,
    sha256_hash VARCHAR(64) NOT NULL
);
```

---

## 3. MCP Tool Interface Reference

### 3.1 `extract_document_data`
Extracts key-value fields (e.g. invoice numbers, tax amounts, line items) from attached PDF or PNG documents.

```json
{
  "name": "extract_document_data",
  "description": "Parses email attachment PDF/PNG and returns structured JSON fields.",
  "parameters": {
    "type": "object",
    "properties": {
      "attachment_id": { "type": "string" },
      "target_schema": { "type": "string", "enum": ["INVOICE", "CONTRACT", "RECEIPT"] }
    },
    "required": ["attachment_id", "target_schema"]
  }
}
```

---

## Sources & References

- [https://github.com/ji-podhead/ad1](https://github.com/ji-podhead/ad1)
