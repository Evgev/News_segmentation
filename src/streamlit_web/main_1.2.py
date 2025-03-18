import sys
import os
sys.path.append(os.getcwd() +"/get_data_realtime/")

import streamlit as st
import threading
from collections import deque
from rbc_parser import rss_parser  # Импортируем функцию парсинга

def main():
    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=90)
    # 100 первых символов от текста новости - это ключ для проверки повторений
    n_test_chars = 100
    new_entries = []

    # Запускаем функцию парсинга. Используем отдельный поток.
    thread = threading.Thread(target=rss_parser, args=(posted_q, n_test_chars, new_entries), daemon=True)
    thread.start()

    # Заголовок в Streamlit
    st.title("Новости из RBC")

    # Выпадающий список для выбора источника
    source = st.selectbox("Выберите источник новостей", ["RBC"])

    if source == "RBC":
        st.subheader("Последние новости RBC:")

        # Создаем множество для уникальности отображаемых записей
        displayed_entries_set = set()  # Множество для уникальных идентификаторов
        displayed_entries = []  # Список для отображаемых новостей

        # Создаем контейнер для таблицы, чтобы обновлять его
        table_container = st.empty()

        # Флаг для проверки, были ли хоть какие-то новости
        has_news = False

        # Отображаем новые новости в табличном формате
        while True:
            # Проверяем, есть ли новые записи
            if new_entries:
                # Получаем последние 5 новостей
                latest_entries = new_entries[-20:]

                # Обновляем отображаемые записи
                for news in latest_entries:
                    # Создаем уникальный идентификатор для новости
                    news_id = f"{news['Заголовок']} | {news['Описание'][:50]}"  # Заголовок + часть описания
                    
                    # Если новости нет в отображаемых записях, добавляем ее
                    if news_id not in displayed_entries_set:
                        displayed_entries.append(news)
                        displayed_entries_set.add(news_id)
                        has_news = True  # Нам удалось добавить новость

                # Ограничиваем длину списка отображаемых новостей до 5
                displayed_entries = displayed_entries[-20:]

                # Обновляем содержимое таблицы в контейнере
                with table_container:
                    table_container.table(displayed_entries)

            else:
                # Первоначальная инициализация; убираем сообщение о пустых новостях
                if has_news:
                    table_container.write("Нет доступных новостей.")

            # Принудительное обновление, чтобы сразу не ждать таймера
            if not has_news:
                pass  # Просто ничего не делаем, если еще нет новостей
            else:
                with st.spinner("Обновление новостей..."):
                    threading.Event().wait(5)  # Обновляем новости каждые 5 секунд

if __name__ == "__main__":
    main()
