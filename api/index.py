import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from urllib.parse import urljoin
from semanticscholar import SemanticScholar

app = Flask(__name__)

ch = SemanticScholar(api_key="rckeUk4ySL4hhvWVn3TlT8My8uhjURC1vzYqaCn2")

@app.route("/")
def index():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        results = sch.search_paper(url, fields = ["title", "abstract", "venue", "year", "authors", "tldr", "embedding", "externalIds"])
    except (results)== 0:
        return jsonify({"error": "Request failed"}), 400

    paper_info = []
    for index, item in enumerate(results):
        title = item.title
        author = item.authors
        author = [a.name for a in author]
        author = ",".join(author)
        abstract = item.abstract
        year = item.year
        citationCount = item.citationCount
        paper_dict = {
            "title":title,
            "doi":dor_url,
            "Cite":citationCount,
            "author": author,
            "abstract": abstract,
            "year": year
        }
        paper_info.append(paper_dict)


    feed = {
        "version": "https://jsonfeed.org/version/1",
        "title": f"Papers of ({url})",
        "feed_url": "https://example.org/feed.json",
        "items": [
            {
                "title": p["title"],
                "content_text": p["abstract"],
                "url": p["doi"],
                "year": p["year"],
                "author":p["author"],
            }
            for p in papers
        ]
    }
    return jsonify(feed)