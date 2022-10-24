import json
import os
import re
from datetime import datetime

import requests
from background_task import background
from django.db.models import Q
from lxml import html

from cms.aws_helpers import upload, upload_for_background_jobs, upload_people
from genres.models import Genres
from movies.models import Infos, Movies, MoviesPeople, People
from tvshows.models import (
    Episodes,
    EpisodeTranslations,
    Seasons,
    SeasonTranslations,
    TvShowPeople,
    TvShows,
    TvShowTranslations,
)

# 4 methods (for): Movie, TvShow, Info, TvShowTranslation
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


def get_imdb_id(tmdb_id, media_type):
    data = json.loads(api_call(tmdb_id, media_type, "/external_ids", ""))
    return data.get("imdb_id")


def get_tmdb_id(imdb_id, media_type):
    tmdb_id = None
    s = requests.Session()
    response = s.get(
        f"http://api.themoviedb.org/3/{media_type}/{imdb_id}"
        f"?api_key={TMDB_API_KEY}&external_source=imdb_id"
    )

    data = json.loads(response.text)
    movie_results = data["movie_results"]
    if movie_results:
        tmdb_id = movie_results[0].get("id")
    return tmdb_id


def get_imdb_rating(instance, imdb_id):
    imdb_rating = None
    url = f"https://www.imdb.com/title/{imdb_id}/"
    s = requests.Session()
    result = s.get(url)
    tree = html.fromstring(result.content)
    data = json.loads(tree.xpath('//script[@type="application/ld+json"]/text()')[0])
    ratings = data.get("aggregateRating")
    if ratings:
        imdb_rating = str(ratings.get("ratingValue"))
        if imdb_rating:
            imdb_rating = imdb_rating.replace(",", ".")
    instance.imdb_rating = imdb_rating
    instance.save()


def api_call(tmdb_id, media_type, data_type, language):
    if not language:
        url = (
            f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            f"{data_type}?api_key={TMDB_API_KEY}"
        )
    else:
        url = (
            f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}"
            f"{data_type}?api_key={TMDB_API_KEY}"
            f"&language={language}"
        )

    s = requests.Session()
    response = s.get(url)
    return response.text


def upload_images(image_details, instance, object_id, amazon_media_type, image_types):
    backdrop_url = None
    poster_url = None
    profile_url = None

    if amazon_media_type == "people":
        profiles = image_details.get("profiles")

        if profiles and "profiles" in image_types:
            profile = profiles[0]
            profile_url = (
                f"https://image.tmdb.org/t/p/original/" f"{profile.get('file_path')}"
            )
            upload_people(instance, profile_url, object_id, amazon_media_type)

        return profile_url, poster_url
    else:
        backdrops = image_details.get("backdrops")
        posters = image_details.get("posters")

        if backdrops and "backdrops" in image_types:
            backdrop = backdrops[0]
            backdrop_url = (
                f"https://image.tmdb.org/t/p/original/" f"{backdrop.get('file_path')}"
            )
            amazon_data_type = "photos"
            upload_for_background_jobs(
                backdrop_url, object_id, amazon_media_type, amazon_data_type
            )

        if posters and "posters" in image_types:
            for poster in posters:
                language = poster.get("iso_639_1")
                if amazon_media_type in ["movies", "tv_shows"]:
                    if language != "en" and language is not None:
                        continue
                elif amazon_media_type == "tv_show_translation":
                    if language != "de":
                        continue
                poster_url = (
                    f"https://image.tmdb.org/t/p/original/" f"{poster.get('file_path')}"
                )
                amazon_data_type = "posters"
                upload_for_background_jobs(
                    poster_url, object_id, amazon_media_type, amazon_data_type
                )
                break

        return backdrop_url, poster_url


