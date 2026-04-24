import glob
import re

for f in glob.glob("frontend/*.html"):
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r'<script src="components/toast\.js[^>]*></script>\s*', '', content)
    with open(f, "w", encoding="utf-8") as file:
        file.write(content)
print("Toast removed")
