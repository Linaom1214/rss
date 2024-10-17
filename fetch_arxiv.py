import arxiv
import json
import requests
import logging
import os
import yaml

# 设置日志记录
logging.basicConfig(level=logging.INFO)

def get_authors(authors, first_author=False):
    if first_author:
        return authors[0].name if authors else ""
    return ", ".join(author.name for author in authors)

def load_config():
    with open("config.yml", "r") as f:
        return yaml.safe_load(f)

def parse_filters(filters: list) -> str:
    ret = ''
    for idx, filter in enumerate(filters):
        ret += (EXCAPE + filter + EXCAPE) if len(filter.split()) > 1 else filter
        if idx != len(filters) - 1:
            ret += f" {OR} "
    return ret


def fetch_arxiv():
    config = load_config()
    max_results = config["max_results"]
    arxiv_url = "https://arxiv.org/"
    base_url = "https://arxiv.paperswithcode.com/api/v0/papers/"
    
    cache_file = "arxiv_data.json"

    # 读取缓存数据
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                articles = json.load(f)
            logging.info("Using cached data.")
        except:
            articles = []
    else:
        articles = []

    new_articles = []

    for keyword, data in config["keywords"].items():
        filters = data["filters"]    
        filters = parse_filters(filters)
        search_engine = arxiv.Search(
            query=filter_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        for result in search_engine.results():
            paper_id = result.get_short_id()
            paper_title = result.title
            paper_url = result.entry_id
            paper_abstract = result.summary.replace("\n", " ")
            paper_authors = get_authors(result.authors)
            paper_first_author = get_authors(result.authors, first_author=True)
            publish_time = result.published.date()

            logging.info(f"Title: {paper_title}, Author: {paper_first_author}")

            # 获取代码链接（如果有）
            code_url = f"{base_url}{paper_id}"
            try:
                r = requests.get(code_url).json()
                repo_url = None
                if "official" in r and r["official"]:
                    repo_url = r["official"]["url"]
            except Exception as e:
                logging.error(f"Error fetching code URL: {e}")
                repo_url = None

            new_articles.append({
                "title": paper_title,
                "author": paper_authors,
                "summary": paper_abstract,
                "published": publish_time.isoformat(),
                "link": paper_url,
                "code_url": repo_url,
                "category":keyword +"-"+ filter_query
            })

    # 如果没有新文章，则使用缓存数据
    if new_articles:
        articles = new_articles
        # 写入缓存文件
        with open(cache_file, "w") as f:
            json.dump(articles, f, indent=2)
    else:
        logging.info("No new articles found. Using cached data.")

    return articles

if __name__ == "__main__":
    fetch_arxiv()
