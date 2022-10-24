import os
from io import BytesIO

import boto3
import PIL
import requests
from background_task import background
from PIL import Image


def resize_photo(img, x, y):
    img_ratio = float(img.size[0]) / img.size[1]
    resize_ratio = float(x) / y
    size = img.convert("RGB")

    if img_ratio > resize_ratio:
        output_width = x * img.size[1] / y
        output_height = img.size[1]
        originX = img.size[0] / 2 - output_width / 2
        originY = 0
        cropBox = (originX, originY, originX + output_width, originY + output_height)
        size = size.crop(cropBox)
        size = size.resize((x, y), PIL.Image.ANTIALIAS)
    else:
        output_width = img.size[0]
        output_height = y * img.size[0] / x
        originX = 0
        originY = img.size[1] / 2 - output_height / 2
        cropBox = (originX, originY, originX + output_width, originY + output_height)
        size = size.crop(cropBox)
        size = size.resize((x, y), PIL.Image.ANTIALIAS)

    return size


@background(schedule=10)
def upload_for_background_jobs(file, file_id, app, file_type):
    pics = {}

    if file_type == "posters":
        # instance.poster_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 360, 540)
        tiny = resize_photo(img, 180, 270)
        medium = resize_photo(img, 540, 810)

        pics = {"tiny": tiny, "small": small, "medium": medium, "original": original}
    elif file_type == "photos":
        # instance.photo_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 640, 360)
        tiny = resize_photo(img, 320, 180)
        medium = resize_photo(img, 960, 540)

        pics = {"tiny": tiny, "small": small, "medium": medium, "original": original}
    elif file_type == "media":
        # instance.photo_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 640, 360)
        tiny = resize_photo(img, 320, 180)

        pics = {"tiny": tiny, "small": small, "original": original}

    else:
        return

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    for name, pic in pics.items():
        imageBuffer = BytesIO()
        pic.save(imageBuffer, format="jpeg")
        imageBuffer.seek(0)
        s3.put_object(
            Bucket="kinode",
            Key=f"production/{app}/{file_type}/{file_id}/{name}.jpg",
            Body=imageBuffer,
            ContentType="image/jpeg",
        )


def upload(instance, file, file_id, app, file_type):
    pics = {}

    if file_type == "posters":
        instance.poster_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 360, 540)
        tiny = resize_photo(img, 180, 270)
        medium = resize_photo(img, 540, 810)

        pics = {"tiny": tiny, "small": small, "medium": medium, "original": original}
    elif file_type == "photos":
        instance.photo_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 640, 360)
        tiny = resize_photo(img, 320, 180)
        medium = resize_photo(img, 960, 540)

        pics = {"tiny": tiny, "small": small, "medium": medium, "original": original}
    elif file_type == "media":
        instance.photo_file_name = "original.jpg"

        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(file)

        original = img.convert("RGB")
        small = resize_photo(img, 640, 360)
        tiny = resize_photo(img, 320, 180)

        pics = {"tiny": tiny, "small": small, "original": original}

    else:
        return

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    for name, pic in pics.items():
        imageBuffer = BytesIO()
        pic.save(imageBuffer, format="jpeg")
        imageBuffer.seek(0)
        s3.put_object(
            Bucket="kinode",
            Key=f"production/{app}/{file_type}/{file_id}/{name}.jpg",
            Body=imageBuffer,
            ContentType="image/jpeg",
        )


def delete_from_s3(instance, file_id, app, file_type):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    objects_to_delete = s3.meta.client.list_objects(
        Bucket="kinode", Prefix=f"production/{app}/{file_type}/{file_id}/"
    )
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [
        {"Key": k}
        for k in [obj["Key"] for obj in objects_to_delete.get("Contents", [])]
    ]

    if delete_keys != {"Objects": []}:
        s3.meta.client.delete_objects(Bucket="kinode", Delete=delete_keys)


