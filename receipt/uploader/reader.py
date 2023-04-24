from PIL import Image
import pytesseract
import threading
import re
from typing import List, Tuple
from datetime import date
from dateutil.parser import parse
from uploader.models import Receipt, ProcessedState
from autocorrect import Speller
import json
from PIL import Image

from uploader.constants import SET_FIELDS_VENDOR, SET_FIELDS_SUBTOTAL, SET_FIELDS_TOTAL, SET_FIELDS_DATE, SET_FIELDS_DESCRIPTION
#pytesseract.pytesseract.tesseract_cmd = "D:\\py-tesseract\\tesseract.exe"

usefulSubtotals = (
    "sub total",
    "subtotal",
    "subtotal amount",
    "sub tofal",
    "subtofal",
    "subtofal amount",
)

usefulTotals = (
    "grand total",
    "total amount",
    "grand tofal",
    "tofal amount",
)

usefulDates = (
    "receipt total",
    "receipt date",
)


def isDate(string, fuzzy=False):
    try:
        return True, parse(string, fuzzy=fuzzy)
    except ValueError:
        return False, date.today()


def isNum(num):
    try:
        float(num)
    except:
        return False, -1

    return True, float(num)


class ReceiptReaderThread(threading.Thread):
    def __init__(self, path=None, data=None, pk=None):
        super().__init__()
        self.path = path
        self.data = data
        self.pk = pk
        self.spell = Speller(lang="en")

    def autoCorrect(self):
        ...

    def readReceipt(self):
        receipt_data = (
            pytesseract.image_to_string(Image.open(self.path), lang="eng")
            if not self.data
            else self.data
        )
        sane_receipt = re.sub(r"[^a-zA-Z\d\.\%\#\s:]", " ", receipt_data)
        self.receipt = sane_receipt

    def extractVendor(self):
        return re.sub(r"[^a-zA-Z\d\s:\.]", "-", self.receipt.split("\n")[0])

    def isLikelyToBeCorrectTotal(self, value):
        return value > 0 and value < 1000000

    def __preProcess(self):
        processedList = list(
            filter(lambda x: x.replace(" ", "") !=
                   "", self.receipt.split("\n"))
        )

        # usefulInfo = usefulDates + usefulTotals + usefulSubtotals
        potentialSubTotals = []
        potentialTotals = []
        potentialDates = []

        others = []
        for _, item in enumerate(processedList):
            found = False
            for i in usefulSubtotals:
                if i in item.lower():
                    potentialSubTotals.append(item.lower())
                    found = True
            for i in usefulTotals:
                if i in item.lower():
                    potentialTotals.append(item.lower())
                    found = True

            for i in usefulDates:
                if i in item.lower():
                    potentialDates.append(item.lower())
                    found = True

            if not found:
                others.append(item.lower())

        return potentialSubTotals, potentialTotals, potentialDates, others

    def findTotalAndSubtotal(
        self, potentialTotals: List[str], potentialSubTotals: List[str]
    ):
        potentialSubTotal = 0
        potentialTotal = 0

        try:
            potentialTotal = float(self.removeKeysAndFindNumber(
                potentialTotals, usefulTotals))
        except:
            pass

        try:
            potentialSubTotal = float(self.removeKeysAndFindNumber(
                potentialSubTotals, usefulSubtotals
            ))
        except:
            pass

        return potentialSubTotal, potentialTotal

    def findReceiptDate(self, potentialDates: List[str], keys: Tuple[str]):
        retDate = date.today()

        for line in potentialDates:
            for key in keys:
                line.replace(key, "")
            entries = line.split()

            for item in entries:
                isADate, retDate = isDate(item)
                if isADate:
                    return retDate
        return retDate

    def removeKeysAndFindNumber(self, canidates: List[str], keys: Tuple[str]):
        for line in canidates:
            for key in keys:
                line.replace(key, "")
            entries = line.split()

            for item in entries:
                isANum, val = isNum(item)
                if isANum and self.isLikelyToBeCorrectTotal(val):
                    return val

    def extractInformation(self):
        infoDict = {}
        (
            potentialSubTotals,
            potentialTotals,
            potentialDates,
            others,
        ) = self.__preProcess()

        potentialSubTotalAmt, potentialTotalAmt = self.findTotalAndSubtotal(
            potentialTotals, potentialSubTotals
        )

        potentialDateVal = self.findReceiptDate(potentialDates, usefulDates)

        if potentialSubTotalAmt is not None and potentialTotalAmt is None:
            potentialTotalAmt = potentialSubTotalAmt

        infoDict = {
            "total": potentialTotalAmt,
            "subTotal": potentialSubTotalAmt,
            "date": potentialDateVal,
            "lines": others,
        }

        return infoDict

    def run(self):
        self.readReceipt()
        receipt_dict = self.extractInformation()
        receipt_obj = Receipt.objects.get(pk=self.pk)

        set_fields = json.loads(receipt_obj.set_fields)
        #SET_FIELDS_VENDOR, SET_FIELDS_SUBTOTAL, SET_FIELDS_TOTAL, SET_FIELDS_DATE, SET_FIELDS_DESCRIPTION

        if "total" in receipt_dict and not SET_FIELDS_TOTAL in set_fields:
            receipt_obj.total_amount = receipt_dict.get("total", 0)
        elif SET_FIELDS_TOTAL in set_fields:
            receipt_obj.total_amount = set_fields.get(SET_FIELDS_TOTAL, 0)
        else:
            receipt_obj.total_amount = 0

        if "subTotal" in receipt_dict and not SET_FIELDS_SUBTOTAL in set_fields:
            receipt_obj.sub_amount = receipt_dict.get("subTotal", 0)
        elif SET_FIELDS_SUBTOTAL in set_fields:
            receipt_obj.sub_amount = set_fields.get(SET_FIELDS_SUBTOTAL, 0)
        else:
            receipt_obj.sub_amount = 0

        if "date" in receipt_dict and not SET_FIELDS_DATE in set_fields:
            receipt_obj.receipt_date = receipt_dict.get("date", date.today())
            receipt_obj.receipt_date_datetime = receipt_dict.get(
                "date", date.today())

        elif SET_FIELDS_DATE in set_fields:
            receipt_obj.receipt_date = set_fields.get(
                SET_FIELDS_DATE, date.today())
            receipt_obj.receipt_date_datetime = parse(
                set_fields.get(SET_FIELDS_DATE, str(date.today())))
        else:
            receipt_obj.receipt_date = date.today()
            receipt_obj.receipt_date_datetime = date.today()

        if "lines" in receipt_dict:
            all_lines = receipt_dict.get("lines", [])
            receipt_obj.all_lines = "\n".join(all_lines)

            if len(all_lines) > 1 and not SET_FIELDS_VENDOR in set_fields:
                receipt_obj.vendor = all_lines[0]

        if SET_FIELDS_VENDOR in set_fields:
            receipt_obj.vendor = set_fields.get(SET_FIELDS_VENDOR, "")

        receipt_obj.status = ProcessedState.POPULATED
        receipt_obj.save()
