import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

# Загрузка данных
data = pd.read_excel('/root/News_segmentation/data/lenta_ru_2024_03_19-2025_03_18_without_bodies.xlsx')  # Предположим, что данные хранятся в CSV файле

data = data[data.topics.isin([
  "Забота о себе",
  "Интернет и СМИ",
  "Культура",
  "Наука и техника",
  "Силовые структуры",
  "Спорт",
  "Экономика",
  "Ценности",
  "Среда обитания",
])]
data = data.dropna()
print(data.info())
print(data.describe())
# Разделение данных на признаки (заголовки) и целевую переменную (категории)
X = data['titles']
y = data['topics']

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание пайплайна: векторизация текста + модель классификации
model = Pipeline([
    ('tfidf', TfidfVectorizer()),  # Преобразование текста в числовые признаки
    ('clf', LogisticRegression())  # Модель классификации
])

# Обучение модели
model.fit(X_train, y_train)

# Предсказание на тестовой выборке
y_pred = model.predict(X_test)

# Оценка качества модели
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# # Применение модели к неразмеченным данным
# unlabeled_data = pd.read_csv('unlabeled_news.csv')  # Загрузка неразмеченных данных
# unlabeled_X = unlabeled_data['заголовок']

# # Предсказание категорий для неразмеченных данных
# predicted_categories = model.predict(unlabeled_X)

# # Добавление предсказанных категорий в DataFrame
# unlabeled_data['предсказанная_категория'] = predicted_categories

# # Сохранение результатов
# unlabeled_data.to_csv('labeled_news.csv', index=False)