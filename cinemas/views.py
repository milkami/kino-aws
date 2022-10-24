import os
import json
from datetime import date, datetime, time

import django.apps
import requests
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.utils.text import capfirst

from media.models import Media
from movies.models import Infos, Movies, MoviesPeople

from .models import Cinemas, Showtimes
from django.contrib import messages

# get_models returns all the models, but there are
# some which we would like to ignore
IGNORE_MODELS = (
    "sites",
    "sessions",
    "admin",
    "contenttypes",
)

# WIP
# def rundeckkinoparsers(request):
#     proj_url = "https://rundeck.stroeermb.de/api/21/project/Kinode-Parsers/jobs?format=json&groupPath=Kino parsers"
#     headers = {"X-Rundeck-Auth-Token":"YVrEfSY6SdOFp8nCoMG49qjB9IauEXdG"}
#     job_resp = requests.get(proj_url, headers=headers).json()

#     executions_url = "https://rundeck.stroeermb.de/api/21/project/Kinode-Parsers/executions?format=json&groupPath=Kino parsers&recentFilter=3d&max=100"
#     executions_resp = requests.get(executions_url, headers=headers).json()

#     sorted_executions = sorted(executions_resp["executions"], key=lambda d: d['date-started']['unixtime'])
    
#     result = []
#     for job in job_resp:
#         job_executions = [d for d in sorted_executions if d["job"]["id"]==job["id"]]
#         job["execution"] = job_executions[-1]
#         job["runtime"] = datetime.strptime(job_executions[-1]["date-started"]["date"], '%Y-%m-%dT%H:%M:%SZ')
#         duration = job_executions[-1]["job"]["averageDuration"]/1000
#         duration_formated = f"{duration/3600%3600}:{duration/60%60}:{duration%60}"
#         job["duration"] = job_executions[-1]["job"]["averageDuration"]
#         result.append(job)

#     return render(request, "admin/rundeck_parsers.html", {"jobs": result})


def run_parser(request):
    parser_name = request.GET.get("parser_name", None)
    cinema_id = request.GET.get("cinema_id", None)
    previous = request.META.get("HTTP_REFERER", "/admin/cinemas/parsers")

    headers = {"X-Rundeck-Auth-Token":os.getenv("RUNDECK_TOKEN")}
    job_url = f"https://rundeck.stroeermb.de/api/14/job/9c4b7bef-6a24-4bd0-9385-62267d524e38/run?argString=-parser_name {parser_name} -cinema_id {cinema_id}"
    response = requests.post(job_url, headers=headers)
    if response.status_code == 200:
        messages.add_message(request, messages.SUCCESS, f'Started parser {parser_name} for cinema_id {cinema_id}')
    else:
        messages.add_message(request, messages.ERROR, f"Error occured: {response.status_code} {response.reason}")

    return redirect(previous)


# Create your views here.
def newkinoheldcinemas(request):
    ignored_cinemas_ids = [1032, 1307, 1581, 1589, 1591, 1621]
    api_cinemas_url = (
        "https://api.kinoheld.de/app/v1/cinemas?"
        "apikey=sfnp3blNVdT8WSH5fdVZ&all=1&ref=kinodeap"
    )
    s = requests.Session()
    response = s.get(api_cinemas_url)
    kinoheld_json = json.loads(response.text)

    missing_cinemas = []
    new_added_cinemas = []
    kinoheld_ids = (
        Cinemas.objects.all().values_list("kinoheld_id", flat=True).distinct()
    )
    for c_id in kinoheld_json:
        if (
            c_id != ""
            and c_id is not None
            and c_id not in kinoheld_ids
            and int(c_id) not in ignored_cinemas_ids
            and int(c_id) not in new_added_cinemas
        ):
            missing_cinemas.append(kinoheld_json[c_id])
            new_added_cinemas.append(int(c_id))

    for m_c in missing_cinemas:
        api_shows_url = f"https://api.kinoheld.de/app/v1/shows?apikey=sfnp3blNVdT8WSH5fdVZ&cinema={m_c['cinema_id']}"
        s = requests.Session()
        res = s.get(api_shows_url)
        try:
            json_shows_doc = json.loads(res.text)
        except:
            print("An exception occurred")

        cinema_doc = {}
        for cinema in json_shows_doc:
            if int(cinema) == m_c["cinema_id"]:
                cinema_doc = json_shows_doc[cinema]

        shows_count = 0
        for movie in cinema_doc:
            shows_count = shows_count + len(cinema_doc[movie])
        m_c["comment"] = str(date.today()) + " Total showtimes: " + str(shows_count)
    return render(request, "admin/newkinoheldcinemas.html", {"total": missing_cinemas})


"""
# deprecated
def movie_playlist(request, id):
    infos = Infos.objects.filter(showtimes__cinema_id=int(id)).distinct()
    media = {}
    for info in infos:
        media[info.id] = Media.objects.filter(media_connection_type="Info", media_connection_id=info.id).count()

    actors = {}
    for info in infos:
        actors[info.id] = MoviesPeople.objects.filter(movie_id=info.movie_id, person_role="actor").count()

    number_of_showtimes = {}
    for info in infos:
        number_of_showtimes[info.id] = Showtimes.objects.filter(cinema_id=id, info_id=info.id).count()

    return render(request, "admin/movie_playlist.html", {'infos': infos, 'media': media, 'id': id, 'actors': actors, 'number_of_showtimes': number_of_showtimes })
"""


def ignore_movie(request, id):
    movie = Movies.objects.get(id=id)
    if movie.ignore:
        movie.ignore = 0
    else:
        movie.ignore = 1
    movie.save()
    return redirect(request.META["HTTP_REFERER"])
