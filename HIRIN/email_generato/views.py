# email_generato/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings
from django.core.files.base import ContentFile
import os
import re
from datetime import datetime

from .models import GeneratedDocument
from .utils import (
    generate_documents,
    save_content,
    extract_text_from_pdf,
    extract_jd_details,
    fix_contact_details
)

@login_required
def email_generator_home(request):
    """Main page for email/cover letter generator"""
    
    # Get recent documents for this user
    recent_docs = GeneratedDocument.objects.filter(user=request.user)[:10]
    
    context = {
        'recent_docs': recent_docs,
        'generated_doc': None,
    }
    
    return render(request, 'jobseeker/email_generator.html', context)

@login_required
def generate_document(request):
    """Generate cover letter and/or cold email based on user input"""
    
    if request.method == 'POST':
        try:
            # Get form data
            resume_file = request.FILES.get('resume')
            job_description = request.POST.get('job_description', '')
            company_name = request.POST.get('company_name', '')
            job_role = request.POST.get('job_role', '')
            recruiter_name = request.POST.get('recruiter_name', '')
            tone = request.POST.get('tone', 'professional')
            document_type = request.POST.get('document_type', 'both')
            
            # Validate tone - match your original 5 options
            allowed_tones = ['professional', 'confident', 'enthusiastic', 
                           'fresher-friendly', 'experienced']
            if tone not in allowed_tones:
                tone = 'professional'
            
            # Validate document type
            allowed_types = ['cover_letter', 'cold_email', 'both']
            if document_type not in allowed_types:
                document_type = 'both'
            
            # Validate required fields
            if not resume_file:
                messages.error(request, 'Please upload your resume (PDF)')
                return redirect('email_generato:home')
            
            if not job_description:
                messages.error(request, 'Please enter job description')
                return redirect('email_generato:home')
            
            if not company_name:
                messages.error(request, 'Please enter company name')
                return redirect('email_generato:home')
            
            if not job_role:
                messages.error(request, 'Please enter job role')
                return redirect('email_generato:home')
            
            # Save resume temporarily to extract text
            temp_resume_path = os.path.join(settings.MEDIA_ROOT, 'temp_resume.pdf')
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            
            with open(temp_resume_path, 'wb+') as destination:
                for chunk in resume_file.chunks():
                    destination.write(chunk)
            
            # Extract text from PDF
            resume_text = extract_text_from_pdf(temp_resume_path)
            
            # Clean up temp file
            if os.path.exists(temp_resume_path):
                os.remove(temp_resume_path)
            
            if not resume_text:
                messages.error(request, 'Failed to extract text from resume. Please ensure it\'s a valid PDF.')
                return redirect('email_generato:home')
            
            # Auto-extract details from job description if not provided
            extracted_company, extracted_role, extracted_recruiter = extract_jd_details(job_description)
            if not company_name and extracted_company:
                company_name = extracted_company
            if not job_role and extracted_role:
                job_role = extracted_role
            if not recruiter_name and extracted_recruiter:
                recruiter_name = extracted_recruiter
            
            # Generate documents using AI
            result = generate_documents(
                resume_text=resume_text,
                job_description=job_description,
                company_name=company_name,
                job_role=job_role,
                recruiter_name=recruiter_name,
                tone=tone,
                document_type=document_type
            )
            
            if not result:
                messages.error(request, 'Failed to generate documents. Please try again.')
                return redirect('email_generato:home')
            
            # Save to database
            doc = GeneratedDocument(
                user=request.user,
                company_name=company_name,
                job_role=job_role,
                recruiter_name=recruiter_name,
                tone=tone,
                document_type=document_type,
                cover_letter_content=result.get('cover_letter'),
                cold_email_content=result.get('cold_email')
            )
            doc.save()
            
            # Save files to media directory
            output_dir = os.path.join(settings.MEDIA_ROOT, 'generated_docs')
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare content for saving based on document type
            content = ""
            if document_type in ['cover_letter', 'both'] and result.get('cover_letter'):
                content += result['cover_letter']
                if document_type == 'both' and result.get('cold_email'):
                    content += "\n\n--- SEPARATOR ---\n\n"
            
            if document_type in ['cold_email', 'both'] and result.get('cold_email'):
                if document_type == 'both':
                    content += result['cold_email']
                else:
                    content = result['cold_email']
            
            # Save files
            saved_files = save_content(content, document_type, output_dir)
            
            # Update model with file paths
            if saved_files:
                if 'cover_letter' in saved_files:
                    cover_data = saved_files['cover_letter']
                    if cover_data.get('pdf'):
                        with open(cover_data['pdf'], 'rb') as f:
                            doc.cover_letter_pdf.save(
                                os.path.basename(cover_data['pdf']),
                                ContentFile(f.read()),
                                save=False
                            )
                    if cover_data.get('docx'):
                        with open(cover_data['docx'], 'rb') as f:
                            doc.cover_letter_docx.save(
                                os.path.basename(cover_data['docx']),
                                ContentFile(f.read()),
                                save=False
                            )
                
                if 'cold_email' in saved_files:
                    email_data = saved_files['cold_email']
                    if email_data.get('pdf'):
                        with open(email_data['pdf'], 'rb') as f:
                            doc.cold_email_pdf.save(
                                os.path.basename(email_data['pdf']),
                                ContentFile(f.read()),
                                save=False
                            )
                    if email_data.get('docx'):
                        with open(email_data['docx'], 'rb') as f:
                            doc.cold_email_docx.save(
                                os.path.basename(email_data['docx']),
                                ContentFile(f.read()),
                                save=False
                            )
            
            doc.save()
            
            # Prepare data for template
            generated_doc = {
                'id': doc.id,
                'company_name': doc.company_name,
                'job_role': doc.job_role,
                'tone': doc.get_tone_display(),
                'cover_letter_content': doc.cover_letter_content,
                'cold_email_content': doc.cold_email_content,
                'cover_letter_pdf': doc.cover_letter_pdf,
                'cover_letter_docx': doc.cover_letter_docx,
                'cold_email_pdf': doc.cold_email_pdf,
                'cold_email_docx': doc.cold_email_docx,
                'created_at': doc.created_at,
            }
            
            messages.success(request, 'Documents generated successfully!')
            
            # Get recent docs for the page
            recent_docs = GeneratedDocument.objects.filter(user=request.user)[:10]
            
            context = {
                'recent_docs': recent_docs,
                'generated_doc': generated_doc,
                'company_name': company_name,
                'job_role': job_role,
                'recruiter_name': recruiter_name,
                'selected_tone': tone,
                'selected_doc_type': document_type,
                'job_description': job_description,
            }
            
            return render(request, 'jobseeker/email_generator.html', context)
            
        except Exception as e:
            messages.error(request, f'Error generating documents: {str(e)}')
            return redirect('email_generato:home')
    
    return redirect('email_generato:home')