def fetch_photos(tmdb_id, object_id, flag):
    image_details = None
    instance = None
    amazon_media_type = ""
    image_types = None

    if flag == "person":
        media_type = "person"
        amazon_media_type = "people"
        image_types = "profiles"

        data = api_call(tmdb_id, media_type, "/images", None)
        image_details = json.loads(data)

        instance = People.objects.filter(id=object_id).first()

    elif flag == "movie":
        media_type = "movie"
        amazon_media_type = "movies"
        data = api_call(tmdb_id, media_type, "/images", None)
        image_details = json.loads(data)
        image_types = "backdrops&posters"

        instance = Movies.objects.filter(id=object_id).first()

    elif flag == "tvshow":
        media_type = "tv"
        amazon_media_type = "tv_shows"
        image_types = "backdrops&posters"

        data = api_call(tmdb_id, media_type, "/images", None)
        image_details = json.loads(data)

        instance = TvShows.objects.filter(id=object_id).first()

    elif flag == "translation":
        language = "de"
        media_type = "tv"
        amazon_media_type = "tv_show_translation"
        image_types = "posters"

        data = api_call(tmdb_id, media_type, "/images", language)
        image_details = json.loads(data)

        instance = TvShowTranslations.objects.filter(id=object_id).first()
    elif flag == "season":
        language = "de"
        media_type = "tv"
        amazon_media_type = "seasons"
        image_types = "posters"

        instance = Seasons.objects.filter(id=object_id).first()
        season_number = instance.season_number

        data = api_call(
            tmdb_id, media_type, f"/season/{season_number}/images", language
        )

        image_details = json.loads(data)
        if not image_details.get("posters"):
            language = None
            data = api_call(
                tmdb_id, media_type, f"/season/{season_number}/images", language
            )
            image_details = json.loads(data)

    elif flag == "episode":
        language = None
        media_type = "tv"
        amazon_media_type = "episodes"
        image_types = "photos"

        instance = Episodes.objects.filter(id=object_id).first()
        season_number = instance.season_number
        episode_number = instance.episode_number

        data = api_call(
            tmdb_id,
            media_type,
            f"/season/{season_number}/episode/{episode_number}/images",
            language,
        )
        image_details = json.loads(data)

    backdrop_url, poster_url = upload_images(
        image_details, instance, object_id, amazon_media_type, image_types
    )

    return backdrop_url, poster_url


def create_person(tmdb_id):
    url = f"https://api.themoviedb.org/3/person/{tmdb_id}" f"?api_key={TMDB_API_KEY}"

    s = requests.Session()
    response = s.get(url)
    person_details = json.loads(response.text)

    also_known_as = None
    if person_details.get("also_known_as"):
        also_known_as = "---"
        for item in person_details.get("also_known_as"):
            also_known_as += "\r\n- " + item

    p = People.objects.create(
        tmdb_id=tmdb_id,
        imdb_id=person_details.get("imdb_id"),
        also_known_as=also_known_as,
        biography=person_details.get("biography"),
        birthday=person_details.get("birthday"),
        deathday=person_details.get("deathday"),
        homepage=person_details.get("homepage"),
        name=person_details.get("name"),
        place_of_birth=person_details.get("place_of_birth"),
        popularity=person_details.get("popularity"),
        show_images=1,
    )

    person_id = p.id

    photo_path = person_details.get("profile_path")
    photo_url = (
        "https://image.tmdb.org/t/p/original" + photo_path if photo_path else None
    )

    if not photo_url:
        photo_url, poster_url = fetch_photos(tmdb_id, person_id, "person")

    p.photo_path = photo_url
    p.save()

    return p


