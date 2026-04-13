import torch
from sklearn.metrics.pairwise import cosine_similarity
from models import get_embedding_model
import config
from references import match_references_to_chunks, extract_document_references

# ============================================================
# EMBEDDING GENERATION
# ============================================================

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def get_embedding(text):
    model, tokenizer = get_embedding_model()
    
    inputs = tokenizer(
        text, 
        return_tensors="pt", 
        truncation=True, 
        max_length=config.EMBEDDING_MAX_LENGTH, 
        padding=True
    )
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    embedding = mean_pooling(outputs, inputs['attention_mask'])
    return embedding[0].numpy()


def generate_chunk_embeddings(chunks):
    print(f"Generating embeddings for {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        chunk['embedding'] = get_embedding(chunk['text'])
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(chunks)} chunks...")
    print(f"✓ Completed\n")
    return chunks


# ============================================================
# SEMANTIC SIMILARITY FILTERING
# ============================================================


# def get_relevant_chunks(question, chunks_with_embeddings, similarity_threshold=0.50):
#     # Extract references
#     references = extract_document_references(question)
#     referenced_chunk_ids = match_references_to_chunks(references, chunks_with_embeddings)
    
#     # Get question embedding
#     question_embedding = get_embedding(question)
    
#     # Calculate similarity
#     relevant_chunks = []
    
#     if referenced_chunk_ids:
#         # If references exist, search only those and give them 1.0 similarity
#         for chunk in chunks_with_embeddings:
#             if chunk['chunk_id'] in referenced_chunk_ids:
#                 relevant_chunks.append({
#                     'chunk_id': chunk['chunk_id'],
#                     'document_name': chunk['document_name'],
#                     'lecture': chunk.get('document_name', ''),
#                     'chunk_index': chunk.get('chunk_index', 0),
#                     'similarity_score': 1.0,
#                     'text': chunk['text'],
#                     'from_reference': True
#                 })
#     else:
#         # No references: search all chunks
#         for chunk in chunks_with_embeddings:
#             similarity = cosine_similarity([question_embedding], [chunk['embedding']])[0][0]
#             if similarity >= similarity_threshold:
#                 relevant_chunks.append({
#                     'chunk_id': chunk['chunk_id'],
#                     'document_name': chunk['document_name'],
#                     'lecture': chunk.get('lecture', chunk.get('document_name', '')),
#                     'chunk_index': chunk.get('chunk_index', 0),
#                     'similarity_score': float(similarity),
#                     'text': chunk['text'],
#                     'from_reference': False
#                 })
    
#     return sorted(relevant_chunks, key=lambda x: x['similarity_score'], reverse=True)

def get_relevant_chunks(question, chunks_with_embeddings, similarity_threshold=0.50, 
                        num_lecture_exercise=4, num_forum=2):
    """
    Get relevant chunks with two different strategies:
    
    Scenario 1 (With references): 
    - Top 4 lecture/exercise chunks (from references)
    - Top 2 forum chunks (by similarity)
    
    Scenario 2 (No references):
    - Top 5 chunks (all types combined, by similarity)
    """
    # Extract references
    references = extract_document_references(question)
    referenced_chunk_ids = match_references_to_chunks(references, chunks_with_embeddings)
    
    # Get question embedding
    question_embedding = get_embedding(question)
    
    # ===== SCENARIO 1: HAS REFERENCES =====
    if referenced_chunk_ids:
        # 1. Extract lecture/exercise chunks with references (similarity = 1.0)
        lecture_exercise_chunks = []
        for chunk in chunks_with_embeddings:
            if chunk['chunk_id'] in referenced_chunk_ids:
                chunk_data = {
                    'chunk_id': chunk['chunk_id'],
                    'document_name': chunk['document_name'],
                    'lecture': chunk.get('document_name', ''),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'similarity_score': 1.0,
                    'text': chunk['text'],
                    'from_reference': True
                }
                lecture_exercise_chunks.append(chunk_data)
        
        # 2. Rank forum chunks by similarity
        forum_chunks = []
        for chunk in chunks_with_embeddings:
            if 'forum' in chunk['document_name'].lower():
                similarity = cosine_similarity([question_embedding], [chunk['embedding']])[0][0]
                chunk_data = {
                    'chunk_id': chunk['chunk_id'],
                    'document_name': chunk['document_name'],
                    'lecture': chunk.get('document_name', ''),
                    'chunk_index': chunk.get('chunk_index', 0),
                    'similarity_score': float(similarity),
                    'text': chunk['text'],
                    'from_reference': False
                }
                forum_chunks.append(chunk_data)
        
        forum_chunks = sorted(forum_chunks, key=lambda x: x['similarity_score'], reverse=True)
        
        # Take top 4 from referenced + top 2 from forum
        return {
            'lecture_exercise': lecture_exercise_chunks[:num_lecture_exercise],
            'forum': forum_chunks[:num_forum]
        }
    
    # ===== SCENARIO 2: NO REFERENCES =====
    else:
        all_chunks = []
        
        # Compute similarity for ALL chunks (combined)
        for chunk in chunks_with_embeddings:
            similarity = cosine_similarity([question_embedding], [chunk['embedding']])[0][0]
            chunk_data = {
                'chunk_id': chunk['chunk_id'],
                'document_name': chunk['document_name'],
                'lecture': chunk.get('document_name', ''),
                'chunk_index': chunk.get('chunk_index', 0),
                'similarity_score': float(similarity),
                'text': chunk['text'],
                'from_reference': False
            }
            all_chunks.append(chunk_data)
        
        # Sort all by similarity and take top 5
        all_chunks = sorted(all_chunks, key=lambda x: x['similarity_score'], reverse=True)[:5]
        
        # Separate into lecture_exercise and forum for return format
        lecture_exercise = [c for c in all_chunks if 'forum' not in c['document_name'].lower()]
        forum = [c for c in all_chunks if 'forum' in c['document_name'].lower()]
        
        return {
            'lecture_exercise': lecture_exercise,
            'forum': forum
        }
