import httpx
import feedparser
from collections import deque
import time

def rss_parser(posted_q, n_test_chars, new_entries):
    '''Парсер rss ленты'''
    rss_link = 'https://rssexport.rbc.ru/rbcnews/news/90/full.rss'

    while True:
        try:
            response = httpx.get(rss_link)
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            time.sleep(10)
            continue

        feed = feedparser.parse(response.text)

        for entry in feed.entries[::-1]:
            summary = entry.get('summary', '')  # Используем метод get для избежания ошибок
            title = entry.get('title', '')
            link = entry.get('link', '')  # Получаем ссылку на новость

            news_text = f'{title}\n{summary}'
            head = news_text[:n_test_chars].strip()

            if head in posted_q:
                continue

            new_entries.append({
                'Заголовок': title,
                'Описание': summary,
                'Ссылка': link  # Добавляем ссылку на новость в словарь
            })

            posted_q.appendleft(head)

        time.sleep(5)  # Пауза между запросами
