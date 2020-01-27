# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import mysql.connector

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
        sql = "INSERT INTO albums (title, artist, url) VALUES (%s, %s, %s)"
        self.cursor.execute(sql,
                            (
                                item.get("title"),
                                item.get("artist"),
                                item.get("url"),
                            ))
        self.conn.commit()
        self.process_genres(self.cursor.lastrowid, 'album', item.get("genres"))

    def process_musics(self, item):
        sql = "INSERT INTO musics (title, artist, duration, uploaded, listens, " \
              "starred, comments, downloads) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

        self.cursor.execute(sql,
                            (
                                item.get("title"),
                                item.get("artist"),
                                item.get("duration"),
                                self.convert_date(item.get("uploaded")),
                                item.get("listens"),
                                item.get("starred"),
                                item.get("comments"),
                                item.get("downloads"),
                            ))
        self.conn.commit()
        self.process_genres(self.cursor.lastrowid, 'music', item.get("genres"))

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

    def close_spider(self, spider):
        self.conn.close()
