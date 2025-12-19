import csv
import os
import re
import logging
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ConfBot-Data')
logger.setLevel(logging.DEBUG)

@dataclass
class PaperMeta:
    title: str
    authors: str
    abstract: str


@dataclass
class PaperRecord:
    id: int
    conference: str
    year: str
    title: str
    authors: str  
    abstract: str
    keyword: str = "" 


def from_meta_to_csv(path, url, result: List[PaperMeta]):
    logger.info("Analysis the conference and year...")
    year_match = re.search(r'20\d{2}', url)
    current_year = year_match.group(0) if year_match else "Unknown"
    
    url_lower = url.lower()
    current_conf = "Unknown"
    valid_confs = ['icse', 'ase', 'fse', 'issta']
    for conf in valid_confs:
        if conf in url_lower:
            current_conf = conf
            break
    logger.info(f"Conf: {current_conf}, Year: {current_year}")
    fieldnames = ['id', 'conference', 'year', 'title', 'authors', 'abstract', 'keywords']
    
    all_rows = []
    existing_titles = set()
    next_id = 1
    
    if os.path.exists(path):
        try:
            with open(path, mode='r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_rows.append(row)
                    existing_titles.add(row['title'])
                    if row['id'].isdigit():
                        next_id = max(next_id, int(row['id']) + 1)
        except Exception as e:
            logger.info(f"Failed to read file {e}. Create a new file.")
    logger.info("Add the new data...")
    new_count = 0
    for paper in result:
        if paper.title not in existing_titles:
            new_row = {
                'id': next_id,
                'conference': current_conf,
                'year': current_year,
                'title': paper.title,
                'authors': paper.authors,
                'abstract': paper.abstract,
                'keywords': ''
            }
            all_rows.append(new_row)
            existing_titles.add(paper.title)
            next_id += 1
            new_count += 1
    
    logger.info("Write back to file...")
    try:
        with open(path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
        logger.info(f"Success. Original {len(all_rows) - new_count}. Add {new_count}")
        logger.info(f"Conference: {current_conf} Year: {current_year}")

    except IOError as e:
        logger.info(f"Failed to write into file {e}")


def read_papers_from_csv(path: str) -> List[PaperRecord]:
    results = []
    if not os.path.exists(path):
        logger.info(f"File not found: {path}")
        return results

    try:
        # Use utf-8-sig to handle potential BOM
        with open(path, mode='r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                paper = PaperRecord(
                    id=int(row['id']),
                    conference=row['conference'],
                    year=row['year'],
                    title=row['title'],
                    authors=row['authors'],
                    keyword=row.get('keywords', ""), 
                    abstract=row['abstract']
                )
                results.append(paper)
        return results
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return []


def save_papers_to_csv(path: str, papers: List[PaperRecord]):
    # Define header order
    fieldnames = ['id', 'conference', 'year', 'title', 'authors', 'abstract', 'keywords']
    
    try:
        # Use 'w' mode to overwrite
        with open(path, mode='w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for paper in papers:
                row = {
                    'id': paper.id,
                    'conference': paper.conference,
                    'year': paper.year,
                    'title': paper.title,
                    'authors': paper.authors, 
                    'keywords': paper.keyword,
                    'abstract': paper.abstract
                }
                writer.writerow(row)
    except Exception as e:
        logger.error(f"Failed to save file: {e}")


# --- 测试代码 ---
if __name__ == "__main__":
    # 模拟数据
    papers = [
        PaperMeta(title="AI for SE", authors="Alice, Bob", abstract="Abstract 1"),
        PaperMeta(title="Testing LLMs", authors="Charlie", abstract="Abstract 2"),
        PaperMeta(title="AI for SE", authors="Alice, Bob", abstract="Duplicate Title Test") # 测试重复
    ]
    
    csv_path = "papers.csv"
    test_url = "https://conf.org/issta/2023/index.html"
    
    from_meta_to_csv(csv_path, test_url, papers)