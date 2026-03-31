#!/usr/bin/env python3
"""
极简静态博客引擎 — 数学笔记发布
用法:
    python build.py build    # 构建全站
    python build.py serve    # 本地预览（保存自动重建）
"""

import os, sys, re, shutil, time, threading
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

try:
    import markdown
except ImportError:
    print("✗  缺少依赖: pip install markdown")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("✗  缺少依赖: pip install pyyaml")
    sys.exit(1)

# ── 路径 ──────────────────────────────────────────────
ROOT      = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
DIST_DIR  = ROOT / "dist"
TEMPLATE  = ROOT / "template.html"
STYLE     = ROOT / "style.css"
CONFIG    = ROOT / "config.yaml"

def load_config():
    if CONFIG.exists():
        with open(CONFIG, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}

SITE_CONFIG = load_config()

def get_conf(key_path, default=""):
    keys = key_path.split('.')
    v = SITE_CONFIG
    try:
        for k in keys:
            v = v[k]
        return v
    except (KeyError, TypeError):
        return default


# ── YAML front matter 解析（不依赖 pyyaml） ──────────
def parse_frontmatter(text):
    """解析 YAML front matter，只支持 key: value 单行格式"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip()
    body  = text[end + 3:].strip()
    meta  = {}
    for line in block.splitlines():
        line = line.strip()
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body

# ── 数学公式保护 ─────────────────────────────────────
def protect_math(text):
    """替换数学公式为占位符，返回 (处理后文本, 占位符字典)"""
    holders = {}
    counter = 0

    def _replace(m):
        nonlocal counter
        key = f"\x00MATH{counter}\x00"
        counter += 1
        holders[key] = m.group(0)
        return key

    text = re.sub(r'\$\$[\s\S]+?\$\$', _replace, text)
    text = re.sub(r'(?<!\$)\$(?!\$)(?!\s)(.+?)(?<!\s)\$(?!\$)', _replace, text)
    return text, holders

def restore_math(html, holders):
    for key, val in holders.items():
        html = html.replace(key, val)
        escaped_key = key.replace('\x00', '&#0;')
        html = html.replace(escaped_key, val)
    return html

# ── Markdown → HTML ──────────────────────────────────
def _slugify(value, separator):
    slug = re.sub(r'[^\w\u4e00-\u9fff-]', '', value.lower().replace(' ', separator))
    return slug or f"section-{hash(value) % 10000}"

def md_to_html(md_text):
    protected, holders = protect_math(md_text)
    html = markdown.markdown(
        protected,
        extensions=["fenced_code", "tables"],
    )
    html = restore_math(html, holders)
    # 手动为标题添加 id（如果还没有）
    html = add_ids_to_headings(html)
    return html

def add_ids_to_headings(html):
    """为 HTML 中没有 id 的标题添加 id 属性"""
    def replace_heading(m):
        tag = m.group(1)  # h1, h2, h3 等
        attrs = m.group(2)  # 其他属性
        text = m.group(3)  # 标题文本
        # 如果已经有 id，保留原样
        if 'id=' in attrs:
            return m.group(0)
        # 生成 slug
        slug_id = _slugify(text, '-')
        return f'<{tag}{attrs} id="{slug_id}">{text}</{tag}>'
    
    pattern = r'<(h[1-6])([^>]*)>([^<]*)</(h[1-6])>'
    return re.sub(pattern, replace_heading, html)

# ── 目录提取 ─────────────────────────────────────────
def extract_toc(html):
    pattern = r'<(h[1-3])[^>]*\bid="([^"]*)"[^>]*>(.*?)</\1>'
    headings = re.findall(pattern, html, re.DOTALL)
    if not headings:
        return ""
    items = []
    for tag, hid, text in headings:
        clean = re.sub(r'<[^>]+>', '', text).strip()
        level = int(tag[1]) - 1
        items.append(f'<a class="toc-item toc-level-{level}" href="#{hid}">{clean}</a>')
    return "\n".join(items)

# ── 文章头部 meta ─────────────────────────────────────
def build_meta_block(meta):
    parts = []
    author   = meta.get("author", "")
    date     = meta.get("date", "")
    abstract = meta.get("abstract", "")
    category = meta.get("category", "")

    line = []
    if author:
        line.append(f'<span class="author">{author}</span>')
    if date:
        line.append(f'<time>{date}</time>')
    if category:
        cat_slug = f"category-{_slugify(category, '-')}"
        line.append(f'in <a href="{cat_slug}.html" class="category-label">{category}</a>')
    if line:
        parts.append('<div class="post-meta">' + " &middot; ".join(line) + '</div>')

    if abstract:
        parts.append(f'<p class="post-abstract">{abstract}</p>')

    return "\n".join(parts)

# ── 提取正文纯文本摘要 ───────────────────────────────
def extract_excerpt(body_md, length=80):
    """从 Markdown 源文本中提取前 N 个字的纯文本"""
    # 去掉标题行、公式块、空行
    lines = []
    in_math = False
    for line in body_md.splitlines():
        stripped = line.strip()
        if stripped.startswith('$$'):
            in_math = not in_math
            continue
        if in_math:
            continue
        if stripped.startswith('#'):
            continue
        if not stripped:
            continue
        # 去掉行内公式和 markdown 标记
        clean = re.sub(r'\$[^$]+\$', '', stripped)
        clean = re.sub(r'[*_`\[\]()>]', '', clean)
        clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
        clean = clean.strip()
        if clean:
            lines.append(clean)
    text = " ".join(lines)
    if len(text) > length:
        text = text[:length] + "…"
    return text

# ── 构建单篇文章 ─────────────────────────────────────
def build_post(md_path, template):
    raw  = md_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)

    title    = meta.get("title", md_path.stem)
    date     = meta.get("date", "")
    category = meta.get("category", "")
    abstract = meta.get("abstract", "")
    excerpt  = extract_excerpt(body)

    content_html = md_to_html(body)
    toc_html     = extract_toc(content_html)
    meta_block   = build_meta_block(meta)

    page = f'''  <div class="layout">
    <main class="content">
      <article>
        <div class="post-header">
          <h1>{title}</h1>
          {meta_block}
        </div>
        {content_html}
      </article>
    </main>

    <nav class="toc" id="toc">
      <div class="toc-title">目录</div>
      {toc_html}
    </nav>
  </div>'''

    html = render_template(template, title, page)

    slug = md_path.stem
    out  = DIST_DIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")

    return {
        "title": title, "date": date, "category": category,
        "abstract": abstract, "excerpt": excerpt,
        "slug": slug, "file": out,
    }

# ── SVG 图标 ─────────────────────────────────────────
ICONS = {
    "blog": '<svg viewBox="0 0 24 24"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1h-2z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "github": '<svg viewBox="0 0 24 24"><path d="M12 .3a12 12 0 00-3.8 23.38c.6.12.83-.26.83-.57L9 20.86c-3.37.74-4.08-1.63-4.08-1.63-.55-1.4-1.34-1.77-1.34-1.77-1.1-.75.08-.73.08-.73 1.21.08 1.85 1.24 1.85 1.24 1.08 1.84 2.82 1.31 3.51 1 .11-.78.42-1.31.76-1.61-2.69-.31-5.52-1.35-5.52-6a4.68 4.68 0 011.25-3.25 4.35 4.35 0 01.12-3.21s1.02-.33 3.34 1.24a11.52 11.52 0 016.06 0c2.31-1.57 3.33-1.24 3.33-1.24a4.35 4.35 0 01.12 3.21 4.68 4.68 0 011.25 3.25c0 4.66-2.84 5.69-5.54 5.99.44.37.82 1.12.82 2.26l-.01 3.35c0 .32.22.7.84.57A12 12 0 0012 .3"/></svg>',
    "pixiv": '<svg viewBox="0 0 24 24"><path d="M4.94 2.04c2.1-.22 4.92.22 6.53 2.04 2.7-.48 5.12.86 6.13 3.15 1.06 2.39.66 5.32-1.15 7.2-1.25 1.3-3.04 1.92-4.83 1.87-.34 1.74-.64 3.49-.97 5.24H7.87l.78-4.16c-1.56-.74-2.56-2.35-2.6-4.06a4.7 4.7 0 012.36-4.33c-.28-1.27-.52-2.55-.79-3.82-.73 0-1.46-.01-2.19-.03v-3.1h.01zm5.19 5.7a2.6 2.6 0 00-1.7 2.8c.12.95.84 1.77 1.77 1.97.44-.76.86-1.53 1.3-2.3-.5-.77-.94-1.58-1.37-2.4v-.07zm3.14-.14c-.56.93-1.08 1.87-1.6 2.82.65.67 1.27 1.38 1.95 2.02.94-.5 1.6-1.5 1.65-2.56.07-1.12-.74-2.18-1.83-2.3l-.17.02z"/></svg>',
    "bilibili": '<svg viewBox="0 0 24 24"><path d="M17.81 4.47c.08 0 .16-.02.23-.06.74-.4 1.38-.96 1.87-1.67a.26.26 0 00-.23-.38h-.01a.27.27 0 00-.21.11c-.45.63-1.02 1.15-1.68 1.52a.27.27 0 00.03.48zm-11.6 0a.27.27 0 00.03-.48A5.58 5.58 0 014.56 2.47.27.27 0 004.33 2.36h-.01a.27.27 0 00-.23.38c.49.71 1.13 1.27 1.87 1.67a.28.28 0 00.25.06zM22 8.12a2 2 0 00-2-2H4a2 2 0 00-2 2v9.5a2 2 0 002 2h16a2 2 0 002-2v-9.5zm-1.5.5v8.5a1 1 0 01-1 1H4.5a1 1 0 01-1-1v-8.5a1 1 0 011-1h15a1 1 0 011 1zM10 13.25a.74.74 0 01-.75.75H7.5a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75zm7.25 0a.74.74 0 01-.75.75H14.75a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75z"/></svg>'
}
ICON_GITHUB  = '<svg viewBox="0 0 24 24"><path d="M12 .3a12 12 0 00-3.8 23.38c.6.12.83-.26.83-.57L9 20.86c-3.37.74-4.08-1.63-4.08-1.63-.55-1.4-1.34-1.77-1.34-1.77-1.1-.75.08-.73.08-.73 1.21.08 1.85 1.24 1.85 1.24 1.08 1.84 2.82 1.31 3.51 1 .11-.78.42-1.31.76-1.61-2.69-.31-5.52-1.35-5.52-6a4.68 4.68 0 011.25-3.25 4.35 4.35 0 01.12-3.21s1.02-.33 3.34 1.24a11.52 11.52 0 016.06 0c2.31-1.57 3.33-1.24 3.33-1.24a4.35 4.35 0 01.12 3.21 4.68 4.68 0 011.25 3.25c0 4.66-2.84 5.69-5.54 5.99.44.37.82 1.12.82 2.26l-.01 3.35c0 .32.22.7.84.57A12 12 0 0012 .3"/></svg>'
ICON_PIXIV   = '<svg viewBox="0 0 24 24"><path d="M4.94 2.04c2.1-.22 4.92.22 6.53 2.04 2.7-.48 5.12.86 6.13 3.15 1.06 2.39.66 5.32-1.15 7.2-1.25 1.3-3.04 1.92-4.83 1.87-.34 1.74-.64 3.49-.97 5.24H7.87l.78-4.16c-1.56-.74-2.56-2.35-2.6-4.06a4.7 4.7 0 012.36-4.33c-.28-1.27-.52-2.55-.79-3.82-.73 0-1.46-.01-2.19-.03v-3.1h.01zm5.19 5.7a2.6 2.6 0 00-1.7 2.8c.12.95.84 1.77 1.77 1.97.44-.76.86-1.53 1.3-2.3-.5-.77-.94-1.58-1.37-2.4v-.07zm3.14-.14c-.56.93-1.08 1.87-1.6 2.82.65.67 1.27 1.38 1.95 2.02.94-.5 1.6-1.5 1.65-2.56.07-1.12-.74-2.18-1.83-2.3l-.17.02z"/></svg>'
ICON_BILIBILI = '<svg viewBox="0 0 24 24"><path d="M17.81 4.47c.08 0 .16-.02.23-.06.74-.4 1.38-.96 1.87-1.67a.26.26 0 00-.23-.38h-.01a.27.27 0 00-.21.11c-.45.63-1.02 1.15-1.68 1.52a.27.27 0 00.03.48zm-11.6 0a.27.27 0 00.03-.48A5.58 5.58 0 014.56 2.47.27.27 0 004.33 2.36h-.01a.27.27 0 00-.23.38c.49.71 1.13 1.27 1.87 1.67a.28.28 0 00.25.06zM22 8.12a2 2 0 00-2-2H4a2 2 0 00-2 2v9.5a2 2 0 002 2h16a2 2 0 002-2v-9.5zm-1.5.5v8.5a1 1 0 01-1 1H4.5a1 1 0 01-1-1v-8.5a1 1 0 011-1h15a1 1 0 011 1zM10 13.25a.74.74 0 01-.75.75H7.5a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75zm7.25 0a.74.74 0 01-.75.75H14.75a.75.75 0 010-1.5h1.75c.41 0 .75.34.75.75z"/></svg>'

def render_template(template_str, title_val, page_content):
    import time
    site_title = get_conf("site.title", "My Blog")
    favicon = get_conf("site.favicon", "")
    author = get_conf("site.author", "Author")
    author_link = get_conf("site.author_link", "#")
    
    favicon_html = f'<link rel="icon" href="{favicon}">' if favicon else ""
    year = time.strftime("%Y")
    
    theme_css = ""
    theme_conf = get_conf("theme", {})
    if theme_conf:
        vars = [f"--{k}: {v};" for k, v in theme_conf.items()]
        theme_css = "<style>:root {\n  " + "\n  ".join(vars) + "\n}</style>"
    
    html = template_str.replace("{{page_content}}", page_content)
    html = html.replace("</head>", f"{theme_css}\n</head>")
    html = html.replace("{{title}}", title_val)
    html = html.replace("{{site_title}}", site_title)
    html = html.replace("{{author}}", author)
    html = html.replace("{{author_link}}", author_link)
    html = html.replace("{{favicon_tag}}", favicon_html)
    html = html.replace("{{year}}", year)
    return html

# ── 构建首页 ─────────────────────────────────────────
def build_index(posts, template):
    posts.sort(key=lambda p: p["date"], reverse=True)

    categories = sorted(set(p["category"] for p in posts if p["category"]))
    cat_counts = {}
    for p in posts:
        c = p["category"]
        if c:
            cat_counts[c] = cat_counts.get(c, 0) + 1

    site_title = get_conf("site.title", "标题")
    site_subtitle = get_conf("site.subtitle", "副标题")
    
    links_html = []
    for link in get_conf("social_links", []):
        icon_key = link.get("icon", "")
        svg = ICONS.get(icon_key, "")
        url = link.get("url", "#")
        name = link.get("name", "")
        # 主博客不要 target=_blank
        target = ' target="_blank"' if "blog" not in icon_key else ""
        css_class = ' class="blog-link"' if "blog" in icon_key else ""
        links_html.append(f'<a{css_class} href="{url}"{target}>{svg} {name}</a>')
        
    links_str = '\n      <span class="sep">/</span>\n      '.join(links_html)

    hero = f'''  <div class="hero">
    <h1 class="hero-title">{site_title}</h1>
    <p class="hero-subtitle">{site_subtitle}</p>
    <div class="hero-links">
      {links_str}
    </div>
  </div>'''

    # ── 左侧时间轴 ──
    sidebar_tl = '    <aside class="sidebar-timeline">\n'
    current_year = ""
    for p in posts:
        date_str = p.get("date", "").split(" ")[0] # 去除时间部分
        year = date_str[:4] if len(date_str) >= 4 else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\n'
        date_short = date_str[5:] if len(date_str) >= 10 else date_str
        sidebar_tl += f'      <a href="#{p["slug"]}" class="tl-dot">{date_short}</a>\n'
    sidebar_tl += '    </aside>'

    # ── 中间文章预览（平铺，无卡片） ──
    entries = '    <div class="post-entries">\n'
    for p in posts:
        cat_link = f'<a href="category-{_slugify(p["category"], '-')}.html" class="post-entry-cat">{p["category"]}</a>' if p["category"] else ""
        abstract_html = f'\n        <div class="post-entry-abstract">{p["abstract"]}</div>' if p["abstract"] else ""
        excerpt_html  = f'\n        <div class="post-entry-excerpt">{p["excerpt"]}</div>' if p["excerpt"] else ""
        entries += f'''      <div class="post-entry" id="{p['slug']}">
        <div class="post-entry-title"><a href="{p["slug"]}.html">{p["title"]}</a></div>
        <div class="post-entry-meta"><span>{p["date"]}</span>{cat_link}</div>{abstract_html}{excerpt_html}
        <a class="post-entry-more" href="{p["slug"]}.html">Read More</a>
      </div>
'''
    entries += '    </div>'

    # ── 右侧分类 ──
    sidebar_cats = '    <aside class="sidebar-cats">\n'
    sidebar_cats += '      <div class="sidebar-cats-title">分类</div>\n'
    for c in categories:
        sidebar_cats += f'      <a href="category-{_slugify(c, '-')}.html">{c} <span class="cat-count">{cat_counts[c]}</span></a>\n'
    sidebar_cats += '    </aside>'

    # ── 组合 ──
    page = f'''{hero}

  <div class="home-body">
{sidebar_tl}
{entries}
{sidebar_cats}
  </div>'''

    html = render_template(template, get_conf("site.title", "首页"), page)
    out = DIST_DIR / "index.html"
    out.write_text(html, encoding="utf-8")

# ── 构建分类页面 ───────────────────────────────────
def build_category(category, posts, template):
    """为指定分类构建一个页面"""
    posts.sort(key=lambda p: p["date"], reverse=True)
    category_posts = [p for p in posts if p["category"] == category]

    hero = f'''  <div class="hero" style="min-height: 40vh;">
    <h1 class="hero-title">{category}</h1>
  </div>'''

    sidebar_tl = '    <aside class="sidebar-timeline">\n'
    current_year = ""
    for p in category_posts:
        date_str = p.get("date", "").split(" ")[0] # 去除时间部分
        year = date_str[:4] if len(date_str) >= 4 else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\n'
        date_short = date_str[5:] if len(date_str) >= 10 else date_str
        sidebar_tl += f'      <a href="#{p["slug"]}" class="tl-dot">{date_short}</a>\n'
    sidebar_tl += '    </aside>'

    entries = '    <div class="post-entries">\n'
    for p in category_posts:
        cat_link = f'<a href="category-{_slugify(p["category"], '-')}.html" class="post-entry-cat">{p["category"]}</a>' if p["category"] else ""
        abstract_html = f'\n        <div class="post-entry-abstract">{p["abstract"]}</div>' if p["abstract"] else ""
        excerpt_html  = f'\n        <div class="post-entry-excerpt">{p["excerpt"]}</div>' if p["excerpt"] else ""
        entries += f'''      <div class="post-entry" id="{p['slug']}">
        <div class="post-entry-title"><a href="{p["slug"]}.html">{p["title"]}</a></div>
        <div class="post-entry-meta"><span>{p["date"]}</span>{cat_link}</div>{abstract_html}{excerpt_html}
        <a class="post-entry-more" href="{p["slug"]}.html">Read More</a>
      </div>
'''
    entries += '    </div>'

    page = f'''{hero}

  <div class="home-body">
{sidebar_tl}
{entries}
  </div>'''

    html = render_template(template, f"{category} — {get_conf('site.title', '')}", page)
    slug = f"category-{_slugify(category, '-')}"
    out = DIST_DIR / f"{slug}.html"
    out.write_text(html, encoding="utf-8")
    return slug

# ── 完整构建 ─────────────────────────────────────────
def build():
    print("⚙  构建中...")
    start = time.time()

    if DIST_DIR.exists():
        for item in DIST_DIR.iterdir():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
            except PermissionError:
                pass
    else:
        DIST_DIR.mkdir(parents=True)

    shutil.copy2(STYLE, DIST_DIR / "style.css")
    
    # 拷贝 images 文件夹到 dist 目录
    images_dir = ROOT / "images"
    if images_dir.exists():
        shutil.copytree(images_dir, DIST_DIR / "images", dirs_exist_ok=True)
        print("   ✓ 复制 images/ 图片资源")

    template = TEMPLATE.read_text(encoding="utf-8")

    md_files = sorted(POSTS_DIR.glob("*.md"))
    if not md_files:
        print("⚠  posts/ 目录下没有 .md 文件")

    posts = []
    for md in md_files:
        info = build_post(md, template)
        posts.append(info)
        print(f"   ✓ {md.name} → {info['file'].name}")

    build_index(posts, template)
    print(f"   ✓ index.html")
    
    # 构建所有分类页面
    categories = sorted(set(p["category"] for p in posts if p["category"]))
    for cat in categories:
        cat_slug = build_category(cat, posts, template)
        print(f"   ✓ {cat_slug}.html")

    elapsed = time.time() - start
    print(f"✔  构建完成 ({len(posts)} 篇, {elapsed:.2f}s)")

# ── 本地预览服务器 ───────────────────────────────────
class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST_DIR), **kwargs)
    def log_message(self, fmt, *args):
        if args and str(args[1]) != "200":
            super().log_message(fmt, *args)

def watch_and_rebuild(interval=1.0):
    watch_files = [TEMPLATE, STYLE]
    def get_mtimes():
        mtimes = {}
        for f in watch_files:
            if f.exists():
                mtimes[str(f)] = f.stat().st_mtime
        for md in POSTS_DIR.glob("*.md"):
            mtimes[str(md)] = md.stat().st_mtime
        return mtimes

    last_mtimes = get_mtimes()
    while True:
        time.sleep(interval)
        current = get_mtimes()
        if current != last_mtimes:
            print("\n♻  检测到变化，重建...")
            try:
                build()
            except Exception as e:
                print(f"✗  构建失败: {e}")
            last_mtimes = get_mtimes()

def serve(port=8000):
    build()
    watcher = threading.Thread(target=watch_and_rebuild, daemon=True)
    watcher.start()
    print(f"\n🌐 预览服务器: http://localhost:{port}")
    print("   (保存文件自动重建，Ctrl+C 退出)\n")
    server = HTTPServer(("", port), QuietHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 再见")
        server.shutdown()

# ── 入口 ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "build":
        build()
    elif sys.argv[1] == "serve":
        p = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        serve(p)
    else:
        print(f"用法: python {sys.argv[0]} [build|serve]")
        sys.exit(1)