def upload_people(instance, file, file_id, app):
    instance.poster_file_name = "original.jpg"

    if type(file) == str:
        img = Image.open(requests.get(file, stream=True).raw)
    else:
        img = Image.open(file)

    original = img.convert("RGB")
    small = resize_photo(img, 180, 240)
    medium = resize_photo(img, 360, 480)
    large = resize_photo(img, 540, 720)

    pics = {"small": small, "medium": medium, "original": original, "large": large}

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    for name, pic in pics.items():
        imageBuffer = BytesIO()
        pic.save(imageBuffer, format="jpeg")
        imageBuffer.seek(0)
        s3.put_object(
            Bucket="kinode",
            Key=f"production/{app}/{file_id}/{name}.jpg",
            Body=imageBuffer,
            ContentType="image/jpeg",
        )


def delete_people_from_s3(instance, file_id, app):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    objects_to_delete = s3.meta.client.list_objects(
        Bucket="kinode", Prefix=f"production/{app}/{file_id}/"
    )
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [
        {"Key": k}
        for k in [obj["Key"] for obj in objects_to_delete.get("Contents", [])]
    ]

    if delete_keys != {"Objects": []}:
        s3.meta.client.delete_objects(Bucket="kinode", Delete=delete_keys)


def upload_spotlights(instance, file, app, file_type):
    pics = {}

    if file_type == "background_56_portraits":
        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(instance.background_56_portrait_file_name)

        original = img.convert("RGB")
        small = resize_photo(img, 640, 1136)
        medium = resize_photo(img, 750, 1334)
        large = resize_photo(img, 1242, 2208)

        pics = {
            "small": small,
            "original": original,
            "medium": medium,
            "large": large,
        }

    elif file_type == "background_75_portraits":
        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(instance.background_75_portrait_file_name)

        original = img.convert("RGB")
        small = resize_photo(img, 768, 1024)
        medium = resize_photo(img, 1536, 2048)
        large = resize_photo(img, 2048, 2732)

        pics = {
            "small": small,
            "original": original,
            "medium": medium,
            "large": large,
        }

    elif file_type == "background_75_landscapes":
        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(instance.background_75_landscape_file_name)

        original = img.convert("RGB")
        small = resize_photo(img, 1024, 768)
        medium = resize_photo(img, 2048, 1536)
        large = resize_photo(img, 2732, 2048)

        pics = {
            "small": small,
            "original": original,
            "medium": medium,
            "large": large,
        }

    elif file_type == "photos":
        if type(file) == str:
            img = Image.open(requests.get(file, stream=True).raw)
        else:
            img = Image.open(instance.photo_file_name)

        original = img.convert("RGB")
        tiny = resize_photo(img, 320, 180)
        small = resize_photo(img, 640, 360)
        medium = resize_photo(img, 853, 505)
        large = resize_photo(img, 960, 540)
        xlarge = resize_photo(img, 1280, 720)
        xxlarge = resize_photo(img, 1600, 900)

        pics = {
            "tiny": tiny,
            "small": small,
            "original": original,
            "medium": medium,
            "large": large,
            "xlarge": xlarge,
            "xxlarge": xxlarge,
        }

    else:
        return

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    for name, pic in pics.items():
        imageBuffer = BytesIO()
        pic.save(imageBuffer, format="jpeg", quality=85)
        imageBuffer.seek(0)
        s3.put_object(
            Bucket="kinode",
            Key=f"production/{app}/{instance.id}/{file_type}/{name}.jpg",
            Body=imageBuffer,
            ContentType="image/jpeg",
        )


def delete_spotlights_from_s3(instance, file_id, app, file_type):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    objects_to_delete = s3.meta.client.list_objects(
        Bucket="kinode", Prefix=f"production/{app}/{file_id}/{file_type}/"
    )
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [
        {"Key": k}
        for k in [obj["Key"] for obj in objects_to_delete.get("Contents", [])]
    ]
    if delete_keys != {"Objects": []}:
        s3.meta.client.delete_objects(Bucket="kinode", Delete=delete_keys)


def delete_spotlight_from_s3(file_id, app):
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    objects_to_delete = s3.meta.client.list_objects(
        Bucket="kinode", Prefix=f"production/{app}/{file_id}/"
    )
    delete_keys = {"Objects": []}
    delete_keys["Objects"] = [
        {"Key": k}
        for k in [obj["Key"] for obj in objects_to_delete.get("Contents", [])]
    ]
    if delete_keys != {"Objects": []}:
        s3.meta.client.delete_objects(Bucket="kinode", Delete=delete_keys)
