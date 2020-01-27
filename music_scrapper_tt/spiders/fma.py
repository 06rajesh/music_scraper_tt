# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from music_scrapper_tt.items import AlbumItem, MusicItem


class FmaSpider(scrapy.Spider):
    name = 'fma'
    allowed_domains = ['freemusicarchive.org']
    base_url = 'http://freemusicarchive.org/'

    @staticmethod
    def safe_strip(content):
        if isinstance(content, str):
            return content.strip()
        else:
            return content

    @staticmethod
    def remove_char(content):
        if isinstance(content, str):
            new = ""
            for char in content:
                if (45 < ord(char) < 58) or (62 < ord(char) < 91) or (96 < ord(char) < 123):
                    new += char
            return new
        else:
            return content

    def start_requests(self):
        urls = [
            'http://freemusicarchive.org/genre/Blues/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for play_item in response.css('div.playlist div.play-item'):
            song_url = play_item.css('div.playtxt span.ptxt-track a::attr(href)').extract_first()
            if len(song_url) > 0:
                yield Request(self.base_url + song_url, callback=self.parse_music_page)

            album_url = play_item.css('div.playtxt span.ptxt-album a::attr(href)').extract_first()
            if len(album_url) > 0:
                yield Request(self.base_url + album_url, callback=self.parse_album_page)

    def parse_music_page(self, response):
        page_bcumb = '//div[@id="content"]/div[@class="bcrumb"]'

        music_dict = MusicItem()

        music_dict["title"] = self.safe_strip(response.xpath(page_bcumb + '/h1/text()').extract()[1])
        music_dict["artist"] = self.safe_strip(response.xpath(page_bcumb + '/h1/span[@class="subh1"]/a/text()')
                                               .extract_first())
        music_dict["duration"] = self.safe_strip(response.css('div.playlist div.play-item span.playtxt::text').extract()[2])

        for stats in response.css('div.colr-sml-toppad div.sbar-stat'):
            stat_key = self.remove_char(stats.css('span.stathd::text').extract_first().lower())
            stat_val = self.safe_strip(stats.css('b::text').extract_first())
            try:
                music_dict[stat_key] = stat_val
            except KeyError:
                pass

        genre_stats = response.xpath('//div[@class="colr-lrg"]/div[@class="sbar-stat-auto"]/'
                                     'div[@class="stat-item"]/a/text()').extract()
        music_dict["genres"] = genre_stats

        yield music_dict

    def parse_album_page(self, response):
        album_dict = AlbumItem()
        page_bcumb = '//div[@id="content"]/div[@class="bcrumb"]'

        album_dict["title"] = self.safe_strip(response.xpath(page_bcumb + '/h1/text()').extract_first())
        album_dict["artist"] = self.safe_strip(response.xpath(page_bcumb + '/h1/span[@class="subh1"]/a/text()')
                                               .extract_first())
        album_dict['url'] = response.request.url
        infobox = response.css('div.col-l div.sbar-stnd')

        album_dict["image_url"] = infobox.css('div.album-image img::attr(src)').extract_first()
        for stat in infobox.css('div.sbar-stat'):
            stat_key = self.remove_char(stat.css('span.stathd::text').extract_first().lower())
            stat_val = self.safe_strip(stat.css('b::text').extract_first())
            try:
                album_dict[stat_key] = stat_val
            except KeyError:
                pass

        for stat in infobox.css('div.sbar-stat-multi'):
            stat_key = self.remove_char(stat.css('span.stathd::text').extract_first().lower())
            stat_val = self.safe_strip(stat.css('ul li a::text').extract())
            try:
                album_dict[stat_key] = stat_val
            except KeyError:
                pass

        description = ""
        for para in infobox.css("div.main-txt-lessbot p"):
            description += self.safe_strip(para.css('*::text').extract_first())

        album_dict['desc'] = description

        return album_dict
