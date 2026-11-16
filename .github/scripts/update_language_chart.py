
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


# --------------------------------------------------
# FETCH GITHUB REPOSITORY DATA
# --------------------------------------------------

repos = github_get(
    f"https://api.github.com/users/{USERNAME}/repos?per_page=100&type=owner"
)

language_counts = Counter()
repos_with_languages = 0

for repo in repos:
    if repo["fork"]:
        continue

    name = urllib.parse.quote(repo["name"], safe="")
    url = f"https://api.github.com/repos/{USERNAME}/{name}/languages"

    languages = github_get(url)

    if languages:
        repos_with_languages += 1

    for language, bytes_used in languages.items():
        if bytes_used > 0:
            language_counts[language] += 1

if not language_counts:
    raise RuntimeError("No programming languages found.")


# --------------------------------------------------
# DESIGN CONFIGURATION
# --------------------------------------------------

width, height = 760, 420

cx, cy = 195, 235

outer_radius = 115
inner_radius = 75
center_radius = 52

total = sum(language_counts.values())

# Original redesigned gradient palette
gradients = [
    ("grad-blue", "#38bdf8", "#0284c7"),
    ("grad-amber", "#fbbf24", "#d97706"),
    ("grad-yellow", "#fde047", "#ca8a04"),
    ("grad-indigo", "#60a5fa", "#2563eb"),
    ("grad-orange", "#fb923c", "#ea580c"),
    ("grad-purple", "#c084fc", "#7c3aed"),
    ("grad-cyan", "#22d3ee", "#0891b2"),
    ("grad-green", "#4ade80", "#16a34a"),
    ("grad-pink", "#f472b6", "#db2777"),
]


# --------------------------------------------------
# SVG HELPERS
# --------------------------------------------------

def polar(radius, angle):
    radians = math.radians(angle)

    x = cx + radius * math.cos(radians)
    y = cy + radius * math.sin(radians)

    return x, y


def donut_segment(start_angle, end_angle, color):
    fraction = (end_angle - start_angle) / 360

    x1, y1 = polar(outer_radius, start_angle)
    x2, y2 = polar(outer_radius, end_angle)

    x3, y3 = polar(inner_radius, end_angle)
    x4, y4 = polar(inner_radius, start_angle)

    large_arc = 1 if fraction > 0.5 else 0

    return (
        f'<path d="'
        f'M {x1:.3f},{y1:.3f} '
        f'A {outer_radius},{outer_radius} 0 {large_arc} 1 {x2:.3f},{y2:.3f} '
        f'L {x3:.3f},{y3:.3f} '
        f'A {inner_radius},{inner_radius} 0 {large_arc} 0 {x4:.3f},{y4:.3f} '
        f'Z" fill="url(#{color})"/>'
    )


# --------------------------------------------------
# SVG START
# --------------------------------------------------

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{width}" height="{height}" '
    f'viewBox="0 0 {width} {height}">',

    '<defs>',

    # Background gradient
    '''
    <radialGradient id="bg-grad" cx="15%" cy="15%" r="85%">
      <stop offset="0%" stop-color="#182232"/>
      <stop offset="100%" stop-color="#0a0e14"/>
    </radialGradient>
    ''',

    # Border gradient
    '''
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.4"/>
      <stop offset="50%" stop-color="#8b5cf6" stop-opacity="0.2"/>
      <stop offset="100%" stop-color="#1f2937" stop-opacity="0.1"/>
    </linearGradient>
    ''',

    # Shadow
    '''
    <filter id="drop-shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="8" stdDeviation="12"
                    flood-color="#000000" flood-opacity="0.5"/>
    </filter>
    '''
]

# Generate all gradient definitions
for gradient_id, color1, color2 in gradients:
    svg.append(f'''
    <linearGradient id="{gradient_id}" x1="0%" y1="0%"
                    x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
    ''')

svg.append('</defs>')


# --------------------------------------------------
# BACKGROUND
# --------------------------------------------------

svg.append('''
<rect width="100%" height="100%" rx="24"
      fill="url(#bg-grad)" filter="url(#drop-shadow)"/>

<rect x="1" y="1" width="758" height="418" rx="23"
      fill="none" stroke="url(#border-grad)" stroke-width="2"/>
''')


