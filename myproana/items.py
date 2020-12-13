

import scrapy
from scrapy.item import Field
from scrapy.loader.processors import MapCompose, TakeFirst
import re
import datetime


def extract_authorname(text):
    text = re.sub('\n|\t|,', '', text).strip()
    splits = str(text).split(' ')
    text = ' '.join(splits[2:])
    return str(text)


def clean_noposts(text):
    text = re.sub('\n|\t|,', '', text).strip()
    text = re.sub('posts', '', text).strip()
    value = str(text) if len(str(text)) > 0 else 'N/A'
    return value


def remove_tab(text):
    text = re.sub('\n|\t|,', '', text).strip()
    if len(text) == 0:
        text = 'Admin'
    return str(text)


def clean_content(text):
    text = re.sub('(<\/?(.*?)>)', '', text).strip()
    text = re.sub('\n|\t|,|\xa0', ' ', text)
    text = re.sub('\\\\', '', text)
    value = str(text) if len(str(text)) > 0 else 'N/A'
    return value


def extract_sig(text):
    text = re.sub('[ \t]{4,}', '', text).strip()
    matches = re.findall('(>(.*?)<)', str(text))
    arr = []
    for i, item in matches:
        if len(str(item).strip()) > 0:
            arr.append(str(item))
    if len(arr) > 0:
        return ' '.join(arr)
    else:
        return 'N/A'


def converttodate_trd(text):
    try:
        date = datetime.datetime.strptime(str(text), '%d %b %Y').strftime('%Y-%m-%d')
    except:
        if 'Today' in str(text):
            date = datetime.datetime.today().strftime('%Y-%m-%d')
        elif 'Yesterday' in str(text):
            date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            date = str(text)

    return date


def converttodate_ps(text):
    text = re.sub('-', '', str(text))
    try:
        date = datetime.datetime.strptime(str(text), '%d %B %Y %I:%M %p').strftime('%Y-%m-%d')
    except:
        if 'Today' in str(text):
            date = datetime.datetime.today().strftime('%Y-%m-%d')
        elif 'Yesterday' in str(text):
            date = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            date = str(text)

    return date


def remove_first(text):
    return str(text[1:])


def converttostring(text):
    return str(text)


class PostItem(scrapy.Item):
    threadtitle = Field(
        input_processor=MapCompose(converttostring),
        output_processor=TakeFirst()
    )

    authorname = Field(
        input_processor=MapCompose(converttostring),
        output_processor=TakeFirst()
    )

    authortype = Field(
        input_processor=MapCompose(remove_tab),
        output_processor=TakeFirst()
    )

    authorsign = Field(
        input_processor=MapCompose(extract_sig),
        output_processor=TakeFirst()
    )

    postcontent = Field(
        input_processor=MapCompose(clean_content),
        output_processor=TakeFirst()
    )

    date = Field(
        input_processor=MapCompose(converttodate_ps),
        output_processor=TakeFirst()
    )

    noposts = Field(
        input_processor=MapCompose(clean_noposts),
        output_processor=TakeFirst()
    )


class ThreadItem(scrapy.Item):
    subforumname = Field(
        input_processor=MapCompose(remove_first),
        output_processor=TakeFirst()
    )
    authorname = Field(
        input_processor=MapCompose(extract_authorname),
        output_processor=TakeFirst()
    )
    threadtitle = Field(
        input_processor=MapCompose(converttostring),
        output_processor=TakeFirst()
    )

    startdate = Field(
        input_processor=MapCompose(converttodate_trd),
        output_processor=TakeFirst()
    )

    url = Field(
        output_processor=TakeFirst()
    )
