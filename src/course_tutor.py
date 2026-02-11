from txt_processor import load_lecture_texts, load_exercise_texts
from processors import chunk_lectures_by_section, chunk_exercises_by_question, build_master_keywords
from semantic import generate_chunk_embeddings
from classifier import classify_question_complete
from llm_handler import process_question_with_response
import config

class CourseTutor:
    def __init__(self):
        
        # Initialize components
        print("=" * 150)
        print("INITIALIZING COURSE TUTOR")
        print("=" * 150 + "\n")
        
        # Load TXT files
        print("Loading lecture TXT files...")
        self.lecture_texts = load_lecture_texts(config.LECTURES_PATH)
        print(f"✓ Loaded {len(self.lecture_texts)} lecture files")

        print("Loading exercise TXT files...")
        self.exercise_texts = load_exercise_texts(config.EXERCISES_PATH)
        print(f"✓ Loaded {len(self.exercise_texts)} exercise files\n")
        
        # Build keyword database
        print("Building keyword database...")
        all_texts = list(self.lecture_texts.values()) + list(self.exercise_texts.values())
        self.master_keywords = build_master_keywords(all_texts)
        print(f"✓ Master keywords: {len(self.master_keywords)} unique terms\n")
        # Chunk lectures by section
        print("Chunking lectures by section...")
        self.lecture_chunks = chunk_lectures_by_section(self.lecture_texts)
        print(f"✓ Created {len(self.lecture_chunks)} lecture chunks")
        
        # Chunk exercises by question
        print("Chunking exercises by question...")
        self.exercise_chunks = chunk_exercises_by_question(self.exercise_texts)
        print(f"✓ Created {len(self.exercise_chunks)} exercise chunks")
        
        # Combine all chunks
        self.all_chunks = self.lecture_chunks + self.exercise_chunks
        print(f"✓ Total: {len(self.all_chunks)} chunks\n")
        
        # Generate embeddings
        print("Generating embeddings for all chunks...")
        self.chunks_with_embeddings = generate_chunk_embeddings(self.all_chunks)
        
        print("=" * 150)
        print(f"✓ COURSE TUTOR READY")
        print(f"  Using optimal parameters: k={config.OPTIMAL_K:.2f}, threshold={config.CONFIDENCE_THRESHOLD:.2f}")
        print("=" * 150 + "\n")
    

    def classify_question(self, question):
        return classify_question_complete(
            question, 
            self.master_keywords, 
            self.chunks_with_embeddings
        )
    

    def process_question(self, question):
        classification_result = self.classify_question(question)
        response_data = process_question_with_response(classification_result)
        return response_data
    

    def process_question_no_context(self, question):
        from llm_handler import get_llm

        llm = get_llm()
        prompt = f"""You are a helpful university tutor for a decision and risk course for university undergraduates.

                Answer the following question. 
                If you don't have enough information to answer the question, say so honestly.
                Be concise and precise in your answer.

                QUESTION: {question}

        QUESTION: {question}
            
        ANSWER:"""
        
        try:
            llm_response = llm.invoke(prompt).strip()
        except Exception as e:
            llm_response = f"Error generating response: {str(e)}\nMake sure Ollama is running with: ollama serve"
        
        return {
            'question': question,
            'classification': 'Relevant (Chatbot)',
            'response': llm_response,
            'sources': [],
            'num_sources': 0
        }
