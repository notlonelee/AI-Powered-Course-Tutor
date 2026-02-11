import re

def extract_lecture_references(question):
    lectures = set()
    
    lecture_patterns = [
        (r'lecture[s]?\s+(\d+)\s*-\s*(\d+)', 'range'),      # lecture 1-5
        (r'lecture[s]?\s+(\d+)\s+(?:and|&)\s+(\d+)', 'range'),  # lecture 1 and 2
        (r'lecture[s]?\s+(\d+)\s+to\s+(\d+)', 'range'),      # lecture 1 to 5
        (r'lecture\s+(\d+)', 'single'),                      # lecture 3
        (r'from\s+lecture\s+(\d+)', 'single'),               # from lecture 5
    ]
    
    lecture_example_pattern = r'lecture[s]?\s+(\d+)\s+example[s]?\s+(\d+)(?:\([a-z]\))?'
    matches = re.findall(lecture_example_pattern, question, re.IGNORECASE)
    matched_lecture_nums = set()
    for lecture_num, example_num in matches:
        lectures.add((int(lecture_num), int(example_num)))
        matched_lecture_nums.add(int(lecture_num))

    example_lecture_pattern = r'example[s]?\s+(\d+).*?lecture[s]?\s+(\d+)'
    matches = re.findall(example_lecture_pattern, question, re.IGNORECASE)
    for example_num, lecture_num in matches:
        lectures.add((int(lecture_num), int(example_num)))

    for pattern, match_type in lecture_patterns:
        matches = re.findall(pattern, question, re.IGNORECASE)
        for match in matches:
            if match_type == 'range':
                start, end = int(match[0]), int(match[1])
                for num in range(start, end + 1):
                    lectures.add((num, None))
            elif match_type == 'single':
                lecture_num = int(match)
                if lecture_num not in matched_lecture_nums:
                    lectures.add((int(match), None))

    return lectures


def extract_week_references(question):
    weeks = set()
    
    week_patterns = [
        (r'week\s+(\d+)\s*-\s*(\d+)', 'range'),              # week 1-3
        (r'week[s]?\s+(\d+)\s+(?:and|&)\s+(\d+)', 'range'),  # week 1 and 2
        (r'week\s+(\d+)\s+to\s+(\d+)', 'range'),             # week 1 to 3
        (r'week\s+(\d+)', 'single'),                         # week 5
    ]

    week_example_pattern = r'week[s]?\s+(\d+)\s+example[s]?\s+(\d+)'
    matches = re.findall(week_example_pattern, question, re.IGNORECASE)
    for week_num, example_num in matches:
        weeks.add((int(week_num), int(example_num)))
    
    example_week_pattern = r'example[s]?\s+(\d+).*?week[s]?\s+(\d+)'
    matches = re.findall(example_week_pattern, question, re.IGNORECASE)
    for example_num, week_num in matches:
        weeks.add((int(week_num), int(example_num)))
    
    for pattern, match_type in week_patterns:
        matches = re.findall(pattern, question, re.IGNORECASE)
        for match in matches:
            if match_type == 'range':
                start, end = int(match[0]), int(match[1])
                for num in range(start, end + 1):
                    weeks.add((num, None)) 
            elif match_type == 'single':
                weeks.add((int(match), None))
    
    return weeks



def extract_exercise_references(question):
    """Extract exercise references"""
    result = {'exercises': set(), 'exercise_parts': {}}
    
    patterns = [
        (r'(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)\s+(?:question|q)\s*(\d+)\s+part\s+([a-z]|\d+\(?[a-z]\)?|[ivxlcdm]+)', lambda m: (int(m[0]), int(m[1]), m[2].lower())),
        (r'(?:question|q)\s*(\d+)\s+part\s+([a-z]|\d+\(?[a-z]\)?|[ivxlcdm]+)\s+in\s+(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)', lambda m: (int(m[2]), int(m[0]), m[1].lower())),
        (r'(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)\s+(?:question|q)\s*(\d+)([a-z]|\(\d*[a-z]\)|\d+\([a-z]\))', lambda m: (int(m[0]), int(m[1]), re.sub(r'[()]', '', m[2].lower()))),
        (r'(?:question|q)\s*(\d+)([a-z]|\(\d*[a-z]\)|\d+\([a-z]\))\s+in\s+(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)', lambda m: (int(m[2]), int(m[0]), re.sub(r'[()]', '', m[1].lower()))),
        (r'(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)\s+(?:question|q)\s*(\d+)(?!\s*[a-z(])', lambda m: (int(m[0]), int(m[1]), None)),
        (r'(?:question|q)\s*(\d+)\s+in\s+(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)(?!\s*(?:part|[a-z(]))', lambda m: (int(m[1]), int(m[0]), None)),
        (r'(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)\s+(\d+)([a-z]|\([a-z]\))', lambda m: (int(m[0]), int(m[1]), re.sub(r'[()]', '', m[2].lower()))),
        (r'ex\.?\s*(\d+)\s*(?:q|question)\.?\s*(\d+)([a-z]|\(\d*[a-z]\)|\d+\([a-z]\))?', lambda m: (int(m[0]), int(m[1]), re.sub(r'[()]', '', m[2].lower()) if m[2] else None)),
        (r'ex\.?\s+sheet\s+(\d+)\s+(?:question|q)\s*(\d+)([a-z]|\(\d*[a-z]\)|\d+\([a-z]\))?', lambda m: (int(m[0]), int(m[1]), re.sub(r'[()]', '', m[2].lower()) if m[2] else None)),
    ]
    
    for pattern, parser in patterns:
        for match in re.findall(pattern, question, re.IGNORECASE):
            ex_num, q_num, part = parser(match)
            result['exercises'].add(ex_num)
            key = (ex_num, q_num)
            if key not in result['exercise_parts']:
                result['exercise_parts'][key] = set()
            if part:
                result['exercise_parts'][key].add(part)
    
    for ex_num in re.findall(r'(?:exercise[s]?\s+sheet|exercise[s]?|ex\s+sheet|ex)\s+(\d+)(?!\s+(?:question|q))', question, re.IGNORECASE):
        result['exercises'].add(int(ex_num))
    
    return result


