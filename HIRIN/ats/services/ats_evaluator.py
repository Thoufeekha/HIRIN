import os
import json
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv


class ATSEvaluator:

    def __init__(self):

        # Load .env from Email folder
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        load_dotenv(BASE_DIR / "Email" / ".env")

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found")

        self.client = Groq(
            api_key=api_key
        )

    def call_groq(
        self,
        resume_json,
        target_profile
    ):

        prompt = f"""
You are an ATS Resume Evaluator.

Compare the resume against
the target job profile.

Resume:

{json.dumps(resume_json, indent=2)}

Target Profile:

{json.dumps(target_profile, indent=2)}

Return ONLY valid JSON.

Schema:

{{
    "ats_score": 0,

    "job_match": 0,

    "matched_skills": [],

    "missing_skills": [],

    "strengths": [],

    "weaknesses": [],

    "suggestions": []
}}

Scoring Rules:

- ATS Score between 0 and 100
- Job Match between 0 and 100
- Compare skills
- Compare projects
- Compare experience
- Compare education
- Identify missing skills
- Give realistic suggestions
- Do not invent experience

Return JSON only.
"""

        response = (
            self.client.chat.completions.create(
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

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    def parse_json(
        self,
        result
    ):

        result = (
            result
            .replace(
                "```json",
                ""
            )
            .replace(
                "```",
                ""
            )
            .strip()
        )

        start = result.find("{")
        end = result.rfind("}")

        if start == -1 or end == -1:
            raise ValueError(
                "JSON not found"
            )

        result = result[
            start:end + 1
        ]

        return json.loads(
            result
        )

    def evaluate(
        self,
        resume_json,
        target_profile
    ):

        raw_response = self.call_groq(
            resume_json,
            target_profile
        )

        print("\n========== RAW GROQ RESPONSE ==========")
        print(raw_response)
        print("=======================================\n")

        parsed = self.parse_json(raw_response)

        print("\n========== PARSED ATS RESULT ==========")
        print(json.dumps(parsed, indent=4))
        print("=======================================\n")

        return parsed


# Example usage
if __name__ == "__main__":
    # Initialize the evaluator
    evaluator = ATSEvaluator()
    
    # Sample resume data (you would replace this with actual data)
    sample_resume = {
        "name": "John Doe",
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL"],
        "experience": [
            {
                "company": "Tech Corp",
                "role": "Software Engineer",
                "duration": "2020-2023",
                "description": "Developed web applications using React and Node.js"
            }
        ],
        "education": {
            "degree": "B.S. Computer Science",
            "university": "MIT",
            "year": "2020"
        },
        "projects": [
            {
                "name": "E-commerce Platform",
                "description": "Built full-stack e-commerce site"
            }
        ]
    }
    
    # Sample target profile
    sample_profile = {
        "title": "Full Stack Developer",
        "required_skills": ["Python", "React", "Node.js", "Docker", "AWS"],
        "preferred_skills": ["TypeScript", "GraphQL"],
        "experience_required": "3+ years",
        "education_required": "Bachelor's in CS or related"
    }
    
    # Run evaluation
    try:
        result = evaluator.evaluate(sample_resume, sample_profile)
        print("\n✅ Evaluation completed successfully!")
        print(f"ATS Score: {result.get('ats_score', 'N/A')}")
        print(f"Job Match: {result.get('job_match', 'N/A')}")
    except Exception as e:
        print(f"\n❌ Error: {e}")