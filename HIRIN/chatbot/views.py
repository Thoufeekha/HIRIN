from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# from .chatbot_code.router import get_response


# Temporary fix - chatbot disabled

import json


def chatbot_page(request):

    answer = ""

    if request.method == "POST":

        query = request.POST.get("query")

        answer = get_response(
            query,
            request.user
        )

    return render(
        request,
        "jobseeker/chatbot.html",
        {
            "answer": answer
        }
    )


@csrf_exempt
def chatbot_api(request):

    if request.method == "POST":

        data = json.loads(request.body)

        query = data.get("message")

        answer = get_response(
            query,
            request.user
        )

        return JsonResponse({
            "reply": answer
        })

    return JsonResponse({
        "reply": "Invalid request"
    })