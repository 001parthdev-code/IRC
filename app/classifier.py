from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.support_categories import SUPPORT_CATEGORIES


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


# Pre-compute category embeddings once when the application starts.
CATEGORY_EMBEDDINGS = {}

for category, examples in SUPPORT_CATEGORIES.items():
    CATEGORY_EMBEDDINGS[category] = model.encode(examples)


def classify_ticket(ticket: str) -> dict:
    ticket_embedding = model.encode([ticket])

    scores = {}

    for category, embeddings in CATEGORY_EMBEDDINGS.items():
        similarities = cosine_similarity(
            ticket_embedding,
            embeddings
        )[0]

        scores[category] = float(max(similarities))

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    category, score = ranked[0]

    return {
        "category": category,
        "semantic_score": round(score, 4),
        "scores": {
            name: round(value, 4)
            for name, value in ranked
        }
    }