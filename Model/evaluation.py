import json
import re
from sentence_transformers import SentenceTransformer, util
from LLM.llm import OpenAIWrapper
import numpy as np
from word2number import w2n

model = SentenceTransformer('all-MiniLM-L6-v2')
llm = OpenAIWrapper()

number_word_map = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,  "five": 5, "six":6, 
    "seven": 7, "eight": 8, "nine": 9, "ten": 10}

def load_results(file_path):
    """Load results from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# def compute_cosine_similarity(answer1, answer2):
#     """Compute cosine similarity between two answers."""
#     try:
#         embedding1 = model.encode(answer1, convert_to_tensor=True)
#         embedding2 = model.encode(answer2, convert_to_tensor=True)
#         similarity = util.pytorch_cos_sim(embedding1, embedding2)
#         return similarity.item()
#     except Exception as e:
#         print(f"Error computing similarity: {e}")
#         return 0.0

def compute_cosine_similarity(answer1, answer2):
    embedding1 = model.encode(answer1, convert_to_tensor=True)
    embedding1 = np.array(embedding1)
    embedding2 = model.encode(answer2, convert_to_tensor=True)
    embedding2 = np.array(embedding2)
    
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    similarity = dot_product / (norm1 * norm2)
    return similarity

def contains_ground_truth(answer, ground_truth):
    """Check if the ground_truth is a substring of the answer."""
    return ground_truth.lower() in answer.lower()

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


def compute_accuracy(results, similarity_threshold=0.3):
    """Compute the accuracy of the results."""
    total_questions = 0
    rag_correct_answers = 0
    memory_correct_answers = 0

    for user_id, questions in results.items():
        for question in questions:
            total_questions += 1
            ground_truth = question['ground_truth']
            rag_answer = question['rag_answer']['answer']
            memory_answer = question['memory_answer']['answer']
            
            if "I don't know" in rag_answer and "I don't know" in memory_answer:
                total_questions -= 1
                continue
            
            rag_answer = convert_to_number(rag_answer)
            memory_answer = convert_to_number(memory_answer)
            
            print("user_id:", user_id)
            print("Question:", question['question'])
            print("Ground Truth:", ground_truth)
            print("RAG Answer:", rag_answer)
            print("Memory Answer:", memory_answer)
            
            # ground_truth_embedding = llm.calculate_embeddings(ground_truth)
            # rag_embedding = llm.calculate_embeddings(rag_answer)
            # memory_embedding = llm.calculate_embeddings(memory_answer)

            rag_similarity = compute_cosine_similarity(ground_truth, rag_answer)
            memory_similarity = compute_cosine_similarity(ground_truth, memory_answer)

            if contains_ground_truth(rag_answer, ground_truth):
                rag_correct_answers += 1
                print("RAG | Correct Answer :)")
            elif rag_similarity >= similarity_threshold:
                rag_correct_answers += 1
                print("RAG | Correct Answer by cosine similarity :)")
            else:
                print("RAG | Incorrect Answer :(")
            
            if contains_ground_truth(memory_answer, ground_truth):
                memory_correct_answers += 1
                print("Memory | Correct Answer :)")
            elif memory_similarity >= similarity_threshold:
                memory_correct_answers += 1
                print("Memory | Correct Answer by cosine similarity:)") 
            else:
                print("Memory | Incorrect Answer :(")
            print("\n\n")
            
    rag_accuracy = rag_correct_answers / total_questions if total_questions > 0 else 0
    memory_accuracy = memory_correct_answers / total_questions if total_questions > 0 else 0
    return rag_accuracy, memory_accuracy, rag_correct_answers, memory_correct_answers, total_questions

def main():
    results_file = "results/gemini_qa/all_users_results_yasser2.json"
    results = load_results(results_file)

    rag_accuracy, memory_accuracy, rag_correct_answers, memory_correct_answers, total_questions = compute_accuracy(results)

    print(f"Total Questions: {total_questions}")
    print(f"RAG Correct Answers: {rag_correct_answers}")
    print(f"RAG Accuracy: {rag_accuracy:.2%}")
    print("---------------")
    print(f"Memory Correct Answers: {memory_correct_answers}")
    print(f"Memory Accuracy: {memory_accuracy:.2%}")

if __name__ == "__main__":
    main()