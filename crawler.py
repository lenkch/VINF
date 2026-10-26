import re
import time
import requests
import csv
from pathlib import Path
from urllib.parse import urljoin, urlparse

USER_AGENT = (
    "STU-FIIT-student-project-crawler"
)
TIMEOUT = 20
TIMEOUT_BETWEEN_REQUESTS = 2
PAGES_COUNT = 204



class Crawler:
    def __init__(self, start_url):
        
        self.start_url = start_url
        self.base_url = "https://www.themoviedb.org"

        self.headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

        self.timeout = TIMEOUT

        self.visited = set()

        self.metadata_file = Path("Metadata.tsv")
        self.metadata = self.load_metadata()

    def fetch(self, url, method="GET", data=None, headers=None):
        request_headers = headers or self.headers

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=request_headers,
                data=data,
                timeout=self.timeout
            )

            response.raise_for_status()

            time.sleep(TIMEOUT_BETWEEN_REQUESTS)

            return response.text

        except requests.RequestException as error:
            print(f"Chyba pri sťahovaní {url}: {error}")
            return None

    
    def fetch_movie_page(self, page):
        url = "https://www.themoviedb.org/discover/movie/items"

        headers = {
            **self.headers,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.start_url,
        }

        return self.fetch(
            url,
            method="POST",
            data={"page": page},
            headers=headers
        )


    def load_progress_pages(self):
        progress_file = Path("progress.txt")

        if progress_file.exists():
            return int(progress_file.read_text(encoding="utf-8"))

        return 0


    def save_progress_pages(self, page):
        Path("progress.txt").write_text(
            str(page),
            encoding="utf-8"
        )


    def load_metadata(self):
        metadata = {}

        if not self.metadata_file.exists():
            return metadata

        with self.metadata_file.open(
            "r", encoding="utf-8", newline=""
        ) as file:
            reader = csv.DictReader(file, delimiter="\t")

            for row in reader:
                if row.get("url"):
                    metadata[row["url"]] = row

        return metadata

    def update_metadata(
        self, url, entity_type, entity_id,
        status, file_path="", size_bytes=0
    ):
        record = {
            "url": url,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "status": status,
            "file_path": str(file_path),
            "size_bytes": size_bytes,
        }

        self.metadata[url] = record

        columns = [
            "url", "entity_type", "entity_id",
            "status", "file_path", "size_bytes"
        ]

        file_exists = (
            self.metadata_file.exists()
            and self.metadata_file.stat().st_size > 0
        )

        with self.metadata_file.open(
            "a", encoding="utf-8", newline=""
        ) as file:
            writer = csv.DictWriter(
                file, fieldnames=columns, delimiter="\t"
            )

            if not file_exists:
                writer.writeheader()

            writer.writerow(record)

    def extract_movie_links(self, html):
        links = re.findall(
            r'href="(/movie/[0-9]+-[a-zA-Z0-9-]+)"',
            html
        )

        full_links = []

        for link in links:
            full_url = urljoin(self.base_url, link)

            if full_url not in full_links:
                full_links.append(full_url)

        return full_links

    def crawl_movies(self):
        all_movie_links = []
        max_iterations = PAGES_COUNT

        last_page = self.load_progress_pages()
        page = last_page + 1
        print(f"Pokračujem od strany: {page}")
        print(f"Maximálny počet stránok na prehľadanie: {max_iterations}")

        while page <= max_iterations:
            html = self.fetch_movie_page(page)

            if html is None:
                break

            movie_links = self.extract_movie_links(html)

            if not movie_links:
                break

            for link in movie_links:
                if link in self.visited:
                    continue

                self.visited.add(link)
                all_movie_links.append(link)

                self.download_entity(link, "movie")
                cast_url = link.rstrip("/") + "/cast"
                self.download_entity(cast_url, "cast")

            page += 1
            self.save_progress_pages(page) 

        return all_movie_links

    def download_entity(self, entity_url, entity_type):
        directories = {
            "movie": Path("data_movies"),
            "cast": Path("data_cast"),
            "person": Path("data_persons"),
        }

        if entity_type not in directories:
            raise ValueError(f"Neznámy typ entity: {entity_type}")

        path = urlparse(entity_url).path
        if entity_type in ("movie", "cast"):
            match = re.search(r"/movie/(\d+)", path)
            if not match:
                print(f"Nepodarilo sa získať ID filmu: {entity_url}")
                return None
            entity_id = match.group(1)
        else:
            match = re.search(r"/person/(\d+)", path)
            if not match:
                print(f"Nepodarilo sa získať ID osoby: {entity_url}")
                return None
            entity_id = match.group(1)

        output_dir = directories[entity_type]
        output_dir.mkdir(parents=True, exist_ok=True)

        file_path = output_dir / f"{entity_id}.html"

        if file_path.exists():
            size_bytes = file_path.stat().st_size
            self.update_metadata(
            entity_url, entity_type, entity_id,
            "already_downloaded", file_path, size_bytes
        )
            return file_path

        page_html = self.fetch(entity_url)

        if page_html is None:
            self.update_metadata(
            entity_url, entity_type, entity_id,
            "failed"
        )
            return None

        file_path.write_text(page_html, encoding="utf-8")
        size_bytes = file_path.stat().st_size
        self.update_metadata(
            entity_url, entity_type, entity_id,
            "downloaded", file_path, size_bytes
        )

        return file_path

    def extract_person_links(self, html, movie_id):
        # Nájdeme sekciu obsahujúcu obsadenie filmu
        section_match = re.search(
            r'<ol\b[^>]*class=["\'][^"\']*\bpeople\b[^"\']*\bcredits\b[^"\']*["\'][^>]*>(.*?)</ol>',
            html,
            re.DOTALL
        )

        if not section_match:
            print(f"Sekcia obsadenia sa nenašla pre film ID: {movie_id}")
            return set()

        section_html = section_match.group(1)

        links = re.findall(
            r'href=["\'](/person/\d+[^"\']*)["\']',
            section_html
        )

        person_links = set()

        for link in links:
            person_url = urljoin(self.base_url, link)
            person_links.add(person_url)

        return person_links

    def get_all_person_links(self):
        person_links = set()
        cast_dir = Path("data_cast")

        for file_path in cast_dir.glob("*.html"):
            html = file_path.read_text(encoding="utf-8")
            links = self.extract_person_links(html, file_path.stem)
            person_links.update(links)

        return person_links

    def crawl_persons(self):
        print("=== 2. Sťahovanie profilov osôb ===")
        downloaded_file = "persons_downloaded.txt"
        pending_file = "persons_to_download.txt"

        downloaded = self.load_person_url_list(downloaded_file)
        pending = self.load_person_url_list(pending_file)

        person_links = self.get_all_person_links()

        pending.update(person_links - downloaded)
        pending_to_process = sorted(pending)


        for person_url in pending_to_process:
            print(f"Stahujem profil osoby: {person_url}")
            result = self.download_entity(person_url, "person")

            if result is None:
                print(f"error downloading {person_url}.")
                continue

            pending.remove(person_url)
            downloaded.add(person_url)

            self.save_person_url_list(pending_file, pending)
            self.save_person_url_list(downloaded_file, downloaded)

    def crawl_pages(self):
        print("=== 1. Sťahovanie filmov a obsadenia ===")
        self.crawl_movies()
        print("\n=== 2. Sťahovanie profilov osôb ===")
        self.crawl_persons()
        print("\nCrawlovanie dokončené.")


    def load_person_url_list(self, filename):
        path = Path(filename)

        if not path.exists():
            return set()

        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }


    def save_person_url_list(self, filename, urls):
        Path(filename).write_text(
            "\n".join(sorted(urls)),
            encoding="utf-8"
        )

    def download_missing_cast(self):
        movies_dir = Path("data_movies")
        cast_dir = Path("data_cast")

        cast_dir.mkdir(parents=True, exist_ok=True)

        movie_files = list(movies_dir.glob("*.html"))

        for i, movie_file in enumerate(movie_files, start=1):
            movie_id = movie_file.stem
            cast_path = cast_dir / f"{movie_id}.html"

            # Cast už existuje, netreba ho sťahovať
            if cast_path.exists() and cast_path.stat().st_size > 0:
                continue

            # Nájdeme URL filmu v metadata
            movie_metadata = next(
                (
                    record for record in self.metadata.values()
                    if record["entity_type"] == "movie"
                    and str(record["entity_id"]) == movie_id
                ),
                None
            )

            if not movie_metadata:
                print(f"Chýba URL v metadata pre film {movie_id}")
                continue

            movie_url = movie_metadata["url"].rstrip("/")
            cast_url = f"{movie_url}/cast"

            print(
                f"[{i}/{len(movie_files)}] "
                f"Sťahujem chýbajúci cast pre film {movie_id}"
            )

            result = self.download_entity(cast_url, "cast")

            if result is None:
                print(f"  Sťahovanie zlyhalo pre film {movie_id}")

        print("Kontrola chýbajúcich cast stránok dokončená.")