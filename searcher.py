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
    
    def search(
        self,
        query,
        search_type="movies",
        idf_method="classic",
        top_k=5
    ):
        query_tokens = self.tokenize_query(query)

        if search_type == "movies":
            indexer = self.movie_indexer
        elif search_type == "actors":
            indexer = self.person_indexer
        else:
            raise ValueError("search_type musí byť 'movies' alebo 'actors'")

        if idf_method not in ("classic", "smoothed"):
            raise ValueError("idf_method musí byť 'classic' alebo 'smoothed'")

        if not isinstance(top_k, int) or isinstance(top_k, bool) or not 1 <= top_k <= 5:
            raise ValueError("top_k musí byť celé číslo od 1 do 5")

        results = self.search_index(indexer, query_tokens, idf_method)

        return results[:top_k]        
    def print_results(self, results, search_type="movies"):
        for result in results:
            document = result["document"]
            score = result["score"]

            print(f'ID: {document["id"]} | Skóre: {score:.2f}')

            if search_type == "movies":
                movie = next(
                    (m for m in self.movie_indexer.movies
                    if m["id"] == document["id"]),
                    {}
                )

                print("Názov:", movie.get("title") or "Neznámy")
                print("Popis:", movie.get("overview") or "")

            else:
                person = next(
                    (p for p in self.person_indexer.persons
                    if p["id"] == document["id"]),
                    {}
                )

                print("Meno:", person.get("name") or "Neznáme")

            print("-" * 40)