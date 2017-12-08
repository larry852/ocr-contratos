from django.shortcuts import render
from .models import Document
from . import utils, google
from django.shortcuts import get_object_or_404
import logging
import logging.config
import sys

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)


def index(request, document=None):
    if document:
        show_form = False
        # Get PDF file from DB
        document = get_object_or_404(Document, pk=document)
        request.method = 'POST'
    elif request.method == 'POST':
        show_form = True
        # Get PDF file from form
        pdf = request.FILES['pdf']

        # Save PDF file on model
        document = Document(file=pdf)
        document.save()
    else:
        return render(request, 'upload.html', {'show_form': True})

    # Get path of document
    path = document.file.path

    # Convert pdf to image
    logging.info("Conversión pdf a imagen ...")
    pages = utils.convert(path)

    context = []
    for page in range(pages):
        logging.info("\nProcesando página " + str(page + 1) + " ...")

        # Get OCR
        logging.info("Extracción OCR")
        text = google.extract_OCR('page-{}.jpg'.format(page))

        # Get numbers
        numbers = google.extract_numbers(text)

        # Get NIT
        nit = []
        for number in numbers:
            if utils.is_nit(number):
                logging.info("NIT detectado")
                number = utils.clean_number(number)
                if document.nit == Document._meta.get_field('nit').get_default():
                    document.nit = number
                    document.save()
                nit.append(number)
        if not nit:
            for number in numbers:
                if utils.is_nit_2(number):
                    logging.info("NIT detectado")
                    number = utils.clean_number(number)
                    if document.nit == Document._meta.get_field('nit').get_default():
                        document.nit = number
                        document.save()
                    nit.append(number)

        # Get clausula dia habil
        text_clausula_dia_habil = utils.extract_clausula_dia_habil(text)

        # Get numeral
        numeral = []
        if text_clausula_dia_habil is not None:
            logging.info("Cláusula 3 detectada")
            numbers_clausula = google.extract_numbers(text_clausula_dia_habil)
            for number in numbers_clausula:
                if utils.is_numeral(number):
                    numeral.append(number)
            if not numeral:
                numeral.append('No detect')

        # Response
        data = {'url': '/media/output/page-{}.jpg'.format(page), 'text': text, 'nit': nit, 'numeral': numeral}
        context.append(data)

    return render(request, 'upload.html', {
        'context': context,
        'show_form': show_form,
        'document': {'url': document.file.url, 'name': utils.get_name_document(document)}
    })
