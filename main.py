import click
import logging
from crawler import crawler_papers
from data import from_meta_to_csv
from genkw import batch_update_keywords

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConfBot-Main')
logger.setLevel(logging.DEBUG)

@click.command()
@click.option('--urls', prompt=True, required=True, help='The SE conference links you want. Use , to seperate each link.')
@click.option('--keyword/--no-keyword', default=True, type=click.BOOL, help='whether generate the keyword ')
@click.option('--crawler/--no-crawler', default=True, type=click.BOOL, help='whether scrape the data')
@click.option('--retry', default=3, type=click.INT, help='Max retries for crawler errors', show_default=True)
@click.option('--metasave', default='meta.csv', help='Path for save the meta information', show_default=True)
@click.option('--browser', default=True)
def main(urls, keyword, crawler, retry, metasave, browser):
    urls = urls.split(',')
    if crawler:
        for url in urls:
            logging.info(f'Start crawler for {url}...')
            for i in range(retry):
                result = crawler_papers(url)
                if result:
                    logger.info('Success')
                    break
                else:
                    logger.info(f'Failed, retry (remain {retry-i-1} times)')
        from_meta_to_csv(metasave, url, result)
    if keyword:
        batch_update_keywords(metasave)


if __name__ == '__main__':
    main()