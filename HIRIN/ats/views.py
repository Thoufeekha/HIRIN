from django.shortcuts import render
from django.core.files.storage import FileSystemStorage

from .services.pipeline import ATSPipeline


def ats_resume(request):
    """
    Upload Resume Page
    """

    if request.method == "POST":

        job_description = request.POST.get("job_description")
        resume = request.FILES.get("resume")

        if resume:

            fs = FileSystemStorage()
            filename = fs.save(resume.name, resume)
            file_path = fs.path(filename)

            pipeline = ATSPipeline()

            result = pipeline.run(
                pdf_path=file_path,
                role=None,
                jd=job_description
            )

            context = {
                "result": result["ats_result"]
            }

            # Open Report Page
            return render(
                request,
                "jobseeker/ats_resume.html",
                context
            )

    # First time opening the page
    return render(
        request,
        "jobseeker/ats_resume.html"
    )