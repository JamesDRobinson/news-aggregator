import datetime
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
import urllib.request
import random
import email.utils
import re

# Matrix Quote Engine
QUOTES = [
    "\"You take the red pill, you stay in Wonderland, and I show you how deep the rabbit hole goes.\" — Morpheus",
    "\"There is a difference between knowing the path and walking the path.\" — Morpheus",
    "\"The Matrix is a system, Neo. That system is our enemy.\" — Morpheus",
    "\"What's really going to bake your noodle later on is, would you still have broken it if I hadn't said anything?\" — The Oracle",
    "\"Ever have that feeling where you're not sure if you're awake or dreaming?\" — Neo",
    "\"I'm trying to free your mind, Neo. But I can only show you the door. You're the one that has to walk through it.\" — Morpheus",
    "\"Choice is an illusion created between those with power and those without.\" — The Merovingian",
    "\"It is the question that drives us, Neo. It's the question that brought you here.\" — Trinity",
    "\"The body cannot live without the mind.\" — Morpheus",
    "\"Free your mind.\" — Morpheus"
]
selected_quote = random.choice(QUOTES)

all_articles = []
target_timezone = ZoneInfo("America/New_York")
now_eastern = datetime.datetime.now(target_timezone)

# Helper function to compute relative time intervals
def compute_time_ago(article_dt, current_dt):
    diff = current_dt - article_dt
    seconds = diff.total_seconds()
    
    if seconds < 0:
        return "just now"
        
    minutes = int(seconds // 60)
    hours = int(minutes // 60)
    days = int(hours // 24)
    
    if days > 0:
        return f"{days}d ago"
    elif hours > 0:
        return f"{hours}h ago"
    elif minutes > 0:
        return f"{minutes}m ago"
    else:
        return "just now"

# Helper function to clean and strip down source names to clean domains
def strip_to_clean_domain(channel_title, feed_url):
    # Step 1: Force lowercase and remove common clutter phrases
    cleaned = channel_title.lower()
    cleaned = re.sub(r'(\brss\b|\bfeed\b|\bofficial\b|\bnews\b|\bblog\b)', '', cleaned)
    
    # Step 2: Remove special characters, leaving spaces and alphanumeric strings
    cleaned = re.sub(r'[^a-z0-9\s\.]', '', cleaned).strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Step 3: If the title is now empty or too generic, extract domain directly from URL
    if not cleaned or len(cleaned) < 3 or cleaned in ['unknown source', 'home']:
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', feed_url)
        if domain_match:
            return domain_match.group(1).lower()
        return "unknown"
        
    # Step 4: Format explicit channel identities to clean asset styles
    # If it's multiple clean text words (e.g. "center for a stateless society"), join them cleanly
    if " " in cleaned:
        # Check if an absolute short token exists or make it a unified terminal handle
        if "stateless society" in cleaned or "c4ss" in cleaned:
            return "c4ss.org"
        if "crimethinc" in cleaned:
            return "crimethinc.com"
        if "one championship" in cleaned or "one fc" in cleaned:
            return "onefc.com"
        return cleaned.replace(" ", ".")
        
    return cleaned

# Read feeds
with open("feeds.txt", "r", encoding="utf-8") as f:
    feeds = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

# Fetch and parse feeds
for url in feeds:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            raw_title = root.find('.//channel/title').text or "Unknown Source"
            
            # Apply domain sanity stripping matching terminal specs
            clean_source = strip_to_clean_domain(raw_title, url)
            
            # Pull only top 3 items per source
            items = root.findall('.//item')[:3]
            
            for item in items:
                title = item.find('title').text
                link = item.find('link').text
                
                # Timestamp parsing logic
                pub_date_raw = item.find('pubDate')
                if pub_date_raw is not None and pub_date_raw.text:
                    try:
                        dt = email.utils.parsedate_to_datetime(pub_date_raw.text)
                        dt_eastern = dt.astimezone(target_timezone)
                    except Exception:
                        dt_eastern = now_eastern
                else:
                    dt_eastern = now_eastern

                # Tag Extraction Logic
                tags = []
                category_elements = item.findall('category')
                for cat in category_elements:
                    if cat.text:
                        cleaned_tag = cat.text.strip().lower()
                        if cleaned_tag and "/" not in cleaned_tag and len(cleaned_tag) < 25:
                            if cleaned_tag not in tags:
                                tags.append(cleaned_tag)
                
                tags = tags[:5]

                all_articles.append({
                    "title": title, 
                    "link": link, 
                    "source": clean_source,
                    "tags": tags,
                    "datetime": dt_eastern
                })
    except Exception as e:
        print(f"Error parsing {url}: {e}")

# Chronological sort (Newest at top)
all_articles.sort(key=lambda x: x["datetime"], reverse=True)

# Generate HTML
current_time_str = now_eastern.strftime("%Y-%m-%d %I:%M %p ET")

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal // Chronological_Feed</title>
    <style>
        body {{ 
            font-family: 'Courier New', Courier, monospace; 
            max-width: 900px; 
            margin: 40px auto; 
            padding: 0 20px; 
            background-color: #0d0d0d; 
            color: #00ff41; 
            line-height: 1.6; 
        }}
        ::selection {{ background: #00ff41; color: #000; }}
        h1 {{ 
            font-size: 1.6rem; 
            border-bottom: 1px dashed #00ff41; 
            padding-bottom: 10px; 
            margin-bottom: 5px;
            letter-spacing: 2px;
            text-transform: uppercase;
            text-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
        }}
        .quote-box {{
            font-style: italic;
            color: #00ff41;
            opacity: 0.85;
            margin-top: 15px;
            margin-bottom: 5px;
            font-size: 0.95rem;
            word-wrap: break-word;
        }}
        .meta {{ color: #008f11; margin-bottom: 30px; font-size: 0.85rem; border-top: 1px dashed #008f11; padding-top: 5px; }}
        ul {{ list-style-type: none; padding: 0; margin-top: 20px; }}
        li {{ 
            margin-bottom: 18px; 
            display: flex; 
            flex-direction: column;
            align-items: flex-start; 
        }}
        .link-row {{
            display: flex;
            align-items: flex-start;
            width: 100%;
            border-bottom: 1px dotted rgba(255, 255, 255, 0.15);
            padding-bottom: 4px;
        }}
        .link-row::before {{ content: "> "; margin-right: 8px; color: #008f11; flex-shrink: 0; }}
        
        a {{ 
            color: #00ff41; 
            text-decoration: none; 
            text-transform: uppercase;
        }}
        a:hover {{ background-color: #00ff41; color: #000; }}
        a:visited {{ color: #005f0c; }}
        
        /* Fixed Source Label style to ensure domain text handles look sharp */
        .source {{ 
            color: #008f11; 
            font-size: 0.8rem; 
            margin-left: 10px; 
            white-space: nowrap;
            text-transform: lowercase;
        }}
        
        .tag-row {{
            margin-left: 20px;
            font-size: 0.75rem;
            color: #008f11;
            opacity: 0.8;
            margin-top: 4px;
            word-wrap: break-word;
        }}
    </style>
</head>
<body>
    <h1>root@news:~# cat unified_timeline</h1>
    <div class="quote-box">{selected_quote}</div>
    <div class="meta">SYS_STATUS: ONLINE | TIMESTAMP: {current_time_str}</div>
    
    <ul>
"""

# Render loop
for art in all_articles:
    time_badge = compute_time_ago(art["datetime"], now_eastern)
    
    html_content += f'        <li>\n            <div class="link-row"><a href="{art["link"]}" target="_blank">{art["title"]}</a><span class="source">[{art["source"]}]</span></div>\n'
    
    tag_build = f"posted: {time_badge}"
    if art["tags"]:
        tag_build += f" | tags: {' '.join([f'#{t}' for t in art['tags']])}"
        
    html_content += f'            <div class="tag-row">{tag_build}</div>\n        </li>\n'

html_content += """    </ul>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("Timeline compiled successfully with domain sanity parsing rules.")
