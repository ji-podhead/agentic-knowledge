---
okf_version: "1.0"
id: "okf-rag-gra-ontology-driven-graphrag"
title: "Ontology-Driven GraphRAG: From Chunks to a Validated Knowledge Graph"
topic: "general/retrieval-augmented-generation"
subtopic: "graphrag"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - graphrag
  - knowledge-graph
  - ontology
  - taxonomy
  - surrealdb
  - leiden
summary: "Turning flat chunks into an ontology-validated knowledge graph: triple extraction, Leiden communities, multi-hop reasoning with path validation, adaptive taxonomy growth."
---

# Ontology-Driven GraphRAG: From Chunks to a Validated Knowledge Graph

## Executive Summary

Classic RAG destroys structure: chunks are isolated units, and similarity cannot answer how things are related. GraphRAG rebuilds the topology as a knowledge graph; binding the extraction to an ontology keeps the graph precise instead of noisy. The result handles multi-hop questions, corpus-level summaries and explainable retrieval paths.

## Taxonomy vs. Ontology

A taxonomy classifies: a tree of categories, one home per document, rigid but instantly decidable — its job is excluding irrelevant domains with certainty. An ontology is a formal rule set of concepts, properties and relations (a medication TREATS a diagnosis; a sensor HAS_POINT in a room); its job is precise traversal. Industry-grade examples: SNOMED CT and ICD-10/LOINC for medicine, Brick Schema for buildings. A retrieval architecture needs both: the taxonomy for routing, the ontology for reasoning.

## The GraphRAG Pipeline

    1. Entity and relation extraction: an LLM reads text and emits triples
       (subject) -[predicate]-> (object), e.g. (Metformin) -[treats]-> (Diabetes)
    2. Hierarchical clustering: community detection (Leiden) groups related nodes;
       clusters get summaries at several abstraction levels
    3. Two search modes: local search navigates edges around a specific node
       (multi-hop detail); global search reads precomputed cluster summaries
       for corpus-wide questions

## Binding Extraction to the Ontology

Free-form extraction produces messy graphs. Constraint-based extraction binds the LLM to ontology classes, which guarantees a clean entity base. Semantic enrichment inherits properties along the ontology hierarchy (a node room-101 inherits everything an office-room is). Multi-hop reasoning with path validation lets the agent navigate the graph while the ontology validates the paths — preventing logically impossible conclusions. A building example: find all devices affected by the failure of pump X — the walk follows feeds/hasPoint/isLocationOf edges, validated by Brick semantics.

## Adaptive Taxonomy Growth

The ontology does not need manual curation forever. Every skill-gain event or tool invocation can trigger lightweight concept extraction; a candidate concept is deduplicated against existing nodes by embedding similarity (above roughly 0.92 cosine similarity it is the same concept), otherwise created and linked to its dimension root via broader/related/covers edges. Storage pattern: a graph-capable database (for example SurrealDB) holds concept nodes with embeddings plus relation tables (broader, related, covers, derives), with HNSW vector indexes on concept embeddings; Qdrant stays the scale-out store for raw chunk vectors.

## Conclusion

GraphRAG turns retrieval into navigation. Bind extraction to an ontology, cluster with Leiden, and serve global questions from community summaries while local questions walk validated paths. Keep the taxonomy for instant exclusion and let the ontology grow adaptively — precision without permanent manual curation.
