# app_final_navbar.py — Complete Career Guidance App with Horizontal Navbar
import os, json, hashlib, tempfile
from pathlib import Path
import streamlit as st
from utils import speak_local, stop_speaking, listen_once_browser,career_ai_reply
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Optional AI / TTS imports
try:
    import openai
except:
    openai = None
try:
    import pyttsx3
except:
    pyttsx3 = None
try:
    import speech_recognition as sr
except:
    sr = None
try:
    import docx
except:
    docx = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# DOMAINS / ROLES / SKILLS
# -----------------------------
DOMAINS = {
    "Data Science": [
        {"role": "Data Analyst", "skills": ["Python", "SQL", "Pandas", "Tableau"], "trend": "High", "avg": "3–6 LPA"},
        {"role": "Machine Learning Engineer", "skills": ["Python", "ML", "TensorFlow", "Pandas"], "trend": "High", "avg": "6–15 LPA"},
        {"role": "Data Scientist", "skills": ["ML", "Statistics", "Python", "NLP"], "trend": "High", "avg": "6–20 LPA"}
    ],

    "Web Development": [
        {"role": "Frontend Developer", "skills": ["HTML", "CSS", "JavaScript", "React"], "trend": "High", "avg": "3–7 LPA"},
        {"role": "Backend Developer", "skills": ["Node.js", "Django", "APIs", "Databases"], "trend": "High", "avg": "4–10 LPA"},
        {"role": "Full Stack Developer", "skills": ["Node.js", "React", "Databases"], "trend": "High", "avg": "4–12 LPA"}
    ],

    "Cloud": [
        {"role": "Cloud Engineer", "skills": ["AWS", "Docker", "Kubernetes"], "trend": "High", "avg": "5–14 LPA"},
        {"role": "DevOps Engineer", "skills": ["CI/CD", "Docker", "Linux"], "trend": "High", "avg": "6–16 LPA"}
    ],

    "Cybersecurity": [
        {"role": "Security Analyst", "skills": ["Networking", "Python", "Pentesting"], "trend": "High", "avg": "4–12 LPA"},
        {"role": "Ethical Hacker", "skills": ["Kali Linux", "BurpSuite", "Web Pentesting"], "trend": "High", "avg": "4–15 LPA"}
    ],

    "Mechanical": [
        {"role": "Mechanical Design Engineer", "skills": ["CAD", "SolidWorks", "Design"], "trend": "Stable", "avg": "3–8 LPA"},
        {"role": "Manufacturing Engineer", "skills": ["Lean", "Automation", "Quality Control"], "trend": "Stable", "avg": "3–7 LPA"}
    ],

    "Finance": [
        {"role": "Financial Analyst", "skills": ["Excel", "Financial Modeling", "Valuation"], "trend": "Stable", "avg": "4–12 LPA"},
        {"role": "Investment Banking Analyst", "skills": ["Valuation", "Pitchbooks", "Excel"], "trend": "High", "avg": "8–25 LPA"}
    ],

    "Marketing": [
        {"role": "Digital Marketer", "skills": ["SEO", "Analytics", "Content"], "trend": "High", "avg": "3–8 LPA"},
        {"role": "SEO Specialist", "skills": ["SEO", "SEM", "Analytics"], "trend": "High", "avg": "3–7 LPA"}
    ],

    "Artificial Intelligence": [
        {"role": "AI Engineer", "skills": ["Python", "Deep Learning", "NLP"], "trend": "High", "avg": "6–18 LPA"},
        {"role": "NLP Engineer", "skills": ["Transformers", "SpaCy", "LLMs"], "trend": "High", "avg": "6–16 LPA"}
    ],

    "Mobile App Development": [
        {"role": "Android Developer", "skills": ["Kotlin", "Java", "Firebase"], "trend": "High", "avg": "3–10 LPA"},
        {"role": "iOS Developer", "skills": ["Swift", "Xcode"], "trend": "High", "avg": "4–12 LPA"},
        {"role": "Flutter Developer", "skills": ["Dart", "Flutter"], "trend": "High", "avg": "3–9 LPA"}
    ],

    "UI/UX": [
        {"role": "UI Designer", "skills": ["Figma", "Wireframing", "Prototyping"], "trend": "High", "avg": "3–7 LPA"},
        {"role": "UX Researcher", "skills": ["User Research", "Personas", "Usability Testing"], "trend": "High", "avg": "4–10 LPA"}
    ],

    "Game Development": [
        {"role": "Game Developer", "skills": ["Unity", "C#", "Game Physics"], "trend": "High", "avg": "3–10 LPA"},
        {"role": "Game Designer", "skills": ["Level Design", "3D Modeling"], "trend": "Medium", "avg": "3–8 LPA"}
    ],

    "IoT": [
        {"role": "IoT Engineer", "skills": ["Microcontrollers", "Sensors", "Python"], "trend": "High", "avg": "4–12 LPA"},
        {"role": "Embedded Engineer", "skills": ["C", "PCB Design", "RTOS"], "trend": "High", "avg": "3–10 LPA"}
    ],

    "Human Resources": [
        {"role": "HR Executive", "skills": ["Recruitment", "Payroll", "Onboarding"], "trend": "Stable", "avg": "3–6 LPA"},
        {"role": "Talent Acquisition Specialist", "skills": ["Sourcing", "ATS", "Interviewing"], "trend": "High", "avg": "3–7 LPA"}
    ],

    "Civil Engineering": [
        {"role": "Site Engineer", "skills": ["AutoCAD", "Construction", "Estimation"], "trend": "Stable", "avg": "3–7 LPA"},
        {"role": "Structural Engineer", "skills": ["STAAD Pro", "Analysis"], "trend": "Medium", "avg": "4–10 LPA"}
    ],

    "Healthcare": [
        {"role": "Health Data Analyst", "skills": ["Python", "Healthcare Data", "SQL"], "trend": "High", "avg": "4–10 LPA"},
        {"role": "Medical Coder", "skills": ["ICD-10", "Anatomy", "Coding"], "trend": "High", "avg": "2–6 LPA"}
    ]
}
#DATA HELPERS
# -----------------------------
DATA_FILE = Path(__file__).parent / "data.json"

