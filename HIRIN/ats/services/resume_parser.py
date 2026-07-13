import os
import re
import json
import spacy

from groq import Groq
from dotenv import load_dotenv

from .resume_extractor import ResumeExtractor


class ResumeParser:

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(

                "GROQ_API_KEY not found in .env file"
            )

        self.client = Groq(
            api_key=api_key
        )

        self.nlp = spacy.load(
            "en_core_web_sm"
        )

    def extract_contact_info(self, text):

        email = None
        phone = None
        linkedin = None
        github = None

        email_pattern = (
            r"[A-Za-z0-9._%+-]+"
            r"@[A-Za-z0-9.-]+"
            r"\.[A-Za-z]{2,}"
        )

        phone_pattern = (
            r"(?:\+91[-\s]?)?\d{10}"
        )

        linkedin_pattern = (
            r"(https?:\/\/)?"
            r"(www\.)?"
            r"linkedin\.com\/[^\s]+"
        )

        github_pattern = (
            r"(https?:\/\/)?"
            r"(www\.)?"
            r"github\.com\/[^\s]+"
        )

        email_match = re.search(
            email_pattern,
            text,
            re.IGNORECASE
        )

        if email_match:
            email = email_match.group()

        phone_match = re.search(
            phone_pattern,
            text
        )

        if phone_match:
            phone = phone_match.group()

        linkedin_match = re.search(
            linkedin_pattern,
            text,
            re.IGNORECASE
        )

        if linkedin_match:
            linkedin = linkedin_match.group()

        github_match = re.search(
            github_pattern,
            text,
            re.IGNORECASE
        )

        if github_match:
            github = github_match.group()

        return {
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github
        }

    def preprocess_text(self, text):

        doc = self.nlp(text)

        tokens = []

        for token in doc:

            if token.is_space:
                continue

            tokens.append(token.text)

        return " ".join(tokens)

    def call_groq(self, cleaned_text):

        prompt = f"""
You are an expert ATS Resume Parser.

Analyze the resume and return ONLY valid JSON.

Schema:

{{
    "name": "",

    "summary": "",

    "skills": [],

    "projects": [
        {{
            "name": "",
            "technologies": []
        }}
    ],

    "experience": [
        {{
            "role": "",
            "company": "",
            "location": "",
            "duration": ""
        }}
    ],

    "education": [
        {{
            "degree": "",
            "institution": "",
            "duration": ""
        }}
    ],

    "certifications": []
}}

Rules:

- Return ONLY valid JSON
- No markdown
- No explanations
- No comments
- Do not invent information
- Extract project technologies whenever possible
- Extract role, company, location and duration separately
- Extract education details separately
- Keep skills as list of strings
- Use empty strings if unavailable

Resume:

{cleaned_text}
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

    def parse_groq_json(self, result):

        try:

            result = (
                result
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            start = result.find("{")
            end = result.rfind("}")

            if start == -1 or end == -1:
                raise ValueError(
                    "No JSON object found."
                )

            result = result[
                start:end + 1
            ]

            parsed_json = json.loads(
                result
            )

            return parsed_json

        except Exception as e:

            print(
                "\n===== RAW GROQ RESPONSE =====\n"
            )
            print(result)

            raise ValueError(
                f"Failed to parse JSON: {e}"
            )

    def parse_resume(self, resume_text):

        contact_info = (
            self.extract_contact_info(
                resume_text
            )
        )

        cleaned_text = (
            self.preprocess_text(
                resume_text
            )
        )

        raw_response = (
            self.call_groq(
                cleaned_text
            )
        )

        parsed_json = (
            self.parse_groq_json(
                raw_response
            )
        )

        parsed_json["email"] = (
            contact_info["email"]
        )

        parsed_json["phone"] = (
            contact_info["phone"]
        )

        parsed_json["linkedin"] = (
            contact_info["linkedin"]
        )

        parsed_json["github"] = (
            contact_info["github"]
        )

        return parsed_json


