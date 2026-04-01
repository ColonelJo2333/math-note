# Math-Notes SSG

一个用于数学和物理笔记的静态网站生成器。纯 Python 实现，不依赖 Node.js 或任何前端构建工具。

---

## 为什么要做这个

用 Hexo、Hugo 这类常规静态博客写数学文档，最头疼的问题是 Markdown 解析器和 LaTeX 语法打架。

LaTeX 里大量使用下划线 `_` 表示下标、星号 `*` 表示乘法，但这些符号在 Markdown 里是斜体和加粗的标记。矩阵环境里的 `\\` 换行符也经常在转义过程中丢失。结果就是公式传到 MathJax 或 KaTeX 的时候已经残缺不全，不得不手动改成 `\\_` 或 `\\\\` 来迎合解析器。

本项目的做法是在 `build.py` 里接管 Markdown 的转换流程：

1. 解析前，先用正则把所有 `$...$` 和 `$$...$$` 公式提取出来，替换成占位符
2. Markdown 引擎只处理正文的标题、列表、加粗，碰不到数学公式
3. 解析完成后，把占位符换回原始的 LaTeX 内容
4. 前端用 KaTeX 渲染，公式完整无损

最终采用纯客户端渲染：在 `template.html` 里引入 KaTeX 的 auto-render 脚本，让浏览器加载页面后自动识别并渲染公式。这样做的好处是构建速度快（不用在 Python 端生成复杂的公式 HTML），也不存在 SSR/CSR 不一致导致的水合报错。Markdown 引擎只管排版，KaTeX 只管公式，各司其职。

---

## 使用方法

### 安装依赖

需要 Python 3.x：

```bash
pip install -r requirements.txt
```

依赖只有 `markdown` 和 `PyYAML`。

### 目录结构

```
.
├── posts/            # Markdown 文章
├── images/           # 图标和配图
├── config.yaml       # 网站配置
├── build.py          # 构建脚本
├── style.css         # 样式
├── template.html     # HTML 模板
└── dist/             # 生成的静态页面
```

### 本地预览

```bash
python build.py serve
```

启动后访问 `http://localhost:8000`。修改 `posts/` 里的文章或 `config.yaml` 后保存，后台会自动重建，刷新页面即可看到更新。

---

## 配置

网站信息和样式都在 `config.yaml` 里设置，包括标题、作者、社交链接、主题颜色等。改配置不需要动代码。

### 站点地图（sitemap.xml）

每次执行 `python build.py build`（或 `serve` 自动重建）都会在 `dist/` 下自动生成 `sitemap.xml`，包含：

- 首页 `/`
- 所有文章页面 `/*.html`
- 所有分类页面 `/category-*.html`

为了生成正确的绝对链接，请在 `config.yaml` 中设置：

```yaml
site:
	url: "https://your-site-domain.com"
```

如果未设置 `site.url`，程序会尝试使用 `site.author_link` 作为回退地址。

---

## 部署到 Vercel

项目已包含 `vercel.json` 配置：

1. 把代码推送到 GitHub（`dist/` 已在 `.gitignore` 中排除）
2. 在 Vercel 导入仓库
3. 直接部署，不需要额外设置

之后每次 `git push` 新文章，网站会自动更新。