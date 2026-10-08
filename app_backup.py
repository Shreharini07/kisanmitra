import io
import json

import streamlit as st
from PIL import Image
from google import genai
from google.genai import types


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="KisanMitra",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS ONLY
# =========================================================

st.markdown("""
<style>
.stApp {
    background-color: #f5f8f3;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #123524;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #103a27, #1d6542, #3d8b5c);
    border-radius: 24px;
    padding: 42px;
    margin-bottom: 30px;
    color: white;
    box-shadow: 0 12px 35px rgba(18,53,36,0.18);
}

.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    padding: 7px 14px;
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.7px;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 18px;
}

.hero-description {
    font-size: 16px;
    line-height: 1.7;
    max-width: 720px;
    margin-top: 15px;
    color: #edf7ef;
}

/* Cards */
.card {
    background: white;
    border: 1px solid #e0e8df;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.035);
}

.card-title {
    font-size: 18px;
    font-weight: 750;
    color: #123524;
    margin-bottom: 10px;
}

.card-text {
    color: #5d6961;
    line-height: 1.7;
}

/* Summary */
.metric-card {
    background: white;
    border: 1px solid #e0e8df;
    border-radius: 18px;
    padding: 20px;
    min-height: 110px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.035);
}

.metric-label {
    font-size: 12px;
    font-weight: 700;
    color: #77827b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

.metric-value {
    font-size: 23px;
    font-weight: 800;
    color: #123524;
    margin-top: 8px;
}

/* Problems */
.problem-card {
    background: #fff8e8;
    border-left: 5px solid #dfa52f;
    border-radius: 10px;
    padding: 12px 15px;
    margin-bottom: 9px;
    color: #594719;
}

/* Actions */
.action-card {
    background: #edf8ef;
    border-left: 5px solid #3d8b5c;
    border-radius: 10px;
    padding: 12px 15px;
    margin-bottom: 9px;
    color: #294e35;
}

/* Footer */
.footer {
    text-align: center;
    color: #7b867e;
    padding-top: 30px;
    line-height: 1.8;
    font-size: 13px;
}

/* Button */
.stButton > button {
    background-color: #1d6542 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    min-height: 48px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

.stButton > button:hover {
    background-color: #12492e !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background-color: white;
    border-radius: 16px;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# GEMINI
# =========================================================

MODEL = "gemini-3.8-flash"

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM = """
You are KisanMitra, an AI agricultural assistant helping
small farmers in India understand crop health.

Analyze the uploaded crop or plant image.

Reply ONLY with valid JSON:

{
    "crop_guess": "string",
    "what_i_see": "string",
    "likely_problems": ["string"],
    "confidence": "LOW",
    "severity": "LOW",
    "first_steps": ["string"],
    "see_an_expert_if": "string"
}

Rules:

1. Identify the likely crop if possible.
2. Describe visible symptoms.
3. Give up to 3 possible problems.
4. Confidence must be LOW, MEDIUM, or HIGH.
5. Severity must be LOW, MEDIUM, or HIGH.
6. Give simple safe first steps.
7. Never provide pesticide names.
8. Never provide pesticide doses.
9. Never provide chemical application instructions.
10. If the image is not a plant, say so and set confidence to LOW.
11. If the image is unclear, say so.
12. Do not pretend to be certain.
13. Recommend an agriculture expert when appropriate.
14. Use simple language.
"""


# =========================================================
# IMAGE PREPARATION
# =========================================================

def prepare_image(uploaded_file):

    image = Image.open(uploaded_file).convert("RGB")

    image.thumbnail((1024, 1024))

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=85
    )

    return buffer.getvalue()


# =========================================================
# ANALYSIS
# =========================================================

def analyse_plant(image_bytes, language):

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type="image/jpeg"
    )

    instruction = f"""
Analyze this crop or plant image.

Return the answer in {language}.

Do not provide pesticide names,
pesticide doses, or chemical instructions.

Give safe first-step guidance.
Mention uncertainty when appropriate.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=[
            image_part,
            instruction
        ],
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM,
            temperature=0.3,
            response_mime_type="application/json"
        )
    )

    return json.loads(response.text)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        "# 🌾 KisanMitra"
    )

    st.caption(
        "AI Crop Health Assistant"
    )

    st.divider()

    st.subheader("🌐 Language")

    language = st.selectbox(
        "Choose response language",
        ["English", "Tamil"],
        label_visibility="collapsed"
    )

    st.divider()

    st.subheader("✨ Features")

    st.markdown("""
    🌱 Crop identification

    🦠 Possible disease detection

    📊 Confidence estimation

    ⚠️ Severity estimation

    👀 Symptom analysis

    💡 Safe first-step guidance
    """)

    st.divider()

    st.caption(
        "KisanMitra provides AI-based guidance only. "
        "Consult an agricultural professional for treatment decisions."
    )


# =========================================================
# HERO
# =========================================================

