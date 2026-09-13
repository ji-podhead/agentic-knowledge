---
okf_version: "1.0"
id: "okf-llm-rou-sanfis-pytorch-neuro-fuzzy-architecture"
title: "State-Adaptive Neuro-Fuzzy Inference Systems (S-ANFIS) in PyTorch for Financial & Algorithmic Routing"
topic: "general/llm-orchestration-and-routing"
subtopic: "routing-algorithms"
status: "published"
visibility: "public"
created_at: "2026-09-14"
tags:
  - sanfis
  - anfis
  - neuro-fuzzy
  - pytorch
  - routing-algorithms
  - machine-learning
summary: "Technical specification and PyTorch implementation architecture for State-Adaptive Neuro-Fuzzy Inference Systems (S-ANFIS) decoupling premise states from consequence variables."
---

# State-Adaptive Neuro-Fuzzy Inference Systems (S-ANFIS) in PyTorch for Financial & Algorithmic Routing

## Executive Summary

Standard Takagi-Sugeno-Kang (TSK) Adaptive Neuro-Fuzzy Inference Systems (ANFIS) use a unified input vector for both premise membership fuzzification and consequence rule output evaluation. In dynamic regime-switching applications (such as financial market regime modeling or LLM cost/quality routing), the state variables governing system regimes ($s$) often differ structurally from the explanatory features ($x$).

**State-ANFIS (S-ANFIS)** generalizes traditional ANFIS by explicitly decoupling premise inputs from consequence inputs, enabling state-dependent membership activation over arbitrary explanatory spaces.

---

## 1. Mathematical Formulation

```
                                Premise Inputs (s)
                                       |
                                       v
                             +-------------------+
                             | Fuzzification     |
                             | (Bell Membership) |
                             +---------+---------+
                                       |
                                       v
  Explanatory Inputs (x) ---> +-------------------+ ---> Output y(s, x)
                              | Consequence Rules |
                              | (Normalized Firing|
                              |  Strength w_i)    |
                              +-------------------+
```

### 1.1 Fuzzification Layer (Premise State $s$)
Premise membership uses Generalized Bell Membership Functions:

$$\mu_{A_i}(s) = \frac{1}{1 + \left| \frac{s - c_i}{a_i} \right|^{2b_i}}$$

where $\{a_i, b_i, c_i\}$ are learnable parameters representing premise width, slope, and center.

### 1.2 Rule Firing & Normalization
For $R$ rules, the firing strength $w_i(s)$ is the T-norm product of membership functions:

$$w_i(s) = \prod_{j=1}^{P} \mu_{A_{i,j}}(s_j)$$

Normalized firing strength:

$$\bar{w}_i(s) = \frac{w_i(s)}{\sum_{k=1}^{R} w_k(s)}$$

### 1.3 Consequence Layer (Explanatory Variables $x$)
Each rule $i$ computes a linear consequence output over explanatory variables $x$:

$$f_i(x) = \sum_{j=1}^{M} p_{i,j} x_j + r_i$$

The final aggregated system output $y(s, x)$ is given by:

$$y(s, x) = \sum_{i=1}^{R} \bar{w}_i(s) f_i(x)$$

---

## 2. PyTorch Modular Implementation Architecture

```python
import torch
import torch.nn as nn

class BellMembership(nn.Module):
    def __init__(self, num_rules: int, num_states: int):
        super().__init__()
        self.a = nn.Parameter(torch.ones(num_rules, num_states))
        self.b = nn.Parameter(torch.ones(num_rules, num_states))
        self.c = nn.Parameter(torch.zeros(num_rules, num_states))

    def forward(self, s: torch.Tensor) -> torch.Tensor:
        # s shape: [batch_size, num_states]
        s_expanded = s.unsqueeze(1) # [batch_size, 1, num_states]
        diff = torch.abs((s_expanded - self.c) / (self.a + 1e-6))
        memberships = 1.0 / (1.0 + torch.pow(diff + 1e-6, 2 * self.b))
        return torch.prod(memberships, dim=-1) # Rule firing strengths: [batch_size, num_rules]

class SANFIS(nn.Module):
    def __init__(self, num_rules: int, num_states: int, num_inputs: int):
        super().__init__()
        self.num_rules = num_rules
        self.premise = BellMembership(num_rules, num_states)
        self.consequence = nn.Linear(num_inputs, num_rules)

    def forward(self, s: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
        # Firing strengths w(s)
        w = self.premise(s)
        w_norm = w / (torch.sum(w, dim=-1, keepdim=True) + 1e-6)

        # Consequence evaluation f(x)
        # Assuming single output dimension for simple regression
        f = self.consequence(x) # [batch_size, num_rules]

        # Weighted sum
        out = torch.sum(w_norm * f, dim=-1, keepdim=True)
        return out
```

---

## 3. Key Findings & Verification

- [x] **Decoupled State Inputs**: S-ANFIS enables separate state-conditioned gating without forcing high-dimensional feature space into fuzzy rules.
- [x] **Gradient Propagation**: Verified end-to-end autodiff through bell membership parameters $(a, b, c)$ using PyTorch standard autograd engine.
- [x] **Numerical Stability**: Added $\epsilon = 10^{-6}$ epsilon guards against zero-division in firing strength normalization.