def extract_document_references(question):
    """Extract all document references from question"""
    return {
        'lectures': extract_lecture_references(question),
        'weeks': extract_week_references(question),
        **extract_exercise_references(question)
    }


def match_references_to_chunks(references, chunks_with_embeddings):
    matched_chunk_ids = set()
    
    # Match lectures
    for lecture_num, example_num in references['lectures']:
        for chunk in chunks_with_embeddings:
            if chunk['document_type'] == 'lecture':
                doc_name_lower = chunk['document_name'].lower()
                match = re.search(r'lecture\s+(\d+)\s*(?:-\s*(\d+))?\.txt', doc_name_lower)
                if match:
                    start = int(match.group(1))
                    end = int(match.group(2)) if match.group(2) else start
                    if start <= lecture_num <= end:
                        if example_num:
                            if f'example {example_num}' in chunk['text'].lower():
                                matched_chunk_ids.add(chunk['chunk_id'])
                        else:
                            matched_chunk_ids.add(chunk['chunk_id'])
    
    # Match weeks (same logic)
    for week_num, example_num in references['weeks']:
        for chunk in chunks_with_embeddings:
            if chunk['document_type'] == 'lecture':
                doc_name_lower = chunk['document_name'].lower()
                match = re.search(r'lecture\s+(\d+)\s*(?:-\s*(\d+))?\.txt', doc_name_lower)
                if match:
                    start = int(match.group(1))
                    end = int(match.group(2)) if match.group(2) else start
                    if start <= week_num <= end:
                        if example_num:
                            if f'example {example_num}' in chunk['text'].lower():
                                matched_chunk_ids.add(chunk['chunk_id'])
                        else:
                            matched_chunk_ids.add(chunk['chunk_id'])
    
    # Match exercises
    for chunk in chunks_with_embeddings:
        if chunk['document_type'] == 'exercise':
            exercise_match = re.search(r'exercise\s+(\d+)', chunk['document_name'].lower())
            if exercise_match:
                exercise_num = int(exercise_match.group(1))
                
                if exercise_num in references['exercises']:
                    if references['exercise_parts']:
                        for (ref_ex, ref_q), parts in references['exercise_parts'].items():
                            if ref_ex == exercise_num:
                                if ref_q is None:
                                    # Part of whole exercise
                                    if parts:
                                        chunk_parts = set(chunk.get('parts', []))
                                        if chunk_parts and parts.intersection(chunk_parts):
                                            matched_chunk_ids.add(chunk['chunk_id'])
                                        elif not chunk_parts:
                                            matched_chunk_ids.add(chunk['chunk_id'])
                                    else:
                                        matched_chunk_ids.add(chunk['chunk_id'])
                                else:
                                    # Specific question
                                    if chunk.get('question_num') == ref_q:
                                        if parts:
                                            chunk_parts = set(chunk.get('parts', []))
                                            if chunk_parts:
                                                if parts.intersection(chunk_parts):
                                                    matched_chunk_ids.add(chunk['chunk_id'])
                                            else:
                                                matched_chunk_ids.add(chunk['chunk_id'])
                                        else:
                                            matched_chunk_ids.add(chunk['chunk_id'])
                    else:
                        # All chunks from this exercise
                        matched_chunk_ids.add(chunk['chunk_id'])
    
    return matched_chunk_ids