@background(schedule=10)
def fetch_credits_data(tmdb_id, flag, id):
    url = None
    data = None
    if flag == "movie":
        data = api_call(tmdb_id, "movie", "/credits", "en")
    elif flag == "tvshow":
        data = api_call(tmdb_id, "tv", "/credits", "en")

    people_details = json.loads(data)
    cast = people_details.get("cast")
    crew = people_details.get("crew")

    for people in cast:
        person_tmdb_id = people.get("id")
        character_name = people.get("character")
        person = People.objects.filter(tmdb_id=person_tmdb_id).first()

        if not person:
            person = create_person(person_tmdb_id)
            person_id = person.id
        else:
            person_id = person.id

        if flag == "movie":
            movie_person = MoviesPeople.objects.filter(
                movie_id=id, person_id=person_id
            ).first()
            if not movie_person:
                new_movie_person = MoviesPeople(
                    person_id=person_id,
                    movie_id=id,
                    person_role="actor",
                    order=cast.index(people),
                    character_name=character_name,
                )
                new_movie_person.save()
        elif flag == "tvshow":
            tvshow_person = TvShowPeople.objects.filter(
                person_id=person_id, tv_show_id=id
            ).first()
            if not tvshow_person:
                new_tvshow_person = TvShowPeople(
                    person_id=person_id,
                    tv_show_id=id,
                    person_role="actor",
                    order=cast.index(people),
                    character_name=character_name,
                )
                new_tvshow_person.save()

    for people in crew:
        person_tmdb_id = people.get("id")
        person = People.objects.filter(tmdb_id=person_tmdb_id).first()

        if not person:
            person = create_person(person_tmdb_id)
            person_id = person.id
        else:
            person_id = person.id

        if flag == "movie":
            roles = ["actor", "director", "writer", "producer"]
            role = people.get("job").lower()
            if role not in roles:
                continue
            if role == "screenplay":
                role = "writer"
            movie_person = MoviesPeople.objects.filter(
                person_id=person_id, movie_id=id
            ).first()
            if not movie_person:
                new_movie_person = MoviesPeople(
                    person_id=person_id,
                    movie_id=id,
                    person_role=role,
                    order=crew.index(people),
                )
                new_movie_person.save()
        elif flag == "tvshow":
            roles = ["actor", "director"]
            role = people.get("job").lower()
            if role not in roles:
                continue
            if role == "director":
                role = "creator"

            tvshow_person = TvShowPeople.objects.filter(
                person_id=person_id, tv_show_id=id
            ).first()
            if not tvshow_person:
                new_tvshow_person = TvShowPeople(
                    person_id=person_id,
                    tv_show_id=id,
                    person_role=role,
                    order=crew.index(people),
                )
                new_tvshow_person.save()


def fetch_info_data(tmdb_id, movie_id):
    title = None
    data = api_call(tmdb_id, "movie", "", "de")
    info_details = json.loads(data)

    instance = Infos.objects.filter(movie_id=movie_id).first()
    if not instance:
        instance = Infos.objects.create(movie_id=movie_id)

    if instance.locked_attributes:
        locked_attributes = instance.locked_attributes
    else:
        locked_attributes = ""

    if (
        info_details.get("status_code") == 34
        or info_details.get("status_message")
        == "The resource you requested could not be found."
    ):
        return
    else:
        genres = info_details.get("genres")
        genre_names = []
        for genre in genres:
            genre_name = genre.get("name").lower()
            if "&" in genre_name:
                genre1, genre2 = genre_name.split(" & ")
                genre_names.append(genre1)
                genre_names.append(genre2)
            elif genre_name == "science fiction":
                genre_name = "sci-fi"
                genre_names.append(genre_name)
            else:
                genre_names.append(genre_name)
        genre_string = ", ".join(genre_names)

        if "title" not in locked_attributes and re.match("^[A-Za-z0-9?!.,-]*$", info_details.get("title")):
            instance.title = info_details.get("title")

        premiere_date = info_details.get("release_date")
        if premiere_date > datetime.now().strftime("%Y-%m-%d"):
            coming_soon = 1
        else:
            coming_soon = 0

        director_ids = list(
            MoviesPeople.objects.filter(
                Q(movie_id=movie_id) & Q(person_role="director")
            ).values_list("person_id", flat=True)
        )

        director_names = list(
            People.objects.filter(id__in=director_ids).values_list("name", flat=True)
        )
        director_names = ", ".join(director_names)

        info_id = instance.id
        if premiere_date == "":
            premiere_date = None
        instance.movie_id = movie_id
        instance.locale = "de"
        instance.genre = genre_string
        instance.premiere_date = (
            premiere_date if not instance.premiere_date else instance.premiere_date
        )
        instance.duration = info_details.get("runtime")
        instance.directors = director_names
        instance.popularity = info_details.get("popularity")
        instance.coming_soon = coming_soon
        instance.save()


