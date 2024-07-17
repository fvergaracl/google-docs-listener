from sentence_transformers import SentenceTransformer, util
from utils import print_debug


def evaluate_contributions(topic, task_description, contributions):
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
    # Cargar el modelo preentrenado
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
    results = []
    # Definir las frases
    for contribution in contributions:
        print_debug(f"contribution: {contribution}")
        # Generar las representaciones de los textos
        embedding_task = model.encode(task_description, convert_to_tensor=True)
        embedding_response = model.encode(contribution, convert_to_tensor=True)

        # Calcular la similitud de coseno entre las dos frases
        similarity = util.pytorch_cos_sim(
            embedding_task, embedding_response).item()

        # Interpretar el resultado
        # Convertir a porcentaje para facilitar la interpretación
        similarity_score = similarity * 10
        results.append({
            "topic": topic,
            "task": task_description,
            "contribution": contribution,
            "score": similarity_score
        })

        print_debug(f"similarity_score: {similarity_score}")

    return results
