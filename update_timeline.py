import re

with open('build.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update theme in render_template
theme_injection = """    theme_css = ""
    theme_conf = get_conf("theme", {})
    if theme_conf:
        vars = [f"--{k}: {v};" for k, v in theme_conf.items()]
        theme_css = "<style>:root {\\n  " + "\\n  ".join(vars) + "\\n}</style>"
    
    html = template_str.replace("{{page_content}}", page_content)
    html = html.replace("</head>", f"{theme_css}\\n</head>")
    html = html.replace("{{title}}", title_val)"""

text = text.replace(
    '    html = template_str.replace("{{page_content}}", page_content)\n    html = html.replace("{{title}}", title_val)',
    theme_injection
)

# 2. Update date parsing and timeline links in build_index
old_index_tl = """    # ── 左侧时间轴 ──
    sidebar_tl = '    <aside class="sidebar-timeline">\\n'
    current_year = ""
    for p in posts:
        year = p["date"][:4] if p["date"] else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\\n'
        date_short = p["date"][5:] if len(p["date"]) >= 10 else p["date"]
        sidebar_tl += f'      <div class="tl-dot">{date_short}</div>\\n'
    sidebar_tl += '    </aside>'"""

new_index_tl = """    # ── 左侧时间轴 ──
    sidebar_tl = '    <aside class="sidebar-timeline">\\n'
    current_year = ""
    for p in posts:
        date_str = p.get("date", "").split(" ")[0] # 去除时间部分
        year = date_str[:4] if len(date_str) >= 4 else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\\n'
        date_short = date_str[5:] if len(date_str) >= 10 else date_str
        sidebar_tl += f'      <a href="#{p["slug"]}" class="tl-dot">{date_short}</a>\\n'
    sidebar_tl += '    </aside>'"""

text = text.replace(old_index_tl, new_index_tl)

# 3. Update entry ID in build_index
old_index_entry = """        entries += f'''      <div class="post-entry">"""
new_index_entry = """        entries += f'''      <div class="post-entry" id="{p["slug"]}">'''"""
text = text.replace(old_index_entry, new_index_entry)

# 4. Update timeline links in build_category
old_cat_tl = """    sidebar_tl = '    <aside class="sidebar-timeline">\\n'
    current_year = ""
    for p in category_posts:
        year = p["date"][:4] if p["date"] else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\\n'
        date_short = p["date"][5:] if len(p["date"]) >= 10 else p["date"]
        sidebar_tl += f'      <div class="tl-dot">{date_short}</div>\\n'
    sidebar_tl += '    </aside>'"""

new_cat_tl = """    sidebar_tl = '    <aside class="sidebar-timeline">\\n'
    current_year = ""
    for p in category_posts:
        date_str = p.get("date", "").split(" ")[0] # 去除时间部分
        year = date_str[:4] if len(date_str) >= 4 else ""
        if year != current_year:
            current_year = year
            sidebar_tl += f'      <div class="tl-year">{year}</div>\\n'
        date_short = date_str[5:] if len(date_str) >= 10 else date_str
        sidebar_tl += f'      <a href="#{p["slug"]}" class="tl-dot">{date_short}</a>\\n'
    sidebar_tl += '    </aside>'"""

text = text.replace(old_cat_tl, new_cat_tl)

# Update entry ID in build_category
old_cat_entry = """        entries += f'''      <div class="post-entry">"""
# It's already the same string so it matched above if I used replace, but let's be careful.
text = text.replace(old_cat_entry, new_index_entry)

with open('build.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")