def fetch_movie_data(instance, id, tmdb_id):
    original_title = None
    genre_string = None
    if not tmdb_id:
        message = f"TMDB id is needed to fetch data."
        return message

    data = api_call(tmdb_id, "movie", "", "en")
    movie_details = json.loads(data)

    if instance.locked_attributes:
        locked_attributes = instance.locked_attributes
    else:
        locked_attributes = ""

    if (
        movie_details.get("status_code") == 34
        or movie_details.get("status_message")
        == "The resource you requested could not be found."
    ):
        message = f"Movie with is not available or does not exist."
        return message
    else:
        if "genre" not in locked_attributes:
            genres = movie_details.get("genres")
            genre_names = []
            for genre in genres:
                genre_name = genre.get("name").lower()
                if "&" in genre_name:
                    genre1, genre2 = genre_name.split(" & ")
                    if Genres.objects.filter(name__in=[genre1]).exists():
                        genre_names.append(genre1)
                    if Genres.objects.filter(name__in=[genre2]).exists():
                        genre_names.append(genre2)
                elif genre_name == "science fiction":
                    genre_name = "sci-fi"
                    genre_names.append(genre_name)
                else:
                    if Genres.objects.filter(name__in=[genre_name]).exists():
                        genre_names.append(genre_name)
            genre_string = " ".join(genre_names)

        if "original_title" not in locked_attributes:
            original_title = movie_details.get("original_title")
            en_title = movie_details.get("title")

            if original_title and not re.match("^[A-Za-z0-9?!.,-]*$", original_title):
                original_title = en_title

        spoken_languages = movie_details.get("spoken_languages")
        spoken_languages = [l.get("iso_639_1") for l in spoken_languages]
        spoken_languages = ", ".join(spoken_languages)

        origin_country = movie_details.get("production_countries")
        if type(origin_country) == list:
            made_in = ""
            for i, country in enumerate(origin_country):
                if i == len(origin_country) - 1:
                    made_in = made_in + country["iso_3166_1"]
                else:
                    made_in = made_in + country["iso_3166_1"] + ", "
        else:
            made_in = origin_country

        premiere_date = movie_details.get("release_date")
        if "-" in premiere_date:
            premiere_date = premiere_date.split("-")[0]

        if "original_title" not in locked_attributes:
            instance.original_title = original_title
        if "genre" not in locked_attributes:
            instance.genre = genre_string
        instance.premiere_date = (
            premiere_date if premiere_date else instance.premiere_date
        )
        instance.tmdb_popularity = (
            movie_details.get("popularity")
            if movie_details.get("popularity")
            else instance.tmdb_popularity
        )
        instance.status = (
            movie_details.get("status")
            if movie_details.get("status")
            else instance.status
        )
        instance.budget = (
            movie_details.get("budget")
            if movie_details.get("budget")
            else instance.budget
        )
        instance.revenue = (
            movie_details.get("revenue")
            if movie_details.get("revenue")
            else instance.revenue
        )
        instance.spoken_languages = (
            spoken_languages if spoken_languages else instance.spoken_languages
        )
        instance.imdb_id = (
            movie_details.get("imdb_id")
            if movie_details.get("imdb_id")
            else instance.imdb_id
        )
        instance.original_language = (
            movie_details.get("original_language")
            if movie_details.get("original_language")
            else instance.original_language
        )
        instance.ignore = 0
        instance.made_in = made_in if made_in else instance.made_in

        poster_path = movie_details.get("poster_path")
        poster_url = (
            "https://image.tmdb.org/t/p/original" + poster_path if poster_path else None
        )
        backdrop_path = movie_details.get("backdrop_path")
        photo_url = (
            "https://image.tmdb.org/t/p/original" + backdrop_path
            if backdrop_path
            else None
        )

        if poster_url and "poster" not in locked_attributes:
            upload(instance, poster_url, id, "movies", "posters")
        if photo_url and "photo" not in locked_attributes:
            upload(instance, photo_url, id, "movies", "photos")
        if not poster_url or not photo_url:
            photo_url, poster_url = fetch_photos(tmdb_id, id, "movie")

        if "photo" not in locked_attributes:
            instance.paths_to_photos = photo_url
        if "poster" not in locked_attributes:
            instance.paths_to_posters = poster_url
        instance.save()

        fetch_credits_data(tmdb_id, "movie", id)
        fetch_info_data(tmdb_id, id)

        message = "Fetching movie data from TMDB is finished."
        return message


