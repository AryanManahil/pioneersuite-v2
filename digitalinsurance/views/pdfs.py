from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from digitalinsurance.models import InsurancePolicy


@login_required
def download_policy_pdf(request, policy_id):
    policy = get_object_or_404(InsurancePolicy, id=policy_id, user=request.user)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Title
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 80, "Policy Certificate")

    # Policy Info
    p.setFont("Helvetica", 12)
    y = height - 120
    line_height = 20

    fields = [
        ("Policy Number", policy.policy_number),
        ("Product", policy.product.name),
        ("Status", policy.status),
        ("Start Date", policy.start_date.strftime('%B %d, %Y')),
        ("End Date", policy.end_date.strftime('%B %d, %Y')),
        ("Premium Amount", f"{policy.premium_amount} BDT"),
    ]

    for label, value in fields:
        p.drawString(50, y, f"{label}: {value}")
        y -= line_height

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 50, "This is a system-generated document.")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=policy_{policy.policy_number}.pdf'
    return response
