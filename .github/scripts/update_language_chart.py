import json
import math
import os
import urllib.parse
import urllib.request
from collections import Counter
from html import escape

USERNAME = "cpint2410"
TOKEN = os.environ["GITHUB_TOKEN"]

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "GitHub-Language-Chart"
}

def github_get(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read())

# Get public repositories
repos = github_get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
)

language_counts = Counter()

# Count each language once per repository
for repo in repos:
    if repo["fork"]:
        continue

    name = urllib.parse.quote(repo["name"], safe="")
    url = f"https://api.github.com/repos/{USERNAME}/{name}/languages"

    languages = github_get(url)

    for language, bytes_used in languages.items():
        if bytes_used > 0:
            language_counts[language] += 1

if not language_counts:
    raise RuntimeError("No programming languages found.")

colors = [
    "#3572A5", "#B07219", "#F1E05A",
    "#3178C6", "#E34F26", "#563D7C",
    "#00ADD8", "#6E4C13", "#8B949E"
]

total = sum(language_counts.values())

width, height = 760, 420
cx, cy, radius = 190, 210, 140

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" rx="16" fill="#0d1117"/>',
    '<text x="35" y="35" fill="#ffffff" '
    'font-size="21" font-weight="bold" '
    'font-family="Arial">Languages Across My Projects</text>'
]

start_angle = -90

for i, (language, count) in enumerate(language_counts.most_common()):
    fraction = count / total
    end_angle = start_angle + fraction * 360
    color = colors[i % len(colors)]

    if count == total:
        svg.append(
            f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>'
        )
    else:
        x1 = cx + radius * math.cos(math.radians(start_angle))
        y1 = cy + radius * math.sin(math.radians(start_angle))
        x2 = cx + radius * math.cos(math.radians(end_angle))
        y2 = cy + radius * math.sin(math.radians(end_angle))

        large_arc = 1 if fraction > 0.5 else 0

        svg.append(
            f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} '
            f'A {radius} {radius} 0 {large_arc} 1 '
            f'{x2:.2f} {y2:.2f} Z" fill="{color}"/>'
        )

    start_angle = end_angle

# Legend
for i, (language, count) in enumerate(language_counts.most_common()):
    y = 105 + i * 43
    color = colors[i % len(colors)]

    svg.append(
        f'<rect x="405" y="{y-13}" width="15" height="15" '
        f'rx="3" fill="{color}"/>'
    )

    svg.append(
        f'<text x="432" y="{y}" fill="#ffffff" '
        f'font-size="15" font-family="Arial">'
        f'{escape(language)} — {count} repositories</text>'
    )

svg.append(
    '<text x="405" y="375" fill="#8b949e" '
    'font-size="12" font-family="Arial">'
    'A repository can contain multiple languages</text>'
)

svg.append('</svg>')

os.makedirs("assets", exist_ok=True)

with open("assets/language-chart.svg", "w") as file:
    file.write("\n".join(svg))

print("Language pie chart generated!")
print(dict(language_counts))
