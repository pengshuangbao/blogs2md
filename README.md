# blogs2md

支持将主流的博客网站的博客批量下载并生成博客预览，生成markdown文件。

## 环境与依赖

- python 3.6.4rc1
- node.js v8
- python bs4
- html5lib
- selenium
- chrome-driver  2.34 headless模式

## 使用方法

### 配置

将workDir工作目录替换成自己的有读写权限的目录

![image](http://p82ruazh4.bkt.clouddn.com/jpg/2018/5/9/9fdad54baeae5aea589ae00eaafb80da.jpg)

### 将下面的url替换为自己的博客主页地址

```python
if __name__ == "__main__":
    spider = CSDNDownloader(url="https://blog.csdn.net/sbpeng")
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
```

## 待优化

- 目前不支持表格以及数学公式的转换
- 目前只支持CSDN的博客转换，需要支持更多的博客转换