def fetch_episodes_translations_data(season_number, tv_show_id, seasons_data):
    episodes_details = seasons_data.get("episodes")

    for episode in episodes_details:
        episode_number = episode.get("episode_number")
        episode_id = (
            Episodes.objects.filter(
                tv_show_id=tv_show_id,
                season_number=season_number,
                episode_number=episode_number,
            )
            .first()
            .id
        )

        episode_info = {
            "overview": episode.get("overview"),
            "name": episode.get("name"),
        }

        q = EpisodeTranslations.objects.filter(episode_id=episode_id).first()

        if not q:
            q = EpisodeTranslations.objects.create(
                episode_id=episode_id,
                summary=episode_info.get("overview"),
                title=episode_info.get("name"),
                locale="de",
            )
        else:
            q.episode_id = episode_id
            q.summary = episode_info.get("overview")
            q.title = episode_info.get("name")
            q.locale = "de"

        q.save()


@background(schedule=10)
def fetch_episodes_data(id, tmdb_id, season_id, season_number, episodes, seasons_data):
    for episodes_details in episodes:
        episode_id = None

        photo_path = episodes_details.get("still_path")
        photo_url = (
            "https://image.tmdb.org/t/p/original" + photo_path if photo_path else None
        )

        episode_info = {
            "tv_show_id": id,
            "season_id": season_id,
            "season_number": season_number,
            "air_date": episodes_details.get("air_date"),
            "tmdb_id": episodes_details.get("id"),
            "episode_number": episodes_details.get("episode_number"),
            "photo_path": photo_url,
            "name": episodes_details.get("name"),
        }

        q = Episodes.objects.filter(
            tv_show_id=id,
            season_number=season_number,
            episode_number=episodes_details.get("episode_number"),
        ).first()

        air_date = episodes_details.get("air_date")
        air_date = air_date if air_date else None

        if not q:
            q = Episodes.objects.create(
                tv_show_id=id,
                season_id=episode_info.get("season_id"),
                season_number=episode_info.get("season_number"),
                air_date=air_date,
                tmdb_id=episode_info.get("tmdb_id"),
                episode_number=episode_info.get("episode_number"),
                original_title=episodes_details.get("name"),
            )
            episode_id = q.id
            episode_number = q.episode_number
        else:
            episode_id = q.id
            episode_number = q.episode_number
            q.tv_show_id = id
            q.season_id = episode_info.get("season_id")
            q.season_number = episode_info.get("season_number")
            q.air_date = air_date
            q.tmdb_id = episode_info.get("tmdb_id")
            q.episode_number = episode_info.get("episode_number")
            q.original_title = episodes_details.get("name")

        if photo_url:
            upload_for_background_jobs(photo_url, episode_id, "episodes", "photos")
        else:
            photo_url, poster_url = fetch_photos(tmdb_id, episode_id, "episode")
        q.photo_path = photo_url
        q.photo_file_name = photo_url
        q.save()

    fetch_episodes_translations_data(season_number, id, seasons_data)


