---
okf_version: "1.0"
id: "okf-sec-gua-keyhacks-openai-cti-summarizer"
title: "Cyber Security Validation & Intelligence: KeyHacks Leaked API Key Verification & OpenAI CTI Summarization"
topic: "general/security-and-observability"
subtopic: "guardrails-and-firewalls"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - keyhacks
  - cti
  - threat-intelligence
  - api-key-validation
  - openai
  - fastapi
summary: "Technical guide covering KeyHacks methodologies for programmatic leaked API key validation and OpenAI-driven Cyber Threat Intelligence (CTI) report summarization."
---

# Cyber Security Validation & Intelligence: KeyHacks Leaked API Key Verification & OpenAI CTI Summarization

## Executive Summary

Security Operations (SecOps) teams face two continuous operational challenges: validating whether credentials leaked in public repositories or bug bounty disclosures are active, and processing vast volumes of unstructured Cyber Threat Intelligence (CTI) reports.

This document details two specialized security automation specifications: **`keyhacks`** (a collection of lightweight, non-destructive API verification signatures) and **`openai-cti-summarizer`** (a FastAPI microservice utilizing OpenAI LLMs to extract structured Indicators of Compromise [IoCs] and executive summaries from threat reports).

---

## 1. KeyHacks API Key Verification Signatures

`keyhacks` provides minimalistic cURL and Python patterns to test leaked tokens without causing destructive side effects.

### 1.1 Signature Verification Matrix

```bash
# Algolia Search API Key Verification
curl -X GET "https://YOUR_APPLICATION_ID.algolia.net/1/keys" \
     -H "X-Algolia-API-Key: LEAKED_API_KEY" \
     -H "X-Algolia-Application-Id: YOUR_APPLICATION_ID"

# Slack Bot Token Verification
curl -X POST "https://slack.com/api/auth.test" \
     -H "Authorization: Bearer xoxb-LEAKED_SLACK_TOKEN"

# Asana Personal Access Token Verification
curl -X GET "https://app.asana.com/api/1.0/users/me" \
     -H "Authorization: Bearer LEAKED_ASANA_TOKEN"
```

---

## 2. OpenAI CTI Threat Report Summarizer (`openai-cti-summarizer`)

The CTI summarizer uses FastAPI and Pydantic schema enforcing to transform unstructured text into validated JSON containing threat summaries and extracted IoCs (IPv4, Domains, Hashes).

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI(title="CTI Report Summarizer")
client = OpenAI()

class CTIAnalysisRequest(BaseModel):
    report_text: str

class CTIAnalysisResponse(BaseModel):
    executive_summary: str
    target_industries: list[str]
    iocs_ip: list[str]
    iocs_domain: list[str]
    iocs_md5: list[str]

@app.post("/api/v1/analyze", response_model=CTIAnalysisResponse)
async def analyze_cti_report(req: CTIAnalysisRequest):
    system_prompt = (
        "You are an expert Cyber Threat Intelligence (CTI) analyst. "
        "Analyze the provided report text and return a JSON object with: "
        "executive_summary, target_industries, iocs_ip, iocs_domain, and iocs_md5."
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.report_text}
            ]
        )
        return CTIAnalysisResponse.model_validate_json(completion.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Sources & References

- [https://github.com/ji-podhead/keyhacks](https://github.com/ji-podhead/keyhacks)
- [https://github.com/ji-podhead/openai-cti-summarizer](https://github.com/ji-podhead/openai-cti-summarizer)
