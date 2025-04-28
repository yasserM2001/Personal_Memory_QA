import json
import os
import re


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
    
    # Check if the photo exists
    if not os.path.exists(photo_path):
        return None
        
    # Retrieve the photo's data from the JSON file
    photo_data = json_data.get(photo_name)
    
    return photo_data

def count_words(text):
    words = re.split(r'[ \n,.!?():"/;]+', text)
    word_count = len([word for word in words if word])
    
    return word_count

####################################################################################

def parse_memory_to_string(memory: dict) -> str:
    filename = memory['filename']

    capture_method = memory['metadata']['capture_method']

    temporal = memory['metadata']['temporal_info']
    date_string = temporal['date_string']
    day_of_week = temporal['day_of_week']
    time_of_the_day = temporal['time_of_the_day']
    temporal_info = f'{date_string}, {day_of_week}, {time_of_the_day}'

    location = memory['metadata']['location']
    address = location.get('address', 'Unknown')

    content = memory['content']

    caption = content.get('caption', '')
    objects = content.get('objects', [])
    people = content.get('people', [])
    activities = content.get('activities', [])
    text = content.get('text', '')
    speech = content.get('speech', '')

    word_count = count_words(text)
    text_in_prompt = text if word_count < 100 else ""

    memory_string = f'''
memory_id: {filename}
capture method: {capture_method}
temporal info: {temporal_info}
location: {address}

Content: 
caption: {caption}
visible objects: {objects}
visible people: {people}
visible text: {text_in_prompt}
heard speech: {speech}
inferred activities: {activities}\n\n'''
    return memory_string

def parse_memory_to_string_lite(memory: dict) -> str:
    filename = memory['filename']

    capture_method = memory['metadata']['capture_method']

    temporal = memory['metadata']['temporal_info']
    date_string = temporal['date_string']
    day_of_week = temporal['day_of_week']
    time_of_the_day = temporal['time_of_the_day']
    temporal_info = f'{date_string}, {day_of_week}, {time_of_the_day}'

    location = memory['metadata']['location']
    address = location.get('address', 'Unknown')

    content = memory['content']

    caption = content.get('caption', '')
    objects = content.get('objects', [])
    people = content.get('people', [])
    activities = content.get('activities', [])
    text = content.get('text', '')
    speech = content.get('speech', '')

    word_count = count_words(text)
    text_in_prompt = text if word_count < 100 else ""

    memory_string = f'''
memory_id: {filename}
capture method: {capture_method}
temporal info: {temporal_info}
location: {address}

Content: 
caption: {caption}
visible objects: {objects}
visible people: {people}
visible text: {text_in_prompt}
heard speech: {speech}
inferred activities: {activities}\n\n'''
    return memory_string

def parse_composite_context_to_string(composite_context: dict) -> str:
    event_name = composite_context['event_name']
    start_date = composite_context['start_date']
    end_date = composite_context['end_date']
    location = composite_context['location']
    # is_multi_days = composite_context['is_multi_days']
    # importance = composite_context['importance']

    composite_context_string = f'''
    event_name: {event_name}
    start_date: {start_date}
    end_date: {end_date}
    location: {location}\n\n'''
    return composite_context_string

def parse_knowledge_to_string(knowledge: dict) -> str:
    knowledge_string = f'''
    knowledge: {knowledge['knowledge']}
    memory_ids: {knowledge['memory_ids']}\n\n'''
    return knowledge_string

####################################################################################
####################################################################################

def parse_memory_to_string_update(memory: dict) -> str:
    filename = memory['filename']

    capture_method = memory['metadata']['capture_method']

    temporal = memory['metadata']['temporal_info']
    date_string = temporal['date_string']
    day_of_week = temporal['day_of_week']
    time_of_the_day = temporal['time_of_the_day']
    temporal_info = f'{date_string}, {day_of_week}, {time_of_the_day}'

    location = memory['metadata']['location']
    address = location.get('address', 'Unknown')

    content = memory['content']

    caption = content.get('caption', '')
    objects = content.get('objects', [])
    people = content.get('people', [])
    activities = content.get('activities', [])
    text = content.get('text', '')
    speech = content.get('speech', '')
    face_tags = content.get('face_tags', [])

    word_count = count_words(text)
    text_in_prompt = text if word_count < 100 else ""

    memory_string = f'''
memory_id: {filename}
capture method: {capture_method}
temporal info: {temporal_info}
location: {address}

Content: 
caption: {caption}
visible objects: {objects}
visible people: {people}
face tags: {face_tags}
visible text: {text_in_prompt}
heard speech: {speech}
inferred activities: {activities}\n\n'''
    return memory_string