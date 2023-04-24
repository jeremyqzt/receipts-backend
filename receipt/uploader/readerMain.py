import cv2
from io import BytesIO
#import pytesseract
from dateutil.parser import parse
from datetime import date
from pathlib import Path
import threading
from uploader.models import Receipt, ProcessedState
from django.core.files.base import ContentFile
# pytesseract.pytesseract.tesseract_cmd = "D:\\py-tesseract\\tesseract.exe"
from PIL import Image
import json
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
import numpy as np
import urllib
import uuid
from django.core.files import File
from uploader.constants import VALID_EXT
import requests
from django.conf import settings
from uploader.constants import SET_FIELDS_VENDOR, SET_FIELDS_SUBTOTAL, SET_FIELDS_TOTAL, SET_FIELDS_DATE
from django.conf import settings


def pill(im):
    buffer = BytesIO()
    im = im.convert('RGB')
    im.save(fp=buffer, format='JPEG')
    buff_val = buffer.getvalue()
    return ContentFile(buff_val)


def makeThumbnail(path):
    fileName = str(uuid.uuid4()) + "_thumbnail.jpg"
    MAX_SIZE = (100, 100)
    image = Image.open(path)

    image.thumbnail(MAX_SIZE)
    image.save(fileName)
    return fileName


def removeIfExist(fpath):
    if os.path.exists(fpath):
        os.remove(fpath)

def get_float(element: any) -> float:
    if element is None: 
        return 0
    try:
        return float(element)
    except ValueError:
        return 0

def updateReceipt(receipt_obj, receipt_dict):
    set_fields = json.loads(receipt_obj.set_fields)
    # SET_FIELDS_VENDOR, SET_FIELDS_SUBTOTAL, SET_FIELDS_TOTAL, SET_FIELDS_DATE, SET_FIELDS_DESCRIPTION

    if "sum" in receipt_dict and not SET_FIELDS_TOTAL in set_fields:

        receipt_obj.total_amount = get_float(receipt_dict.get("sum", 0))
    elif SET_FIELDS_TOTAL in set_fields:
        receipt_obj.total_amount = get_float(set_fields.get(SET_FIELDS_TOTAL, 0))
    else:
        receipt_obj.total_amount = 0

    if "company" in receipt_dict and not SET_FIELDS_VENDOR in set_fields:
        receipt_obj.vendor = receipt_dict.get("company", '')
        if receipt_obj.category == 1:
            receipt_obj.category = receipt_dict.get("category", 1)
    elif SET_FIELDS_VENDOR in set_fields:
        receipt_obj.vendor = set_fields.get(SET_FIELDS_VENDOR, '')
    else:
        receipt_obj.vendor = ''

    if "subTotal" in receipt_dict and not SET_FIELDS_SUBTOTAL in set_fields:
        receipt_obj.sub_amount = get_float(receipt_dict.get("subtotal", 0))
    elif SET_FIELDS_SUBTOTAL in set_fields:
        receipt_obj.sub_amount = get_float(set_fields.get(SET_FIELDS_SUBTOTAL, 0))
    else:
        receipt_obj.sub_amount = 0

    if "date" in receipt_dict and not SET_FIELDS_DATE in set_fields:
        receipt_obj.receipt_date = receipt_dict.get(
            "date", date.today()) or date.today()
        receipt_obj.receipt_date_datetime = receipt_dict.get(
            "date", date.today()) or date.today()

    elif SET_FIELDS_DATE in set_fields:
        receipt_obj.receipt_date = set_fields.get(
            SET_FIELDS_DATE, date.today()) or date.today()
        receipt_obj.receipt_date_datetime = parse(
            set_fields.get(SET_FIELDS_DATE, str(date.today()))) or str(date.today())
    else:
        receipt_obj.receipt_date = date.today()
        receipt_obj.receipt_date_datetime = date.today()

    receipt_obj.status = ProcessedState.POPULATED
    receipt_obj.save()


class ReceiptProcessorThread(threading.Thread):
    def __init__(self, path=None, pk=None):
        super().__init__()
        self.path = path
        self.pk = pk

    def run(self):
        self.readImage(self.path)

    def url_to_image(self, url):
        if not url:
            return None

        if url[0] == "/":
            return url

        resp = urllib.request.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        fileName = str(uuid.uuid4()) + ".jpg"

        cv2.imwrite(fileName, image)

        return fileName

    def readImage(self, path):
        if settings.DONT_READ_RECEIPT:
            return
        receipt_obj = Receipt.objects.get(pk=self.pk)

        if not receipt_obj.file.name:
            return

        localFile = self.url_to_image(receipt_obj.base_image_url)
        f = Path(localFile)
        fName = f.stem
        fExt = f.suffix

        if not fExt in VALID_EXT:
            receipt_obj.status = ProcessedState.PARSING_DONE
            receipt_obj.save()
            return

        croppedName = "{fName}-cropped{fExt}".format(fExt=fExt, fName=fName)

        try:
            im = localFile
            im = Image.open(path)
            crop = json.loads(receipt_obj.crop)
            im1 = im.rotate(int(crop.get("rotation", 0)) * -90, expand=1)
            if crop.get("x", None) and crop.get("y", None) and crop.get("width", None) and crop.get("height", None):
                im1 = im1.crop((crop["x"], crop["y"], crop["x"] +
                               crop["width"], crop["y"] + crop["height"]))

            receipt_obj.cropped_file.save(croppedName,
                                          InMemoryUploadedFile(
                                              pill(im1), None, croppedName, 'image/jpeg', im1.tell, None).file
                                          )
            receipt_obj.save()
        except Exception as e:
            raise e
        finally:
            removeIfExist(localFile)

        # Download because old image is in memory only
        localFile = self.url_to_image(receipt_obj.cropped_image_url)

        thumb = makeThumbnail(localFile)
        thumb_file = open(thumb, 'rb')
        receipt_obj.thumbnail_file.save(thumb, File(thumb_file))
        thumb_file.close()
        removeIfExist(thumb)

        try:
            with open(localFile, 'rb') as f:
                files = {'file': ('upload.jpeg', open(localFile, 'rb'), 'image/jpeg'),
                         'Content-Disposition': 'form-data; name="file"; filename="' + 'upload.jpeg' + '"',
                         'Content-Type': 'multipart/form-data'}
                r = requests.post(settings.PARSE_URL, files=files)
                if (r.status_code == 200):
                    updateReceipt(receipt_obj, r.json())
        except Exception as e:
            receipt_obj.status = ProcessedState.PARSING_DONE
            receipt_obj.save()
            raise e
        finally:
            removeIfExist(localFile)
            removeIfExist(croppedName)
