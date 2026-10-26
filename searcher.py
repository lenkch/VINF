import re
import string


class Searcher:
    def __init__(self, movie_indexer, person_indexer):
        self.movie_indexer = movie_indexer
        self.person_indexer = person_indexer

    def tokenize_query(self, query):
        text = query.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        text = text.translate(
            str.maketrans("", "", string.punctuation)
        )
        return text.split()

    def search_index(self, indexer, query_tokens, idf_method):
        scores = {}

        if idf_method == "classic":
            idf_values = indexer.idf
        elif idf_method == "smoothed":
            idf_values = indexer.idf_smoothed
        else:
            raise ValueError("Neznáma IDF metóda")

        for token in query_tokens:
            doc_ids = indexer.inverted_index.get(token, [])

            for doc_id in doc_ids:
                tf = indexer.tf.get(doc_id, {}).get(token, 0)
                idf = idf_values.get(token, 0)

                scores[doc_id] = scores.get(doc_id, 0) + tf * idf

        documents_by_id = {
            document["id"]: document
            for document in indexer.documents
        }

        results = []

        for doc_id, score in scores.items():
            results.append({
                "document": documents_by_id[doc_id],
                "score": score
            })

        return sorted(
            results,
            key=lambda result: result["score"],
            reverse=True
        )
    
    def search(self, query):
        query_tokens = self.tokenize_query(query)

        return {
            "movies": {
                "classic": self.search_index(
                    self.movie_indexer, query_tokens, "classic"
                ),
                "smoothed": self.search_index(
                    self.movie_indexer, query_tokens, "smoothed"
                )
            },
            "actors": {
                "classic": self.search_index(
                    self.person_indexer, query_tokens, "classic"
                ),
                "smoothed": self.search_index(
                    self.person_indexer, query_tokens, "smoothed"
                )
            }
        }
    def print_results(self, results):
        print("MOVIES")

        for method, label in [
            ("classic", "normal idf"),
            ("smoothed", "smoothed idf")
        ]:
            print(f"{label}:")

            movies = results["movies"][method]

            if movies:
                result = movies[0]
                document = result["document"]
                score = result["score"]

                movie = next(
                    (m for m in self.movie_indexer.movies
                    if m["id"] == document["id"]),
                    {}
                )

                print(f'{document["id"]} {score:.2f}')
                print(movie.get("overview") or "")
            else:
                print("Žiadne výsledky")

        print("\nACTORS")

        for method, label in [
            ("classic", "normal idf"),
            ("smoothed", "smoothed idf")
        ]:
            print(f"{label}:")

            persons = results["actors"][method]

            if persons:
                result = persons[0]
                document = result["document"]
                score = result["score"]

                print(f'{document["id"]} {score:.2f}')
                print(document.get("name") or "")
            else:
                print("Žiadne výsledky")