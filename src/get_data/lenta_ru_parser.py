import datetime
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import pandas as pd

async def get_news_body(session, news_link):
    """
    Асинхронная функция для извлечения текста новости по ссылке.
    """
    try:
        async with session.get(news_link) as response:
            news_page = await response.text()
            news_soup = BeautifulSoup(news_page, 'lxml')
            
            # Извлечение текста новости (пример для сайта lenta.ru)
            body = news_soup.find('div', {"class": "topic-body__content"})
            if body:
                return body.get_text(separator="\n").strip()  # Возвращаем текст
            else:
                return 'None'  # Если текст не найден
    except Exception as e:
        print(f"Ошибка при обработке ссылки {news_link}: {e}")
        return 'None'

async def fetch_news_links(session, date, num_pages):
    """
    Асинхронная функция для получения ссылок на новости за определенную дату.
    """
    links = []
    while True:
        url = f'https://lenta.ru/{date.strftime("%Y/%m/%d")}/page/{num_pages}/'
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'lxml')
            news_list = soup.find_all('a', {"class": "card-full-news _archive"}, href=True)
            if not news_list:
                break
            for news in news_list:
                news_link = news['href']
                if not news_link.startswith('http'):
                    news_link = 'https://lenta.ru' + news_link
                links.append(news_link)
            num_pages += 1
    return links

async def lenta_ru():
    async with aiohttp.ClientSession() as session:
        dates = []
        topics = []
        titles = []
        links = []
        bodies = []

        for day in range(1, 4):  # Сбор данных за последние 9 дней
            date = datetime.datetime.today() - datetime.timedelta(days=day)
            news_links = await fetch_news_links(session, date, 1)
            
            # Параллельное выполнение асинхронных задач для получения текста новостей
            tasks = [get_news_body(session, link) for link in news_links]
            bodies_list = await asyncio.gather(*tasks)
            
            for news_link, body in zip(news_links, bodies_list):
                dates.append(date)
                links.append(news_link)
                bodies.append(body)

        # Сохранение данных в Excel
        start_date = datetime.datetime.today().strftime('%Y_%m_%d')
        end_date = date.strftime('%Y_%m_%d')
        save_path = f"./../../data/lenta_ru_{end_date}-{start_date}.xlsx"

        df = pd.DataFrame({
            'Дата': dates,
            'Ссылка': links,
            'Текст новости': bodies
        })
        df.to_excel(save_path, index=False)

# Запуск асинхронной функции
asyncio.run(lenta_ru())