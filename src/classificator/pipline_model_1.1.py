import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import nltk
import re
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

# Удаление строк с пропущенными значениями
data = data.dropna()

print(data.info())
print(data.describe())

# Лемматизация текста
nltk.download('punkt')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

def lemmatize_text(text):
    # Удаление символов, не являющихся буквами
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Токенизация текста
    tokens = word_tokenize(text.lower())
    # Лемматизация каждого слова
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)

# Применение лемматизации к заголовкам
data['titles'] = data['titles'].apply(lemmatize_text)

# Разделение данных на признаки (заголовки) и целевую переменную (категории)
X = data['titles']
y = data['topics']

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Создание пайплайна: векторизация текста + модель классификации
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer()),  # Преобразование текста в числовые признаки
    ('clf', LogisticRegression())  # Модель классификации
])

# Настройка гиперпараметров с помощью GridSearchCV
parameters = {
    'tfidf__max_df': (0.5, 0.75, 1.0),  # Максимальная частота слова
    'tfidf__ngram_range': [(1, 1), (1, 2)],  # Использование униграмм и биграмм
    'clf__C': [0.1, 1, 10],  # Параметр регуляризации для логистической регрессии
    'clf__solver': ['liblinear', 'lbfgs']  # Алгоритм оптимизации
}

grid_search = GridSearchCV(pipeline, parameters, cv=5, n_jobs=-1, verbose=1)
grid_search.fit(X_train, y_train)

# Вывод лучших параметров
print("Лучшие параметры:", grid_search.best_params_)

# Предсказание на тестовой выборке
y_pred = grid_search.predict(X_test)

# Оценка качества модели
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# # Применение модели к неразмеченным данным
# unlabeled_data = pd.read_csv('unlabeled_news.csv')  # Загрузка неразмеченных данных
# unlabeled_X = unlabeled_data['titles'].apply(lemmatize_text)  # Лемматизация

# # Предсказание категорий для неразмеченных данных
# predicted_categories = grid_search.predict(unlabeled_X)

# # Добавление предсказанных категорий в DataFrame
# unlabeled_data['предсказанная_категория'] = predicted_categories

# # Сохранение результатов
# unlabeled_data.to_csv('labeled_news.csv', index=False)