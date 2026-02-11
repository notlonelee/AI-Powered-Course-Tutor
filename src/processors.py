import re
import string
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from langchain_text_splitters import RecursiveCharacterTextSplitter
import config


# ============================================================
# TEXT PREPROCESSING
# ============================================================

def preprocess_text(text):
    # Remove section headers and page numbers
    text = re.sub(r'^\s*\d+(\.\d+)*\s+|\s+\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove "Last updated" lines
    text = re.sub(r'Last updated.*?\n', '', text, flags=re.IGNORECASE)
    
    # Remove dots
    text = re.sub(r'\.(\s*\.)+', ' ', text)
    
    # Clean excessive spacing
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([,.;:])', r'\1', text)
    
    return text.strip()


# ============================================================
# LECTURE CHUNKING
# ============================================================

def chunk_lectures_by_section(lecture_texts, chunk_size=None):
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE

    all_chunks = []
    
    for lecture_name, text in lecture_texts.items():
        section_pattern = r'(\\subsection\{[^}]+\}|\\section\{[^}]+\})'
        sections = re.split(section_pattern, text)
        
        current_section_title = "Preamble"
        current_content = ""
        chunk_index = 0
        
        for part in sections:
            if re.match(section_pattern, part):
                # Save previous chunk
                if current_content.strip():
                    all_chunks.append({
                        'chunk_id': f"{lecture_name}_{chunk_index}",
                        'document_name': lecture_name,
                        'document_type': 'lecture',
                        'chunk_index': chunk_index,
                        'section_title': current_section_title,
                        'text': current_content.strip(),
                        'char_length': len(current_content)
                    })
                    chunk_index += 1
                
                current_section_title = part
                current_content = ""
            else:
                current_content += part
        
        # Save last chunk
        if current_content.strip():
            all_chunks.append({
                'chunk_id': f"{lecture_name}_{chunk_index}",
                'document_name': lecture_name,
                'document_type': 'lecture',
                'chunk_index': chunk_index,
                'section_title': current_section_title,
                'text': current_content.strip(),
                'char_length': len(current_content)
            })
    
    # Split large chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "$$", "\n", ". ", " "]
    )
    
    final_chunks = []
    for chunk in all_chunks:
        if chunk['char_length'] > chunk_size:
            sub_chunks = splitter.split_text(chunk['text'])
            for j, sub_chunk in enumerate(sub_chunks):
                final_chunks.append({
                    'chunk_id': f"{chunk['chunk_id']}_sub{j}",
                    'document_name': chunk['document_name'],
                    'document_type': chunk['document_type'],
                    'chunk_index': chunk['chunk_index'],
                    'section_title': chunk['section_title'],
                    'text': sub_chunk,
                    'char_length': len(sub_chunk)
                })
        else:
            final_chunks.append(chunk)
    
    return final_chunks


def chunk_exercises_by_question(exercise_texts, chunk_size=None):
    if chunk_size is None:
        chunk_size = config.CHUNK_SIZE

    all_chunks = []
    
    for exercise_name, text in exercise_texts.items():
        # Split by questions
        question_pattern = r'\\(?:sub)?section\*\{Question\s+(\d+)\}'
        questions = re.split(question_pattern, text)
        
        for i in range(1, len(questions), 2):
            if i + 1 < len(questions):
                question_num = questions[i]
                question_content = questions[i + 1]
                
                # Extract part labels
                part_pattern = r'\\item\s*\[\(?([a-z]|[ivxlcdm]+)\)?\]'
                parts = re.findall(part_pattern, question_content, re.IGNORECASE)
                
                chunk = {
                    'chunk_id': f"{exercise_name}_Q{question_num}",
                    'document_name': exercise_name,
                    'document_type': 'exercise',
                    'question_num': int(question_num),
                    'section_title': f"Question {question_num}",
                    'text': question_content.strip(),
                    'char_length': len(question_content),
                    'parts': parts
                }
                all_chunks.append(chunk)
    
    # Split large chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0,
        separators=["\n\n", "$$", "\n", ". ", " "]
    )
    
    final_chunks = []
    for chunk in all_chunks:
        if chunk['char_length'] > chunk_size:
            sub_chunks = splitter.split_text(chunk['text'])
            for j, sub_chunk in enumerate(sub_chunks):
                final_chunks.append({
                    'chunk_id': f"{chunk['chunk_id']}_sub{j}",
                    'document_name': chunk['document_name'],
                    'document_type': chunk['document_type'],
                    'question_num': chunk['question_num'],
                    'section_title': chunk['section_title'],
                    'text': sub_chunk,
                    'char_length': len(sub_chunk),
                    'parts': chunk['parts']
                })
        else:
            final_chunks.append(chunk)
    
    return final_chunks


# ============================================================
# KEYWORD EXTRACTION
# ============================================================

def extract_keywords(text, score_threshold=0.025, min_length=3):
    vectorizer = TfidfVectorizer(
        stop_words=list(ENGLISH_STOP_WORDS),
        min_df=1, max_df=1, ngram_range=(1, 3),
        lowercase=True
    )
    
    X = vectorizer.fit_transform([text])
    mean_tfidf = np.asarray(X.mean(axis=0)).ravel()
    feature_names = vectorizer.get_feature_names_out()
    
    keywords_with_scores = []
    for word, score in zip(feature_names, mean_tfidf):
        if (score < score_threshold or len(word) < min_length or 
            word in config.MATH_NOISE or any(char in config.GREEK_CHARS for char in word) or
            any(char.isdigit() for char in word) or '_' in word):
            continue
        keywords_with_scores.append((word, score))
    
    return sorted(keywords_with_scores, key=lambda x: x[1], reverse=True)


def build_master_keywords(texts):
    master_keywords = set()
    for text in texts:
        master_keywords.update(word for word, _ in extract_keywords(text))
    print(f"✓ Completed processing keywords from all lectures")
    return sorted(master_keywords)


def filter_question(question, master_keywords, min_keywords=2):
    question_lower = question.lower()
    words = {word.strip(string.punctuation) for word in question_lower.split()}
    
    keywords_found = [w for w in words if w in master_keywords and w not in ENGLISH_STOP_WORDS]
    is_relevant = len(keywords_found) >= min_keywords
    
    return is_relevant, keywords_found, len(keywords_found)
