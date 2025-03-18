import datetime
from requests import Request, Session
from bs4 import BeautifulSoup
import pandas as pd


def lenta_ru():
    s = Session()
    dates = []
    topics = []
    titles = []

    for day in range(1, 365):
        num_pages = 1
        while True:  # получить все новости за дату разом нельзя, как и узнать количество страниц, поэтому пришлось прибегнуть к while:
            date = (datetime.datetime.today() - datetime.timedelta(days=day))
            link = s.get(
                'https://lenta.ru/{}/page/{}/'.format(date.strftime('%Y/%m/%d'), num_pages))
            soup = BeautifulSoup(link.text, 'lxml')
            news_list = soup.find_all(
                'a', {"class": "card-full-news _archive"}, href=True)
            if len(
                    news_list) == 0:  # если на странице нет новостей, переходим к следующей дате
                break

            for news in news_list:  # собираем данные по каждой новости
                dates.append(date)
                title = news.find_all('h3', {"class": "card-full-news__title"})
                titles.append(
                    (title[0].get_text() if len(title) > 0 else 'None'))
                topic = news.find_all(
                    'span', {
                        "class": "card-full-news__info-item card-full-news__rubric"})
                topics.append(
                    (topic[0].get_text() if len(topic) > 0 else 'None'))
            num_pages += 1

    start_date = datetime.datetime.today().strftime('%Y_%m_%d')
    end_date = date.strftime('%Y_%m_%d')
    save_path = "../../data/lenta_ru_{0}-{1}_without_bodies.xlsx".format(end_date, start_date)

    df = pd.DataFrame({'dates': dates, 'topics': topics, 'titles': titles})
    df.to_excel(save_path)


lenta_ru()
