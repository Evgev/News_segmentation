import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Загрузка данных
@st.cache_data
def load_data():
    source_data = pd.read_excel("/mnt/d/Desktop/Projects/diploma/news_segmentation/src/tests/lenta_ru_2025_03_16-2025_03_17.xlsx")
    return source_data

# Сегментация новостей по категориям
def segment_news(source_data, categories):
    vectorizer = TfidfVectorizer()
    source_vectors = vectorizer.fit_transform(source_data['Текст новости'])
    category_vectors = vectorizer.transform(categories)
    
    # Вычисляем косинусное сходство
    similarity_matrix = cosine_similarity(source_vectors, category_vectors)
    source_data['Категория'] = similarity_matrix.argmax(axis=1)
    source_data['Категория'] = source_data['Категория'].apply(lambda x: categories[x])
    return source_data

# Основное приложение
def main():
    st.title("Сегментация новостей по категориям")
    
    # Загрузка файла с категориями
    uploaded_file = st.file_uploader("Загрузите Excel-файл с категориями", type=["xlsx"])
    
    if uploaded_file is not None:
        categories_df = pd.read_excel(uploaded_file)
        categories = categories_df.iloc[:, 0].tolist()
        
        # Загрузка исходных данных
        source_data = load_data()
        
        # Сегментация новостей
        segmented_data = segment_news(source_data, categories)
        
        # Вывод таблицы с количеством статей по категориям
        st.write("Количество статей по категориям:")
        category_counts = segmented_data['Категория'].value_counts().reset_index()
        category_counts.columns = ['Категория', 'Количество статей']
        st.table(category_counts)
        
        # Выбор категории для построения графика
        selected_category = st.selectbox("Выберите категорию для построения графика", categories)
        
        # Фильтрация данных по выбранной категории
        filtered_data = segmented_data[segmented_data['Категория'] == selected_category]
        filtered_data['Дата'] = pd.to_datetime(filtered_data['Дата'])
        
        # Группировка по дням и подсчет количества статей
        daily_counts = filtered_data.resample('D', on='Дата').size().reset_index()
        daily_counts.columns = ['Дата', 'Количество статей']
        
        # Выбор интервала времени
        min_date = daily_counts['Дата'].min()
        max_date = daily_counts['Дата'].max()
        date_range = st.date_input("Выберите интервал времени", [min_date, max_date])
        
        # Фильтрация данных по выбранному интервалу времени
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_daily_counts = daily_counts[(daily_counts['Дата'] >= start_date) & (daily_counts['Дата'] <= end_date)]
        
        # Построение графика
        st.write(f"Распределение новостей по категории '{selected_category}' во времени:")
        fig, ax = plt.subplots()
        ax.plot(filtered_daily_counts['Дата'], filtered_daily_counts['Количество статей'], marker='o')
        ax.set_xlabel('Дата')
        ax.set_ylabel('Количество новостей')
        ax.set_title(f"Распределение новостей по категории '{selected_category}'")
        st.pyplot(fig)

if __name__ == "__main__":
    main()