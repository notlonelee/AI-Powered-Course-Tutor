import re
from pathlib import Path
import os

# ============================================================
# FILE PATHS
# ============================================================
BASE_DIR = Path(__file__).parent.parent
LECTURES_PATH = BASE_DIR / "data" / "lectures"
EXERCISES_PATH = BASE_DIR / "data" / "exercises"

LECTURES_PATH.mkdir(parents=True, exist_ok=True)
EXERCISES_PATH.mkdir(parents=True, exist_ok=True)

# ============================================================
# KEYWORD EXTRACTION NOISE FILTERING
# ============================================================
MATH_NOISE = {
        'u', 'v', 't', 'x', 'y', 'z', 'o', 'p', 'q', 'n', 'k', 'm', 'r', 's',
        'h', 'e', 'w', 'c', 'a', 'b', 'd', 'f', 'g', 'i', 'j', 'l',
        
        'pt', 'yt', 'ut', 'xt', 'zt',
        'p_t', 'y_t', 'u_t', 'x_t', 'z_t',
        'vt', 'v_t', 'ˆut',

        'exp', 'variance', 'squared', 'zero',  'sqrt', 'rnorm', 'norm',
    }
    
GREEK_CHARS = {'σ', 'μ', 'α', 'β', 'ε', 'γ', 'ω', 'θ', 'λ', 'ρ', 'π', 'δ', 'φ'}


# ============================================================
# KEYWORDS TO REDIRECT
# ============================================================
ADMIN_WORDS = ['upload', 'recording', 'recordings', 'deadline', 'post', 'provide', 'provided', 'office hours']

EXAM_WORDS = ['examinable', 'examined', 'memorise', 'memorize', 'memorisation', 'recite', 'remember',
              'memorization', 'required', 'grasp', 'expected to', 'tested', 'statistical tables', 
              'marks', 'difficulty', 'assessed', 'formula sheet', 'calculator', 'ipac', 'exam',
              'submit', 'report', 'csv', 'r script', 'r code', 'ica', 'submission', 'task', ]


# ============================================================
# THRESHOLD
# ============================================================
# Keyword threshold
MIN_KEYWORDS = 3
# Semantic similarity threshold
SIMILARITY_THRESHOLD = 0.50
# Optimal confidence threshold
CONFIDENCE_THRESHOLD = 0.25
# Optimal k
OPTIMAL_K = 0.15


# ============================================================
# CHUNKING PARAMETERS
# ============================================================
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
CHUNK_SEPARATORS = ["\n\n", "\n", ". ", " "]


# ============================================================
# EMBEDDING MODEL
# ============================================================
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_MAX_LENGTH = 512


# ============================================================
# LLM PARAMETERS
# ============================================================
LLM_MODEL = "qwen2-math:1.5b"
HF_MODEL = "Qwen/Qwen2.5-Math-1.5B"
# HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
LLM_TEMPERATURE = 0.3
LLM_TOP_P = 0.9
LLM_NUM_PREDICT = 2048


# ============================================================
# LLM RESPONSE TEMPLATES
# ============================================================
REDIRECT_MESSAGE = ("Please redirect questions regarding the exam or adminstrative matters to the forum.")
IRRELEVANT_MESSAGE = ("This question is likely out of syllabus. If you think that is wrong, please rephrase your question and ask again, or submit it to the forum.")