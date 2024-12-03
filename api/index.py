import asyncio
from flask import Flask, request, jsonify
from semanticscholar import SemanticScholar

app = Flask(__name__)
sch = SemanticScholar()

@app.route("/")
async def index():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, sch.search_paper, str(url), year="2023-", fields=["title", "abstract", "venue", "year", "authors", "externalIds"], limit=5)
    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 400

    if not results:
        return jsonify({"error": "No results found"}), 404
    
    paper_info = []
    for item in results:
        paper_info.append({
            "title": item['title'],
            "author": ",".join(a['name'] for a in item['authors']),
            "abstract": item['abstract'],
            "year": item['year'],
            "doi": item['externalIds'].get('doi', ''),
        })

    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": f"Papers of ({url})",
        "items": [
            {
                "title": p["title"],
                "content_text": p["abstract"],
                "url": p["doi"],
                "year": p["year"],
                "author": p["author"],
            }
            for p in paper_info
        ]
    }
    return jsonify(feed)
