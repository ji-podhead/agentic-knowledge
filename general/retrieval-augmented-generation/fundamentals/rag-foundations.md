---
okf_version: "1.0"
id: "okf-rag-fun-rag-foundations"
title: "RAG Foundations: Retrieval as a Precision Filter, Not a Vending Machine"
topic: "general/retrieval-augmented-generation"
subtopic: "fundamentals"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - retrieval-augmented-generation
  - rag
  - vector-search
  - qdrant
  - embeddings
summary: "Core RAG concepts: vector search with payload filters, curated vs instance ingestion, and RAG as a synthesis engine between knowledge base and instance data."
---

# RAG Foundations: Retrieval as a Precision Filter, Not a Vending Machine

## Executive Summary

Retrieval-Augmented Generation grounds an LLM in facts it was never trained on. The failure mode of naive RAG is treating retrieval as a black box; the working pattern treats the vector database as a precision filter: semantic search over embeddings, sharpened by structured payload metadata, feeding a generation step that cites what it used.

## The Three Steps

    Retrieval:    query the vector store (semantic similarity, optional metadata filters)
    Augmentation: pack the results together with the question into the prompt
    Generation:   the LLM reads the context and answers in natural language

Vector search represents every object as a vector and returns nearest neighbors (cosine similarity). Semantic search understands intent beyond keywords; historically via knowledge graphs, thesauri and word nets, today mostly via embeddings. Fuzzy search (Levenshtein distance) still matters for identifiers, error codes and names.

## Embeddings Are Holistic, Entities Are Selective

Document embeddings translate whole text into a vector space that captures meaning; the output is a list of vectors and it is holistic — it does not isolate single tokens. Entity extraction is the opposite: it finds and labels the specific things in text (names, organizations, variables) and ignores the rest. A production RAG needs both: embeddings for recall, entities and structured metadata for precision.

## Payloads Are the Primary Filter

A naive implementation relies on cosine similarity alone. The robust pattern stores rich payload metadata with every vector (for example user_id, document_id, doc_type, created_at) and uses metadata as the primary, exact filter — the vector search then ranks within an already-correct subset. Qdrant implements this with payload filters and HNSW indexes; per-user isolation becomes a filter clause, not an application-layer patch.

## Two Ingestion Processes, One Synthesis Engine

    Process A — build the knowledge base (expensive once, reused forever):
      intelligent chunking (LLM-assisted, semantic boundaries) ->
      entity extraction per chunk -> relevance reranking (drop the junk) ->
      embedding and storage of high-value chunks only

    Process B — ingest instance data (cheap, repeatable):
      targeted metadata extraction against the ontology schema ->
      simple chunking -> embedding and storage with rich payload

RAG is the synthesis engine between the two: precise, filtered queries against instance data, enriched with deep context from the curated knowledge base. A medical assistant example: patients_data collection (ICD-10 and LOINC coded, per patient) plus medical_knowledge collection (curated guidelines), with a PubMed search tool closing the gap to current research. The same architecture swaps the ontology for another domain — SNOMED for medicine, Brick Schema for buildings — which is what makes the platform domain-agnostic.

## Conclusion

Treat retrieval as a precision filter: chunk on real boundaries, embed, but let structured metadata do the exact filtering. Invest once in a curated knowledge base (Process A), keep instance ingestion cheap (Process B), and let generation cite what it actually used. Everything downstream — reranking, GraphRAG, verification — builds on this foundation.
