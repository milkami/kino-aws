import json
import re

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from cms.trailer_helpers import (
    fine_uploader_config,
    fine_uploader_data,
    fine_uploader_policy,
)

from .models import Media


# Create your views here.
@csrf_exempt
def proxy(request):
    if request.method == "GET":
        path = request.GET.get("path")
        res = fine_uploader_config(path)
        return JsonResponse({"success": True, "aws_key": res["aws_key"]})
    else:
        path = request.GET.get("path")
        if "data" in path:
            if "_changelist_filters" in request.GET:
                media_id = re.findall(
                    r"media_connection_id=(?P<id>\d+)",
                    request.GET.get("_changelist_filters"),
                )[0]
            else:
                media_id = None
            smb_video = fine_uploader_data(
                path,
                json.loads(request.body.decode("utf-8"))["filename"],
                json.loads(request.body.decode("utf-8"))["target"],
                json.loads(request.body.decode("utf-8"))["priority"],
            )
            if media_id:
                media = Media.objects.create(
                    media_connection_type="Info",
                    media_connection_id=int("0" + media_id),
                    smb_video_id=smb_video["video_id"],
                    name=smb_video["filename"],
                    smb_video_url="http://videos.kntk.de/files/"
                    + str(smb_video["video_id"]),
                    active=False,
                    trailer_language="de",
                    popularity=100.0,
                    smb_checked_at=now(),
                )
            else:
                media = Media.objects.create(
                    media_connection_type="Info",
                    smb_video_id=smb_video["video_id"],
                    name=smb_video["filename"],
                    smb_video_url="http://videos.kntk.de/files/"
                    + str(smb_video["video_id"]),
                    active=False,
                    trailer_language="de",
                    popularity=100.0,
                    smb_checked_at=now(),
                )
            return JsonResponse(
                {
                    "success": True,
                    "transaction_id": smb_video["transaction_id"],
                    "remote": smb_video["remote"],
                    "upload_url": smb_video["upload_url"],
                    "folder": smb_video["folder"],
                    "video_id": smb_video["video_id"],
                    "filename": smb_video["filename"],
                }
            )

        elif "policy" in path:
            res = fine_uploader_policy(
                path, json.loads(request.body.decode("utf-8"))["headers"]
            )
            return JsonResponse({"signature": res["signature"]})
