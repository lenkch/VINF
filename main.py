from crawler import Crawler
from indexer import Indexer
from parser import Parser
from pathlib import Path

    
if __name__ == "__main__":
    #crawler = Crawler("https://www.themoviedb.org/movie")
    #crawler.crawl_pages()


    # for file_path in Path("data_movies").glob("*.html"):
    #     movie_id = int(file_path.stem)

    #     with open(file_path, "r", encoding="utf-8") as file:
    #         html = file.read()
    #         print(f"Processing movie ID: {movie_id}")
    #         parser = Parser(html, id=movie_id)
    #         parser.extract_all_information()
    indexer = Indexer("results")
    indexer.index_movies()
    print(len(indexer.documents))  # celkový počet filmov
print(len(indexer.inverted_index["spider"]))  # počet filmov so slovom spider
print(indexer.idf["spider"])  # vypočítané IDF