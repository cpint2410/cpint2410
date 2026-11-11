import json
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape

username = "cpint2410"
today = datetime.now(timezone.utc).date()
start = today - timedelta(days=29)

url = f"https://api.github.com/users/{username}/events/public?per_page=100"
req = urllib.request.Request(url, headers={
    "Accept": "application/vnd.github+json",
    "User-Agent": "GitHub-Activity-Chart"
})

with urllib.request.urlopen(req) as response:
    events = json.loads(response.read())

counts = Counter()

for event in events:
    day = datetime.fromisoformat(
        event["created_at"].replace("Z", "+00:00")
    ).date()

    if start <= day <= today:
        counts[day] += 1

width, height = 850, 240
left, top = 35, 45
chart_height = 125
bar_width = 15
gap = 11

maximum = max(counts.values(), default=1)

bars = []

for i in range(30):
    day = start + timedelta(days=i)
    value = counts[day]
    bar_height = (value / maximum) * chart_height
    x = left + i * (bar_width + gap)
    y = top + chart_height - bar_height

    color = "#58a6ff" if value else "#30363d"

    bars.append(
        f'<rect x="{x}" y="{y}" width="{bar_width}" '
        f'height="{max(bar_height, 2)}" rx="4" fill="{color}">'
        f'<title>{day}: {value} public events</title></rect>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" rx="12" fill="#0d1117"/>
<text x="35" y="28" fill="#ffffff" font-size="17"
font-family="Arial" font-weight="bold">My GitHub Activity</text>
<text x="35" y="215" fill="#8b949e" font-size="12"
font-family="Arial">Last 30 days · Public GitHub events</text>
{''.join(bars)}
</svg>'''

import os
os.makedirs("assets", exist_ok=True)

with open("assets/activity.svg", "w") as file:
    file.write(svg)

print("Activity chart generated!")