# --------------------------------------------------
# HEADER
# --------------------------------------------------

svg.append('''
<g transform="translate(35, 38)">

  <rect width="36" height="36" rx="10"
        fill="#3b82f6" fill-opacity="0.15"
        stroke="#3b82f6" stroke-opacity="0.3"/>

  <path d="M 12 11 L 7 18 L 12 25
           M 24 11 L 29 18 L 24 25
           M 19 9 L 17 27"
        stroke="#60a5fa"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
        fill="none"/>

  <text x="50" y="24"
        fill="#f8fafc"
        font-size="20"
        font-weight="700"
        font-family="system-ui, -apple-system, sans-serif"
        letter-spacing="-0.3">
    Languages Across My Projects
  </text>

</g>
''')


# --------------------------------------------------
# DONUT CHART
# --------------------------------------------------

start_angle = -90

for i, (language, count) in enumerate(
    language_counts.most_common()
):

    fraction = count / total
    end_angle = start_angle + fraction * 360

    gradient_id = gradients[i % len(gradients)][0]

    if len(language_counts) == 1:

        # Full donut when only one language exists
        svg.append(f'''
        <circle cx="{cx}" cy="{cy}"
                r="{outer_radius}"
                fill="url(#{gradient_id})"/>
        ''')

    else:

        svg.append(
            donut_segment(
                start_angle,
                end_angle,
                gradient_id
            )
        )

    start_angle = end_angle


# --------------------------------------------------
# CENTER HOLE
# --------------------------------------------------

svg.append(f'''
<circle cx="{cx}" cy="{cy}"
        r="{center_radius}"
        fill="#0f172a"
        stroke="#1e293b"
        stroke-width="3"/>

<text x="{cx}" y="{cy - 5}"
      text-anchor="middle"
      fill="#ffffff"
      font-size="18"
      font-weight="700"
      font-family="system-ui, -apple-system, sans-serif">
    {repos_with_languages}
</text>

<text x="{cx}" y="{cy + 15}"
      text-anchor="middle"
      fill="#64748b"
      font-size="11"
      font-weight="600"
      font-family="system-ui, -apple-system, sans-serif"
      letter-spacing="0.5">
    REPOS
</text>
''')


# --------------------------------------------------
# LEGEND
# --------------------------------------------------

legend_items = language_counts.most_common()

legend_start_y = 96

# Adapt spacing if more than six languages are detected
legend_gap = min(
    40,
    230 / max(1, len(legend_items) - 1)
)

for i, (language, count) in enumerate(legend_items):

    y = legend_start_y + i * legend_gap

    gradient_id = gradients[i % len(gradients)][0]

    repo_label = "repo" if count == 1 else "repos"

    svg.append(f'''
    <g transform="translate(405, {y:.2f})">

      <rect width="14" height="14" rx="4"
            fill="url(#{gradient_id})"/>

      <text x="28" y="12"
            fill="#f1f5f9"
            font-size="14"
            font-weight="600"
            font-family="system-ui, sans-serif">
        {escape(language)}
      </text>

      <text x="215" y="12"
            text-anchor="end"
            fill="#94a3b8"
            font-size="13"
            font-family="system-ui, sans-serif">
        {count} {repo_label}
      </text>

    </g>
    ''')


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

svg.append('''
<line x1="35" y1="355" x2="725" y2="355"
      stroke="#1e293b" stroke-width="1.5"/>

<text x="35" y="383"
      fill="#64748b"
      font-size="12"
      font-weight="500"
      font-family="system-ui, -apple-system, sans-serif">
    ✨ A repository can contain multiple languages
</text>
''')

svg.append('</svg>')


# --------------------------------------------------
# SAVE SVG
# --------------------------------------------------

os.makedirs("assets", exist_ok=True)

with open(
    "assets/language-chart.svg",
    "w",
    encoding="utf-8"
) as file:

    file.write("\n".join(svg))

print("Language donut chart generated successfully!")
print(dict(language_counts))
print(f"Repositories counted: {repos_with_languages}")
