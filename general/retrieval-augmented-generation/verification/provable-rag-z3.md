---
okf_version: "1.0"
id: "okf-rag-ver-provable-rag-z3"
title: "Provable RAG: Verifying Retrieval-Augmented Answers with Z3"
topic: "general/retrieval-augmented-generation"
subtopic: "verification"
status: "published"
visibility: "public"
created_at: "2026-09-16"
tags:
  - verification
  - z3
  - smt
  - proof-of-search
  - hallucination
  - trust
summary: "A referee-verified RAG pipeline: evidence provenance checks, prior-knowledge UNSAT detection of answer leakage, and Z3-verified reasoning chains with scored outcomes."
---

# Provable RAG: Verifying Retrieval-Augmented Answers with Z3

## Executive Summary

Retrieval quality is not answer trustworthiness. A fluent answer built on retrieved chunks is still a claim; only a proof is a guarantee. Provable RAG adds a referee layer around retrieval and generation: every search step is logged, and an SMT solver (Z3) formally checks that the conclusion was derived from the actual search results — and not from prior knowledge.

## The Referee Pattern

A referee agent controls the information flow: the answering agent has no direct internet access, only a sandboxed search session through the referee proxy. The referee logs every query, every result snippet and every token; it enforces budgets (maximum searches, maximum tokens) and feeds the collected evidence into the verifier. Verification is architectural, not prompt-based — the agent cannot talk its way around it.

## The Three Formal Checks

    Check 1 — Evidence Source Check:
      every cited evidence item must be traceable to the logged search corpus.
      Evidence that appears nowhere in the search results -> CHEATING.

    Check 2 — Prior Knowledge Check (the interesting one):
      encode the declared prior knowledge as axioms and ask Z3 whether the
      thesis alone is satisfiable from it. SAT means the answer was derivable
      without any search -> the search was theater -> CHEATING.
      UNSAT means the search was genuinely necessary.

    Check 3 — Reasoning Chain Check:
      model each evidence item as a boolean axiom set to TRUE and require the
      conclusion to follow:

        solver.add(*[v == True for v in evidence_vars])
        solver.add(Implies(And(*evidence_vars), conclusion_var))
        result = solver.check()   # sat -> VERIFIED, otherwise INVALID

## Status Codes and Scoring

| Status | Meaning |
|---|---|
| VERIFIED | Conclusion follows from evidence; the search was necessary |
| INVALID | Evidence does not support the conclusion |
| INCOMPLETE | Not enough evidence collected |
| CHEATING | Evidence fabricated, or answer derivable from prior knowledge |
| ERROR | Verifier exception (falls back to heuristic scoring) |

Outcomes are scored, not just flagged: search efficiency (optimal vs. actual searches), token efficiency, path efficiency (dead-end penalty), a reasoning-coherence score (PoT) and evidence quality combine into a final score. Ties break toward fewer searches and fewer tokens.

## The Z3-DSL Pattern for LLM Outputs

A robust way to make LLM reasoning checkable: the model emits a JSON program for an SMT solver instead of free-text reasoning — sorts, functions, constants, a knowledge base, rules and exactly one verification condition. The interpreter runs it through an AST sandbox (no imports, no dunder access, empty builtins), resolves sort dependencies topologically, and interprets the result as SAT = true, UNSAT = false. Entailment is checked via negation: KB and not-phi must be UNSAT for KB to entail phi. Failed programs go back to the model with the error trace, up to a small retry budget — a self-healing loop that turns hallucinated programs into valid ones.

## Beyond the Single Proof

The proof family extends to the whole agent loop. PoT (Proof of Thought) scores reasoning coherence and acts as a quality gate: results below the threshold are retried, and only artifacts above the threshold become persistent memory — which prevents poisoned memories from contaminating future retrieval. PoD (Proof of Delivery) attaches a signed certificate (Ed25519, result and parameter hashes) to every tool call, making delivery auditable. Trust weights make the hierarchy explicit: a proven result carries maximum weight, a search-sourced claim less, a bare assertion least.

## Limits and When to Use It

Z3 verifies what can be encoded: boolean, symbolic and bounded-arithmetic claims. Open-ended natural-language judgments stay heuristic and are handled by scoring, not proof. The overhead (referee session, solver calls) is justified where answers carry consequences — benchmarks, compliance, autonomous pipelines — and unnecessary for casual chat. A pragmatic rollout: verify the answers that get persisted, cite the proof status alongside every stored fact.

## Conclusion

Provable RAG replaces "the model says it found it" with a formal guarantee: evidence must come from the search, the search must have been necessary, and the conclusion must follow from the evidence. Combined with a quality gate before memory writes, the pipeline stops accumulating unverified beliefs — the root cause of compounding hallucination.
