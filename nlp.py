import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Cargar el modelo de lenguaje de spaCy
nlp = spacy.load('en_core_web_md')

# Definir la tarea
task_description = """
Create a detailed action plan for the prevention, detection, and mitigation of fires in a specific region.
The plan should include preventive measures, detection systems, mitigation strategies, resource identification, and risk assessment.
"""

# Aportes de ejemplo
contributions = [
    "We should create firebreaks and conduct awareness campaigns to prevent fires.",
    "Using drone technology to monitor fire-prone areas can enhance early detection.",
    "Implementing rapid response strategies and coordinating with local fire departments is crucial.",
    "Identify available resources such as fire trucks, water sources, and trained personnel."
]

# Preprocesar el texto de la tarea y los aportes


def preprocess_text(text):
    doc = nlp(text)
    tokens = [
        token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)


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
for i, contribution in enumerate(contributions):
    relevance_score = cosine_similarities[i]
    print(f"Aporte: {contribution}\nRelevancia: {relevance_score:.2f}\n")
