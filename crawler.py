import logging
import time
from typing import List
from data import PaperMeta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConfBot-Crawler')
logger.setLevel(logging.DEBUG)

def get_driver():
    chrome_options = Options()
    driver_path = './chromedriver'
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.page_load_strategy = 'eager'
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)
    driver.set_page_load_timeout(60)
    logger.info("Start browser")
    
    return driver


def get_url(url, driver):
    try:
        logger.info(f"Connect to {url}...")
        driver.get(url)
        logger.info(f"Connect Successful. The title of the page is {driver.title}")
        logger.info(f"wait 1 seconds to load the page")
        time.sleep(1)
        return True
    except Exception as e:
        logger.error(e)
        logger.info("Connect Error.")
        driver.close()
        return False


def get_paper(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    rows = soup.select("#event-overview table tbody tr")
    logger.info(f'find {len(rows)} papers')
    result = []
    idx = 0
    for row in rows:
        title_url = row.select('td a')[0]
        title = title_url.get_text().strip()
        performers = [performer.get_text().strip() for performer in row.select('td div.performers a')]
        performers = ','.join(performers)
        modal_id = title_url['data-event-modal']
        selenium_element = driver.find_element(By.XPATH, f'//*[@id="event-overview"]/table/tbody/tr[{idx+1}]/td[2]/a')
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", selenium_element)
        time.sleep(1) # 给页面一点缓冲时间
        selenium_element.click()
        time.sleep(1) # 给页面一点缓冲时间
        after_click_page_source = driver.page_source
        soup_after_click = BeautifulSoup(after_click_page_source, 'html.parser')
        content = soup_after_click.select(f'#modal-{modal_id} div div div.modal-body div.bg-info.event-description p')
        abstract = " ".join([p.get_text().strip() for p in content if p.get_text().strip() != ""])
        close_bnt = driver.find_element(By.XPATH, f'//*[@id="modal-{modal_id}"]/div/div/div[1]/a[1]')
        close_bnt.click()
        result.append(PaperMeta(title, performers, abstract))
        idx += 1
        if idx % 30 == 0:
            logger.info(f'obtain {idx}/{len(rows)} paper...')
    return result


def crawler_papers(url) -> List[PaperMeta]:
    logger.info("Start ConfBot Crawler")
    driver = get_driver()
    if get_url(url, driver):
        result = get_paper(driver)
        driver.quit()
        return result
    else:
        logger.info("End Crawler")
        driver.quit()
        return []
