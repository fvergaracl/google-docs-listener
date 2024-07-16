import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import print_debug

# Cargar el modelo de lenguaje de spaCy
nlp = spacy.load('es_core_news_md')


def preprocess_text(text):
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)


def evaluate_contributions(task_description, contributions):
    print_debug(" ")
    print_debug(" ")
    print_debug('Evaluating contributions...')
    print_debug(" ")
    print_debug(f"task_description: {task_description}")
    print_debug(" ")
    print_debug(f"contributions: {contributions}")
    print_debug(" ")
    print_debug(" ")
    print_debug('Preprocessing text...')
    # Preprocesar el texto de la tarea y los aportes
    preprocessed_task = preprocess_text(task_description)
    preprocessed_contributions = [preprocess_text(
        contribution) for contribution in contributions]

    # Vectorizar el texto usando TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(
        [preprocessed_task] + preprocessed_contributions)

    # Calcular la similitud del coseno entre la tarea y cada aporte
    cosine_similarities = cosine_similarity(
        tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Evaluar y mostrar la relevancia de cada aporte
    results = []
    for i, contribution in enumerate(contributions):
        relevance_score = cosine_similarities[i]
        results.append((contribution, relevance_score))

    return results
