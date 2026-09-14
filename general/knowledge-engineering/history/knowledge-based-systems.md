---
okf_version: "1.0"
id: "okf-kno-his-knowledge-based-systems"
title: "Knowledge-Based Systems: Facts, Rules and the Inference Machine"
topic: "general/knowledge-engineering"
subtopic: "history"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - knowledge-engineering
  - expert-systems
  - rule-based-systems
  - inference
  - history
summary: "The knowledge-based system playbook: fact base, rule base and inference machine — the ancestor of every curated RAG knowledge base and answer verifier."
---

# Knowledge-Based Systems: Facts, Rules and the Inference Machine

## Executive Summary

A knowledge-based system (KBS) represents knowledge explicitly and reasons over it. Its two central components — the knowledge base and the inference machine — map directly onto modern retrieval-augmented generation: the curated vector collection is the knowledge base, and the answer verifier is the inference machine. Understanding the classic playbook explains both why agentic RAG works and where it inherits its oldest failure modes.

## The Definition

A knowledge-based system is an intelligent information system in which knowledge is represented with explicit methods of knowledge representation and modeling, making it usable rather than merely storable. The term is often used synonymously with expert systems, but it is the wider family: rule-based systems, expert systems, and software agents all belong to it.

## Rule-Based Systems

A rule-based system consists of a fact base, a set of rules (production rules, business rules — also called the rule repository), and a control system with a rule interpreter: the inference machine, known in business software as the rule engine.

Inference, from the Latin inferre ("to carry in"), is the process of deriving new statements from given premises. Two directions matter: forward chaining derives conclusions from accumulated facts; backward chaining starts from a goal and works back to the facts that support it. Every modern rules engine is a descendant of this loop.

## Expert Systems

An expert system (XPS) is a program that supports humans in solving complex problems by deriving recommendations from a knowledge base — one of the classic attempts at implementing AI as a logical decision machine. The canon: DENDRAL inferring molecular structures, MYCIN recommending antibiotic therapy, XCON configuring computer systems at DEC at a scale that saved millions annually.

Expert systems worked because their domains were narrow and the knowledge could be written down. They stalled for the same reason: knowledge acquisition was manual, brittle and expensive, and the systems could not gracefully express uncertainty. The knowledge acquisition bottleneck is the oldest problem in applied AI.

## The Two Central Components

    Knowledge base:    the explicit, curated store of facts and rules
    Inference machine: the interpreter that derives new statements from it

Everything else — explanation facilities, acquisition tools, user interfaces — is accessory. Any architecture that claims to reason over knowledge must answer where its knowledge base lives and what plays the inference machine.

## Why It Matters for Modern RAG

The mapping is direct. The curated vector collection with ontology-shaped metadata is the knowledge base, rebuilt for embeddings. The answer verifier is the inference machine, rebuilt for evidence chains: an answer is accepted only if it follows from the documents that were actually retrieved. The knowledge acquisition bottleneck was the classic killer — and LLM-driven ingestion pipelines (intelligent chunking, entity extraction, reranking) are the first credible attack on it. Finally, the classic failure mode of expert systems — confidently wrong answers outside their competence — now has a new name: hallucination.

## Conclusion

The knowledge-based system playbook is not history to outgrow; it is the design that agentic RAG rediscovers. Keep the knowledge explicit and curated, keep an interpreter that derives and validates, and treat knowledge acquisition as the primary engineering cost. The systems that respect these three constraints are the ones that stop hallucinating.