def ensure_data_file():
    if not Path(DATA_FILE).exists():
        with open(DATA_FILE, "w") as f:
            json.dump({"users": {}}, f)

def load_data():
    ensure_data_file()
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# -----------------------------
# THEME
# -----------------------------
def set_theme(theme_choice="Gradient"):
    if theme_choice == "Light":
        bg = "#e3a9a8"       # Soft light background
        text = "#2C3E50"     # Dark charcoal text
    elif theme_choice == "Dark":
        bg = "#1F2937"       # Darker slate/charcoal background (more modern than #111827)
        text = "#FFCBA4"     # Slight off-white text (softer than pure white)
    else:  # Gradient
        bg = "linear-gradient(120deg, #00B4DB 0%,#FCE38A 100%)"   
        text = "#ffffff"

    css = f'''
    <style>
    .stApp {{
        background: {bg};
        color: {text};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .stButton>button {{
    background-color: #ffffff !important;   /* Change this for button background */
    color: #000000 !important;             /* Change this for button text */
    border-radius: 6px;
    padding: 0.6em 1.2em;
    font-size: 16px;
    }}
    .card {{
        background: rgba(255,255,255,0.03);
        padding: 1rem;
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    }}
    .chat-box {{
        background: rgba(255,255,255,0.08);
        padding: 0.75rem;
        border-radius: 10px;
        margin-bottom: 6px;
    }}
    input, textarea {{ background: #dbc323 !important; color: #1A1A1A !important; }}
    </style>
    '''
    st.markdown(css, unsafe_allow_html=True)

# ---------------------------------------------------
# FIXED + ENHANCED OPENAI CHAT
# ---------------------------------------------------
def long_ai_reply(user_text):
    prompt = f"""
You are a friendly assistant. Give detailed helpful answers.
User: {user_text}
Reply in 5–8 sentences, complete and natural.
"""

    ans = openai_chat(prompt)
    return ans


# -----------------------------
# AI / TTS
# -----------------------------
def openai_chat(prompt: str) -> str:
    if not openai or not OPENAI_API_KEY:
        return "(AI not configured)"
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role":"system","content":"You are a helpful career guidance assistant."},
                {"role":"user","content":prompt}
            ],
            temperature=0.2
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"(OpenAI error: {e})"

# -----------------------------
# SESSION STATE INIT
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "data" not in st.session_state:
    st.session_state.data = {"users": {}}
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# -----------------------------
# HORIZONTAL NAVBAR
# -----------------------------
pages = ["Home","Register","Login","Dashboard","Roles & Skills","Resume","Voice Assistant"]
cols = st.columns(len(pages))
for i, p in enumerate(pages):
    if cols[i].button(p):
        st.session_state.page = p
        st.rerun()