def fetch_seasons_data(id, tmdb_id, season_numbers):
    for num in season_numbers:
        data = api_call(tmdb_id, "tv", f"/season/{num}", "de")
        seasons_details = json.loads(data)

        poster_path = seasons_details.get("poster_path")
        poster_url = (
            "https://image.tmdb.org/t/p/original" + poster_path if poster_path else None
        )

        air_date = seasons_details.get("air_date")
        air_date = air_date if air_date else None

        season_info = {
            "tmdb_id": seasons_details.get("id"),
            "tv_show_id": id,
            "air_date": air_date,
            "season_number": num,
            "poster_path": poster_url,
        }

        q = Seasons.objects.filter(tv_show_id=id, season_number=num).first()
        if not q:
            q = Seasons.objects.create(
                tmdb_id=season_info.get("tmdb_id"),
                tv_show_id=season_info.get("tv_show_id"),
                air_date=air_date,
                season_number=season_info.get("season_number"),
            )
            season_id = q.id
        else:
            season_id = q.id
            q.tmdb_id = season_info.get("tmdb_id")
            q.tv_show_id = season_info.get("tv_show_id")
            q.air_date = air_date
            q.season_number = season_info.get("season_number")

        if poster_url:
            upload_for_background_jobs(poster_url, season_id, "seasons", "posters")
        # else:
        #     photo_url, poster_url = fetch_photos(tmdb_id, season_id, "season")
        q.poster_path = poster_url
        q.save()

        season_translation = SeasonTranslations.objects.filter(season_id=q.id).first()

        if not season_translation:
            season_translation = SeasonTranslations.objects.create(
                season_id=Seasons.objects.get(tv_show_id=id, season_number=num),
                locale="de",
            )

        episodes = seasons_details.get("episodes")
        fetch_episodes_data(id, tmdb_id, season_id, num, episodes, seasons_details)


def fetch_tvshow_translation_data(tvshow_id, tmdb_id):
    data = api_call(tmdb_id, "tv", "", "de")
    translation_details = json.loads(data)

    instance = TvShowTranslations.objects.filter(tv_show_id=tvshow_id).first()
    if not instance:
        instance = TvShowTranslations.objects.create(movie_id=tvshow_id)

    if instance.locked_attributes:
        locked_attributes = instance.locked_attributes
    else:
        locked_attributes = ""

    translation_id = instance.id
    instance.tv_show_id = tvshow_id
    instance.summary = (
        translation_details.get("overview")
        if not instance.summary
        else instance.summary
    )
    if "title" not in locked_attributes and re.match("^[A-Za-z0-9?!.,-]*$", translation_details.get("name")):
        instance.title = translation_details.get("name")

    instance.locale = "de"
    instance.popularity = translation_details.get("popularity")

    photo_url, poster_url = fetch_photos(tmdb_id, translation_id, "translation")

    instance.poster_path = poster_url
    instance.save()


