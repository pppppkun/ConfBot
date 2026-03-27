import json
import logging
from typing import List

from bs4 import BeautifulSoup
from playwright.sync_api import Page, sync_playwright

from data import PaperMeta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ConfBot-Crawler")
logger.setLevel(logging.DEBUG)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def get_driver(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    logger.info("Start browser")
    return browser, context, page


def get_url(url: str, page: Page) -> bool:
    try:
        logger.info(f"Connect to {url}...")
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_selector(
            "#event-overview table tbody tr", state="attached", timeout=15000
        )
        logger.info(f"Connect Successful. The title of the page is {page.title()}")
        return True
    except Exception as e:
        logger.error(e)
        logger.info("Connect Error.")
        return False


def get_paper(page: Page) -> List[PaperMeta]:
    page_source = page.content()
    soup = BeautifulSoup(page_source, "html.parser")
    rows = soup.select("#event-overview table tbody tr")
    logger.info(f"find {len(rows)} papers")
    result = []
    for idx, row in enumerate(rows, start=1):
        title_links = row.select("td a")
        if not title_links:
            continue

        title_url = title_links[0]
        title = title_url.get_text().strip()
        performers = [
            performer.get_text().strip()
            for performer in row.select("td div.performers a")
        ]
        performers = ",".join(performers)
        modal_id = title_url.get("data-event-modal")
        abstract = ""
        if modal_id:
            abstract = get_abstract(page, modal_id)
        else:
            logger.warning(f"Missing modal id for paper: {title}")

        result.append(PaperMeta(title, performers, abstract))
        if idx % 30 == 0:
            logger.info(f"obtain {idx}/{len(rows)} paper...")
    return result


def get_abstract(page: Page, modal_id: str) -> str:
    selector = f'a[data-event-modal="{modal_id}"]'
    try:
        with page.expect_response(
            lambda response: "eventDetailsModalByAjaxConferenceEdition" in response.url,
            timeout=30000,
        ) as response_info:
            page.locator(selector).first.evaluate("element => element.click()")

        payload = json.loads(response_info.value.text())
        modal_html = next(
            (
                action.get("value", "")
                for action in payload
                if action.get("action") == "append"
                and f"modal-{modal_id}" in action.get("value", "")
            ),
            "",
        )
        if not modal_html:
            logger.warning(f"Missing modal html for paper modal: {modal_id}")
            return ""

        modal_soup = BeautifulSoup(modal_html, "html.parser")
        content = modal_soup.select("div.modal-body div.bg-info.event-description p")
        return " ".join([p.get_text().strip() for p in content if p.get_text().strip()])
    except Exception as exc:
        logger.warning(f"Failed to fetch abstract for modal {modal_id}: {exc}")
        return ""


def crawler_papers(url) -> List[PaperMeta]:
    logger.info("Start ConfBot Crawler")
    with sync_playwright() as playwright:
        browser, context, page = get_driver(playwright)
        try:
            if get_url(url, page):
                return get_paper(page)
            logger.info("End Crawler")
            return []
        finally:
            context.close()
            browser.close()
