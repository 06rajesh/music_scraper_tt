# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AlbumItem(scrapy.Item):
    title = scrapy.Field()
    artist = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()
    length = scrapy.Field()
    released = scrapy.Field()
    label = scrapy.Field()
    genres = scrapy.Field()
    desc = scrapy.Field()


class MusicItem(scrapy.Item):
    title = scrapy.Field()
    artist = scrapy.Field()
    duration = scrapy.Field()
    url = scrapy.Field()
    uploaded = scrapy.Field()
    listens = scrapy.Field()
    starred = scrapy.Field()
    comments = scrapy.Field()
    downloads = scrapy.Field()
    genres = scrapy.Field()
