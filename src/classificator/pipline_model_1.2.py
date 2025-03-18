import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import Adam
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
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = word_tokenize(text.lower())
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)

data['titles'] = data['titles'].apply(lemmatize_text)

# Разделение данных на признаки (заголовки) и целевую переменную (категории)
X = data['titles']
y = data['topics']

# Векторизация текста
vectorizer = TfidfVectorizer(max_df=0.5, ngram_range=(1, 2))
X_vectorized = vectorizer.fit_transform(X)

# Преобразование категорий в числовые метки
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y_encoded, test_size=0.2, random_state=42)

# Создание нейронной сети
model = Sequential([
    Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(len(label_encoder.classes_), activation='softmax')
])

# Компиляция модели
model.compile(optimizer=Adam(learning_rate=0.001),
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Обучение модели
model.fit(X_train.toarray(), y_train, epochs=10, batch_size=32, validation_split=0.2)

# Оценка модели на тестовых данных
loss, accuracy = model.evaluate(X_test.toarray(), y_test)
print(f"Test Accuracy: {accuracy}")

# # Применение модели к неразмеченным данным
# unlabeled_data = pd.read_csv('unlabeled_news.csv')
# unlabeled_X = unlabeled_data['заголовок'].apply(lemmatize_text)
# unlabeled_X_vectorized = vectorizer.transform(unlabeled_X)

# # Предсказание категорий
# predictions = model.predict(unlabeled_X_vectorized.toarray())
# predicted_categories = label_encoder.inverse_transform(np.argmax(predictions, axis=1))

# # Добавление предсказанных категорий в DataFrame
# unlabeled_data['предсказанная_категория'] = predicted_categories

# # Сохранение результатов
# unlabeled_data.to_csv('labeled_news_nn.csv', index=False)