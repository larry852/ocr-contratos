from google.cloud import vision
from google.cloud import language
import six


def extract_OCR(filename):
    # Extract text of the image fiel
    client = vision.Client()
    with open('media/output/' + filename, 'rb') as image_file:
        image = client.image(content=image_file.read())
    texts = image.detect_text()
    return texts[0].description


def extract_numbers(text):
    # Extract numbres of the text
    client = language.LanguageServiceClient()
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)
    tokens = client.analyze_syntax(document).tokens
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
               'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')
    data = []
    for token in tokens:
        if pos_tag[token.part_of_speech.tag] == 'NUM':
            data.append(token.text.content)
    return data


def extract_entities(text):
    # Detect entities of the text
    # need to implement return
    client = language.LanguageServiceClient()
    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
    document = language.types.Document(
        content=text,
        type=language.enums.Document.Type.PLAIN_TEXT)
    entities = client.analyze_entities(document).entities
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
