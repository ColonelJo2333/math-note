with open("build.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    '        entries += f\'\'\'      <div class="post-entry" id="{p["slug"]}">\'\'\'\n',
    '        entries += f\'\'\'      <div class="post-entry" id="{p[\'slug\']}">\n'
)

with open("build.py", "w", encoding="utf-8") as f:
    f.write(text)
print("done")
