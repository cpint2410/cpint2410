import json
import os
import urllib.request
from collections import Counter

username = "cpint2410"
token = os.environ["GITHUB_TOKEN"]

languages = Counter()
page = 1

while True:
    url = (
        f"https://api.github.com/users/{username}/repos"
        f"?per_page=100&page={page}&type=owner"
    )

    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    })

    with urllib.request.urlopen(request) as response:
        repos = json.loads(response.read())

    if not repos:
        break

    for repo in repos:
        if not repo["fork"] and repo["language"]:
            languages[repo["language"]] += 1

    page += 1

if not languages:
    raise RuntimeError("No repository languages found.")

colors = [
    "#3178C6", "#F1E05A", "#E34F26", "#B07219",
    "#3572A5", "#563D7C", "#00ADD8", "#6E4C13"
]

chart = {
    "type": "doughnut",
    "data": {
        "labels": list(languages.keys()),
        "datasets": [{
            "data": list(languages.values()),
            "backgroundColor": [
                colors[i % len(colors)]
                for i in range(len(languages))
            ]
        }]
    },
    "options": {
        "plugins": {
            "title": {
                "display": True,
                "text": "Repositories by Programming Language"
            },
            "legend": {"position": "bottom"}
        }
    }
}

import urllib.parse

chart_url = (
    "https://quickchart.io/chart?width=650&height=400&format=png&c="
    + urllib.parse.quote(json.dumps(chart))
)

os.makedirs("assets", exist_ok=True)

image_request = urllib.request.Request(chart_url)

with urllib.request.urlopen(image_request) as response:
    with open("assets/language-chart.png", "wb") as image:
        image.write(response.read())

print("Language counts:", dict(languages))
print("Chart generated successfully!")
