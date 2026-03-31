---
title: Fourier 变换速查
author: ChenHu
date: 2026-03-28
category: 分析
abstract: Fourier 变换的核心定义、基本性质与卷积定理速查。
---

## 定义

设 $f \in L^1(\mathbb{R})$，其 **Fourier 变换**定义为：

$$
\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) \, e^{-2\pi i x \xi} \, dx
$$

## 基本性质

### 线性

$\widehat{af + bg} = a\hat{f} + b\hat{g}$，其中 $a, b \in \mathbb{C}$。

### 平移与调制

- 时域平移：$\widehat{f(x - a)}(\xi) = e^{-2\pi i a \xi} \hat{f}(\xi)$
- 频域调制：$\widehat{e^{2\pi i a x} f(x)}(\xi) = \hat{f}(\xi - a)$

### Parseval 定理

若 $f, g \in L^2(\mathbb{R})$，则：

$$
\int_{-\infty}^{\infty} f(x)\overline{g(x)} \, dx = \int_{-\infty}^{\infty} \hat{f}(\xi)\overline{\hat{g}(\xi)} \, d\xi
$$

特别地，$\|f\|_2 = \|\hat{f}\|_2$（**能量守恒**）。

## 卷积定理

$$
\widehat{f * g} = \hat{f} \cdot \hat{g}
$$

这是 Fourier 分析最强大的结论之一：**时域卷积等于频域相乘**。

## 逆变换

若 $\hat{f} \in L^1(\mathbb{R})$，则：

$$
f(x) = \int_{-\infty}^{\infty} \hat{f}(\xi) \, e^{2\pi i x \xi} \, d\xi
$$

> Fourier 变换将微分方程转化为代数方程，将卷积转化为乘法——这就是它的威力所在。
