import requests
import config
import re

class OllamaLLM:
    def __init__(self, host):
        self.host = host
        self.model = config.OLLAMA_MODEL
    
    def invoke(self, prompt):
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": config.LLM_TEMPERATURE,
                "top_p": config.LLM_TOP_P,
                "num_predict": config.LLM_NUM_PREDICT
            }
        )
        return type('Response', (), {'content': response.json()['response']})()

def get_llm():

    try: 
        response = requests.get(f"{config.OLLAMA_HOST}/api/tags")
        if response.status_code != 200:
            raise Exception("Cannot connect to Ollama server")
    except Exception as e:
        raise ValueError(f"Cannot reach Ollama at {config.OLLAMA_HOST}: {str(e)}")

    return OllamaLLM(config.OLLAMA_HOST)


def convert_latex_delimiters(text):
    text = text.replace(r'\[', '$$')
    text = text.replace('\\[', '$$')
    text = text.replace(r'\]', '$$')
    text = text.replace('\\]', '$$')
    text = text.replace(r'\(', '$')
    text = text.replace('\\(', '$')
    text = text.replace(r'\)', '$')
    text = text.replace('\\)', '$')
    text = text.replace(r'\ [', '$$')
    text = text.replace('\\ [', '$$')
    text = text.replace(r'\ ]', '$$')
    text = text.replace('\\ ]', '$$')
    text = text.replace(r'\ (', '$')
    text = text.replace('\\ (', '$')
    text = text.replace(r'\ )', '$')
    text = text.replace('\\)', '$')

    return text



def generate_chatbot_response(question, relevant_chunks, llm=None):
    if llm is None:
        llm = get_llm()
    
    # context = "\n\n---\n\n".join([
    #     f"[From {chunk['document_name']}, chunk {chunk['chunk_index']}]\n{chunk['text']}"
    #     for chunk in relevant_chunks[:5]
    # ])

    context_parts = []

    # Add lecture/exercise chunks
    if isinstance(relevant_chunks, dict):
        lecture_exercise = relevant_chunks.get('lecture_exercise', [])
        forum = relevant_chunks.get('forum', [])
        all_chunks = lecture_exercise + forum
    else:
        all_chunks = relevant_chunks

    for chunk in all_chunks[:5]:
        context_parts.append(
            f"[From {chunk['document_name']}, chunk {chunk['chunk_index']}]\n{chunk['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)
    
    prompt =   f"""You are a helpful university tutor for a decision and risk course for university undergraduates.

                Answer the following question ONLY using the notation and information provided in the context from course materials. 
                If the context doesn't contain enough information to answer the question, say so honestly.
                Be concise and precise in your answer.
                
                Provide step-by-step working and reasoning only. Do not include a final boxed answer or conclusion statement at the end.
                
                Context from course materials:
                {context}

                QUESTION: {question}
                """

    response = llm.invoke(prompt).content
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
        llm_response = f"Error generating response: {str(e)}"
    
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
