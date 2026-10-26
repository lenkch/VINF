import re
from pathlib import Path
import json
import html


class MovieParser:

    def __init__(self, html, id=None):
        self.html = html
        self.id = id
        self.title = None
        self.overview = None
        self.release = None
        self.score=None
        self.certification=None
        self.genre=None
        self.director=None
        self.cast=None 


    def extract_movie_information(self):
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
        

        output_dir = Path("results_movies")
        output_dir.mkdir(parents=True, exist_ok=True)


        with open(f"results_movies/{self.id}.json", "w", encoding="utf-8") as f:
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
        pattern = (
            r'<li class="profile">\s*'
            r'<p[^>]*>\s*<a[^>]*>(.*?)</a>\s*</p>\s*'
            r'<p class="character">\s*Director\s*</p>\s*'
            r'</li>'
        )

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
            


class PersonParser:

    def __init__(self, html, id=None):
        self.html = html
        self.id = id
        self.name=None
        self.biography=None
        self.movies=None
        self.age=None
        self.birthdate=None
        self.death_date=None
        self.place_of_birth=None
        self.deathplace=None
        self.gender=None    
        self.birthday=None
        self.known_for=None 
        
    def extract_person_information(self):
        self.extract_person_name()
        self.extract_person_biography()
        self.extract_person_movies()
        self.extract_person_birthdate()
        self.extract_person_place_of_birth()
        self.extract_person_death_date()
        self.extract_person_gender()    
        self.extract_person_known_for()

        birth_year = None

        if self.birthday:
            year_match = re.search(r'\b(\d{4})\b', self.birthday)

            if year_match:
                birth_year = int(year_match.group(1))

        if self.age is None and birth_year:
            self.age = 2026 - birth_year


        person_details = {
            "id": self.id,
            "name": self.name,
            "biography": self.biography,
            "movies": self.movies,
            "birthdate": self.birthday,
            "birthplace": self.place_of_birth,
            "age": self.age,
            "deathdate": self.death_date,
            "alive": self.death_date is None,
            "gender": self.gender,
            "known_for": self.known_for,
        }


        output_dir = Path("results_persons")
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(f"results_persons/{self.id}.json", "w", encoding="utf-8") as f:
            json.dump(person_details, f, ensure_ascii=False, indent=4)

        return person_details
    def extract_person_name(self):
        pattern = r'<h2 class="title"[^>]*>\s*<a[^>]*>(.*?)</a>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.name = match.group(1).strip()
    def extract_person_biography(self):
        pattern = r'<section class="full_wrapper biography">.*?<div class="text[^"]*">(.*?)</div>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            biography = re.sub(r'<[^>]+>', ' ', match.group(1))
            self.biography = html.unescape(
                re.sub(r'\s+', ' ', biography).strip()
            )

    def extract_person_movies(self):
        pattern = r'<a class="title"[^>]*>\s*<bdi>(.*?)</bdi>'

        self.movies = [
            html.unescape(movie.strip())
            for movie in re.findall(pattern, self.html, re.DOTALL)
        ]
    def extract_person_birthdate(self):
        pattern = (
            r'<strong><bdi>Birthday</bdi></strong>'
            r'\s*(.*?)(?=\s*\(\d+\s+years old\)|\s*<|$)'
        )

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.birthday = re.sub(
                r'\s+', ' ', match.group(1)
            ).strip()
            
            age_match = re.search(
                r'\((\d+)\s+years old\)', match.group(0)
            )

            if age_match:
                self.age = int(age_match.group(1))

    def extract_person_place_of_birth(self):
        pattern = r'<strong><bdi>Place of Birth</bdi></strong>\s*(.*?)</p>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.place_of_birth = re.sub(r'\s+', ' ', match.group(1)).strip()

    def extract_person_gender(self):
        pattern = r'<strong><bdi>Gender</bdi></strong>\s*(.*?)</p>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.gender = match.group(1).strip()

    def extract_person_death_date(self):
        pattern = r'<strong><bdi>Day of Death</bdi></strong>\s*(.*?)\s*\((\d+)\s+years old\)'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.death_date = re.sub(r'\s+', ' ', match.group(1)).strip()
            self.age = int(match.group(2))

    def extract_person_known_for(self):
        pattern = r'<strong><bdi>Known For</bdi></strong>\s*(.*?)</p>'

        match = re.search(pattern, self.html, re.DOTALL)

        if match:
            self.known_for = match.group(1).strip()