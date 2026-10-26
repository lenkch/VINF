from crawler import Crawler
from indexer import MovieIndexer, PersonIndexer
from parser import MovieParser, PersonParser
from pathlib import Path
from searcher import Searcher

    
if __name__ == "__main__":
    # crawler = Crawler("https://www.themoviedb.org/movie")
    # crawler.download_missing_cast()

    # print("=== 3. Parsovanie stiahnutých HTML súborov ===")
    # print("=== 3.1 Parsovanie filmov ===")
    # for file_path in Path("data_movies").glob("*.html"):
    #     movie_id = int(file_path.stem)

    #     with open(file_path, "r", encoding="utf-8") as file:
    #         html = file.read()
    #         parser = MovieParser(html, id=movie_id)
    #         parser.extract_movie_information()

    # print("=== 3.2 Parsovanie osôb ===")
    # for file_path in Path("data_persons").glob("*.html"):
    #     person_id = int(file_path.stem)

    #     with open(file_path, "r", encoding="utf-8") as file:
    #         html = file.read()
    #         parser = PersonParser(html, id=person_id)
    # #         parser.extract_person_information()

    print("=== 4. Indexovanie nájdených filmov ===")
    movie_indexer = MovieIndexer("results_movies")
    movie_indexer.index_movies()
    print("=== 5. Indexovanie nájdených osôb ===")
    person_indexer = PersonIndexer("results_persons")
    person_indexer.index_persons()
    searcher = Searcher(movie_indexer, person_indexer)


    # teraz ideme ziskat input na search, takze vytvorime instanciu Searcher a zavolame search
    while True:
        user_input = input("Enter your search query (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        results = searcher.search(user_input)

        print("=== Search Results ===")
        searcher.print_results(results)