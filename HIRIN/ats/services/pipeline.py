import json

from .resume_parser import ResumeParser
from .resume_extractor import ResumeExtractor
from .requirement_extractor import RequirementExtractor
from .ats_evaluator import ATSEvaluator


class ATSPipeline:

    def __init__(self):

        self.parser = ResumeParser()

        self.requirement_extractor = (
            RequirementExtractor()
        )

        self.evaluator = (
            ATSEvaluator()
        )

    def run(
        self,
        pdf_path,
        role=None,
        jd=None
    ):

        print("\nExtracting resume text...")

        resume_text = (
            ResumeExtractor.extract_text(
                pdf_path
            )
        )

        print("Parsing resume...")

        resume_json = (
            self.parser.parse_resume(
                resume_text
            )
        )

        print("\n========== RESUME JSON ==========")
        print(json.dumps(resume_json, indent=4))
        print("====================================\n")

        print("Extracting job requirements...")

        target_profile = (
            self.requirement_extractor.extract(
                role=role,
                jd=jd
            )
        )

        print("\n========== TARGET PROFILE ==========")
        print(json.dumps(target_profile, indent=4))
        print("=======================================\n")

        print("Running ATS evaluation...")

        ats_result = (
            self.evaluator.evaluate(
                resume_json,
                target_profile
            )
        )

        print("\n========== ATS RESULT ==========")
        print(json.dumps(ats_result, indent=4))
        print("==================================\n")

        return {
            "resume_json": resume_json,
            "target_profile": target_profile,
            "ats_result": ats_result
        }


if __name__ == "__main__":

    pdf_path = "Rizwin.pdf"

    role = "Data Scientist"

    jd = """
    Looking for a Data Scientist with Python,
    SQL, Machine Learning, AWS and Docker.

    Good communication skills required.

    Experience building machine learning models.
    """

    pipeline = (
        ATSPipeline()
    )

    result = pipeline.run(
        pdf_path=pdf_path,
        role=role,
        jd=jd
    )

    print("\n===== FINAL RESUME JSON =====\n")

    print(
        json.dumps(
            result["resume_json"],
            indent=4
        )
    )

    print("\n===== FINAL TARGET PROFILE =====\n")

    print(
        json.dumps(
            result["target_profile"],
            indent=4
        )
    )

    print("\n===== FINAL ATS RESULT =====\n")

    print(
        json.dumps(
            result["ats_result"],
            indent=4
        )
    )