## 使用指南

因为使用的是比较古老的Selenium框架，所以还需要下载一个chromedriver后才可以启动。不启动浏览器的时候会有bug，有时间换成playwright比较好。在main.py中会爬取网站里的论文（仅测试过SE的四大会），然后利用LLM来基于标题和摘要来分配关键词。关键词会用于后续的数据分析，数据分析和展示都是在app.py中进行的。

## 免责声明

This script is developed strictly for academic research and educational purposes. 
The user assumes all responsibility for complying with the target website's 
Terms of Service and robots.txt. The developer shall not be held liable for 
any misuse or legal issues resulting from the execution of this code.


本程序仅用于学术研究与教学目的。使用者需自行承担遵守目标网站服务条款及
robots.txt 协议的责任。开发者不对任何因使用本代码而产生的法律纠纷负责。