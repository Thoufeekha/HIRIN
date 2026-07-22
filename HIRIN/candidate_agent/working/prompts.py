JOB_ANALYSIS_PROMPT = """
You are an expert recruitment analyst.

Analyze the following job posting.

Return ONLY valid JSON.

Schema:

{{
    "title": "",
    "required_skills": [],
    "preferred_skills": [],
    "experience_level": "",
    "job_summary": ""
}}

Rules:

- Return only JSON
- No markdown
- No explanations
- No extra text
- Extract technical and domain skills
- Keep skills as a list of strings

JOB TITLE:
{title}

JOB DESCRIPTION:
{description}

JOB SKILLS:
{skills}
"""

CANDIDATE_EVALUATION_PROMPT = """
You are an expert AI recruiter.

Evaluate how well the candidate matches the job.

Return ONLY valid JSON.

Schema:

{{
    "score": 0,
    "invite": false,
    "reason": ""
}}

Rules:

- score must be between 0 and 100
- invite must be true or false
- reason should be short
- return only JSON
- no markdown
- no explanations

JOB:

{job_data}

CANDIDATE:

Name:
{candidate_name}

Preferred Role:
{preferred_role}

Experience:
{experience}

Skills:
{skills}

Education:
{education}

Field:
{field}
"""

REPORT_PROMPT = """
You are an AI recruiting assistant.

Create a concise recruiter report.

JOB:
{job_title}

INVITED CANDIDATES:
{invited_candidates}

Return a short summary.
"""