st.markdown(
    '<div class="hero">'
    '<div class="hero-badge">🌱 AI-POWERED AGRICULTURAL ASSISTANCE</div>'
    '<div class="hero-title">Smart Crop Health,<br>Powered by AI.</div>'
    '<div class="hero-description">'
    'Upload a photo of your crop leaf and KisanMitra will analyze '
    'visible symptoms, identify possible problems and provide '
    'safe first-step guidance.'
    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# UPLOAD
# =========================================================

st.header("📸 Analyze Your Crop")

st.write(
    "Upload a clear photo of a crop leaf or plant for AI analysis."
)

uploaded_file = st.file_uploader(
    "Upload your crop image",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)


# =========================================================
# IMAGE
# =========================================================

if uploaded_file:

    image = Image.open(uploaded_file)

    left, right = st.columns(
        [1.3, 1],
        gap="large"
    )

    with left:

        st.image(
            image,
            caption="Uploaded crop image",
            use_container_width=True
        )

    with right:

        st.markdown(
            '<div class="card">'
            '<div class="card-title">🌱 Image Ready</div>'
            '<div class="card-text">'
            'Your image is ready for analysis.<br><br>'
            '✓ Keep the leaf clearly visible<br>'
            '✓ Use good lighting<br>'
            '✓ Show the affected area clearly'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

    analyze = st.button(
        "🔍 Analyze My Crop",
        use_container_width=True
    )

else:

    st.info(
        "🌿 Upload a crop leaf image above to begin."
    )

    analyze = False


# =========================================================
# RESULTS
# =========================================================

if uploaded_file and analyze:

    with st.spinner(
        "🌾 KisanMitra is analyzing your crop..."
    ):

        try:

            image_bytes = prepare_image(
                uploaded_file
            )

            result = analyse_plant(
                image_bytes,
                language
            )

            st.divider()

            st.header("🌱 Crop Health Report")

            st.caption(
                "AI-generated analysis based on the uploaded image."
            )

            # -------------------------
            # SUMMARY
            # -------------------------

            c1, c2, c3 = st.columns(3)

            with c1:

                st.markdown(
                    '<div class="metric-card">'
                    '<div class="metric-label">🌱 Crop</div>'
                    f'<div class="metric-value">'
                    f'{result.get("crop_guess", "Unknown")}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with c2:

                st.markdown(
                    '<div class="metric-card">'
                    '<div class="metric-label">📊 Confidence</div>'
                    f'<div class="metric-value">'
                    f'{result.get("confidence", "LOW")}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            with c3:

                st.markdown(
                    '<div class="metric-card">'
                    '<div class="metric-label">⚠️ Severity</div>'
                    f'<div class="metric-value">'
                    f'{result.get("severity", "LOW")}'
                    '</div>'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.write("")

            # -------------------------
            # OBSERVATION
            # -------------------------

            st.markdown(
                '<div class="card">'
                '<div class="card-title">👀 What KisanMitra Sees</div>'
                '<div class="card-text">'
                f'{result.get("what_i_see", "No description available.")}'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            # -------------------------
            # PROBLEMS / ACTIONS
            # -------------------------

            problem_col, action_col = st.columns(2)

            with problem_col:

                st.subheader("🦠 Possible Problems")

                problems = result.get(
                    "likely_problems",
                    []
                )

                if problems:

                    for problem in problems:

                        st.markdown(
                            f'<div class="problem-card">'
                            f'⚠️ {problem}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                else:

                    st.write(
                        "No specific problem identified."
                    )

            with action_col:

                st.subheader("💡 Safe First Steps")

                steps = result.get(
                    "first_steps",
                    []
                )

                if steps:

                    for step in steps:

                        st.markdown(
                            f'<div class="action-card">'
                            f'✅ {step}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                else:

                    st.write(
                        "No specific steps available."
                    )

            # -------------------------
            # EXPERT
            # -------------------------

            st.markdown(
                '<div class="card">'
                '<div class="card-title">'
                '👨‍🌾 When Should You Consult an Expert?'
                '</div>'
                '<div class="card-text">'
                f'{result.get("see_an_expert_if", "Consult a local agriculture expert if symptoms worsen.")}'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

            # -------------------------
            # SAFETY
            # -------------------------

            st.warning(
                "⚠️ KisanMitra provides AI-based first-step "
                "guidance only. It does not provide pesticide "
                "names or doses. Consult a qualified agriculture "
                "professional before making treatment decisions."
            )

        except Exception as error:

            st.error(
                "❌ Something went wrong while analyzing the image."
            )

            st.code(str(error))


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    '<div class="footer">'
    '🌾 <b>KisanMitra</b> · AI-Powered Crop Health Assistant'
    '<br>'
    'Built with Python · Streamlit · Gemini AI'
    '<br>'
    '<small>'
    'AI-generated information should be verified with '
    'agricultural professionals.'
    '</small>'
    '</div>',
    unsafe_allow_html=True
)