def fetch_tvshow_data(instance, id, tmdb_id):
    if not tmdb_id:
        message = f"TMDB id is needed to fetch data."
        return message

    data = api_call(tmdb_id, "tv", "", "en")
    tvshow_details = json.loads(data)

    if instance.locked_attributes:
        locked_attributes = instance.locked_attributes
    else:
        locked_attributes = ""

    if (
        tvshow_details.get("status_code") == 34
        or tvshow_details.get("status_message")
        == "The resource you requested could not be found."
    ):
        message = f"Tv show with is not available or does not exist."
        return message
    else:
        genres = tvshow_details.get("genres")
        genre_names = []
        for genre in genres:
            genre_name = genre.get("name").lower()
            if "&" in genre_name:
                genre1, genre2 = genre_name.split(" & ")
                if Genres.objects.filter(name__in=[genre1]).exists():
                    genre_names.append(genre1)
                if Genres.objects.filter(name__in=[genre2]).exists():
                    genre_names.append(genre2)
            elif genre_name == "science fiction":
                genre_name = "sci-fi"
                genre_names.append(genre_name)
            else:
                if Genres.objects.filter(name__in=[genre_name]).exists():
                    genre_names.append(genre_name)
        genre_string = " ".join(genre_names)

        in_production = tvshow_details.get("in_production")
        if in_production:
            in_production = 1
        else:
            in_production = 0

        languages = ", ".join(tvshow_details.get("languages"))
        networks_list = tvshow_details.get("networks")
        networks = ", ".join([n.get("name") for n in networks_list])
        episode_run_time = tvshow_details.get("episode_run_time")
        episode_run_time = [str(time) for time in episode_run_time]
        runtime = ", ".join(episode_run_time)

        if "original_title" not in locked_attributes:
            original_title = tvshow_details.get("original_name")
            en_title = tvshow_details.get("name")

            if original_title and not re.match("^[A-Za-z0-9?!.,-]*$", original_title):
                original_title = en_title

        origin_country = tvshow_details.get("origin_country")
        if type(origin_country) == list:
            made_in = ", ".join(origin_country)
        else:
            made_in = origin_country

        instance.first_air_date = (
            tvshow_details.get("first_air_date")
            if tvshow_details.get("first_air_date")
            else instance.first_air_date
        )
        instance.last_air_date = (
            tvshow_details.get("last_air_date")
            if tvshow_details.get("last_air_date")
            else instance.last_air_date
        )
        instance.genre = genre_string if genre_string else instance.genre
        instance.homepage = (
            tvshow_details.get("homepage")
            if tvshow_details.get("homepage")
            else instance.homepage
        )
        instance.in_production = (
            in_production if in_production else instance.in_production
        )
        instance.languages = languages if languages else instance.languages
        instance.networks = networks if networks else instance.networks
        instance.number_of_episodes = (
            tvshow_details.get("number_of_episodes")
            if tvshow_details.get("number_of_episodes")
            else instance.number_of_episodes
        )
        instance.number_of_seasons = (
            tvshow_details.get("number_of_seasons")
            if tvshow_details.get("number_of_seasons")
            else instance.number_of_seasons
        )
        instance.episode_run_time = runtime if runtime else instance.episode_run_time
        instance.made_in = made_in if made_in else instance.made_in
        instance.original_language = (
            tvshow_details.get("original_language")
            if tvshow_details.get("original_language")
            else instance.original_language
        )
        if "original_title" not in locked_attributes:
            instance.original_title = original_title
        instance.tmdb_popularity = (
            tvshow_details.get("popularity")
            if tvshow_details.get("popularity")
            else instance.tmdb_popularity
        )
        instance.status = (
            tvshow_details.get("status")
            if tvshow_details.get("status")
            else instance.status
        )
        instance.type = (
            tvshow_details.get("type") if tvshow_details.get("type") else instance.type
        )

        poster_path = tvshow_details.get("poster_path")
        poster_url = (
            "https://image.tmdb.org/t/p/original" + poster_path if poster_path else None
        )
        backdrop_path = tvshow_details.get("backdrop_path")
        photo_url = (
            "https://image.tmdb.org/t/p/original" + backdrop_path
            if backdrop_path
            else None
        )

        if poster_url and "poster" not in locked_attributes:
            upload(instance, poster_url, id, "tv_shows", "posters")
        if photo_url and "photo" not in locked_attributes:
            upload(instance, photo_url, id, "tv_shows", "photos")
        if not photo_url or not poster_url:
            photo_url, poster_url = fetch_photos(tmdb_id, id, "tvshow")

        if "photo" not in locked_attributes:
            instance.photo_path = photo_url
        if "poster" not in locked_attributes:
            instance.poster_path = poster_url
        instance.save()

        fetch_credits_data(tmdb_id, "tvshow", id)
        fetch_tvshow_translation_data(id, tmdb_id)

        seasons = tvshow_details.get("seasons")
        season_numbers = [season.get("season_number") for season in seasons]
        fetch_seasons_data(id, tmdb_id, season_numbers)

        message = "Fetching tv show data from TMDB is finished."
        return message


