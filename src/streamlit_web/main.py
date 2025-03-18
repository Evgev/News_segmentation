

import joblib  # Импортируем joblib для загрузки модели
import pandas as pd
import streamlit as st
import threading
from collections import deque
from segmentation import segmentation_page 
from display_news import display_news_page 

def load_model():
    return joblib.load('MyLogisticRegression.joblib')  # Загружаем модель из файла


def main():
    model = load_model()  # Загрузка модели

    # Поле для выбора страницы с использованием кнопок
    col3, col4 = st.columns([1, 1])  # Создаем две колонки для кнопок

    if 'page_selection' not in st.session_state:
        st.session_state.page_selection = "Актуальные новости"  # Начальная страница

    with col3:
        if st.button("Актуальные новости"):
            st.session_state.page_selection = "Актуальные новости"
    
    with col4:
        if st.button("Сегментация"):
            st.session_state.page_selection = "Сегментация"

    # Вызов соответствующей функции в зависимости от выбранной страницы
    if st.session_state.page_selection == "Актуальные новости":
        display_news_page(model)
    elif st.session_state.page_selection == "Сегментация":
        segmentation_page(model)

if __name__ == "__main__":
    main()