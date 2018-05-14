# coding=utf-8

import re
from configparser import ConfigParser

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import turndown_transform
from blog import Blog
import json
from selenium import webdriver

from common_utils import *


class CSDNDownloader:
    def __init__(self, page_index=1, url=""):
        if "article/list" not in url:
            self.identification = url[find_sub_str("/", url, 3) + 1:len(url) - 1] \
                if url[len(url) - 1] == "/" else url[url.rfind('/') + 1:]
        else:
            self.identification = url[find_sub_str("/", url, 3) + 1:find_sub_str("/", url, 4)]
        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'blogs2md.ini'))
        self.profile = config.get("config", "profile")
        self.work_dir = config.get(self.profile, "workDir") + os.sep + self.identification
        if not os.path.exists(self.work_dir):
            os.mkdir(self.work_dir)
        else:
            delete_file_folder(self.work_dir)
            os.mkdir(self.work_dir)
        self.pageIndex = page_index
        self.url = url
        self.driver = self.get_driver()

    def get_bs(self, url):
        # 请求网页
        driver = self.driver
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        return soup

    @staticmethod
    def get_driver():
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument("--no-sandbox")
        driver = webdriver.Chrome(chrome_options=option)
        return driver

    # 获取博客的博文分页总数
    def get_total_pages(self):
        driver = self.driver
        driver.get(self.url)
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.ID, 'pageBox')))
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        find_all = soup.find_all('li', 'ui-pager')
        pages = find_all[len(find_all) - 3].get_text()
        return int(pages)

    # 读取每个页面上各博文的主题、链接、日期、访问量、评论数等信息
    def get_blog_info(self, page_index):
        res = []
        blogs_res = []
        if "article/list" not in self.url:
            page_url = self.url + "article/list/1" if self.url[
                                                          len(self.url) - 1] == "/" else self.url + "/article/list/1"
        else:
            page_url = self.url[0:self.url.rfind('/') + 1] + str("1")
        soup = self.get_bs(page_url)
        # 得到目标信息
        blog_items = soup.find_all('div', 'article-item-box csdn-tracking-statistics')
        for item in blog_items:
            title = item.find('h4', 'text-truncate').a.get_text()[40:].strip()
            blog = '\n标题:' + title

            link = item.find('h4', 'text-truncate').a.get("href")
            blog += '\n博客链接:' + link

            postdate = item.find('span', 'date').get_text()
            blog += '\n发表日期:' + postdate

            views_text = item.findAll('span', 'read-num')[0].get_text()  # 阅读(38)
            views = re.findall(re.compile(r'(\d+)'), views_text)[0]
            blog += '\n访问量:' + views

            comments_text = item.findAll('span', 'read-num')[1].get_text()
            comments = re.findall(re.compile(r'(\d+)'), comments_text)[0]
            blog += '\n评论数:' + comments + '\n'

            blog_obj = Blog(title, link, postdate, views, comments, page_index)
            blogs_res.append(blog_obj)

            print(blog)
            res.append(blog)
            res.append("-" * 20)
        return res, blogs_res

    def transform2md(self, href):
        soup = self.get_bs(href)
        for code_div in soup.findAll('div', 'dp-highlighter'):
            code_div.extract()
        content_str = soup.find('div', 'article_content').prettify()
        all_code = re.findall(r'<pre class=\".*?\">[\w\W]*?</pre>', content_str, re.M | re.I)
        for one in all_code:
            # 不是markdown编写的文档，这里不用替换
            if "prettyprint" not in one:
                content_str = content_str.replace(one, " #codeBegin#" +
                                                  one[find_sub_str("\"", one, 1) + 1:find_sub_str("\"", one, 2)]
                                                  + one + " #codeEnd# ")
        result = turndown_transform.transform(content_str)
        result = result.replace("#codeBegin#", "```")
        result = result.replace("#codeEnd#", "```")
        return result

    def save_page_overall_file(self, datas, page_index):
        """ 保存每页的博客概览 """
        if not os.path.exists(self.work_dir + os.sep + "page_" + str(page_index + 1)):
            os.mkdir(self.work_dir + os.sep + "page_" + str(page_index + 1))

        page_blog_overall_file_path = self.work_dir + os.sep + "page_" + str(
            page_index + 1) + os.sep + "page_blog_overall.txt"
        with open(page_blog_overall_file_path, 'w', encoding='utf-8') as page_blog_overall_file:
            page_blog_overall_file.write('当前页：' + str(page_index + 1) + '\n')
            for data in datas:
                page_blog_overall_file.write(data)

    def save_overall_file(self, all_blogs):
        """ 保存所有的博客概览 """
        global path, file
        # 保存总体概览json
        path = self.work_dir + os.sep + "overall.json"
        print("save overall file to :" + path)
        with open(path, 'w', encoding='utf-8') as file:
            file.write(
                json.dumps(all_blogs, ensure_ascii=False, default=lambda o: o.__dict__, sort_keys=True, indent=4))

    def save_blogs_in_md(self, all_blog):
        i = 0
        blogs_length = len(all_blog)
        for blog in all_blog:
            i += 1
            print("transform %s to markdown ,remain %d " % (blog.title, (blogs_length - i)))
            md_result = spider.transform2md(blog.link)
            md_path = self.work_dir + os.sep + "page_" + str(blog.page_index) + os.sep + blog.title + ".md "
            with open(md_path, 'w', encoding='utf-8') as md_file:
                md_file.write(md_result)


if __name__ == "__main__":
    spider = CSDNDownloader(url="https://blog.csdn.net/sbpeng")

    try:
        pageNum = spider.get_total_pages()
        print("博客总页数：", pageNum)
        all_blogs = []

        for index in range(pageNum):
            print("正在处理第%s页…" % (index + 1))
            blogsInfo, blogs = spider.get_blog_info(index + 1)
            spider.save_page_overall_file(blogsInfo, index)
            all_blogs.extend(blogs)

        spider.save_overall_file(all_blogs)
        # 单个页面保存
        spider.save_blogs_in_md(all_blogs)
    except(TypeError, IndexError) as err:
        print("got exception" + err)
    finally:
        print("closing driver")
        spider.driver.close()
        spider.driver.quit()
