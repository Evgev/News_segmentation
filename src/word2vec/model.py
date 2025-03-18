import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
import nltk

# Загрузка данных NLTK
nltk.download('punkt')
nltk.download('punkt_tab')

# Загрузка данных
def load_data():
    source_data = pd.read_excel("/root/News_segmentation/data/lenta_ru_2025_03_14-2025_03_17.xlsx")
    return source_data

# Предобработка текста
def preprocess_text(text):
    return word_tokenize(text.lower())  # Токенизация и приведение к нижнему регистру

# Создание эмбеддинга для текста
def get_text_embedding(model, text):
    words = preprocess_text(text)
    vectors = [model.wv[word] for word in words if word in model.wv]
    if len(vectors) > 0:
        return np.mean(vectors, axis=0)  # Усреднение векторов слов
    else:
        return np.zeros(model.vector_size)  # Возвращаем нулевой вектор, если слов нет в модели

# Основная функция
def main():
    # Загрузка данных
    source_data = load_data()
    
    # Предобработка текстов
    texts = source_data['Текст новости'].dropna().tolist()
    tokenized_texts = [preprocess_text(text) for text in texts]
    
    # Обучение модели Word2Vec
    model = Word2Vec(sentences=tokenized_texts, vector_size=100, window=5, min_count=1, workers=4)
    
    # Пример категорий
    categories = ["экономика", "политика", "спорт", "технологии"]
    
    # Создание эмбеддингов для категорий
    category_embeddings = {}
    for category in categories:
        category_embeddings[category] = get_text_embedding(model, category)
    
    # Пример обработки одной статьи
    example_text = source_data['Текст новости'].iloc[0]
    text_embedding = get_text_embedding(model, example_text)
    
    # Вычисление близости между текстом и категориями
    similarities = {}
    for category, category_embedding in category_embeddings.items():
        similarity = cosine_similarity([text_embedding], [category_embedding])[0][0]
        similarities[category] = similarity
    
    # Вывод результатов
    print("Близость текста к категориям:")
    for category, similarity in similarities.items():
        print(f"{category}: {similarity:.4f}")

if __name__ == "__main__":
    main()