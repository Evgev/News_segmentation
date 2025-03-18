import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np


def segmentation_page(model):
    '''Страница сегментации'''

    st.title("Сегментация новостей")

    uploaded_file = st.file_uploader("Загрузите файл Excel с заголовками и датами", type=["xlsx"])

    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        if 'titles' not in df.columns or 'dates' not in df.columns:
            st.error("Файл должен содержать столбцы 'titles' и 'dates'.")
            return
        
        titles = df['titles'].tolist()
        dates = pd.to_datetime(df['dates'])

        # Предсказание категорий
        predicted_categories = model.predict(titles)
        df['Категория'] = predicted_categories

        # Построение графиков распределения
        st.write("Распределение новостей по категориям:")
        category_counts = df['Категория'].value_counts()

        # График распределения категорий
        fig, ax = plt.subplots(figsize=(8, 4), dpi=60)  # Размер графика
        # fig.patch.set_facecolor('lightgray')  # Серый фон для графика
        # ax.set_facecolor('lightgray')  # Серый фон для области графика
        category_counts.plot(kind='bar', ax=ax, color='skyblue', edgecolor='gray')
        ax.set_ylabel('Количество статей')
        ax.set_title('Количество статей по категориям')

        # Оборачиваем график в контейнер Streamlit с заданными размерами
        container1 = st.container()
        with container1:
            st.pyplot(fig)

        # Фильтрация по выбранным категориям и интервалу времени
        selected_categories = st.multiselect("Выберите категории для анализа", options=df['Категория'].unique())
        
        start_date, end_date = st.date_input("Выберите интервал дат", [dates.min().date(), dates.max().date()], format="DD/MM/YYYY")
        filtered_df = df[(dates.dt.date >= start_date) & (dates.dt.date <= end_date)]

        if selected_categories:
            filtered_df = filtered_df[filtered_df['Категория'].isin(selected_categories)]

            # График по датам
            st.write("Количество статей по датам:")
            date_counts = filtered_df.groupby([dates.dt.date, 'Категория']).size().unstack(fill_value=0)

            fig2, ax2 = plt.subplots(figsize=(8, 4), dpi=60)  # Размер графика
            # fig2.patch.set_facecolor('lightgray')  # Серый фон для графика
            # ax2.set_facecolor('lightgray')  # Серый фон для области графика

            # Генерация уникальных цветов
            colors = plt.cm.viridis(np.linspace(0, 1, len(selected_categories)))

            # Построение линий для каждой категории
            for i, category in enumerate(selected_categories):
                ax2.plot(date_counts.index, date_counts[category], marker='o', color=colors[i], label=category)

            ax2.set_ylabel('Количество статей')
            ax2.set_title('Количество статей по датам для выбранных категорий')
            ax2.set_xticks(date_counts.index)  # Установка меток по всем датам
            plt.xticks(rotation=45)  # Поворот меток дат
            ax2.legend(title='Категория')

            # Оборачиваем график в контейнер Streamlit с заданными размерами
            container2 = st.container()
            with container2:
                st.pyplot(fig2)
        else:
            st.warning("Выберите хотя бы одну категорию для отображения графиков.")