# -----------------------------
# THEME SELECTOR
# -----------------------------
theme_choice = st.selectbox(
    "Select Theme", ["Light","Dark","Gradient"], index=["Light","Dark","Gradient"].index(st.session_state.theme)
)
st.session_state.theme = theme_choice
set_theme(theme_choice)

# -----------------------------
# HOME PAGE
# -----------------------------
if st.session_state.page == "Home":
    # Title (rendered as HTML)
    st.markdown("<h1 style='text-align:center; margin-bottom: 8px;'>🌟 CAREER GUIDANCE APP</h1>", unsafe_allow_html=True)

    # Two column layout
    col1, col2 = st.columns([1, 1])

    with col1:
        # Use container width so image scales nicely
        st.image(
            "https://as1.ftcdn.net/jpg/02/19/68/94/1000_F_219689405_Czua1p4ZoT3heknhfMGRQmTMBDGQGQBI.jpg",width=800)

    with col2:
        # Make sure this string has no leading spaces (they create code blocks)
        about_html = """
        <div style="font-size:18px; line-height:1.5; color:#a83305;">
            <strong>About Us:</strong><br>
            This app helps you explore domains, roles, skills, and career insights.<br>
            Use AI guidance to match your skills to roles or roles to required skills.<br>
            Evaluate your resume for ATS compatibility and interact using a built-in voice assistant.
        </div>
        <div style="margin-top:18px; font-size:15px; font-weight:600; color:#121111;">
            ⭐ Register → Login → Dashboard → Role & Skills → Analyze Resume → AI Chatbot
        </div>
        """
        st.markdown(about_html, unsafe_allow_html=True)

    # Small spacer
    st.markdown("<hr/>", unsafe_allow_html=True)


# -----------------------------
# REGISTER PAGE
# -----------------------------
elif st.session_state.page == "Register":
    st.header("🔐 Register")
    username = st.text_input("Username", key="reg_user")
    password = st.text_input("Password", type="password", key="reg_pwd")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save",key="register_save_btn"):
            data = load_data()
            if username.strip() == "":
                st.error("Enter a username")
            elif username in data['users']:
                st.warning("User already registered. Please login.")
            else:
                data['users'][username] = {"password": hash_pw(password), "profile": {}}
                save_data(data)
                st.session_state.data = data
                st.success("Registered! You can proceed to Login.")

    with col2:
        if st.button("Next",key="register_next_btn"):
            if username in st.session_state.data['users']:
                st.session_state.user = username
                st.session_state.page = "Login"
                st.rerun()
            else:
                st.warning("Please register first.")

# -----------------------------
# LOGIN PAGE
# -----------------------------
elif st.session_state.page == "Login":
    st.header("🔑 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pwd")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login",key = "login_btn"):
            data = load_data()
            st.session_state.data = data
            if username in data['users'] and data['users'][username]['password'] == hash_pw(password):
                st.session_state.user = username
                st.success("Login successful!")
            else:
                st.error("Invalid credentials")

    with col2:
        if st.button("Next",key="login_next_btn"):
            if "user" in st.session_state:
                st.session_state.page = "Dashboard"
                st.rerun()
            else:
                st.warning("Please login first.")

    if st.button("Previous"):
        st.session_state.page = "Register"
        st.rerun()

# -----------------------------
# DASHBOARD PAGE
# -----------------------------
elif st.session_state.page == "Dashboard":
    st.header("📋 Dashboard")
    if "user" not in st.session_state:
        st.warning("Please login first")
        st.stop()

    user = st.session_state.user
    data = load_data()
    profile = data['users'][user].get('profile', {})

    name = st.text_input("Full Name", value=profile.get("name",""))
    edu = st.selectbox("Education", ["High School","Diploma","Bachelors","Masters","PhD"], index=1)
    domain = st.selectbox("Interested Domain", list(DOMAINS.keys()), index=0)
    practical = st.slider("Practical Knowledge (1-10)", 1, 10, 5)
    theoretical = st.slider("Theoretical Knowledge (1-10)", 1, 10, 5)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save",key="dashboard_save_btn"):
            profile.update({"name":name,"education":edu,"domain":domain,
                            "practical":practical,"theoretical":theoretical})
            data['users'][user]['profile'] = profile
            save_data(data)
            st.session_state.data = data
            st.success("Dashboard info saved!")

    with col2:
        if st.button("Next", key="dashboard_next_btn"):
            if profile.get("name") and profile.get("domain"):
                st.session_state.page = "Roles & Skills"
                st.rerun()
            else:
                st.warning("Please complete your dashboard before proceeding.")

    if st.button("Previous"):
        st.session_state.page = "Login"
        st.rerun()

