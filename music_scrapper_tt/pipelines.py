# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import mysql.connector
from datetime import datetime
import re

from scrapy.exceptions import NotConfigured
from music_scrapper_tt.items import AlbumItem


class ItemToDBPipeline(object):

    def __init__(self, db, user, password, host):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.conn = None
        self.cursor = None
        self.crawled = 0
        self.failed = 0

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("DB_SETTINGS")
        if not db_settings:  # if we don't define db config in settings
            raise NotConfigured  # then reaise error
        db = db_settings['db']
        user = db_settings['user']
        password = db_settings['password']
        host = db_settings['host']
        return cls(db, user, password, host)  # returning pipeline instance

    @staticmethod
    def convert_date(date_str):
        splitted = date_str.split('/')
        return splitted[2] + "-" + splitted[0] + "-" + splitted[1]

    @staticmethod
    def convert_album_date(date_str):
        if date_str is not None:
            tails = re.findall(r"\d+(st|nd|rd|th)", date_str)
            if len(tails) == 1:
                new_str = date_str.replace(tails[0], "")
                try:
                    date_object = datetime.strptime(new_str, "%B %d, %Y")
                    return date_object.date()
                except ValueError:
                    return None
            else:
                return None
        else:
            return None

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(db=self.db,
                                            user=self.user, passwd=self.password,
                                            host=self.host,
                                            charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item, AlbumItem):
            self.process_albums(item)
        else:
            self.process_musics(item)
        return item

    def process_albums(self, item):
        sql = "INSERT INTO albums (title, artist, url, image, length, released, label, description) VALUES " \
              "(%s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            self.cursor.execute(sql,
                                (
                                    item.get("title"),
                                    item.get("artist"),
                                    item.get("url"),
                                    item.get("image_url"),
                                    item.get("length"),
                                    self.convert_album_date(item.get("released")),
                                    item.get("label"),
                                    item.get("desc"),
                                ))
            self.conn.commit()
            self.process_genres(self.cursor.lastrowid, 'album', item.get("genres"))
            self.crawled += 1
        except mysql.connector.Error as err:
            self.save_failed_urls(item.get("url"))

    def process_musics(self, item):
        sql = "INSERT INTO musics (title, artist, url, duration, uploaded, listens, " \
              "starred, comments, downloads) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

        try:
            self.cursor.execute(sql,
                                (
                                    item.get("title"),
                                    item.get("artist"),
                                    item.get("url"),
                                    item.get("duration"),
                                    self.convert_date(item.get("uploaded")),
                                    item.get("listens"),
                                    item.get("starred"),
                                    item.get("comments"),
                                    item.get("downloads"),
                                ))
            self.conn.commit()
            self.process_genres(self.cursor.lastrowid, 'music', item.get("genres"))
            self.crawled += 1
        except mysql.connector.Error as err:
            self.save_failed_urls(item.get("url"))

    def process_genres(self, item_id, item_type, genres):
        table_name = 'album_genres'
        if item_type == "music":
            table_name = "music_genres"
        if isinstance(genres, list) and len(genres) > 0:
            sql = "INSERT INTO " + table_name + " (" + item_type + ", genre) VALUES (%s, %s)"
            for genre in genres:
                self.cursor.execute(sql,
                                    (
                                        item_id,
                                        genre,
                                    ))
            self.conn.commit()

    def save_failed_urls(self, url):
        sql = "INSERT INTO failed_urls (url) VALUES ('" + url + "')"
        self.cursor.execute(sql)
        self.conn.commit()
        self.failed += 1

    def close_spider(self, spider):
        self.conn.close()
        print("Total {} pages crawled and {} pages failed".format(self.crawled, self.failed))
