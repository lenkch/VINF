from pathlib import Path
import string

import re
import math
import json


class Indexer:
    def __init__(self, movies_path):
        self.movies_path = Path(movies_path)
        self.movies=[]
        self.documents=[]
        self.inverted_index = {}
        self.tf = {}
        self.idf = {}

    def index_movies(self):
        self.load_movies()
        self.create_documents()    
        self.tokenize_documents()
        self.build_inverted_index()
        # self.save_index()
        self.calculate_tf()
        self.calculate_idf()

    def load_movies(self):
        self.movies = []


        for file_path in self.movies_path.glob("*.json"):
            with open(file_path, "r", encoding="utf-8") as file:
                movie = json.load(file)

            self.movies.append(movie)


    def create_documents(self):
        self.documents = []

        for movie in self.movies:
            document = {
                "id": movie["id"],
                "text": (
                    movie["title"] + " "
                    + movie["overview"] + " "
                    + " ".join(movie["genre"]) + " "
                    + movie["director"] + " "
                    + " ".join(movie["actors"]) + " "
                    + " ".join(movie["keywords"])
                )
            }

            self.documents.append(document)

    def tokenize_documents(self):
        for document in self.documents:
            text = document["text"].lower()
            text = re.sub(r"[^\w\s]", " ", text)        
            text = text.translate(str.maketrans("", "", string.punctuation))
            document["tokens"] = text.split()

    def build_inverted_index(self):
        self.inverted_index = {}

        for document in self.documents:
            doc_id = document["id"]

            for token in set(document["tokens"]):
                if token not in self.inverted_index:
                    self.inverted_index[token] = []

                self.inverted_index[token].append(doc_id)

    def calculate_tf(self):
        self.tf = {}

        for document in self.documents:
            doc_id = document["id"]
            self.tf[doc_id] = {}

            for token in document["tokens"]:
                if token not in self.tf[doc_id]:
                    self.tf[doc_id][token] = 0

                self.tf[doc_id][token] += 1


    def calculate_idf(self):
        N = len(self.documents)
        self.idf = {}

        for token, doc_ids in self.inverted_index.items():
            df = len(doc_ids)
            self.idf[token] = math.log(N / df)
        print(self.idf)
        
        return self.idf

