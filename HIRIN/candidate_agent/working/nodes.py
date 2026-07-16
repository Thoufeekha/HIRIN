import os
import json
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import (
    SentenceTransformer
)

from sklearn.metrics.pairwise import (
    cosine_similarity
)

from accounts.models import (
    Job,
    JobSeekerProfile,
    Invitation,
    Notification
)

from .prompts import (
    JOB_ANALYSIS_PROMPT,
    CANDIDATE_EVALUATION_PROMPT,
    REPORT_PROMPT
)
from django.urls import reverse


load_dotenv()

client = Groq(
    api_key=os.getenv(
        "GROQ_API_KEY"
    )
)

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def clean_json_response(text):

    text = (
        text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON returned"
        )

    return json.loads(
        text[start:end + 1]
    )


def analyze_job(state):

    job = Job.objects.get(
        id=state["job_id"]
    )

    prompt = JOB_ANALYSIS_PROMPT.format(
        title=job.title,
        description=job.description,
        skills=job.skills
    )

    response = (
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
    )

    print("\n===== AI RESPONSE =====")
    print(response.choices[0].message.content)

    result = clean_json_response(
        response
        .choices[0]
        .message
        .content
    )

    result["job_id"] = job.id

    state["job_data"] = result

    return state


def fetch_candidates(state):

    candidates = (
        JobSeekerProfile.objects
        .filter(
            profile_completed=True,
            profile_visible=True
        )
        .select_related("user")
    )

    candidate_list = []

    for candidate in candidates:

        candidate_list.append({

            "id":
            candidate.id,

            "user_id":
            candidate.user.id,

            "name":
            candidate.user.get_full_name()
            or candidate.user.username,

            "skills":
            candidate.skills,

            "experience":
            candidate.experience_level,

            "education":
            candidate.education,

            "field":
            candidate.field,

            "preferred_role":
            candidate.preferred_job_role,
        })

    state["candidates"] = (
        candidate_list
    )

    return state


def embedding_match(state):

    job_data = state["job_data"]

    job_text = " ".join(

        job_data.get(
            "required_skills",
            []
        )

    )

    job_embedding = (
        embedding_model.encode(
            job_text
        )
    )

    scored_candidates = []

    for candidate in state["candidates"]:

        candidate_text = (
            f"{candidate['skills']} "
            f"{candidate['preferred_role']}"
        )

        candidate_embedding = (
            embedding_model.encode(
                candidate_text
            )
        )

        similarity = (
            cosine_similarity(
                [job_embedding],
                [candidate_embedding]
            )[0][0]
        )

        candidate[
            "similarity"
        ] = float(similarity)

        scored_candidates.append(
            candidate
        )

    scored_candidates.sort(
        key=lambda x:
        x["similarity"],
        reverse=True
    )

    state["top_candidates"] = (
        scored_candidates[:10]
    )

    return state


def evaluate_candidates(state):

    evaluations = []

    for candidate in state[
        "top_candidates"
    ]:

        prompt = (
            CANDIDATE_EVALUATION_PROMPT
            .format(

                job_data=
                json.dumps(
                    state["job_data"],
                    indent=2
                ),

                candidate_name=
                candidate["name"],

                preferred_role=
                candidate[
                    "preferred_role"
                ],

                experience=
                candidate[
                    "experience"
                ],

                skills=
                candidate[
                    "skills"
                ],

                education=
                candidate[
                    "education"
                ],

                field=
                candidate[
                    "field"
                ]
            )
        )

        response = (
            client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )
        )

        try:

            result = (
                clean_json_response(
                    response
                    .choices[0]
                    .message
                    .content
                )
            )

            result[
                "candidate"
            ] = candidate

            evaluations.append(
                result
            )

        except Exception:

            continue

    state[
        "evaluations"
    ] = evaluations

    return state


def invite_candidates(state):

    job = Job.objects.get(
        id=state["job_id"]
    )

    recruiter = job.recruiter

    invited = []

    for evaluation in state[
        "evaluations"
    ]:

        score = int(
            evaluation.get(
                "score",
                0
            )
        )

        invite = str(
            evaluation.get(
                "invite",
                False
            )
        ).lower() == "true"



        if not invite:
            continue

        if score < 85:
            continue

        candidate = (
            evaluation[
                "candidate"
            ]
        )

        print("\n===== INVITATION CHECK =====")
        print("Candidate:", candidate["name"])
        print("Score:", score)
        print("Invite:", invite)

        invitation, created = (
            Invitation.objects
            .get_or_create(

                recruiter=
                recruiter,

                candidate_id=
                candidate[
                    "user_id"
                ],

                job=job,

                defaults={

                    "match_score":
                    score,

                    "message":
                    f"{recruiter.company_name} "
                    f"invited you to "
                    f"apply for "
                    f"{job.title}"
                }
            )
        )

        if created:

            Notification.objects.create(

                recipient_id=
                candidate["user_id"],

                message=
                f"{recruiter.company_name} "
                f"invited you to "
                f"apply for "
                f"{job.title}",

                link=reverse(
                    "job_detail",
                    args=[job.id]
                )
            )

            invited.append({

                "candidate":
                candidate[
                    "name"
                ],

                "score":
                score
            })

    state[
        "invited_candidates"
    ] = invited

    return state


def generate_report(state):

    job = Job.objects.get(
        id=state["job_id"]
    )

    total_candidates = len(
        state["candidates"]
    )

    total_invited = len(
        state["invited_candidates"]
    )

    prompt = REPORT_PROMPT.format(

        job_title=job.title,

        invited_candidates=
        json.dumps(
            state[
                "invited_candidates"
            ],
            indent=2
        )
    )

    response = (
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )
    )

    report = (
        response
        .choices[0]
        .message
        .content
    )

    Notification.objects.create(

        recipient=job.recruiter.user,

        message=
        (
            f"{total_invited} candidate{'s' if total_invited != 1 else ''} "
            f"invited for {job.title}"
        ),

        link=reverse(
            "agent_invites",
            args=[job.id]
        )
    )

    state["report"] = report

    return state