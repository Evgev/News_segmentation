import pandas as pd
import numpy as np
from gensim.models import Word2Vec
from transformers import pipeline
from nltk.tokenize import word_tokenize
import nltk

# Загрузка данных NLTK
nltk.download('punkt')

# Загрузка данных
def load_data():
    source_data = pd.read_excel("/root/News_segmentation/data/lenta_ru_2025_03_14-2025_03_17.xlsx")
    return source_data

# Предобработка текста
def preprocess_text(text):
    return word_tokenize(text.lower())

# Обучение модели Word2Vec
def train_word2vec(texts):
    tokenized_texts = [preprocess_text(text) for text in texts]
    model = Word2Vec(sentences=tokenized_texts, vector_size=500, window=5, min_count=5, workers=8, epochs=50)
    return model

# Поиск контекстно-близких слов
def find_similar_words(model, category, topn=20):
    try:
        similar_words = model.wv.most_similar(category.lower(), topn=topn)
        return [word for word, _ in similar_words]
    except KeyError:
        print(f"Слово '{category}' отсутствует в словаре модели.")
        return []

# Zero-shot классификация
def zero_shot_classification(texts, categories):
    classifier = pipeline("zero-shot-classification", model="MoritzLaurer/mDeBERTa-v3-base-mnli-xnli")
    results = classifier(texts, candidate_labels=categories)
    return results

# Основная функция
def main():
    # Загрузка данных
    source_data = load_data()
    texts = source_data['Текст новости'].dropna().tolist()
    
    # Обучение Word2Vec
    model = train_word2vec(texts)
    
    # Пример категорий
    categories = ["экономика", "политика", "сми", "технологии", "культура"]
    
    # Поиск контекстно-близких слов для каждой категории
    similar_words = {}
    for category in categories:
        similar_words[category] = find_similar_words(model, category)
    
    # Вывод результатов
    print("Контекстно-близкие слова для категорий:")
    for category, words in similar_words.items():
        print(f"{category}: {', '.join(words)}")
    
    # Пример Zero-shot классификации
    example_texts = texts[:5]  # Пример первых 5 текстов
    results = zero_shot_classification(example_texts, categories)
    
    # Вывод результатов классификации
    print("\nРезультаты Zero-shot классификации:")
    for i, result in enumerate(results):
        print(f"Текст {i+1}:")
        print(f"  Категория: {result['labels'][0]}")
        print(f"  Уверенность: {result['scores'][0]:.4f}")

if __name__ == "__main__":
    main()