from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image
import base64
from google.cloud import vision
from google.cloud import language
import six
import re


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
            nit = []
            for number in numbers:
                if is_nit(number):
                    nit.append(number)
            data = {'url': '/media/output/page-{}.jpg'.format(page), 'text': text, 'nit': nit}
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
    patron = re.compile('([0-9]{3})\.([0-9]{3})\.([0-9]{3})+')
    return patron.match(nit)
