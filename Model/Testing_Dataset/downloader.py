import os
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

class PhotoDownloader:
    """Handles downloading of user photos with concurrent requests"""
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
    
    # photos data should be a dictionary with user IDs as keys and lists of photo entries as values
    # Example: {"10506540@N07": [{"id": "123456", "url": "example url"}, ...]}
    def download_user_photos(self, user_id: str, photos_data: Dict, output_folder: str = 'user_photos') -> None:
        """
        Downloads all photos for a specified user to a folder named with their user ID.
        First checks if all photos already exist to avoid redundant downloads.
        
        Args:
            user_id: Flickr user ID (e.g., "35034354137@N01")
            photos_data: Dictionary containing user photos data
            output_folder: Base output directory
        """
        safe_user_id = self._sanitize_user_id(user_id)
        download_dir = os.path.join(output_folder, safe_user_id)
        
        if user_id not in photos_data:
            print(f"No photos found for user {user_id}")
            return
            
        photo_entries = photos_data[user_id]
        if not photo_entries:
            print(f"No photos found for user {user_id}")
            return

        # Create directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)

        # First check which photos already exist
        existing_files = self._get_existing_photos(download_dir)
        photos_to_download = self._filter_existing_photos(photo_entries, existing_files)

        if not photos_to_download:
            print(f"All {len(photo_entries)} photos already exist for user {user_id}")
            return
            
        print(f"Downloading {len(photos_to_download)}/{len(photo_entries)} photos for user {user_id} to {download_dir}")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(
                lambda entry: self._download_single_photo(entry, download_dir),
                photos_to_download
            ))
        
        successful = sum(1 for result in results if result)
        print(f"\nDownload complete! {successful}/{len(photos_to_download)} new photos downloaded successfully")
        print(f"Total photos now available: {len(existing_files) + successful}")

    def _get_existing_photos(self, download_dir: str) -> set[str]:
        """Get set of already downloaded photo IDs (without extensions)"""
        existing_files = set()
        if os.path.exists(download_dir):
            for filename in os.listdir(download_dir):
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    # Remove extension and add to set
                    photo_id = os.path.splitext(filename)[0]
                    existing_files.add(photo_id)
        return existing_files

    def _filter_existing_photos(self, photo_entries: list[Dict], existing_files: set[str]) -> list[Dict]:
        """Filter out photos that already exist in the download directory"""
        return [
            entry for entry in photo_entries 
            if entry['id'] not in existing_files
        ]

    def _download_single_photo(self, photo_entry: Dict, download_dir: str) -> bool:
        """Download a single photo and save with ID as filename"""
        try:
            url = photo_entry['url']
            photo_id = photo_entry['id']
            ## should be a jpg, but also we could check for other formats
            filepath = os.path.join(download_dir, f"{photo_id}.jpg")
            
            if os.path.exists(filepath):
                print(f"Skipping already downloaded: {photo_id}.jpg")
                return True
                
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            extension = self._get_extension_from_content_type(response.headers.get('content-type', ''))
            filepath = os.path.join(download_dir, f"{photo_id}{extension}")
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            print(f"Downloaded: {photo_id}{extension}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to download photo {photo_entry.get('id', 'unknown')}: {str(e)}")
            return False
        except Exception as e:
            print(f"Unexpected error with photo {photo_entry.get('id', 'unknown')}: {str(e)}")
            return False
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """Determine file extension from content-type header"""
        if 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        return '.jpg'
    
    def _sanitize_user_id(self, user_id: str) -> str:
        """Make user ID filesystem-safe"""
        return user_id.replace('@', '_').replace('/', '_')