@login_required
def view_document(request, doc_id):
    """View a specific generated document"""
    doc = get_object_or_404(GeneratedDocument, id=doc_id, user=request.user)
    
    context = {
        'doc': doc,
    }
    
    return render(request, 'jobseeker/view_document.html', context)

@login_required
def download_file(request, doc_id, doc_type, file_format):
    """Download specific file (PDF or DOCX)"""
    doc = get_object_or_404(GeneratedDocument, id=doc_id, user=request.user)
    
    if doc_type == 'cover_letter':
        if file_format == 'pdf' and doc.cover_letter_pdf:
            file_path = doc.cover_letter_pdf.path
        elif file_format == 'docx' and doc.cover_letter_docx:
            file_path = doc.cover_letter_docx.path
        else:
            raise Http404("File not found")
    elif doc_type == 'cold_email':
        if file_format == 'pdf' and doc.cold_email_pdf:
            file_path = doc.cold_email_pdf.path
        elif file_format == 'docx' and doc.cold_email_docx:
            file_path = doc.cold_email_docx.path
        else:
            raise Http404("File not found")
    else:
        raise Http404("Invalid document type")
    
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Get file name for download
    filename = os.path.basename(file_path)
    
    # Serve the file
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    if file_format == 'pdf':
        response['Content-Type'] = 'application/pdf'
    elif file_format == 'docx':
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    return response

@login_required
def delete_document(request, doc_id):
    """Delete a generated document"""
    doc = get_object_or_404(GeneratedDocument, id=doc_id, user=request.user)
    
    # Delete files from storage
    if doc.cover_letter_pdf:
        doc.cover_letter_pdf.delete(save=False)
    if doc.cover_letter_docx:
        doc.cover_letter_docx.delete(save=False)
    if doc.cold_email_pdf:
        doc.cold_email_pdf.delete(save=False)
    if doc.cold_email_docx:
        doc.cold_email_docx.delete(save=False)
    
    doc.delete()
    messages.success(request, 'Document deleted successfully!')
    return redirect('email_generato:home')