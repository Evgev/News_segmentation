import sys
import os
sys.path.append(os.getcwd() +"/get_data_realtime/")
import streamlit as st
from collections import deque
from rbc_ru_realtime import rss_parser
import time
import threading
import json

# Заголовок страницы
st.title("Новости RBC в реальном времени")

# Файл для хранения данных
DATA_FILE = "news_data.json"

# Инициализация данных
if 'parser_thread' not in st.session_state:
    st.session_state.parser_thread = None

if 'parser_running' not in st.session_state:
    st.session_state.parser_running = True

# Функция для запуска парсера
def run_parser():
    posted_q = deque(maxlen=90)
    while st.session_state.parser_running:
        try:
            rss_parser(
                posted_q,
                n_test_chars=100,
                send_message_func=lambda x: save_news(x),
            )
        except Exception as e:
            print(f"Ошибка в парсере: {e}")
        time.sleep(5)
        
run_parser()