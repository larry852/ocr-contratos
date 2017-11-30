from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image
import base64
from google.cloud import vision
from google.cloud import language
import six
import re
from difflib import SequenceMatcher


def index(request):
    if request.method == 'POST' and request.FILES['pdf']:
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save('input/' + pdf.name, pdf)
        # Convert pdf to image
        print("Conversion pdf a imagen")
        pages = convert(filename)
        # Get OCR
        context = []
        for page in range(pages):
            print("Procesando pagina " + str(page))
            text = extractOCR('page-{}.jpg'.format(page))
            numbers = syntax_text(text)

            numbers_clausula = []
            numeral = []
            str_clausula_dia_habil = clausula_dia_habil(text)
            if str_clausula_dia_habil is not None:
                numbers_clausula = syntax_text(str_clausula_dia_habil)
                for number in numbers_clausula:
                    if is_numeral(number):
                        numeral.append(number)
                if not numeral:
                    numeral.append('No detectado')

            nit = []
            for number in numbers:
                if is_nit(number):
                    nit.append(number)
            if not nit:
                for number in numbers:
                    if is_nit_2(number):
                        nit.append(number)
            data = {'url': '/media/output/page-{}.jpg'.format(page), 'text': text, 'nit': nit, 'numeral': numeral}
            context.append(data)
            # print("Extraccion entidades")
            # entities_text(ocr['text'])

        return render(request, 'upload.html', {
            'context': context
        })

    return render(request, 'upload.html')


def convert(filename, resolution=300):
    pages = 0
    with Image(filename='media/' + filename, resolution=resolution) as img:
        img.save(filename="media/output/page.jpg")
        pages = len(img.sequence)
    return pages


def getBase64(filename):
    encoded_string = ""
    with open('media/output/' + filename, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


def extractOCR(filename):
    client = vision.Client()
    with open('media/output/' + filename, 'rb') as image_file:
        image = client.image(content=image_file.read())
    texts = image.detect_text()
    return texts[0].description


def entities_text(text):
    """Detects entities in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    # entity types from enums.Entity.Type
    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    for entity in entities:
        print('=' * 20)
        print(u'{:<16}: {}'.format('name', entity.name))
        print(u'{:<16}: {}'.format('type', entity_type[entity.type]))
        print(u'{:<16}: {}'.format('metadata', entity.metadata))
        print(u'{:<16}: {}'.format('salience', entity.salience))
        print(u'{:<16}: {}'.format('wikipedia_url',
                                   entity.metadata.get('wikipedia_url', '-')))


def syntax_text(text):
    """Detects syntax in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)

    # Detects syntax in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    tokens = client.analyze_syntax(document).tokens

    # part-of-speech tags from enums.PartOfSpeech.Tag
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
               'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    data = []

    for token in tokens:
        if pos_tag[token.part_of_speech.tag] == 'NUM':
            data.append(token.text.content)

    return data


def is_nit(nit):
    patron = re.compile('([0-9]{3})([\.,;:-])([0-9]{3})([\.,;:-])([0-9]{3})+')
    return patron.match(nit)


def is_nit_2(nit):
    patron = re.compile('^([0-9]{9})$')
    return patron.match(nit)


def is_numeral(numeral):
    patron = re.compile('([0-9]{1,2})([\.,;:-])([0-9]{1,2})([\.,;:-])([0-9]{1,2})+')
    return patron.match(numeral)


def clausula_dia_habil(text):
    text = clean_string(text)
    if 'clausula 3. acuerdo de dia habil\n' in text:
        start = text.find('clausula 3. acuerdo de dia habil\n')
        end = text.find('clausula 4. compensacion\n')
        return text[start:end]


def clean_string(string):
    return string.lower().replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace('ú', "u")


def similar(text1, text2):
    if SequenceMatcher(None, text1, text2).ratio() > 0.7:
        return True
    else:
        return False
