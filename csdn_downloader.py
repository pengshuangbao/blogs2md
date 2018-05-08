# coding=utf-8

import re
from configparser import ConfigParser

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import turndown_transform
from blog import Blog
import json
from selenium import webdriver
import os

from string_utils import find_sub_str


class CSDNDownloader:
    # 初始化爬取的页号、链接以及封装Header
    def __init__(self, page_index=1, url=""):
        if "article/list" not in url:
            self.identification = url[find_sub_str("/", url, 3) + 1:len(url) - 1] if url[len(url) - 1] == "/" else url[url.rfind(
                '/') + 1:]
        else:
            self.identification = url[find_sub_str("/", url, 3) + 1:find_sub_str("/", url, 4)]

        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'blogs2md.ini'))
        self.profile = config.get("config", "profile")
        self.work_dir = config.get(self.profile, "workDir") + "\\" + self.identification
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)
        else:
            os.rmdir(self.work_dir)
            os.mkdir(self.work_dir)

        self.pageIndex = page_index
        self.url = url

    def get_bs(self, url):
        # 请求网页
        driver = self.get_driver()
        driver.get(url)
        # 以html5lib格式的解析器解析得到BeautifulSoup对象
        # 还有其他的格式如：html.parser/lxml/lxml-xml/xml/html5lib
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        return soup

    def get_driver(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        driver = webdriver.Chrome(chrome_options=option)
        return driver

    # 获取博客的博文分页总数
    def get_total_pages(self):
        driver = self.get_driver()
        driver.get(self.url)
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'pageBox')))
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        find_all = soup.find_all('li', 'ui-pager')
        pages = find_all[len(find_all) - 3].get_text()
        return int(pages)

    # 读取每个页面上各博文的主题、链接、日期、访问量、评论数等信息
    def get_blog_info(self, page_index):
        res = []
        blogs = []
        if not "article/list" in self.url:
            page_url = self.url + "article/list/1" if self.url[
                                                          len(self.url) - 1] == "/" else self.url + "/article/list/1"
        else:
            page_url = self.url[0:self.url.rfind('/') + 1] + str("1")
        soup = self.get_bs(page_url)
        # 得到目标信息
        blog_items = soup.find_all('div', 'article-item-box csdn-tracking-statistics')
        for item in blog_items:
            # 博文主题
            title = item.find('h4', 'text-truncate').a.get_text()[40:].strip()
            blog = '\n标题:' + title

            # 博文链接
            link = item.find('h4', 'text-truncate').a.get("href")
            blog += '\n博客链接:' + link

            # 博文发表日期
            postdate = item.find('span', 'date').get_text()
            blog += '\n发表日期:' + postdate

            # 博文的访问量
            views_text = item.findAll('span', 'read-num')[0].get_text()  # 阅读(38)
            views = re.findall(re.compile(r'(\d+)'), views_text)[0]
            blog += '\n访问量:' + views

            # 博文的评论数
            comments_text = item.findAll('span', 'read-num')[1].get_text()
            comments = re.findall(re.compile(r'(\d+)'), comments_text)[0]
            blog += '\n评论数:' + comments + '\n'

            blog_obj = Blog(title, link, postdate, views, comments, page_index)
            blogs.append(blog_obj)
            print(blog)
            res.append(blog)
            res.append("-" * 20)
        return res, blogs

    def transform2md(self, href):
        soup = self.get_bs(href)
        str = soup.find('div', 'article_content').prettify()
        all = re.findall(r'<pre class=\".*?\">[\w\W]*?</pre>', str, re.M | re.I)
        codeRe = re.compile(r'<pre class=\"(.*?)\">', re.M | re.I)
        for one in all:
            str = str.replace(one, " #codeBegin#" + codeRe.match(one).group(1) + one + " #codeEnd# ")
        result = turndown_transform.transform(str)
        result = result.replace("#codeBegin#", "```")
        result = result.replace("#codeEnd#", "```")
        return result

    def saveFile(self, datas, page_index):
        if not os.path.exists(self.work_dir + "\\page_" + str(page_index + 1)):
            os.mkdir(self.work_dir + "\\page_" + str(page_index + 1))

        path = self.work_dir + "\\page_" + str(page_index + 1) + "\page_blog_overall.txt"
        with open(path, 'w', encoding='utf-8') as file:
            file.write('当前页：' + str(page_index + 1) + '\n')
            for data in datas:
                file.write(data)

    def save_overall_file(self):
        global path, file
        # 保存总体概览json
        path = self.work_dir + "\\overall.json"
        with open(path, 'w', encoding='utf-8') as file:
            file.write(
                json.dumps(all_blogs, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    def save_blogs_in_md(self, all_blogs):
        global blog, path, file
        for blog in all_blogs:
            md_result = spider.transform2md(blog.link)
            path = self.work_dir + "\\page_" + str(blog.page_index + 1) + "\\" + blog.title + ".md "
            with open(path, 'w', encoding='utf-8') as file:
                file.write(md_result)


if __name__ == "__main__":
    spider = CSDNDownloader(url="https://blog.csdn.net/sbpeng")
    pageNum = spider.get_total_pages()
    print("博客总页数：", pageNum)
    all_blogs = []

    for index in range(pageNum):
        print("正在处理第%s页…" % (index + 1))
        blogsInfo, blogs = spider.get_blog_info(index + 1)
        spider.saveFile(blogsInfo, index)
        all_blogs.extend(blogs)

    spider.save_overall_file()

    # 单个页面保存
    spider.save_blogs_in_md(all_blogs)
