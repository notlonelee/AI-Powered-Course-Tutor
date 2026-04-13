# ============================================================
# STREAMLIT APP
# ============================================================

import sys 
from pathlib import Path

import streamlit as st
from course_tutor import CourseTutor
from logger import SheetLogger
import time
from llm_handler import convert_latex_delimiters
from classifier import classify_question_complete

# Page configuration
st.set_page_config(
    page_title="AI STAT 11",
    page_icon="📚",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .response-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        color: black;
    }
    .top-source-box {
        background-color: #e8f4f8;
        padding: 12px;
        border-radius: 8px;
        margin-top: 10px;
        color: black;
        font-size: 14px;
    }
    .redirect-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        color: black;
    }
    .irrelevant-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        color: black;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize tutor
@st.cache_resource
def initialize_tutor():
    return CourseTutor()


# Initialize Google Sheets logger
@st.cache_resource
def initialize_logger():
    try:
        sheet_id = st.secrets.get("GOOGLE_SHEET_ID")
        if not sheet_id:
            st.warning("⚠️ GOOGLE_SHEET_ID not found in secrets")
            return None
        
        logger = SheetLogger(sheet_id)
        if logger.worksheet:
            return logger
        else:
            return None
    except Exception as e:
        st.warning(f"⚠️ Google Sheets connection failed: {e}")
        return None


# ============================================================
# MAIN INTERFACE
# ============================================================

st.title("📚 STAT11's AI-Powered Course Tutor")
st.markdown("Ask questions about the course and receive answers based on lecture notes and exercise sheets.")

# Initialize tutor and logger
tutor = initialize_tutor()
logger = initialize_logger()

# ============================================================
# SINGLE QUESTION TEST
# ============================================================

with st.form("question_form"):
    question = st.text_area(
    "Enter your question here:",
    height=100,
    placeholder="e.g. For example 3 in week 7, why can we assume the prior probability equals to 0.03?"
    )
    submitted = st.form_submit_button("Submit Question", use_container_width=True)

if submitted:
    if question.strip():
        with st.spinner("Processing question..."):
            result = tutor.process_question(question)
            
            classification_result = classify_question_complete(
                question,
                tutor.master_keywords,
                tutor.chunks_with_embeddings
            )
            confidence = classification_result['confidence']

            response_with_context = result['response']
            response_with_context = convert_latex_delimiters(response_with_context)

            response_without_context = tutor.process_question_no_context(question)["response"]
            response_without_context = convert_latex_delimiters(response_without_context)

        st.divider()
        
        # Display response
        if result['classification'] == "Redirect to lecturer":
            st.markdown(f'<div class="redirect-box"><strong>⚠️ Please redirect to lecturer</strong><br/>{result["response"]}</div>', 
                       unsafe_allow_html=True)
            
            # Log to Google Sheets
            if logger:
                logger.log_interaction(
                    question=question,
                    classification=result['classification'],
                    answer_with_context=result['response'],
                    answer_without_context="" 
                )

        elif result['classification'] == "Irrelevant":
            st.markdown(f'<div class="irrelevant-box"><strong>❌ Question Out of Syllabus</strong><br/>{result["response"]}</div>', 
                       unsafe_allow_html=True)
            
            # Log to Google Sheets
            if logger:
                logger.log_interaction(
                    question=question,
                    classification=result['classification'],
                    answer_with_context=result['response'],
                    answer_without_context="" 
                )
            
        else:
            response_with_context = result['response']
            result_no_context = tutor.process_question_no_context(question)
            response_without_context = result_no_context["response"]
           
            st.subheader("Response")
            # response_with_context = convert_latex_delimiters(response_with_context)
            # st.markdown(response_with_context)

            response_before_conversion = response_with_context

            response_with_context = convert_latex_delimiters(response_with_context)
            st.markdown(response_with_context)

            # # DEBUG: Show raw response text (both versions)
            # with st.expander("🔍 DEBUG: Raw Response Text"):
            #     st.write("**Before convert_latex_delimiters():**")
            #     st.code(response_before_conversion, language="text")
                
            #     st.write("\n**After convert_latex_delimiters():**")
            #     st.code(response_with_context, language="text")

            
            # Display confidence 
            if confidence >= 0.6:
                color = "#28a745"
                label = "🟢 High Confidence"
            elif confidence >= 0.4:
                color = "#ffc107"
                label = "🟡 Medium Confidence"
            else:
                color = "#dc3545"
                label = "🔴 Low Confidence"
            
            st.markdown(f"""
                <div style="background-color: #e9ecef; border-radius: 10px; padding: 2px;">
                    <div style="background-color: {color}; width: {confidence*100}%; height: 25px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                        {confidence:.0%}
                    </div>
                </div>
                <p style="text-align: center; margin-top: 5px;"><strong>{label}</strong></p>
            """, unsafe_allow_html=True)

            # Display sources only for relevant questions
            if result['sources']:
                top_source = None
                for source in result['sources']:
                    if source.get('lecture') != 'forum.txt': 
                        top_source = source
                        break
                if top_source:
                    source_name = top_source['lecture'].replace(".txt", "")
                    st.markdown(f'<div class="top-source-box"><strong> For more information, you may want to refer to:</strong> {source_name}</div>', 
                                unsafe_allow_html=True)
            
            # Log successful response to Google Sheets
            if logger:
                logger.log_interaction(
                    question=question,
                    classification=result['classification'],
                    answer_with_context=response_with_context,
                    answer_without_context=response_without_context
                )

        st.write("")

        if st.button("Ask a new question", use_container_width=True):
            st.rerun()

        st.divider()
        st.link_button(
            "📝 Submit Feedback / Report Issues",
            url="https://forms.gle/gz1W8sRSL9pA5Kds5",
            use_container_width=True
        )

    else:
        st.warning("Please enter a question.")
