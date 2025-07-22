import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from cachetools import TTLCache
from tools.playwright.playwright_toolkit import *
from langgraph.prebuilt import SupervisorAgent, ReactAgent, Tool

# -----------------------------------------------------------------------------
# 1) TOOLS
# -----------------------------------------------------------------------------

class FetchClosingPage(Tool):
    name = "fetch_closing_page"
    description = "Fetch raw HTML for the 'closing today' page of a given URL."
    
    def run(self, url: str) -> str:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text


class ParseListings(Tool):
    name = "parse_listings"
    description = (
        "Given HTML from a closing page, extract a list of items with "
        "title, link, price (as float), and closing_time."
    )
    
    def run(self, html: str, base_url: str) -> list[dict]:
        soup = BeautifulSoup(html, "html.parser")
        items = []
        # TODO: adjust selectors to match the site’s actual markup:
        for card in soup.select(".listing-card"):
            title_el = card.select_one(".item-title")
            link_el  = card.select_one("a")
            price_el = card.select_one(".current-bid, .price")
            time_el  = card.select_one(".time-left")
            if not (title_el and link_el and price_el):
                continue
            title = title_el.get_text(strip=True)
            href  = link_el["href"]
            link  = urljoin(base_url, href)
            # remove symbols, commas
            price = float(price_el.get_text().replace("$","").replace(",","").strip())
            closing_time = time_el.get_text(strip=True) if time_el else None
            items.append({
                "title": title,
                "url": link,
                "price": price,
                "closing_time": closing_time
            })
        return items




class FilterUnderPriced(Tool):
    name = "filter_under_priced"
    description = (
        "Given a list of items with price & resale_estimate, "
        "return only those ≤ 50% of resale estimate or tagged damaged."
    )
    
    def run(self, items: list[dict]) -> list[dict]:
        out = []
        for it in items:
            est = it.get("resale_estimate")
            if est and it["price"] <= est * 0.5:
                out.append(it)
        return out


# -----------------------------------------------------------------------------
# 2) AGENTS
# -----------------------------------------------------------------------------

# ReactAgent orchestrates each step with chain-of-thought
react_agent = ReactAgent(
    name="scrape_and_evaluate",
    tools=[
        FetchClosingPage(),
        ParseListings(),
        EstimateResaleValue(),
        FilterUnderPriced()
    ],
    llm_config={
        "model": "qwen3-30b-a3b",
        "api_base": "http://localhost:8000/v1",
        "api_key": ""  # empty for lm-studio compatibility
    }
)

# SupervisorAgent puts it all together, calling the ReactAgent once per URL
supervisor = SupervisorAgent(
    name="closing_auction_finder",
    sub_agents=[react_agent],
    llm_config={
        "model": "qwen3-30b-a3b",
        "api_base": "http://localhost:8000/v1",
        "api_key": ""
    }
)

# -----------------------------------------------------------------------------
# 3) MAIN ENTRYPOINT
# -----------------------------------------------------------------------------

def main():
    urls = [
        "https://www.allsurplus.com/en/closing-today",
        "https://www.govdeals.com/en/closing-today/"
    ]
    prompt = (
        "For each URL, fetch the closing-today items, parse title, link, price, "
        "estimate resale, then keep only those priced at 50% or below of resale."
    )
    # Supervisor will invoke the ReactAgent for each URL
    results = supervisor.run({"urls": urls, "prompt": prompt})
    
    # results is a dict mapping URL → filtered items
    for url, items in results.items():
        print(f"\nURL: {url}\n" + "-"*len(url))
        for i in items:
            print(f"{i['title']}\n  ↳ {i['url']}\n  • Current: ${i['price']:.2f}  • Est. resale: ${i['resale_estimate']:.2f}\n")
    

if __name__ == "__main__":
    main()
