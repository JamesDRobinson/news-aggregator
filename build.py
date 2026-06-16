import datetime
import xml.etree.ElementTree as ET
import urllib.request

# Read your custom feeds
with open("feeds.txt", "r") as f:
    feeds = [line.strip() for line in f if line.strip()]

articles = []

# Fetch and parse feeds
for url in feeds:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Find channel title
            channel_title = root.find('.//channel/title').text or "Unknown Source"
            
            # Grab top 5 items from each feed
            items = root.findall('.//item')[:5]
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                articles.append({"title": title, "link": link, "source": channel_title})
    except Exception as e:
        print(f"Error parsing {url}: {e}")

# Generate Minimalist Brutalist HTML
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minimalist News Feed</title>
    <style>
        body {{ font-family: monospace; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #fff; color: #000; line-height: 1.5; }}
        h1 {{ font-size: 1.5rem; border-bottom: 2px solid #000; padding-bottom: 5px; }}
        .meta {{ color: #666; margin-bottom: 30px; font-size: 0.9rem; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ margin-bottom: 12px; }}
        a {{ color: #0000ee; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .source {{ color: #666; font-size: 0.85rem; margin-left: 8px; }}
    </style>
</head>
<body>
    <h1>MINIMALIST NEWS</h1>
    <div class="meta">Updated: {current_time} | Feeds tracking: {len(feeds)}</div>
    <ul>
"""

for art in articles:
    html_content += f'        <li><a href="{art["link"]}" target="_blank">{art["title"]}</a><span class="source">[{art["source"]}]</span></li>\n'

html_content += """    </ul>
</body>
</html>"""

# Save the final static page
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Site built successfully!")
