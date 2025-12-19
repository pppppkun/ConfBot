import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from data import read_papers_from_csv, save_papers_to_csv, PaperRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConfBot-GenKW')
logger.setLevel(logging.DEBUG)

load_dotenv(override=True)

api_key = os.getenv("API_KEY")
base_url = os.getenv("BASE_URL")
model = os.getenv("MODEL")
basic_prompt = open('prompt.txt', 'r').read()

if not api_key:
    raise ValueError("Not find API_KEY, please check .env")


client = OpenAI(
    api_key=api_key,
    base_url=base_url
)


def generate_prompt(keywords, title, abstract):
    prompt = basic_prompt.format(keywords=keywords, title=title, abstract=abstract)
    return prompt


def chat_with_llm(prompt):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        # print(f"请求失败: {e}")
        logger.info(f"Requrest Failed {e}")
        return None


def assign_keywords(keywords, title, abstract):
    prompt = generate_prompt(keywords, title, abstract)
    while content := chat_with_llm(prompt):
        if content:
            return content


def batch_update_keywords(csv_path):
    logger.info(f"Reading {csv_path} ...")
    papers = read_papers_from_csv(csv_path)
    logger.info(f"Total records read: {len(papers)}")

    updated_count = 0
    keywords = set()
    for paper in papers:
        if paper.keyword:
            kws = paper.keyword.split(',')
            keywords.update(kws)
    keywords = list(keywords)
    for index, paper in enumerate(papers):
        if paper.keyword and len(paper.keyword.strip()) > 0:
            continue
            
        logger.info(f"Generating keyword for ID {paper.id}...")
        
        try:
            new_keyword = assign_keywords(keywords, paper.title, paper.abstract)
            paper.keyword = new_keyword
            # keywords += new_keyword.split(',')
            for kw in new_keyword.split(','):
                if kw not in keywords:
                    keywords.append(kw)
            updated_count += 1
            
            if updated_count % 10 == 0:
                logger.info(f"--> Generated {updated_count} new items, performing intermediate save...")
                save_papers_to_csv(csv_path, papers)

        except Exception as e:
            logger.error(f"Error generating for ID {paper.id}: {e}")
            continue

    if updated_count > 0:
        save_papers_to_csv(csv_path, papers)
        logger.info(f"All done! Updated keywords for {updated_count} records.")
    else:
        logger.info("No data needed updates.")