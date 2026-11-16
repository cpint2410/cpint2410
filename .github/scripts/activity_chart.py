
import json
import os
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape

# ==================================================
# CONFIGURATION
# ==================================================

USERNAME = "cpint2410"

WIDTH = 850
HEIGHT = 240

LEFT = 35
TOP = 70

BAR_WIDTH = 15
BAR_GAP = 11

CHART_HEIGHT = 100
BACKGROUND_HEIGHT = 102

OUTPUT_FILE = "assets/activity.svg"

# Optional GitHub Actions token
TOKEN = os.environ.get("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "GitHub-Activity-Chart"
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


# ==================================================
# FETCH PUBLIC GITHUB EVENTS
# ==================================================

today = datetime.now(timezone.utc).date()
start = today - timedelta(days=29)

counts = Counter()

# Fetch up to 300 recent public events.
# GitHub's public events API has a limited event history.
for page in range(1, 4):

    url = (
        f"https://api.github.com/users/{USERNAME}"
        f"/events/public?per_page=100&page={page}"
    )

    request = urllib.request.Request(
        url,
        headers=HEADERS
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        events = json.loads(response.read())

    if not events:
        break

    for event in events:

        created_at = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        )

        day = created_at.date()

        if start <= day <= today:
            counts[day] += 1

    if len(events) < 100:
        break


# ==================================================
# CHART CALCULATIONS
# ==================================================

maximum = max(counts.values(), default=1)

bars = []

for i in range(30):

    day = start + timedelta(days=i)
    value = counts[day]

    # Scale bar height
    bar_height = (
        value / maximum
    ) * CHART_HEIGHT if value else 0

    display_height = max(bar_height, 2)

    y = CHART_HEIGHT - display_height

    # Keep all 30 bars inside the 850px canvas
    x = LEFT + i * (BAR_WIDTH + BAR_GAP)

    day_class = f"d-{i + 1}"

    if value:
        fill = "url(#bar-grad)"
    else:
        fill = "#30363d"

    tooltip = (
        f"{day.isoformat()}: {value} public events"
    )

    bars.append(f'''
    <g class="bar-group {day_class}"
       transform="translate({x}, {TOP})">

      <rect class="activity-bg-bar"
            x="0"
            y="0"
            width="{BAR_WIDTH}"
            height="{BACKGROUND_HEIGHT}"
            rx="4"
            fill="#151b23"/>

      <rect class="bar-anim"
            x="0"
            y="{y:.2f}"
            width="{BAR_WIDTH}"
            height="{display_height:.2f}"
            rx="4"
            fill="{fill}">

        <title>{escape(tooltip)}</title>

      </rect>

    </g>
    ''')


# ==================================================
# SVG DOCUMENT
# ==================================================

svg = [

    f'''<svg xmlns="http://www.w3.org/2000/svg"
         width="{WIDTH}"
         height="{HEIGHT}"
         viewBox="0 0 {WIDTH} {HEIGHT}">''',

    # ------------------------------------------------
    # ANIMATIONS AND STYLING
    # ------------------------------------------------

    '''
    <style>

      @keyframes fadeSlideUp {
        from {
          opacity: 0;
          transform: translateY(10px);
        }

        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes barGrow {
        from {
          transform: scaleY(0);
        }

        to {
          transform: scaleY(1);
        }
      }

      .header-anim {
        animation: fadeSlideUp 0.6s
          cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }

      .bar-group {
        cursor: pointer;
        transition: filter 0.25s ease;
      }

      .bar-anim {
        transform-box: fill-box;
        transform-origin: center bottom;
        animation: barGrow 0.7s
          cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
      }

      .bar-group:hover {
        filter: brightness(1.25)
          drop-shadow(0 0 8px rgba(88,166,255,0.6));
      }

      .bar-group:hover .bar-anim {
        fill: #38bdf8;
      }

      .activity-bg-bar {
        transition: fill 0.2s ease;
      }

      .bar-group:hover .activity-bg-bar {
        fill: #1e293b;
      }

      .d-1  { animation-delay: 0.05s; }
      .d-2  { animation-delay: 0.07s; }
      .d-3  { animation-delay: 0.09s; }
      .d-4  { animation-delay: 0.11s; }
      .d-5  { animation-delay: 0.13s; }
      .d-6  { animation-delay: 0.15s; }
      .d-7  { animation-delay: 0.17s; }
      .d-8  { animation-delay: 0.19s; }
      .d-9  { animation-delay: 0.21s; }
      .d-10 { animation-delay: 0.23s; }
      .d-11 { animation-delay: 0.25s; }
      .d-12 { animation-delay: 0.27s; }
      .d-13 { animation-delay: 0.29s; }
      .d-14 { animation-delay: 0.31s; }
      .d-15 { animation-delay: 0.33s; }
      .d-16 { animation-delay: 0.35s; }
      .d-17 { animation-delay: 0.37s; }
      .d-18 { animation-delay: 0.39s; }
      .d-19 { animation-delay: 0.41s; }
      .d-20 { animation-delay: 0.43s; }
      .d-21 { animation-delay: 0.45s; }
      .d-22 { animation-delay: 0.47s; }
      .d-23 { animation-delay: 0.49s; }
      .d-24 { animation-delay: 0.51s; }
      .d-25 { animation-delay: 0.53s; }
      .d-26 { animation-delay: 0.55s; }
      .d-27 { animation-delay: 0.57s; }
      .d-28 { animation-delay: 0.59s; }
      .d-29 { animation-delay: 0.61s; }
      .d-30 { animation-delay: 0.63s; }

    </style>
    ''',

    # ------------------------------------------------
    # GRADIENT DEFINITIONS
    # ------------------------------------------------

    '''
    <defs>

      <radialGradient id="activity-bg"
                      cx="10%" cy="20%" r="90%">

        <stop offset="0%" stop-color="#182232"/>
        <stop offset="100%" stop-color="#0a0e14"/>

      </radialGradient>

      <linearGradient id="activity-border"
                      x1="0%" y1="0%"
                      x2="100%" y2="100%">

        <stop offset="0%" stop-color="#3b82f6"
              stop-opacity="0.4"/>

        <stop offset="50%" stop-color="#8b5cf6"
              stop-opacity="0.2"/>

        <stop offset="100%" stop-color="#1f2937"
              stop-opacity="0.1"/>

      </linearGradient>

      <filter id="drop-shadow"
              x="-5%" y="-5%"
              width="110%" height="110%">

        <feDropShadow dx="0" dy="6"
                      stdDeviation="10"
                      flood-color="#000000"
                      flood-opacity="0.45"/>

      </filter>

      <linearGradient id="bar-grad"
                      x1="0%" y1="0%"
                      x2="0%" y2="100%">

        <stop offset="0%" stop-color="#38bdf8"/>
        <stop offset="100%" stop-color="#0284c7"/>

      </linearGradient>

    </defs>
    ''',

    # ------------------------------------------------
    # BACKGROUND CARD
    # ------------------------------------------------

    '''
    <rect width="100%" height="100%"
          rx="16"
          fill="url(#activity-bg)"
          filter="url(#drop-shadow)"/>

    <rect x="1" y="1"
          width="848" height="238"
          rx="15"
          fill="none"
          stroke="url(#activity-border)"
          stroke-width="2"/>
    ''',

    # ------------------------------------------------
    # HEADER AND ICON
    # ------------------------------------------------

    '''
    <g class="header-anim"
       transform="translate(35, 25)">

      <rect width="32" height="32"
            rx="8"
            fill="#3b82f6"
            fill-opacity="0.15"
            stroke="#3b82f6"
            stroke-opacity="0.3"/>

      <path d="
        M 16 9
        C 14 11 13 13 13 15.5
        C 13 17.4 14.3 19 16 19
        C 17.7 19 19 17.4 19 15.5
        C 19 13 18 11 16 9 Z

        M 16 21
        C 12.7 21 10 18.5 10 15.5
        C 10 12.5 13 9.5 15 7
        C 15.3 6.6 15.8 6.5 16.2 6.8
        C 16.5 7 16.6 7.5 16.3 7.8
        C 14.8 9.8 12.5 12.3 12.5 15.5
        C 12.5 17.1 14.1 18.5 16 18.5
        C 17.9 18.5 19.5 17.1 19.5 15.5
        C 19.5 14.5 19 13.3 18.2 12.1
        C 17.9 11.7 18 11.2 18.4 10.9
        C 18.8 10.6 19.3 10.7 19.6 11.1
        C 20.6 12.6 21.5 14.1 21.5 15.5
        C 21.5 18.5 19.3 21 16 21 Z"
        fill="#60a5fa"/>

      <text x="42" y="21"
            fill="#f8fafc"
            font-size="18"
            font-weight="700"
            font-family="system-ui, -apple-system, sans-serif"
            letter-spacing="-0.2">

        My GitHub Activity

      </text>

    </g>
    ''',

]

# --------------------------------------------------
# ACTIVITY BARS
# --------------------------------------------------

svg.append('<g class="activity-bars">')

svg.extend(bars)

svg.append('</g>')


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

svg.append('''
<g class="header-anim"
   transform="translate(35, 212)">

  <text x="0" y="0"
        fill="#94a3b8"
        font-size="12"
        font-weight="500"
        font-family="system-ui, -apple-system, sans-serif">

    ⚡ Last 30 days · Public GitHub events

  </text>

</g>
''')

svg.append('</svg>')


# ==================================================
# SAVE CHART
# ==================================================

os.makedirs("assets", exist_ok=True)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as file:

    file.write("\n".join(svg))


# ==================================================
# REPORT
# ==================================================

print("Activity chart generated successfully!")
print(f"Period: {start} to {today}")
print(f"Total public events counted: {sum(counts.values())}")
print(f"Active days: {sum(1 for v in counts.values() if v > 0)}")
print(f"Maximum daily events: {maximum}")
print(f"Output: {OUTPUT_FILE}")
