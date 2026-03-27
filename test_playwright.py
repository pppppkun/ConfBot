from playwright.sync_api import Error, sync_playwright


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


def run_browser():
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=USER_AGENT,
                viewport={"width": 1920, "height": 1080},
            )
            page = context.new_page()

            try:
                url = (
                    "https://conf.researchr.org/track/fse-2025/fse-2025-research-papers"
                )
                print("正在启动浏览器...")
                print(f"正在尝试访问: {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_selector(
                    "#event-overview table tbody tr", state="attached", timeout=15000
                )

                print(f"页面标题: {page.title()}")

                if "Research Papers" in page.content():
                    print("成功检测到 'Research Papers' 关键词！")
                else:
                    print("页面加载了，但没找到关键词，可能被重定向了。")
            except Exception as e:
                print(f"发生错误: {e}")
            finally:
                context.close()
                browser.close()
                print("浏览器已关闭")
    except Error as e:
        print(f"Playwright 启动失败: {e}")
        print("请先执行: uv run playwright install chromium")


if __name__ == "__main__":
    run_browser()
