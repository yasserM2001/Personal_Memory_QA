import json
import os

def read_json_file(filename):
    """
    Reads a JSON file and returns the data as a Python dictionary or list.
    """
    with open(filename, 'r',encoding='utf-8') as file:
        data = json.load(file)
    return data

def create_photo_id_dict(data):
    """
    Creates a dictionary where each key is a photo_id and the value is a dictionary
    containing the corresponding photo's data.
    """
    photo_id_dict = {}
    
    for album in data:
        for i, photo_id in enumerate(album['photo_ids']):
            photo_data = {
                "photo_url": album['photo_urls'][i],
                "photo_gps": album['photo_gps'][i],
                "photo_title": album['photo_titles'][i],
                "photo_tags": album['photo_tags'][i],
                "photo_caption": album['photo_captions'][i],
                "album_title": album['album_title'],
                "album_description": album['album_description'],
                "album_when": album['album_when'],
                "album_where": album['album_where']
            }
            photo_id_dict[photo_id] = photo_data
    
    return photo_id_dict

def save_to_json(data, filename):
    """
    Saves the provided dictionary to a JSON file.
    """
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def get_data_of_photo(photo_name, photo_folder, json_data, extension='jpg'):
    """
    Retrieves the photo from the folder and its corresponding data from the JSON file.
    """
    # Construct the photo file path
    photo_path = os.path.normpath(os.path.join(photo_folder, f"{photo_name}.{extension}"))
    print(photo_path)
    
    # Check if the photo exists
    if not os.path.exists(photo_path):
        return None
        
    # Retrieve the photo's data from the JSON file
    photo_data = json_data.get(photo_name)
    
    return photo_data
