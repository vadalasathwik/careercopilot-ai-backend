import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel, Field

# Load env variables
load_dotenv()

# Configure the Gemini API client
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class ATSAnalysisResultSchema(BaseModel):
    ats_score: int = Field(..., description="An ATS compatibility score between 0 and 100.")
    match_score: int = Field(..., description="A job description match score between 0 and 100.")
    missing_skills: list[str] = Field(..., description="List of missing skills/requirements.")
    recommendations: list[str] = Field(..., description="Actionable recommendations for improvement.")

def analyze_resume_against_jd(resume_text: str, job_description: str) -> dict:
    """
    Analyzes resume text against a job description using Gemini 2.5 Flash.
    Returns a dictionary matching the specified format.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured in the environment.")

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": ATSAnalysisResultSchema,
        }
    )

    prompt = f"""
You are an expert ATS (Applicant Tracking System) and hiring assistant.
Compare the following resume text against the job description.
Calculate the ATS score and general match score (both integers from 0 to 100),
identify any missing skills or requirements in the resume compared to the job description,
and provide actionable recommendations for improvement.

Resume Text:
{resume_text}

Job Description:
{job_description}

Return ONLY valid JSON.
No markdown.
No code fences.
No explanations.
"""

    response = model.generate_content(prompt)
    
    # Parse the response text as JSON
    try:
        data = json.loads(response.text)
        return data
    except Exception as e:
        raise ValueError(f"Failed to parse Gemini response: {e}. Raw response: {response.text}")
