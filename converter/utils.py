from wand.image import Image
import base64
import re
from difflib import SequenceMatcher


def convert(path, resolution=400):
    # Convert PDF file to image file, generate an image for each page
    pages = 0
    with Image(filename=path, resolution=resolution) as img:
        img.save(filename="media/output/page.jpg")
        pages = len(img.sequence)
    return pages


def get_Base64(filename):
    # Encode image file to base64
    encoded_string = ""
    with open('media/output/' + filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


def is_nit(number):
    # Checking number as nit
    patron = re.compile('([0-9]{3})([\.,;:-])([0-9]{3})([\.,;:-])([0-9]{3})+')
    return patron.match(number)


def is_nit_2(number):
    # Checking number as nit
    patron = re.compile('^([0-9]{9})$')
    return patron.match(number)


def is_numeral(number):
    # Checking number as numeral decimal
    patron = re.compile('([0-9]{1,2})([\.,;:-])([0-9]{1,2})([\.,;:-])([0-9]{1,2})+')
    return patron.match(number)


def extract_clausula_dia_habil(text):
    # Extract "clausula dia habil" of the text
    text = clean_string(text)
    if 'clausula 3. acuerdo de dia habil\n' in text:
        start = text.find('clausula 3. acuerdo de dia habil\n')
        end = text.find('clausula 4. compensacion\n')
        return text[start:end]


def clean_string(string):
    # Clean string of tildes
    return string.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace('ú', "u")


def is_similar(text1, text2):
    # Checking similarity of two texts
    return True if SequenceMatcher(None, text1, text2).ratio() > 0.7 else False
