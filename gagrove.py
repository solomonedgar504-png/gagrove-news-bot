import os
import sys
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from google import genai

USER_AGENT = "GagroveNewsBot/1.0"
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v24.0")
RSS_URL = "https://news.google.com/rss/search?q=Malawi&hl=en-MW&gl=MW&ceid=MW:en"


def required_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required GitHub secret: {name}")
    return value


def fetch_news(topic=""):
    query = topic.strip() or "Malawi"
    url = (
        "https://news.google.com/rss/search"
        f"?q={requests.utils.quote(query)}&hl=en-MW&gl=MW&ceid=MW:en"
    )
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()

    root = ET.fromstring(r.content)
    articles = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        description = (item.findtext("description") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
            })
    if not articles:
        raise RuntimeError("No Malawi news items were returned by Google News RSS.")
    return articles[:8]


def generate_post(articles):
    api_key = required_env("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    evidence = "\n\n".join(
        f"ARTICLE {i+1}\nTITLE: {a['title']}\nDATE: {a['pub_date']}\n"
        f"SUMMARY: {a['description']}\nLINK: {a['link']}"
        for i, a in enumerate(articles)
    )

    prompt = f"""
You are the editor of Gagrove, a Malawi news page.

Using ONLY the supplied article information, write ONE Facebook news post.
Rules:
- Do not invent facts, names, numbers, quotes, causes, or locations.
- Do not copy article wording; summarize it in original language.
- If information is developing or not independently confirmed, say so.
- Keep it concise and readable for Malawian Facebook users.
- Use a neutral, factual news tone.
- Start with a short headline.
- Then write 2-4 short paragraphs.
- End with "Source: [publisher name if it is clear from the article title/description]".
- Do not mention that you are an AI.
- Do not use markdown tables.

ARTICLE INFORMATION:
{evidence}
"""

    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty response.")
    return text


def publish_to_facebook(message):
    page_id = required_env("META_PAGE_ID")
    page_token = required_env("META_PAGE_ACCESS_TOKEN")

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/feed"
    r = requests.post(
        url,
        data={
            "message": message,
            "access_token": page_token,
        },
        timeout=30,
    )

    if not r.ok:
        raise RuntimeError(
            f"Facebook publishing failed (HTTP {r.status_code}): {r.text[:1500]}"
        )

    data = r.json()
    if "id" not in data:
        raise RuntimeError(f"Facebook returned an unexpected response: {data}")
    return data["id"]


def main():
    topic = os.getenv("GAGROVE_TOPIC", "").strip()
    print(f"Starting Gagrove news run at {datetime.now(timezone.utc).isoformat()}")
    print(f"Topic: {topic or 'Malawi'}")

    articles = fetch_news(topic)
    print(f"Found {len(articles)} candidate articles.")
    for a in articles[:3]:
        print(" -", a["title"])

    post = generate_post(articles)
    print("\nGenerated post:\n" + post)

    post_id = publish_to_facebook(post)
    print(f"\nSUCCESS: Facebook post published. ID={post_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
