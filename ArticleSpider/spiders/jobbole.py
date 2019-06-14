# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from ArticleSpider.items import JobBoleArticleItem


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['http://blog.jobbole.com/']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章中列表页的文章url并交给scrapy下载后并解析
        2.获取下一页的url交给scrapy下载，下载完成交给parse解析

        """
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_url in post_nodes:
            image_url = post_nodes.css("img::attr(src)").extract_first("")
            post_url = post_nodes.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_ulr": image_url},
                          callback=self.parse_datail)

        # 提取下一页url
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse_datail)
        response.css('#archive .floated-thumb .post-thumb a::attr(href)').extract()

    def parse_datail(self, response):
        article_item = JobBoleArticleItem()
        # 文章封面图
        front_image_url = response.meta.get("front_image_url", "")
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        create_time = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·',
                                                                                                                    '').strip()
        # 点赞数
        praise_nums = int(response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0])
        # 收藏数
        fav_nums = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        match_re = re.match(".*(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        # 评论数
        comments_nums = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        match_re = re.match(".*(\d+).*", comments_nums)
        if match_re:
            comments_nums = int(match_re.group(1))
        else:
            comments_nums = 0
        # 正文内容
        content = response.xpath('//div[@class="entry"]').extract()[0]
        # 标签
        tag_list = response.xpath("//p[@class='entry-meta-hide-on-mobile']/a/text()").extract()
        # tag_list = [element for element in tag_list if not element.strip().endwith("评论")]
        tags = ",".join(tag_list)

        # 提出过CSS选择器提取字段
        # title = response.css(".entry-header h1::text").extract()
        # create_time = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace('·' ,'').strip()
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_time"] = create_time
        article_item["fron_image_url"] = [front_image_url]
        article_item["praise_nums"] = praise_nums
        article_item["comment_nums"] = comments_nums
        article_item["fav_nums"] = fav_nums
        article_item["tags"] = tags
        article_item["content"] = content

        yield article_item

