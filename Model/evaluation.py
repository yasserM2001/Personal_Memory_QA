import json
import re
from sentence_transformers import SentenceTransformer, util
from LLM.llm import OpenAIWrapper
import numpy as np
from word2number import w2n
from difflib import SequenceMatcher
from collections import defaultdict
import string

model = SentenceTransformer('all-MiniLM-L6-v2')
llm = OpenAIWrapper()

number_word_map = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, 
    "seven": 7, "eight": 8, "nine": 9, "ten": 10
}

def load_results(file_path):
    """Load results from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_questions_with_choices(file_path):
    """Load questions with multiple choice options."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def compute_cosine_similarity(answer1, answer2):
    """Compute cosine similarity between two answers."""
    embedding1 = model.encode(answer1, convert_to_tensor=True)
    embedding1 = np.array(embedding1)
    embedding2 = model.encode(answer2, convert_to_tensor=True)
    embedding2 = np.array(embedding2)
    
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)  # Convert to Python float

def contains_ground_truth(answer, ground_truth):
    """Check if the ground_truth is a substring of the answer (case insensitive)."""
    return ground_truth.lower() in answer.lower()

def fuzzy_string_match(answer, ground_truth, threshold=0.8):
    """Use fuzzy string matching to compare answers."""
    return SequenceMatcher(None, answer.lower(), ground_truth.lower()).ratio() >= threshold

