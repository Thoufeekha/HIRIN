import os
import json
import spacy
from pathlib import Path

from groq import Groq
from dotenv import load_dotenv


class RequirementExtractor:

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

        self.nlp = spacy.load(
            "en_core_web_sm"
        )

    def preprocess_text(
        self,
        role=None,
        jd=None
    ):
        """
        Build input text for Groq.

        Supports:
        - Role only
        - JD only
        - Role + JD
        """

        if not role and not jd:
            raise ValueError(
                "Either role or job description is required."
            )

        combined_text = ""

        if role:
            combined_text += (
                f"Role:\n{role}\n\n"
            )

        if jd:
            combined_text += (
                f"Job Description:\n{jd}"
            )

        doc = self.nlp(
            combined_text         
        )

        tokens = []

        for token in doc:

            if token.is_space:
                continue

            tokens.append(
                token.text
            )

        return " ".join(tokens)

    def call_groq(
        self,
        processed_text
    ):

        prompt = f"""
You are an ATS Job Requirement Extractor.

Analyze the provided information and return ONLY valid JSON.

Schema:

{{
    "role": "",
    "source": "",
    "required_skills": [],
    "preferred_skills": [],
    "soft_skills": [],
    "experience_requirements": [],
    "certifications": []
}}

Rules:

1. If a Job Description is provided,
   extract requirements strictly from it.

2. If no Job Description is provided,
   infer common industry-standard
   requirements based on the role.

3. Do not invent company-specific requirements.

4. Extract technical skills.

5. Extract preferred skills.

6. Extract soft skills.

7. Extract certifications.

8. Extract experience requirements.

9. Set source as:
   - "jd_based" if JD is present
   - "role_based" if only role is present

10. Return ONLY valid JSON.

11. No markdown.

12. No explanations.

13. No comments.

Input:

{processed_text}
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

        try:

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

        except Exception as e:

            print(
                "\n===== RAW GROQ RESPONSE =====\n"
            )

            print(result)

            raise ValueError(
                f"Failed to parse JSON: {e}"
            )

    def extract(
        self,
        role=None,
        jd=None
    ):

        processed_text = (
            self.preprocess_text(
                role,
                jd
            )
        )

        raw_response = (
            self.call_groq(
                processed_text
            )
        )

        return self.parse_json(
            raw_response
        )


