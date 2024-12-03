import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from urllib.parse import urljoin
from semanticscholar import SemanticScholar

app = Flask(__name__)

sch = SemanticScholar()

@app.route("/")
def index():
    url = request.args.get("query")
    if not url:
        return jsonify({"error": "Invalid URL"}), 400

    try:
        results = sch.search_paper(str(url), fields=["title", "abstract", "venue", "year", "authors", "tldr", "embedding", "externalIds"])
    except Exception as e:
        return jsonify({"error": f"Request failed: {str(e)}"}), 400

    if not results:
        return jsonify({"error": "No results found"}), 404

    paper_info = []
    for item in results:
        title = item.title
        authors = item.authors
        authors = [a.name for a in authors]
        author = ",".join(authors)  # Concatenate authors into a single string
        abstract = item.abstract
        year = item.year
        citation_count = item.citationCount
        doi_url = item.externalIds.get('doi', '')  # Assuming 'externalIds' contains a 'doi'

        paper_dict = {
            "title": title,
            "doi": doi_url,
            "Cite": citation_count,
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
                "author": p["author"],
            }
            for p in paper_info  # Corrected to use paper_info, not papers
        ]
    }
    return jsonify(feed)
