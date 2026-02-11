import config
from langchain_ollama import OllamaLLM
import os
from langchain_huggingface import HuggingFaceEndpoint

def get_llm():
    api_key = os.getenv("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")

    if not api_key:
            raise ValueError("HUGGINGFACE_API_KEY environment variable not set")
        
    return HuggingFaceEndpoint(
        repo_id=config.HF_MODEL,
        huggingfacehub_api_token=api_key,
        task="text-generation",
        do_sample=True,
        max_new_tokens=config.LLM_NUM_PREDICT,
        temperature=config.LLM_TEMPERATURE,
        top_p=config.LLM_TOP_P
    )

import re


def convert_latex_delimiters(text):
    text = text.replace('\\[', '$$')
    text = text.replace('\\]', '$$')
    text = text.replace('\\(', '$')
    text = text.replace('\\)', '$')
    text = text.replace('\\ [', '$$')
    text = text.replace('\\ ]', '$$')
    text = text.replace('\\ (', '$')
    text = text.replace('\\ )', '$')
    return text



def generate_chatbot_response(question, relevant_chunks, llm=None):
    if llm is None:
        llm = get_llm()
    
    context = "\n\n---\n\n".join([
        f"[From {chunk['lecture']}, chunk {chunk['chunk_index']}]\n{chunk['text']}"
        for chunk in relevant_chunks[:5]
    ])
    
    prompt =   f"""You are a helpful university tutor for a decision and risk course for university undergraduates.

                Answer the following question ONLY using the notation and information provided in the context from course materials. 
                If the context doesn't contain enough information to answer the question, say so honestly.
                Be concise and precise in your answer.
                
                Context from course materials:
                {context}

                QUESTION: {question}
                """

    response = llm.invoke(prompt).strip()
    # response = convert_latex_delimiters(response)

    return response



def process_question_with_response(classification_result):
    classification = classification_result['classification']
    question = classification_result['question']
    
    # Handle admin/exam redirect
    if classification == "Redirect to lecturer":
        return {
            'question': question,
            'classification': classification,
            'response': config.REDIRECT_MESSAGE,
            'sources': [],
            'num_sources': 0
        }
    
    # Handle irrelevant questions
    if classification == "Irrelevant":
        return {
            'question': question,
            'classification': classification,
            'response': config.IRRELEVANT_MESSAGE,
            'sources': [],
            'num_sources': 0
        }
    
    # Handle relevant questions with chatbot response
    relevant_chunks = classification_result['semantic_results']['relevant_chunks']
    
    try:
        llm = get_llm()
        llm_response = generate_chatbot_response(question, relevant_chunks, llm)
    except Exception as e:
        llm_response = f"Error generating response: {str(e)}\nMake sure Ollama is running with: ollama serve"
    
    sources = [
        {
            'lecture': chunk['lecture'],
            'chunk_index': chunk['chunk_index'],
            'similarity_score': chunk['similarity_score'],
            'text_preview': chunk['text'][:100] + "..."
        }
        for chunk in relevant_chunks[:5]
    ]
    
    return {
        'question': question,
        'classification': classification,
        'response': llm_response,
        'sources': sources,
        'num_sources': len(relevant_chunks),
        'confidence': classification_result['confidence']
    }
