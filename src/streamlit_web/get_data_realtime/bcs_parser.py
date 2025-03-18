import httpx
import asyncio
from collections import deque

from scrapy.selector import Selector

def bcs_parser(httpx_client, posted_q, n_test_chars, new_entries):
    '''Кастомный парсер сайта bcs-express.ru'''

    bcs_link = 'https://bcs-express.ru/category'

    while True:
        try:
            response = httpx_client.get(bcs_link)
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            time.sleep(5)
            continue

        selector = Selector(text=response.text)

        for row in selector.xpath('//div[@class="feed__list"]/div/div')[::-1]:
            raw_text = row.xpath('*//text()').extract()

            title = raw_text[3] if len(raw_text) > 3 else ''
            summary = raw_text[5] if len(raw_text) > 5 else ''
            link = row.xpath('.//a/@href').get()  # Получаем ссылку на новость

            if not title or not summary or not link:
                continue  # Пропускаем, если данные отсутствуют

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

        time.sleep(5)

