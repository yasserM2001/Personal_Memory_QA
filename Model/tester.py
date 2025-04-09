import json
import os
from pathlib import Path
from typing import Dict

from Testing_Dataset.downloader import PhotoDownloader
from Testing_Dataset.processor import FlickrDataProcessor
from Preprocess.memory import Memory
from Query.query import QueryHandler

def process_user_questions(user_id: str, memory_instance: Memory, output_file: str = None, batch_size: int = 15) -> None:
    """
    Processes questions for a specific user and saves results in structured format.
    
    Args:
        user_id: Specific user ID to process
        memory_instance: Initialized Memory class instance
        output_file: Path to output JSON file
        batch_size: Save after processing this many questions
    """
    output_file = output_file or os.path.join("results", "all_users_results.json")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    all_results = load_existing_results(output_file)
    processed_questions = get_processed_questions(all_results, user_id)
    print(f"Found {len(processed_questions)} previously processed questions for user {user_id}")

    user_questions = load_user_questions(user_id)
    if not user_questions:
        return
    
    new_questions = filter_new_questions(user_questions, processed_questions)
    if not new_questions:
        print(f"No new questions to process for user {user_id}")
        return
    
    print(f"Processing {len(new_questions)} new questions for user {user_id}")
    
    process_questions(
        user_id,
        new_questions,
        all_results,
        memory_instance,
        output_file,
        batch_size
    )

def load_existing_results(output_file: str) -> Dict:
    """Load existing results if file exists"""
    if not os.path.exists(output_file):
        return {}
    
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading existing results: {str(e)}")
        return {}

def get_processed_questions(all_results: Dict, user_id: str) -> set:
    """Get set of already processed question IDs"""
    return {
        str(q['question_id']) 
        for q in all_results.get(user_id, [])
    }

def load_user_questions(user_id: str) -> list[Dict]:
    """Load questions for specific user"""
    questions_file = os.path.join("dataset", "all_users_questions.json")
    try:
        with open(questions_file, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        return all_questions.get(user_id, [])
    except Exception as e:
        print(f"Error loading questions: {str(e)}")
        return []

def filter_new_questions(user_questions: list[Dict], processed_questions: set) -> list[Dict]:
    """Filter out already processed questions"""
    return [
        q for q in user_questions 
        if str(q['question_id']) not in processed_questions
    ]

def process_questions(user_id: str, questions: list[Dict], all_results: Dict, 
                     memory_instance: Memory, output_file: str, batch_size: int) -> None:
    """Process questions in batches and save results"""
    query_handler = QueryHandler(memory_instance)
    if user_id not in all_results:
        all_results[user_id] = []
    
    processed_count = 0
    
    for i, question_data in enumerate(questions, 1):
        print(f"\nStart Processing question {i}/{len(questions)} (ID: {question_data['question_id']})")
        result = process_single_question(question_data, query_handler)
        if not result:
            continue
            
        all_results[user_id].append(result)
        processed_count += 1
        
        if processed_count % batch_size == 0:
            save_results(all_results, output_file)
            print(f"\nSaved progress after {processed_count} questions processed")
    
    save_results(all_results, output_file)
    print_summary(user_id, processed_count, len(questions), output_file)

def process_single_question(question_data: Dict, query_handler: QueryHandler) -> Dict:
    """Process a single question and return formatted result"""
    try:
        question_id = question_data['question_id']
        print(f"Question: {question_data['question']}")
        
        rag_result = query_handler.query_rag(question_data['question'], topk=15)
        memory_result = query_handler.query_memory(question_data['question'], topk=15)
        
        return {
            "question_id": question_id,
            "question": question_data['question'],
            "ground_truth": question_data['answer'],
            "rag_answer": rag_result,
            "memory_answer": memory_result,
            "album_ids": question_data['album_ids'],
            "evidence_photo_ids": question_data['evidence_photo_ids']
        }
    except Exception as e:
        print(f"Error processing question {question_data.get('question_id', 'unknown')}: {str(e)}")
        return None

def save_results(results: Dict, output_file: str) -> None:
    """Save results to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

def print_summary(user_id: str, processed: int, total: int, output_file: str) -> None:
    """Print processing summary"""
    print(f"\nProcessing complete for user {user_id}!")
    print(f"Total questions processed: {processed}/{total}")
    print(f"Results saved to {output_file}")

if __name__ == '__main__':
    # Initialize components
    downloader = PhotoDownloader(max_workers=5)
    processor = FlickrDataProcessor()
    
    # Load all data
    with open('dataset/all_users_photos.json') as f:
        all_photos_data = json.load(f)
    with open('dataset/all_users_questions.json') as f:
        all_users_questions = json.load(f)
    
    # users = list(set(all_photos_data.keys()).intersection(all_users_questions.keys()))
    users = list(all_photos_data.keys())
    print(f"Total users to process: {len(users)}")
    print(f"Users: {users[:5]}")
    processed_users = 0

    # Process each user
    for user_id in users:
        safe_user_id = user_id.replace('@', '_').replace('/', '_')
        print(f"\n{'='*50}")
        print(f"Processing user: {user_id}")
        print(f"{'='*50}")
        
        try:
            # 1. Download photos
            print("\n[1/3] Downloading photos...")
            downloader.download_user_photos(user_id, all_photos_data)
            print("[1/3] DONE")
            # 2. Initialize memory system
            memory = Memory(
                raw_folder=os.path.join("user_photos", safe_user_id),
                processed_folder=os.path.join("data", "processed", safe_user_id),
                vector_db_folder=os.path.join("data", "vector_db", safe_user_id),
                is_training_data=True,
                json_data_file_path=os.path.join("dataset", "photo_info.json")
            )
            
            # 3. Check and load processed memory
            processed_memory_file = os.path.join("data", "processed", safe_user_id, "memory_content_processed.json")
            vector_db_exists = os.path.exists(os.path.join("data", "vector_db", safe_user_id, "vector_db_list.json"))
            
            if os.path.exists(processed_memory_file) and os.path.exists(vector_db_exists):
                print("\n[2/3] Loading existing processed memory...")
                memory.load_processed_memory()
                print("[2/3] DONE")
            else:
                print("\n[2/3] Preprocessing and augmenting memory...")
                memory.preprocess()
                memory.augment()
                print("[2/3] DONE")
            
            # 4. Process questions
            print("\n[3/3] Processing questions...")
            process_user_questions(
                user_id=user_id,
                memory_instance=memory,
                output_file=os.path.join("results", "all_users_results.json"),
                batch_size=15
            )
            print("[3/3] DONE")
            
            processed_users += 1
            print(f"\nProcessed {processed_users}/{len(users)} users")
            
        except Exception as e:
            print(f"Error processing user {user_id}: {str(e)}")
            continue