from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image
import base64


def index(request):
    if request.method == 'POST' and request.FILES['pdf']:
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save('input/' + pdf.name, pdf)
        pages = convert(filename)

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