# -----------------------------
# ROLES & SKILLS PAGE
# -----------------------------
elif st.session_state.page == "Roles & Skills":
    st.header("💼 Roles & Skills")
    if "user" not in st.session_state:
        st.warning("Please login first")
        st.stop()
    user = st.session_state.user
    profile = st.session_state.data['users'][user].get('profile', {})
    domain = profile.get("domain")
    if not domain:
        st.warning("Please complete Dashboard first")
        st.stop()

    mapping_mode = st.radio("Mapping Mode", ["Role → Skills","Skill → Roles"])

    if mapping_mode == "Role → Skills":
        roles = [r['role'] for r in DOMAINS[domain]]
        selected_roles = st.multiselect("Select Role(s)", roles)
        for r in DOMAINS[domain]:
            if r['role'] in selected_roles:
                st.markdown(f"**Role:** {r['role']}")
                st.markdown(f"- Skills: {','.join(r['skills'])}")
                st.markdown(f"- Trend: {r['trend']} | Avg Package: {r['avg']}")
    else:
        all_skills = sorted({s for r in DOMAINS[domain] for s in r['skills']})
        selected_skills = st.multiselect("Select Skill(s)", all_skills)
        st.markdown("**Suggested Courses & Resources:**")
        for skill in selected_skills:
            st.markdown(f"- {skill}: [Learn here](https://www.google.com/search?q={skill}+course)")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Next", key="roles_next_btn"):
            st.session_state.page = "Resume"
            st.rerun()
    with col2:
        if st.button("Previous", key="roles_prev_btn"):
            st.session_state.page = "Dashboard"
            st.rerun()

# -----------------------------
# RESUME PAGE
# -----------------------------
elif st.session_state.page == "Resume":
    st.header("📄 Resume Checker")
    if "user" not in st.session_state:
        st.warning("Please login first")
        st.stop()

    user = st.session_state.user
    profile = st.session_state.data['users'][user].get('profile', {})
    domain = profile.get("domain")
    if not domain:
        st.warning("Please complete Dashboard first")
        st.stop()

    resume_text = st.text_area("Paste your resume text here")
    role_options = ["--Select--"] + [r["role"] for r in DOMAINS[domain]]
    role = st.selectbox("Select Role for ATS Check", role_options)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Check ATS" ,key="ats_check_btn"):
            if role == "--Select--":
                st.warning("Please select a role")
            else:
                selected_role = next(r for r in DOMAINS[domain] if r['role']==role)
                keywords = selected_role['skills']
                present = [k for k in keywords if k.lower() in resume_text.lower()]
                missing = [k for k in keywords if k.lower() not in resume_text.lower()]
                score = int(len(present)/max(1,len(keywords))*100)
                st.markdown(f"### ✔ ATS Score: **{score}/100**")
                st.markdown(f"- Matched Keywords: {', '.join(present) if present else 'None'}")
                st.markdown(f"- Missing Keywords: {', '.join(missing) if missing else 'None'}")

    with col2:
        if st.button("Previous", key="resume_prev_btn"):
            st.session_state.page = "Roles & Skills"
            st.rerun()

elif st.session_state.page == "Voice Assistant":
    if "va_conversation" not in st.session_state:
        st.session_state.va_conversation = [ ]

    st.header("🎤 Smart Voice Assistant")

    # Browser mic capture + AssemblyAI transcription
    user_text = listen_once_browser()

    if user_text:
        st.session_state.va_conversation.append(("You", user_text))

        st.info("🤖 Generating assistant reply…")
        reply = career_ai_reply(user_text)
        st.session_state.va_conversation.append(("Assistant", reply))

        st.info("🗣️ Speaking reply…")
        speak_local(reply)
    else:
        st.warning("🎤 No speech detected or transcription failed. Try again.")

    st.markdown("---")
    st.subheader("💬 Conversation")
    for speaker, text in st.session_state.va_conversation:
        st.markdown(f"**{speaker}:** {text}")


