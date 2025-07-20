from django.shortcuts import render, get_object_or_404, redirect
from .models import EDocument
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required

@login_required
@permission_required('edocuments.can_view_document', raise_exception=True)
def document_list(request):
    user = request.user
    is_department_head = user.groups.filter(name='Manager').exists()

    if is_department_head:
        # Department head sees all documents from their department
        documents = EDocument.objects.filter(department=user.department)
    else:
        # Regular users see only their own documents
        documents = EDocument.objects.filter(submitted_by=user)

    context = {'documents': documents, 'is_department_head': is_department_head}
    return render(request, 'edocuments/document_list.html', context)

@login_required
@permission_required('edocuments.can_upload_document', raise_exception=True)
def document_upload(request):
    # your upload logic here
    pass

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EDocumentForm
from .models import EDocument

@login_required
@permission_required('edocuments.can_upload_document', raise_exception=True)
def document_create(request):
    if request.method == 'POST':
        form = EDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            edocument = form.save(commit=False)
            edocument.submitted_by = request.user
            edocument.department = request.user.department  # assuming user has department FK
            edocument.save()
            messages.success(request, "Document submitted successfully.")
            return redirect('edocuments:document_list')
    else:
        form = EDocumentForm()
    return render(request, 'edocuments/document_create.html', {'form': form})


@login_required
@permission_required('edocuments.can_approve_document', raise_exception=True)
def document_approve(request, pk):
    user = request.user
    if not user.groups.filter(name='Manager').exists():
        messages.error(request, "You are not authorized to approve documents.")
        return redirect('edocuments:document_list')

    document = get_object_or_404(EDocument, pk=pk, department=user.department)

    if document.status != 'submitted':
        messages.warning(request, "This document is already processed.")
        return redirect('edocuments:document_list')

    document.status = 'approved'
    document.save()
    messages.success(request, "Document approved.")
    return redirect('edocuments:document_list')

@login_required
@permission_required('edocuments.can_approve_document', raise_exception=True)
def document_reject(request, pk):
    user = request.user
    if not user.groups.filter(name='Manager').exists():
        messages.error(request, "You are not authorized to reject documents.")
        return redirect('edocuments:document_list')

    document = get_object_or_404(EDocument, pk=pk, department=user.department)

    if document.status != 'submitted':
        messages.warning(request, "This document is already processed.")
        return redirect('edocuments:document_list')

    document.status = 'rejected'
    document.save()
    messages.success(request, "Document rejected.")
    return redirect('edocuments:document_list')
