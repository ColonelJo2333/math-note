---
title: 测度论基础笔记
author: ChenHu
date: 2026-03-30
category: 实分析
abstract: σ-代数、Borel 集与 Lebesgue 测度的基本定义和性质。
---

## σ-代数与可测空间

设 $X$ 为非空集合。$X$ 上的一个 **σ-代数**（σ-algebra）$\mathcal{F}$ 是 $\mathcal{P}(X)$ 的子集族，满足：

1. $X \in \mathcal{F}$
2. 若 $A \in \mathcal{F}$，则 $A^c \in \mathcal{F}$
3. 若 $\{A_n\}_{n=1}^{\infty} \subset \mathcal{F}$，则 $\bigcup_{n=1}^{\infty} A_n \in \mathcal{F}$

称 $(X, \mathcal{F})$ 为**可测空间**。

## Borel σ-代数

拓扑空间 $(X, \tau)$ 上由开集族生成的 σ-代数称为 **Borel σ-代数**，记为 $\mathcal{B}(X)$。特别地，$\mathcal{B}(\mathbb{R})$ 由所有形如 $(a, b)$ 的开区间生成。

### 生成原理

对任意集族 $\mathcal{C} \subset \mathcal{P}(X)$，存在唯一的最小 σ-代数 $\sigma(\mathcal{C})$ 使得 $\mathcal{C} \subset \sigma(\mathcal{C})$：

$$
\sigma(\mathcal{C}) = \bigcap \{ \mathcal{F} : \mathcal{F} \text{ 是 σ-代数且 } \mathcal{C} \subset \mathcal{F} \}
$$

## 测度的定义

设 $(X, \mathcal{F})$ 为可测空间。映射 $\mu: \mathcal{F} \to [0, +\infty]$ 称为 $\mathcal{F}$ 上的**测度**，若满足：

1. $\mu(\emptyset) = 0$
2. **可数可加性**：若 $\{A_n\}$ 两两不交，则

$$
\mu\left(\bigsqcup_{n=1}^{\infty} A_n\right) = \sum_{n=1}^{\infty} \mu(A_n)
$$

### 测度的基本性质

由上述公理可推出以下性质：

- **单调性**：$A \subset B \implies \mu(A) \le \mu(B)$
- **次可加性**：$\mu\left(\bigcup_{n=1}^{\infty} A_n\right) \le \sum_{n=1}^{\infty} \mu(A_n)$
- **连续性**：若 $A_n \uparrow A$，则 $\mu(A_n) \to \mu(A)$

## Lebesgue 测度

$\mathbb{R}^n$ 上存在唯一的平移不变的 Borel 测度 $\lambda$，使得对任意长方体 $R = \prod_{i=1}^n [a_i, b_i]$ 有：

$$
\lambda(R) = \prod_{i=1}^{n} (b_i - a_i)
$$

这就是 **Lebesgue 测度**。它是 $\mathbb{R}^n$ 上最自然的"体积"概念的推广。

> **注意**：Lebesgue 测度的存在性依赖于 Carathéodory 外测度构造。不是所有 $\mathbb{R}$ 的子集都是 Lebesgue 可测的——著名的 Vitali 集就是一个反例。
