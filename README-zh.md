# ConfBot

ConfBot 用于抓取学术会议论文元数据、可选地通过 LLM 生成关键词，并在 Streamlit 仪表盘中展示分析结果。

项目现已使用 `uv` 管理依赖，并使用 Playwright 进行浏览器自动化抓取。

## 功能

- 抓取会议页面中的论文标题、作者和摘要
- 将标准化后的元数据保存为 CSV
- 通过 LLM 流程生成关键词
- 在 Streamlit 数据看板中查看分析结果

## 环境要求

- Python `3.11+`
- `uv`

## 安装

```bash
uv sync
uv run playwright install chromium
```

如果关键词生成功能依赖环境变量，请在运行前准备 `.env` 文件。

常见变量示例：

- `API_KEY`
- `BASE_URL`
- `MODEL`

## 使用方式

运行抓取与关键词生成主流程：

```bash
uv run python main.py
```

仅抓取指定会议 track，不生成关键词：

```bash
uv run python main.py --urls "https://conf.researchr.org/track/fse-2025/fse-2025-research-papers" --no-keyword
```

启动数据看板：

```bash
uv run streamlit run app.py
```

## 验证

编译主要入口文件：

```bash
uv run python -m py_compile crawler.py test_playwright.py main.py
```

运行 Playwright 冒烟测试：

```bash
uv run python test_playwright.py
```

如果 Playwright 提示缺少浏览器可执行文件，请执行：

```bash
uv run playwright install chromium
```

## 主要文件

- `crawler.py` - 基于 Playwright 的爬虫
- `main.py` - 抓取与关键词生成的 CLI 入口
- `genkw.py` - 关键词生成逻辑
- `analysis.py` - 分析逻辑辅助函数
- `app.py` - Streamlit 数据看板

## 免责声明

本项目仅用于学术研究与教学用途。
使用者需自行遵守目标网站的服务条款及 `robots.txt` 协议。
开发者不对任何因使用本代码而产生的滥用或法律问题负责。
