---
okf_version: "1.0"
id: "okf-rag-hyb-hybrid-search-rrf"
title: "Hybrid Retrieval: BM25, Vector Search and Reciprocal Rank Fusion"
topic: "general/retrieval-augmented-generation"
subtopic: "hybrid-retrieval"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - hybrid-retrieval
  - bm25
  - rrf
  - reranking
  - hyde
  - searxng
summary: "Combining keyword and vector retrieval with Reciprocal Rank Fusion (k=60), reranking, HyDE for zero-shot queries and multi-source web fetching fallbacks."
---

# Hybrid Retrieval: BM25, Vector Search and Reciprocal Rank Fusion

## Executive Summary

A single retrieval signal always fails somewhere: vector search drifts on rare identifiers, keyword search misses paraphrases. Hybrid retrieval runs both and fuses the rankings with Reciprocal Rank Fusion, then reranks a shortlist. On top of that, two boosters matter in practice: HyDE for zero-shot queries and a robust multi-fallback fetch chain for fresh web sources.

## Why Fusion Beats Either Signal

Keyword (BM25-style) ranking rewards exact term overlap; vector ranking rewards meaning. Rare error codes, product names and identifiers favor keyword; paraphrased questions favor vectors. Reciprocal Rank Fusion combines ranked lists without tuning scores:

    rrf_score(doc) = sum over lists of 1 / (k + rank_of_doc_in_list),   k = 60

k=60 dampens the influence of top ranks and is the standard default; it needs no score calibration between a BM25 rank and a cosine score. The pattern streams well: a RAG orchestrator can emit every stage (fetch, index, fuse, analyze) as NDJSON log lines while the pipeline runs.

## Reranking the Shortlist

Fusion produces a candidate set; a reranker orders the final context. Practical setup: take the top 10 candidates, rerank by cross-encoder or embedding-similarity scoring against the query, keep the best few chunks. Even a lightweight embedding-based reranker (embed query and candidate, cosine, sort) removes most of the junk the fusion stage let through.

## Global vs. Local Search

Two questions need two search modes. Local search answers specific, filtered questions: vector search plus payload filters (user_id, doc_type) within one collection. Global search answers corpus-level questions (common themes across all documents) and needs precomputed structure: community detection (Leiden) over the knowledge graph with per-cluster summaries the model can read instead of scanning everything. Query decomposition helps: split a question into a local fact lookup plus a global summary lookup.

## HyDE for Zero-Shot Queries

HyDE (Hypothetical Document Embeddings) lets the LLM generate a handful of hypothetical answer documents for the query, embeds those, and searches with the mean of the hypothetical embeddings. In specialized domains the generated pseudo-documents land closer to the real answer space than the raw question does — a cheap, zero-shot recall booster.

## Fetching Fresh Sources Reliably

Web ingestion needs a fallback chain, because every single fetcher fails eventually:

    1. direct fetch (httpx) plus HTML-to-Markdown conversion
    2. reader proxy (for example r.jina.ai) for JavaScript-heavy pages
    3. Wayback Machine lookup for dead or blocked URLs
    4. headless browser render as the last resort

Run the chain per URL with a shared browser instance, fetch independent URLs concurrently, and tag archived results. A self-hosted SearXNG instance in front of DuckDuckGo/Google/Brave gives multi-provider search as separate, budgetable tools.

## Conclusion

Fuse two weak signals into one strong ranking (RRF, k=60), rerank a shortlist, split global from local questions, and never depend on a single fetcher. These four habits turn a demo-grade retriever into a production-grade one.
