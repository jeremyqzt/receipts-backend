from asyncio import exceptions
from uploader.constants import (
    RECEIPT_DATE_CREATED,
    RECEIPT_DATE,
    RECEIPT_VENDOR,
    RECEIPT_AMOUNT_ASC,
    RECEIPT_AMOUNT_DESC,
    RECEIPT_DATE_CREATED_EARLY,
    RECEIPT_DATE_EARLY
)


def get_sort_text(r_sort):

    sort = RECEIPT_DATE_CREATED

    try:
        sort = int(r_sort)
    except:
        pass

    if sort == RECEIPT_DATE_CREATED:
        return '-upload_date'

    if sort == RECEIPT_DATE_CREATED_EARLY:
        return 'upload_date'

    if sort == RECEIPT_DATE_EARLY:
        return 'receipt_date'

    if sort == RECEIPT_DATE:
        return '-receipt_date'

    if sort == RECEIPT_VENDOR:
        return 'vendor'

    if sort == RECEIPT_AMOUNT_ASC:
        return 'total_amount'

    if sort == RECEIPT_AMOUNT_DESC:
        return '-total_amount'

    return '-receipt_date'
