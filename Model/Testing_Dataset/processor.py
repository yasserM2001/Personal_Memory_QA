import json
from collections import defaultdict
from typing import Dict, List
from pathlib import Path

class FlickrDataProcessor:
    """Processes Flickr user photos and questions from JSON data"""
    
    def __init__(self, output_folder: str = 'dataset'):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
    
    def save_user_photos(self, photo_data: List[Dict], output_file: str = 'all_users_photos.json') -> bool:
        """
        Saves all user photos to a single JSON file with paired URLs and IDs.
        
        Args:
            photo_data: List of album dictionaries containing photo data
            output_file: Name of the output JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_photos = defaultdict(list)
            
            for album in photo_data:
                user_id = album['flickr_user_id']
                if not self._validate_photo_data(album, user_id):
                    continue
                
                user_photos[user_id].extend(
                    {'url': url, 'id': pid}
                    for url, pid in zip(album['photo_urls'], album['photo_ids'])
                )
            
            output_path = self.output_folder / output_file
            with open(output_path, 'w') as f:
                json.dump(dict(user_photos), f, indent=2)
            
            total_photos = sum(len(photos) for photos in user_photos.values())
            print(f"Saved {total_photos} photos from {len(user_photos)} users to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing photos: {str(e)}")
            return False
    
    def save_user_questions(self, qa_data: List[Dict], output_file: str = 'all_users_questions.json') -> bool:
        """
        Saves all user questions to a single JSON file.
        
        Args:
            qa_data: List of question-answer dictionaries
            output_file: Name of the output JSON file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_questions = defaultdict(list)
            
            for qa in qa_data:
                user_id = qa['flickr_user_id']
                user_questions[user_id].append(self._format_question_data(qa))
            
            output_path = self.output_folder / output_file
            with open(output_path, 'w') as f:
                json.dump(dict(user_questions), f, indent=2)
            
            print(f"Saved {len(qa_data)} questions from {len(user_questions)} users to {output_path}")
            return True
            
        except Exception as e:
            print(f"Error processing questions: {str(e)}")
            return False
    
    def _validate_photo_data(self, album: Dict, user_id: str) -> bool:
        """Validate photo data has matching URLs and IDs"""
        if len(album['photo_urls']) != len(album['photo_ids']):
            print(f"Warning: Mismatched photo URLs and IDs for user {user_id}")
            return False
        return True
    
    def _format_question_data(self, qa: Dict) -> Dict:
        """Format question data for output"""
        return {
            'question_id': qa['question_id'],
            'question': qa['question'],
            'answer': qa['answer'],
            'album_ids': qa['album_ids'],
            'evidence_photo_ids': qa.get('evidence_photo_ids', []),
            'multiple_choices': {
                '4_options': qa.get('multiple_choices_4', []),
                '20_options': qa.get('multiple_choices_20', [])
            }
        }