def fetch_seasons_and_episodes(instance, id, tmdb_id):
    if not tmdb_id:
        message = f"TMDB id is needed to fetch data."
        return message

    data = api_call(tmdb_id, "tv", "", "en")
    tvshow_details = json.loads(data)

    if (
        tvshow_details.get("status_code") == 34
        or tvshow_details.get("status_message")
        == "The resource you requested could not be found."
    ):
        message = f"Tv show with is not available or does not exist."
        return message
    else:
        episode_run_time = tvshow_details.get("episode_run_time")
        episode_run_time = [str(time) for time in episode_run_time]
        runtime = ", ".join(episode_run_time)
        instance.first_air_date = (
            tvshow_details.get("first_air_date")
            if tvshow_details.get("first_air_date")
            else instance.first_air_date
        )
        instance.last_air_date = (
            tvshow_details.get("last_air_date")
            if tvshow_details.get("last_air_date")
            else instance.last_air_date
        )
        instance.number_of_episodes = (
            tvshow_details.get("number_of_episodes")
            if tvshow_details.get("number_of_episodes")
            else instance.number_of_episodes
        )
        instance.number_of_seasons = (
            tvshow_details.get("number_of_seasons")
            if tvshow_details.get("number_of_seasons")
            else instance.number_of_seasons
        )
        instance.episode_run_time = runtime if runtime else instance.episode_run_time
        instance.save()

        seasons = tvshow_details.get("seasons")
        season_numbers = [season.get("season_number") for season in seasons]
        fetch_seasons_data(id, tmdb_id, season_numbers)

        message = "Fetching tv show data from TMDB is finished."
        return message


def fetch_person_data(instance, id, tmdb_id):
    url = f"https://api.themoviedb.org/3/person/{tmdb_id}" f"?api_key={TMDB_API_KEY}"

    s = requests.Session()
    response = s.get(url)
    person_details = json.loads(response.text)

    if instance.locked_attributes:
        locked_attributes = instance.locked_attributes
    else:
        locked_attributes = ""

    also_known_as = None
    if person_details.get("also_known_as"):
        also_known_as = "---"
        for item in person_details.get("also_known_as"):
            also_known_as += "\r\n- " + item

    instance.imdb_id = person_details.get("imdb_id")
    instance.also_known_as = also_known_as
    instance.biography = person_details.get("biography")
    instance.birthday = person_details.get("birthday")
    instance.deathday = person_details.get("deathday")
    instance.homepage = person_details.get("homepage")
    instance.name = person_details.get("name")
    instance.place_of_birth = person_details.get("place_of_birth")
    instance.popularity = person_details.get("popularity")
    instance.show_images = 1

    photo_path = person_details.get("profile_path")
    photo_url = (
        "https://image.tmdb.org/t/p/original" + photo_path if photo_path else None
    )

    if not photo_url and "photo" not in locked_attributes:
        photo_url, poster_url = fetch_photos(tmdb_id, id, "person")

    if photo_url and "photo" not in locked_attributes:
        upload_people(instance, photo_url, id, "people")
        instance.photo_path = photo_url
        paths_to_photos = "---"
        paths_to_photos += "\r\n- " + photo_url
        instance.paths_to_photos = paths_to_photos
        instance.photo_file_name = photo_url

    instance.save()

    message = "Fetching person data from TMDB is finished."
    return message
