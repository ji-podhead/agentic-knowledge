---
okf_version: "1.0"
id: "okf-age-fra-evolution-of-ai-planning-goap-pddl-llm"
title: "Evolution of AI Planning: From GOAP State Machines to Behavior Trees, PDDL & LLM Interfaces"
topic: "general/agent-systems-and-browser-automation"
subtopic: "framework-evaluations"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - ai-planning
  - goap
  - pddl
  - behavior-trees
  - ros2
  - llm-interface
  - robotics
summary: "Technical architectural evaluation of the evolution of AI planning: from GOAP in game AI to multi-layered robotics stacks combining Behavior Trees, PDDL formal solvers, and LLMs."
---

# Evolution of AI Planning: From GOAP State Machines to Behavior Trees, PDDL & LLM Interfaces

## Executive Summary

Autonomous task execution has evolved beyond complex Finite State Machines (FSMs) and "state spaghetti." A historical milestone was **Goal-Oriented Action Planning (GOAP)**, popularized in game AI (such as *F.E.A.R.*), which dynamically synthesized action sequences to achieve goal states.

Modern robotics and autonomous AI agent architectures have matured into a **three-layered hybrid planning stack**: combining **Behavior Trees** for reactive control, **Formal Solvers (PDDL)** for multi-step strategic planning, and **Large Language Models (LLMs)** as natural language interface translation layers.

---

## 1. Multi-Layered Hybrid Planning Architecture

```
Human Natural Language Instruction ("Clean up the table")
                           |
                           v
+-------------------------------------------------------------------+
| 3. Interface Layer: Large Language Models (LLMs)                  |
| (Translates natural language into structured PDDL domain/problem) |
+-----------------------------------+-------------------------------+
                                    | Structured PDDL Domain
                                    v
+-------------------------------------------------------------------+
| 2. Strategic Layer: Formal Solvers (PDDL / ROSPlan)               |
| (Generates provably optimal multi-step action sequence)          |
+-----------------------------------+-------------------------------+
                                    | Action Sequence Plan
                                    v
+-------------------------------------------------------------------+
| 1. Execution Layer: Behavior Trees (BehaviorTree.CPP / ROS 2)     |
| (Executes moment-to-moment reactive skill loops & neural policies)|
+-------------------------------------------------------------------+
```

---

## 2. Technical Stack Breakdown

### 2.1 Execution Layer: Behavior Trees
For reactive, real-time control, Behavior Trees have become the industry standard in ROS 2 (e.g., `BehaviorTree.CPP`). They manage tick execution, fallback branches, and skill orchestration (where individual leaf nodes execute sub-symbolic neural network control policies).

### 2.2 Strategic Layer: Formal Planners (PDDL)
For complex multi-step tasks, planning uses the **Planning Domain Definition Language (PDDL)**. Dedicated solvers (such as ROSPlan) generate optimal plan graphs that satisfy pre-conditions and post-effects without search space explosion.

### 2.3 Interface Layer: Large Language Models (LLMs)
Rather than replacing deterministic planners, LLMs act as natural language interfaces. The LLM parses high-level, ambiguous human instructions and translates them into formal PDDL domain definitions, passing them to verified PDDL solvers for execution by the Behavior Tree.

---

## Sources & References

- [https://www.linkedin.com/pulse/evolution-ai-planning-from-games-llm-driven-robotics-leonardo-j--kdkie/](https://www.linkedin.com/pulse/evolution-ai-planning-from-games-llm-driven-robotics-leonardo-j--kdkie/)
- [https://github.com/BehaviorTree/BehaviorTree.CPP](https://github.com/BehaviorTree/BehaviorTree.CPP)
- [https://github.com/KCL-Planning/ROSPlan](https://github.com/KCL-Planning/ROSPlan)
