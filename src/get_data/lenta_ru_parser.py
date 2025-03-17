import datetime
from requests import Session
from bs4 import BeautifulSoup
import pandas as pd


def get_news_body(session, news_link):
    """
    Функция для извлечения текста новости по ссылке.
    """
    try:
        news_page = session.get(news_link)
        news_soup = BeautifulSoup(news_page.text, 'lxml')
        
        # Извлечение текста новости (пример для сайта lenta.ru)
        body = news_soup.find('div', {"class": "topic-body__content"})
        if body:
            return body.get_text(separator="\n").strip()  # Возвращаем текст
        else:
            return 'None'  # Если текст не найден
    except Exception as e:
        print(f"Ошибка при обработке ссылки {news_link}: {e}")
        return 'None'


def lenta_ru():
    s = Session()
    dates = []
    topics = []
    titles = []
    links = []
    bodies = []

    for day in range(1, 10):  # Сбор данных за последний день
        num_pages = 1
        while True:  # Получить все новости за дату разом нельзя, поэтому используем while
            date = (datetime.datetime.today() - datetime.timedelta(days=day))
            link = s.get(
                'https://lenta.ru/{}/page/{}/'.format(date.strftime('%Y/%m/%d'), num_pages))
            soup = BeautifulSoup(link.text, 'lxml')
            news_list = soup.find_all(
                'a', {"class": "card-full-news _archive"}, href=True)
            if len(news_list) == 0:  # Если на странице нет новостей, переходим к следующей дате
                break

            for news in news_list:  # Собираем данные по каждой новости
                dates.append(date)
                
                # Извлекаем заголовок
                title = news.find_all('h3', {"class": "card-full-news__title"})
                titles.append(
                    (title[0].get_text() if len(title) > 0 else 'None'))
                
                # Извлекаем тему (рубрику)
                topic = news.find_all(
                    'span', {
                        "class": "card-full-news__info-item card-full-news__rubric"})
                topics.append(
                    (topic[0].get_text() if len(topic) > 0 else 'None'))
                
                # Извлекаем ссылку на новость
                news_link = news['href']
                if not news_link.startswith('http'):  # Если ссылка относительная, добавляем домен
                    news_link = 'https://lenta.ru' + news_link
                links.append(news_link)

                # Извлекаем текст новости с помощью отдельной функции
                body = get_news_body(s, news_link)
                bodies.append(body)

            num_pages += 1  # Переход на следующую страницу

    # Сохранение данных в Excel
    start_date = datetime.datetime.today().strftime('%Y_%m_%d')
    end_date = date.strftime('%Y_%m_%d')
    save_path = "./../data/lenta_ru_{0}-{1}.xlsx".format(end_date, start_date)

    df = pd.DataFrame({
        'Дата': dates,
        'Тема': topics,
        'Заголовок': titles,
        'Ссылка': links,
        'Текст новости': bodies
    })
    df.to_excel(save_path, index=False)


# Запуск функции
lenta_ru()