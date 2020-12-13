import scrapy
from scrapy.loader import ItemLoader
from myproana.items import PostItem, ThreadItem
import re
import logging
from scrapy.utils.log import configure_logging


class AnaroxiaSpider(scrapy.Spider):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    name = 'anaroxia'
    #allowed_domains = ['https://www.myproana.com/']
    #custom_settings = {'DEPTH_LIMIT': 4000}

    def start_requests(self):
        start_url = "https://www.myproana.com/index.php/forum/62-anorexia-discussions/"#"https://www.myproana.com/index.php/forum/62-anorexia-discussions/"
        yield scrapy.Request(start_url, self.parse_thread)

    def parse_thread(self, response):
        for product in response.css("tr.__topic"):
            loader = ItemLoader(item=ThreadItem(), selector=product)
            loader.add_value('subforumname', response.css("div.ipsLayout_content h1::text").extract_first())
            loader.add_css('threadtitle', "td.col_f_content a.topic_title span::text")
            loader.add_css('authorname', "td.col_f_content span.desc::text")
            loader.add_css('url', "td.col_f_content a.topic_title::attr(href)")
            loader.add_value('startdate', product.css("td.col_f_content span.desc span[itemprop='dateCreated']::text").get())
            yield loader.load_item()

            thread_item = loader.load_item()
            thread_url = product.css("td.col_f_content a.topic_title::attr(href)").extract_first()
            yield response.follow(thread_url, self.parse_post, meta={'thread_item': thread_item})

        next_page = response.css("ul.forward li.next a::attr(href)").extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_thread)

    def parse_post(self, response):
        thread_item = response.meta['thread_item']
        thread_loader = ItemLoader(item=thread_item)
        threadtitle = thread_loader.get_collected_values('threadtitle')

        for product in response.xpath("//div[contains(@class, 'post_block')]"):

            loader = ItemLoader(item=PostItem(), selector=product)
            loader.add_value('threadtitle', threadtitle)

            temp = product.css("div.post_block div.post_wrap div.post_body").extract()
            temp = re.sub('<br>|<strong>|<\/strong>|<em>|<\/em>', ' ', temp[0])
            temp = re.sub('\n', ' ', temp)
            temp = re.sub('<blockquote(.*?)blockquote>', ' ', str(temp))

            selector = scrapy.Selector(text=str(temp))
            loader.add_value("postcontent", selector.xpath("//div[contains(@class,'post_body')]/div[@itemprop='commentText'][1]").extract())


            loader.add_value("authorname", product.css(
                "div.post_wrap div.author_info div.user_details span[itemprop='name']::text").get(default='N/A'))
            loader.add_value("authortype",
                             product.css("div.post_wrap div.author_info div.user_details li.group_title::text").get())
            loader.add_value("noposts",
                             product.css("div.post_wrap div.author_info div.user_details li.post_count::text").get())
            if len(product.css("div.post_wrap div.post_body div.signature").getall()) > 0:
                loader.add_value("authorsign", product.css("div.post_wrap div.post_body div.signature").getall())

            else:
                loader.add_value("authorsign", ['N/A'])

            loader.add_value("date",
                             product.css("div.post_wrap div.post_body p.posted_info abbr.published::text").get())

            yield loader.load_item()

        next_page = response.xpath("//div[contains(@class, 'topic_controls')]/div[contains(@class, 'pagination')]/"
                                   "ul[contains(@class, 'forward')]/li[contains(@class, 'next')]/a/@href").extract_first()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_post, meta={'thread_item': thread_item}) #
