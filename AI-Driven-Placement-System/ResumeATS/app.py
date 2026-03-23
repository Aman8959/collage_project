import os
import streamlit as st
import io
import json
import base64
import google.generativeai as genai
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from google.api_core.exceptions import NotFound

# Load environment variables from .env file
load_dotenv()

# Gemini API key may be stored as either `GOOGLE_API_KEY` or `API_KEY`
# depending on how the project was configured.
API_KEY = os.getenv('GOOGLE_API_KEY') or os.getenv('API_KEY')

if API_KEY:
    # Configure Google Generative AI with the API key from env.
    genai.configure(api_key=API_KEY)

# Some Gemini accounts don’t expose the exact model id you might expect (e.g. `gemini-1.5-flash`),
# but they do expose a different id for their plan.
#
# We will:
# 1) Try `GEMINI_MODEL` (if provided) first
# 2) Try a few common candidates
# 3) If none work, call `genai.list_models()` and show the available ids to the user.
GEMINI_MODEL = os.getenv('GEMINI_MODEL') or ''
MODEL_CANDIDATES = [
    # User override (if set)
    GEMINI_MODEL,
    # Common alternatives
    'gemini-1.5-flash-latest',
    'gemini-1.5-pro-latest',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-1.0-pro',
    'gemini-pro',
]
MODEL_CANDIDATES = [m for m in MODEL_CANDIDATES if m]  # remove empty strings

# Define cached functions
@st.cache_data()
def get_gemini_response(input, pdf_content, prompt):
    @st.cache_data()
    def list_available_models():
        # Returns model objects with a `.name` field in google-generativeai.
        models = genai.list_models()
        return [getattr(m, "name", str(m)) for m in models]

    last_err = None
    for model_name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([input, pdf_content, prompt])
            return response.text
        except NotFound as e:
            last_err = e
            continue

    available = []
    try:
        available = list_available_models()
    except Exception:
        # If model listing fails, keep the original error.
        available = []

    tried = ", ".join(MODEL_CANDIDATES)
    available_preview = (", ".join(available[:25]) + ("..." if len(available) > 25 else "")) if available else "unknown"
    raise RuntimeError(
        "No configured Gemini model id was found for your API key.\n"
        f"Tried: {tried}\n"
        "Available models (preview): "
        f"{available_preview}\n"
        "Set `GEMINI_MODEL` in `ResumeATS/.env` to one of the available ids and restart."
    ) from last_err

@st.cache_data()
def get_gemini_response_keywords(input, pdf_content, prompt):
    @st.cache_data()
    def list_available_models():
        models = genai.list_models()
        return [getattr(m, "name", str(m)) for m in models]

    last_err = None
    for model_name in MODEL_CANDIDATES:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content([input, pdf_content, prompt])
            return json.loads(response.text[8:-4])
        except NotFound as e:
            last_err = e
            continue

    available = []
    try:
        available = list_available_models()
    except Exception:
        available = []

    tried = ", ".join(MODEL_CANDIDATES)
    available_preview = (", ".join(available[:25]) + ("..." if len(available) > 25 else "")) if available else "unknown"
    raise RuntimeError(
        "No configured Gemini model id was found for your API key.\n"
        f"Tried: {tried}\n"
        "Available models (preview): "
        f"{available_preview}\n"
        "Set `GEMINI_MODEL` in `ResumeATS/.env` to one of the available ids and restart."
    ) from last_err

@st.cache_data()
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        # Extract text from PDF using PyPDF2
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="ATS Resume Scanner")
st.header("Application Tracking System")
input_text = st.text_area("Job Description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume(PDF)...", type=["pdf"])

if 'resume' not in st.session_state:
    st.session_state.resume = None

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")
    st.session_state.resume = uploaded_file

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    submit1 = st.button("Tell Me About the Resume")

with col2:
    submit2 = st.button("Get Keywords")

with col3:
    submit3 = st.button("Percentage match")

input_prompt1 = """
 You are an experienced Technical Human Resource Manager, your task is to review the provided resume against the job description. 
 Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt2 = """
As an expert ATS (Applicant Tracking System) scanner with an in-depth understanding of AI and ATS functionality, 
your task is to evaluate a resume against a provided job description. Please identify the specific skills and keywords 
necessary to maximize the impact of the resume and provide response in json format as {Technical Skills:[], Analytical Skills:[], Soft Skills:[]}.

Note: Please do not make up the answer, only answer from the job description provided.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality, 
your task is to evaluate the resume against the provided job description. Give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if st.session_state.resume is not None:
        if not API_KEY:
            st.error("Missing Gemini API key. Set `GOOGLE_API_KEY` or `API_KEY` in `ResumeATS/.env` and restart this app.")
        else:
            try:
                pdf_content = input_pdf_setup(st.session_state.resume)
                response = get_gemini_response(input_prompt1, pdf_content, input_text)
                st.subheader("The Response is")
                st.write(response)
            except Exception as e:
                st.error(f"Gemini model error: {e}")
    else:
        st.write("Please upload the resume")

elif submit2:
    if st.session_state.resume is not None:
        if not API_KEY:
            st.error("Missing Gemini API key. Set `GOOGLE_API_KEY` or `API_KEY` in `ResumeATS/.env` and restart this app.")
        else:
            try:
                pdf_content = input_pdf_setup(st.session_state.resume)
                response = get_gemini_response_keywords(input_prompt2, pdf_content, input_text)
                st.subheader("Skills are:")
                if response is not None:
                    st.write(f"Technical Skills: {', '.join(response['Technical Skills'])}.")
                    st.write(f"Analytical Skills: {', '.join(response['Analytical Skills'])}.")
                    st.write(f"Soft Skills: {', '.join(response['Soft Skills'])}.")
            except Exception as e:
                st.error(f"Gemini model error: {e}")
    else:
        st.write("Please upload the resume")

elif submit3:
    if st.session_state.resume is not None:
        if not API_KEY:
            st.error("Missing Gemini API key. Set `GOOGLE_API_KEY` or `API_KEY` in `ResumeATS/.env` and restart this app.")
        else:
            try:
                pdf_content = input_pdf_setup(st.session_state.resume)
                response = get_gemini_response(input_prompt3, pdf_content, input_text)
                st.subheader("The Response is")
                st.write(response)
            except Exception as e:
                st.error(f"Gemini model error: {e}")
    else:
        st.write("Please upload the resume")
