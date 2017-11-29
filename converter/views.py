from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image
import base64
from google.cloud import vision


def index(request):
    if request.method == 'POST' and request.FILES['pdf']:
        data = []
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save('input/' + pdf.name, pdf)
        # Convert pdf to image
        print("Conversion pdf a imagen")
        pages = convert(filename)
        # Get OCR
        for page in range(pages):
            ocr = {'url': '/media/output/page-{}.jpg'.format(page), 'text': extractOCR('page-{}.jpg'.format(page))}
            data.append(ocr)
            print("Extraccion texto de pagina " + str(page))
        return render(request, 'upload.html', {
            'data': data
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
