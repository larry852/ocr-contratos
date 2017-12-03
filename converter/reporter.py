import xlwt
from django.http import HttpResponse
from . import utils


def generate(documents):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="documents.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Documentos')
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['NIT', 'Documento', 'Fecha de subida', 'Hora de subida']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    for document in documents:
        row_num += 1
        row = [
            document.nit,
            utils.get_name_document(document),
            document.uploaded_at.strftime("%d-%m-%Y"),
            document.uploaded_at.strftime("%I:%M:%S %p"),
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response
