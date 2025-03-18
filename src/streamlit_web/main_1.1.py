import httpx
import asyncio
from collections import deque
import feedparser
import streamlit as st
import queue
import threading

# Очередь из уже опубликованных постов, чтобы их не дублировать
posted_q = deque(maxlen=90)

# 50 первых символов от текста новости - это ключ для проверки повторений
n_test_chars = 100

# Потокобезопасная очередь для передачи новостей
news_queue = queue.Queue()

# Функция для парсинга RSS
async def rss_parser(httpx_client, posted_q, n_test_chars):
    '''Парсер rss ленты'''
    rss_link = 'https://rssexport.rbc.ru/rbcnews/news/90/full.rss'

    while True:
        try:
            response = await httpx_client.get(rss_link)
        except:
            await asyncio.sleep(10)
            continue

        feed = feedparser.parse(response.text)

        for entry in feed.entries[::-1]:
            summary = entry['summary']
            title = entry['title']

            news_text = f'{title}\n{summary}'

            head = news_text[:n_test_chars].strip()

            if head in posted_q:
                continue

            # Добавляем новость в очередь
            news_queue.put(news_text)
            posted_q.appendleft(head)

        await asyncio.sleep(5)

# Функция для запуска асинхронного парсера
def start_parser():
    httpx_client = httpx.AsyncClient()
    asyncio.run(rss_parser(httpx_client, posted_q, n_test_chars))

# Основная функция Streamlit
def main():
    st.title("Новости RBC")

    # Инициализация состояния для хранения новостей
    if "news_items" not in st.session_state:
        st.session_state.news_items = []

    # Выпадающий список для выбора источника новостей
    source = st.selectbox("Выберите источник новостей", ["RBC", "Другой источник"])

    if source == "RBC":
        st.write("if source == RBC:")
        # Запуск парсера в отдельном потоке
        if "parser_started" not in st.session_state:
            st.session_state.parser_started = True
            threading.Thread(target=start_parser, daemon=True).start()

        # Проверяем очередь и обновляем новости
        st.write("Проверяем очередь и обновляем новости", news_queue.empty())
        while not news_queue.empty():
            news_text = news_queue.get()
            st.session_state.news_items.append(news_text)
        st.write("после wile")
        # Отображение новостей
        st.write("Последние новости:")
        st.write(st.session_state.news_items)
        for news in st.session_state.news_items:
            st.write("Внутри for")
            st.write(news)
            st.write("---")

if __name__ == "__main__":
    main()