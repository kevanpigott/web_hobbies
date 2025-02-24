class UserException(Exception):
    pass


model = None


def hobby_similarity(hobby1: str, hobby2: str) -> float:
    """
    Computes a similarity score between two hobbies using sentence embeddings.

    :param hobby1: First hobby as a string.
    :param hobby2: Second hobby as a string.
    :return: Similarity score between 0 and 1.
    """

    # Load the embedding model, which takes a moment
    global model
    if model is None:
        from sentence_transformers import SentenceTransformer, util

        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Convert hobbies to embeddings
    emb1 = model.encode(hobby1, convert_to_tensor=True)
    emb2 = model.encode(hobby2, convert_to_tensor=True)

    # return cosine similarity
    return util.cos_sim(emb1, emb2).item()


if __name__ == "__main__":
    hobby1 = "Playing football"
    hobby2 = "Playing basketball"
    print(hobby_similarity(hobby1, hobby2))
