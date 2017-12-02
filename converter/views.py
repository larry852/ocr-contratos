from django.shortcuts import render
from .models import Document
from . import utils, google
from django.shortcuts import get_object_or_404


def index(request, document=None):
    if document:
        # Get PDF file from DB
        document = get_object_or_404(Document, pk=document)
        request.method = 'POST'
    else:
        # Get PDF file from form
        pdf = request.FILES['pdf']

        # Save PDF file on model
        document = Document(file=pdf)
        document.save()

    if request.method == 'POST':
        # Get path of document
        path = document.file.path

        # Convert pdf to image
        print("Conversión pdf a imagen ...")
        pages = utils.convert(path)

        context = []
        for page in range(pages):
            print("\nProcesando página " + str(page + 1) + " ...")

            # Get OCR
            print("Extracción OCR")
            text = google.extract_OCR('page-{}.jpg'.format(page))

            # Get numbers
            numbers = google.extract_numbers(text)

            # Get NIT
            nit = []
            for number in numbers:
                if utils.is_nit(number):
                    print("NIT detectado")
                    number = utils.clean_number(number)
                    if document.nit == Document._meta.get_field('nit').get_default():
                        document.nit = number
                        document.save()
                    nit.append(number)
            if not nit:
                for number in numbers:
                    if utils.is_nit_2(number):
                        print("NIT detectado")
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
                print("Cláusula 3 detectada")
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
            'context': context
        })

    return render(request, 'upload.html')
