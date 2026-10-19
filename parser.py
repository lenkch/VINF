import re
from pathlib import Path
import json


class Parser:

    def __init__(self, html, id=None):
        self.html = html
        self.id = id
        self.score=None
        self.certification=None
        self.genre=None



    def extract_all_information(self):
        self.extract_movie_title()
        self.extract_movie_overview()
        self.extract_movie_facts()
        self.extract_score()
        self.extract_movie_director()
        self.extract_movie_cast()
        self.extract_movie_details()
        self.extract_keywords()
        movie_details = {
            "id": self.id,
            "title": self.title,
            "overview": self.overview,
            "certification": self.certification,
            "genre": self.genre,
            "release": self.release,
            "rating": self.score,
            "director": self.director,
            "actors": self.cast,
            "status": self.status,
            "original_language": self.original_language,
            "budget": self.budget,
            "revenue": self.revenue,
            "keywords": self.keywords,
        }

        with open(f"results/{self.id}.json", "w", encoding="utf-8") as f:
            json.dump(movie_details, f, ensure_ascii=False, indent=4)

        return movie_details
    def extract_movie_title(self):
        pattern = r'<div class="title.*?">.*?<a[^>]*>(.*?)</a>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.title = match.group(1).strip()
    def extract_movie_overview(self):
        pattern = r'<div class="overview.*?">.*?<p[^>]*>(.*?)</p>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.overview = match.group(1).strip()


    def extract_movie_director(self):
        pattern = r'<li class="profile".*?<p[^>]*>.*?<a[^>]*>(.*?)</a>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.director = match.group(1).strip()
    def extract_movie_facts(self):
        certification_pattern = r'<span class="certification.*?">(.*?)</span>'
        genre_pattern = r'<span class="genres.*?">(.*?)</span>'
        release_pattern = r'<span class="release.*?">(.*?)</span>'

        certification_match = re.search(
            certification_pattern, self.html, re.DOTALL
        )
        genre_match = re.search(
            genre_pattern, self.html, re.DOTALL
        )
        release_match = re.search(
            release_pattern, self.html, re.DOTALL
        )

        self.certification = (
            certification_match.group(1).strip()
            if certification_match else None
        )

        self.genre = (
            re.findall(r'<a[^>]*>(.*?)</a>', genre_match.group(1))
            if genre_match else []
        )

        self.release = (
            re.sub(r'[^0-9/]', '', release_match.group(1))
            if release_match else None
        )
    def extract_score(self):
        score_pattern = r'class="user_score_chart"[^>]*data-percent="(\d+)"'

        match = re.search(score_pattern, self.html)

        self.score = int(match.group(1)) if match else None
    def extract_movie_details(self):
        pattern = (
            r'<strong><bdi>Status</bdi></strong>\s*(.*?)\s*</p>.*?'
            r'<strong><bdi>Original Language</bdi></strong>\s*(.*?)</p>.*?'
            r'<strong><bdi>Budget</bdi></strong>\s*(.*?)</p>.*?'
            r'<strong><bdi>Revenue</bdi></strong>\s*(.*?)</p>'
        )

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.status = match.group(1).strip()
            self.original_language = match.group(2).strip()
            self.budget = match.group(3).strip()
            self.revenue = match.group(4).strip()
        else:
            self.status = None
            self.original_language = None
            self.budget = None
            self.revenue = None
    def extract_movie_cast(self):
        cast_path = Path("data_cast") / f"{self.id}.html"

        cast_html = cast_path.read_text(encoding="utf-8")

        pattern = r'<div class="info">\s*<p><a[^>]*>(.*?)</a></p>\s*<p class="character">(.*?)</p>'

        matches = re.findall(pattern, cast_html, re.DOTALL)

        self.cast = [actor.strip() for actor, character in matches]

        return self.cast
    def extract_keywords(self):
        pattern = r'<section\b(?=[^>]*\bclass="[^"]*\bkeywords\b[^"]*")[^>]*>.*?<ul>(.*?)</ul>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            keywords_html = match.group(1)
            self.keywords = re.findall(r'<li[^>]*>.*?<a[^>]*>(.*?)</a>.*?</li>',
                                    keywords_html, re.DOTALL)
            self.keywords = [keyword.strip() for keyword in self.keywords]
        else:
            self.keywords = []

