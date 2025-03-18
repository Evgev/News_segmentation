import requests
from collections import deque
import feedparser
import time
import streamlit as st

def rss_parser(posted_q, n_test_chars, send_message_func=None):
    '''Синхронный парсер rss ленты'''
    rss_link = 'https://rssexport.rbc.ru/rbcnews/news/10/full.rss'

    count = 5
    while count:
        count -=1
        try:
            response = requests.get(rss_link)
            feed = feedparser.parse(response.text)

            for entry in feed.entries[::-1]:
                summary = entry['summary']
                title = entry['title']
                news_text = f'{title}\n{summary}'
                head = news_text[:n_test_chars].strip()

                if head in posted_q:
                    continue

                if send_message_func is None:
                    print(news_text, '\n')
                else:
                    send_message_func(f'rbc.ru\n{news_text}')

                posted_q.appendleft(head)

        except Exception as e:
            print(f"Ошибка: {e}")

        time.sleep(5)
