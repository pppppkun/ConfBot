from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os

def run_browser():
    # 1. 设置 Chrome 选项
    chrome_options = Options()
    driver_path = './chromedriver'
    
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # --- 关键修改 1: 设置大窗口 ---
    chrome_options.add_argument("--window-size=1920,1080")

    # --- 关键修改 2: 伪装 User-Agent (去掉 Headless 字样) ---
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    
    print("正在启动浏览器...")
    
    driver = webdriver.Chrome(service=Service(executable_path=driver_path), options=chrome_options)

    try:
        url = "https://conf.researchr.org/track/fse-2025/fse-2025-research-papers"

        print(f"正在尝试访问: {url}")
        driver.get(url)

        print(f"页面标题: {driver.title}")
        
        # 简单验证一下是否拿到了内容
        if "Research Papers" in driver.page_source:
            print("成功检测到 'Research Papers' 关键词！")
        else:
            print("页面加载了，但没找到关键词，可能被重定向了。")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        # 5. 务必关闭浏览器，否则会残留进程占满内存
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    run_browser()