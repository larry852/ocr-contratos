from .models import Document
import xlwt
from django.http import HttpResponse

def printDocuments(documents):
    #for document in documents:
    #print(document)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="documents.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Documentos')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Nit', 'Fecha de subida']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    for obj in documents:
        row_num += 1
        row = [
            obj.nit,
            str(obj.uploaded_at) ,
        ]
        print(row)
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
            print(row[col_num])   
    wb.save(response)
    return response
