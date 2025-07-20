from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas

def generate_pdf(filename, draw_func, context_obj):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    draw_func(p, context_obj)  # Only pass the canvas and the object

    p.showPage()
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
