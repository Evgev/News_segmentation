import sys
import os


sys.path.append(os.getcwd() + "/get_data_realtime/")
sys.path.append(os.getcwd() + "/classificator/")

import joblib  # Импортируем joblib для загрузки модели
import pandas as pd
import streamlit as st
import threading
from collections import deque
from rbc_parser import rss_parser  # Импортируем функцию парсинга
from bcs_parser import bcs_parser  # Импортируем функцию парсинга
from segmentation import segmentation_page  # Импортируем функцию сегментации


def predict_categories(model, news_titles):
    return model.predict(news_titles)

def display_news_page( model):
    '''Отображение новостей из выбранного источника'''
    # Заголовок в Streamlit
    st.title("Актуальные новости")

    # Создаем два столбца для выравнивания элементов
    col1, col2 = st.columns(2)

    with col1:
        # Выпадающий список для выбора источника
        source = st.selectbox("Выберите источник новостей", ["RBC", "BCS"])

    with col2:
        # Выпадающий список фильтрации по категориям
        category_placeholder = st.selectbox("Фильтр по категории", ["Все"] + list(model.classes_))
        
    posted_q = deque(maxlen=90)
    n_test_chars = 100
    new_entries = []

    # Запускаем функцию парсинга. Используем отдельный поток.
    if source == "RBC":
        thread = threading.Thread(target=rss_parser, args=(posted_q, n_test_chars, new_entries), daemon=True)
    else:
        thread = threading.Thread(target=bcs_parser, args=(posted_q, n_test_chars, new_entries), daemon=True)
    thread.start()

    st.subheader(f"Последние новости {source}:")
    displayed_entries_set = set()  # Множество для уникальных идентификаторов
    displayed_entries = []  # Список для отображаемых новостей
    table_container = st.empty()  # Создаем контейнер для таблицы

    has_news = False

    # Отображаем новые новости в табличном формате
    while True:
        if new_entries:
            latest_entries = new_entries[-90:]
            for news in latest_entries:
                news_id = f"{news['Заголовок']} | {news['Описание'][:100]} | {news['Ссылка']}"
                if news_id not in displayed_entries_set:
                    displayed_entries.append(news)
                    displayed_entries_set.add(news_id)
                    has_news = True

            displayed_entries = displayed_entries[-90:]

            if has_news:
                titles = pd.Series([entry['Заголовок'] for entry in displayed_entries])
                categories = predict_categories(model, titles)

                for i in range(len(displayed_entries)):
                    displayed_entries[i]['Категория'] = categories[i]

                unique_categories = pd.Series(categories).unique()

                if category_placeholder != "Все":
                    displayed_entries = [entry for entry in displayed_entries if entry['Категория'] == category_placeholder]

                with table_container:
                    table_container.table(displayed_entries)
        else:
            if has_news:
                table_container.write("Нет доступных новостей.")

        if not has_news:
            pass
        else:
            with st.spinner("Обновление новостей..."):
                threading.Event().wait(60)  # Обновляем новости каждые 60 секунд
