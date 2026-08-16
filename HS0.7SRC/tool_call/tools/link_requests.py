from bs4 import BeautifulSoup 
import trafilatura 
import requests, json

def clean_html(html):
    soup = BeautifulSoup(html, "lxml")

    for tag in soup([
        "script", "style",
        "svg", "canvas", "iframe",
        "noscript", "meta", "link"
    ]): tag.decompose()

    return soup

def extract_text(html):
    return trafilatura.extract(html,
        include_links=False,
        include_images=False,
        include_tables=True
    ) or ""

def extract_headings(soup):
    headings = []

    for tag in soup.find_all(["h1", "h2", "h3"]):
        text = tag.get_text(" ", strip=True)
        if text:
            headings.append({
                "level": tag.name,
                "text": text
            })

    return headings

def extract_links(soup):
    links = []

    for a in soup.find_all("a", href=True):
        text = a.get_text(" ", strip=True)

        links.append({"text": text, "url": a["href"]})

    return links

def extract_tables(soup):
    tables = []

    for table in soup.find_all("table"):
        rows = []

        for tr in table.find_all("tr"):
            cells = [
                cell.get_text(" ", strip=True)
                for cell in tr.find_all(["th", "td"])
            ]

            if cells: rows.append(cells)
        if rows: tables.append(rows)

    return tables

def page_to_json(html):
    soup = clean_html(html)

    return {
        "title": soup.title.string.strip() if soup.title else "",
        "text": extract_text(str(soup)),
        "headings": extract_headings(soup),
        "links": extract_links(soup),
        "tables": extract_tables(soup)
    }

def run(url):
    return json.dumps(
        page_to_json(requests.get(url).text), 
        ensure_ascii=False, indent=2
    )