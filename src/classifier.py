import re
from semantic import get_embedding, get_relevant_chunks
from processors import filter_question
import config

def find_prefilter_keywords(text, keyword_lists):
    text_lower = text.lower()
    found = []
    for keywords in keyword_lists:
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found.append(kw)
    return found


def classify_admin_exam(question):
    found_keywords = find_prefilter_keywords(question, [config.ADMIN_WORDS, config.EXAM_WORDS])
    
    if found_keywords:
        return "Redirect to lecturer", found_keywords, False
    else:
        return None, [], True


def filter_question_hybrid(question, master_keywords, chunks_with_embeddings, confidence_threshold=None):
    if confidence_threshold is None:
        confidence_threshold = config.CONFIDENCE_THRESHOLD

    # Keyword filtering
    _, keywords_found, keyword_count = filter_question(question, master_keywords, min_keywords=0)
    
    # Semantic filtering
    relevant_chunks = get_relevant_chunks(question, chunks_with_embeddings, similarity_threshold=0)
    
    top_similarity = relevant_chunks[0]['similarity_score'] if relevant_chunks else 0.0
    
    # Confidence calculation: 30% keyword + 70% semantic
    keyword_confidence = min(keyword_count / 5, 1.0)
    final_confidence = (keyword_confidence * config.OPTIMAL_K) + (top_similarity * (1-config.OPTIMAL_K))
    
    return {
        'status': '✓ ACCEPTED' if final_confidence >= confidence_threshold else '✗ REJECTED',
        'question': question,
        'keywords_found': keywords_found,
        'keyword_count': keyword_count,
        'similarity_score': round(top_similarity, 4),
        'is_relevant': final_confidence >= confidence_threshold,
        'confidence': final_confidence,
        'relevant_chunks': relevant_chunks,
        'num_relevant_chunks': len(relevant_chunks)
    }


def classify_question_complete(question, master_keywords, chunks_with_embeddings, 
                               confidence_threshold=0.50):
    # Stage 1: Pre-filter for admin/exam keywords
    admin_exam_classification, admin_exam_keywords, should_proceed = classify_admin_exam(question)
    
    if not should_proceed:
        return {
            'classification': admin_exam_classification,
            'question': question,
            'stage': 'Pre-filter (Admin/Exam Keywords)',
            'admin_exam_keywords': admin_exam_keywords,
            'semantic_results': None,
            'confidence': 1.0
        }
    
    # Stage 2: Semantic filtering with references
    semantic_result = filter_question_hybrid(question, master_keywords, chunks_with_embeddings)
    
    classification = "Relevant (Chatbot)" if semantic_result['is_relevant'] else "Irrelevant"
    
    return {
        'classification': classification,
        'question': question,
        'stage': 'Semantic Filtering',
        'admin_exam_keywords': [],
        'semantic_results': semantic_result,
        'confidence': semantic_result['confidence']
    }
