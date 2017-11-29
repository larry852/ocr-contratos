from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from wand.image import Image


def index(request):
    if request.method == 'POST' and request.FILES['pdf']:
        pdf = request.FILES['pdf']
        fs = FileSystemStorage()
        filename = fs.save('input/' + pdf.name, pdf)
        # Converting pdf to JPG
        with Image(filename='media/' + filename, resolution=300) as img:
            img.save(filename="media/output/page.jpg")
            pages = len(img.sequence)

        return render(request, 'upload.html', {
            'pages': range(pages)
        })

    return render(request, 'upload.html')