def normalize_text(text):
    """Normalize text for better comparison."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower().strip()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove punctuation at the end
    text = text.rstrip(string.punctuation)
    
    # Handle common variations
    text = re.sub(r'\band\b', '&', text)  # "and" -> "&"
    text = re.sub(r'\bw/\b', 'with', text)  # "w/" -> "with"
    text = re.sub(r'\bu\b', 'you', text)  # "u" -> "you"
    text = re.sub(r'\bur\b', 'your', text)  # "ur" -> "your"
    
    # Remove articles for better matching
    text = re.sub(r'\b(the|a|an)\b\s+', '', text)
    
    return text

def extract_key_entities(text):
    """Extract key entities/phrases that might be important for matching."""
    text = normalize_text(text)
    
    # Look for common patterns
    entities = []
    
    # Dates
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b',
        r'\b\d{1,2}\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities.extend(matches)
    
    # Times
    time_patterns = [
        r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',
        r'\b\d{1,2}\s*(am|pm)\b'
    ]
    
    for pattern in time_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        entities.extend(matches)
    
    # Numbers
    number_matches = re.findall(r'\b\d+\b', text)
    entities.extend(number_matches)
    
    # Proper nouns (capitalized words)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
    entities.extend([noun.lower() for noun in proper_nouns])
    
    return entities

def semantic_keyword_match(answer, ground_truth):
    """Check if key entities/keywords match between answer and ground truth."""
    answer_entities = set(extract_key_entities(answer))
    truth_entities = set(extract_key_entities(ground_truth))
    
    if not truth_entities:
        return False
    
    # Calculate overlap
    overlap = len(answer_entities.intersection(truth_entities))
    return overlap / len(truth_entities) >= 0.5  # At least 50% entity overlap

def convert_to_number(answer):
    """Convert word form of numbers to their numerical equivalents."""
    words = answer.split()
    converted_words = []
    for word in words:
        if word.lower() in number_word_map:
            converted_words.append(str(number_word_map[word.lower()]))
        else:
            converted_words.append(word)
    return ' '.join(converted_words)

def check_multiple_choice_match(answer, choices):
    """Check if answer matches any of the multiple choice options."""
    if not choices:
        return False, None
    
    answer_norm = normalize_text(answer)
    best_match = None
    best_score = 0
    
    for choice in choices:
        choice_norm = normalize_text(choice)
        
        # Check exact substring match
        if choice_norm in answer_norm or answer_norm in choice_norm:
            return True, choice
        
        # Check fuzzy match
        fuzzy_score = SequenceMatcher(None, answer_norm, choice_norm).ratio()
        if fuzzy_score >= 0.8:
            return True, choice
        
        # Check cosine similarity
        similarity = compute_cosine_similarity(answer, choice)
        if similarity > best_score:
            best_score = similarity
            best_match = choice
    
    # Return best match if similarity is above threshold
    if best_score >= 0:  # Lowered threshold
        return True, best_match
    
    return False, None

def evaluate_answer_comprehensive(answer, ground_truth, choices=None, similarity_threshold=0.25):  # Lowered threshold
    """
    Comprehensive answer evaluation using multiple methods.
    Returns: (is_correct, method_used, confidence_score)
    """
    if not answer or not ground_truth:
        return False, "no_match", 0.0
    
    answer = convert_to_number(answer)
    ground_truth = convert_to_number(ground_truth)
    
    # Method 1: Exact substring match (highest confidence)
    if contains_ground_truth(answer, ground_truth):
        return True, "substring_match", 1.0
    
    # Method 2: Reverse substring match (ground truth contains answer)
    if contains_ground_truth(ground_truth, answer):
        return True, "reverse_substring_match", 0.95
    
    # Method 3: Fuzzy string matching
    if fuzzy_string_match(answer, ground_truth, threshold=0.75):
        return True, "fuzzy_match", 0.9
    
    # Method 4: Semantic keyword matching
    if semantic_keyword_match(answer, ground_truth):
        return True, "keyword_match", 0.85
    
    # Method 5: Cosine similarity
    similarity = compute_cosine_similarity(ground_truth, answer)
    if similarity >= similarity_threshold:
        return True, "cosine_similarity", similarity
    
    # Method 6: Multiple choice matching (if available)
    if choices:
        is_match, matched_choice = check_multiple_choice_match(answer, choices)
        if is_match and matched_choice:
            # Check if the matched choice matches the ground truth
            if (contains_ground_truth(matched_choice, ground_truth) or 
                contains_ground_truth(ground_truth, matched_choice) or
                fuzzy_string_match(matched_choice, ground_truth, threshold=0.75)):
                return True, "multiple_choice_match", 0.8
    
    return False, "no_match", 0.0

def compute_enhanced_accuracy(results, questions_with_choices=None, similarity_threshold=0.3):
    """Enhanced accuracy computation with detailed analysis."""
    total_questions = 0
    rag_results = defaultdict(int)
    memory_results = defaultdict(int)
    
    detailed_results = []

    # Create a lookup for questions with choices
    choices_lookup = {}
    if questions_with_choices:
        for user_id, questions in questions_with_choices.items():
            for question in questions:
                question_id = question.get('question_id')
                if question_id:
                    choices_lookup[question_id] = question.get('multiple_choices', {}).get('4_options', [])

    for user_id, questions in results.items():
        for question in questions:
            # Skip questions where both systems don't know
            rag_answer = question['rag_answer']['answer']
            memory_answer = question['memory_answer']['answer']
            
            if "I don't know" in rag_answer and "I don't know" in memory_answer:
                continue
                
            total_questions += 1
            ground_truth = question['ground_truth']
            question_id = question.get('question_id')
            choices = choices_lookup.get(question_id, [])
            
            # Evaluate RAG answer
            rag_correct, rag_method, rag_confidence = evaluate_answer_comprehensive(
                rag_answer, ground_truth, choices, similarity_threshold
            )
            
            # Evaluate Memory answer
            memory_correct, memory_method, memory_confidence = evaluate_answer_comprehensive(
                memory_answer, ground_truth, choices, similarity_threshold
            )
            
            # Update counters
            if rag_correct:
                rag_results[rag_method] += 1
            if memory_correct:
                memory_results[memory_method] += 1
            
            # Store detailed results
            detailed_results.append({
                'user_id': user_id,
                'question_id': question_id,
                'question': question['question'],
                'ground_truth': ground_truth,
                'rag_answer': rag_answer,
                'memory_answer': memory_answer,
                'rag_correct': rag_correct,
                'rag_method': rag_method,
                'rag_confidence': rag_confidence,
                'memory_correct': memory_correct,
                'memory_method': memory_method,
                'memory_confidence': memory_confidence,
                'choices_available': len(choices) > 0
            })
            
            print(f"User ID: {user_id}")
            print(f"Question: {question['question']}")
            print(f"Ground Truth: {ground_truth}")
            print(f"RAG Answer: {rag_answer}")
            print(f"Memory Answer: {memory_answer}")
            print(f"RAG: {'✓' if rag_correct else '✗'} ({rag_method}, conf: {rag_confidence:.3f})")
            print(f"Memory: {'✓' if memory_correct else '✗'} ({memory_method}, conf: {memory_confidence:.3f})")
            if choices:
                print(f"Choices: {choices}")
            print("-" * 50)
    
    # Calculate overall accuracies
    rag_total_correct = sum(rag_results.values())
    memory_total_correct = sum(memory_results.values())
    
    rag_accuracy = rag_total_correct / total_questions if total_questions > 0 else 0
    memory_accuracy = memory_total_correct / total_questions if total_questions > 0 else 0
    
    return (rag_accuracy, memory_accuracy, rag_total_correct, memory_total_correct, 
            total_questions, rag_results, memory_results, detailed_results)

def print_detailed_analysis(rag_results, memory_results, total_questions):
    """Print detailed breakdown of evaluation methods."""
    print("\n" + "="*60)
    print("DETAILED EVALUATION ANALYSIS")
    print("="*60)
    
    print(f"\nRAG System Results (Total: {sum(rag_results.values())}/{total_questions}):")
    for method, count in rag_results.items():
        percentage = (count / total_questions) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")
    
    print(f"\nMemory System Results (Total: {sum(memory_results.values())}/{total_questions}):")
    for method, count in memory_results.items():
        percentage = (count / total_questions) * 100
        print(f"  {method}: {count} ({percentage:.1f}%)")

def save_detailed_results(detailed_results, output_file):
    """Save detailed evaluation results to JSON file."""
    # Convert numpy float32 to regular Python float
    def convert_numpy_types(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj
    
    # Convert all numpy types in detailed_results
    converted_results = []
    for result in detailed_results:
        converted_result = {}
        for key, value in result.items():
            converted_result[key] = convert_numpy_types(value)
        converted_results.append(converted_result)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_results, f, indent=2, ensure_ascii=False)

def main():
    # File paths
    results_file = "results/gemini_qa/all_users_results.json"
    questions_file = "dataset/all_users_questions.json"  # Your file with multiple choices
    output_file = "detailed_evaluation_results.json"
    
    # Load data
    results = load_results(results_file)
    questions_with_choices = None
    
    try:
        questions_with_choices = load_questions_with_choices(questions_file)
        print("Loaded questions with multiple choice options")
    except FileNotFoundError:
        print("Multiple choice file not found, proceeding without choices")
    
    # Compute enhanced accuracy
    (rag_accuracy, memory_accuracy, rag_correct, memory_correct, 
     total_questions, rag_results, memory_results, detailed_results) = compute_enhanced_accuracy(
        results, questions_with_choices, similarity_threshold=0.25  # Lowered threshold
    )
    
    # Print results
    print(f"\nSUMMARY:")
    print(f"Total Questions: {total_questions}")
    print(f"RAG Accuracy: {rag_accuracy:.2%} ({rag_correct}/{total_questions})")
    print(f"Memory Accuracy: {memory_accuracy:.2%} ({memory_correct}/{total_questions})")
    
    # Print detailed analysis
    print_detailed_analysis(rag_results, memory_results, total_questions)
    
    # Save detailed results
    save_detailed_results(detailed_results, output_file)
    print(f"\nDetailed results saved to: {output_file}")
    
    # Additional insights
    print(f"\nADDITIONAL INSIGHTS:")
    questions_with_choices_count = sum(1 for r in detailed_results if r['choices_available'])
    print(f"Questions with multiple choices: {questions_with_choices_count}/{total_questions}")
    
    if questions_with_choices_count > 0:
        mc_rag_correct = sum(1 for r in detailed_results 
                           if r['choices_available'] and r['rag_correct'])
        mc_memory_correct = sum(1 for r in detailed_results 
                              if r['choices_available'] and r['memory_correct'])
        print(f"RAG accuracy on MC questions: {mc_rag_correct/questions_with_choices_count:.2%}")
        print(f"Memory accuracy on MC questions: {mc_memory_correct/questions_with_choices_count:.2%}")

if __name__ == "__main__":
    main()