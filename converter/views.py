from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image
import base64
from google.cloud import vision


def index(request):
    if request.method == 'POST' and request.FILES['pdf']:
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save('input/' + pdf.name, pdf)
        # Convert pdf to image
        pages = convert(filename)
        # Get OCR
        for page in range(pages):
            extractOCR('page-{}.jpg'.format(page))

        return render(request, 'upload.html', {
            'pages': range(pages)
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
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()
    with open('media/output/' + filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')
    for text in texts:
        print('\n"{}"'.format(text.description))
