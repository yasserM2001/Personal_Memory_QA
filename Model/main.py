from PIL import Image

# from ProcessMemoryContent import ProcessMemoryContent
import os
import json
from augment import AugmentContext
# pmc = ProcessMemoryContent(raw_data_folder=r"images\\dataset_sample",
#                             processed_folder=r"data\\processed")
                            ## pass these if using memex dataset photos
                            # is_training_data=True,
                            # json_data_file_path=r"dataset\\photo_info.json")
# pmc.process()

memory_content_processed = [
    {
        "filename": "IMG_051309.HEIC",
        "filepath": "images\\my_images\\IMG_051309.HEIC",
        "media_type": "image",
        "metadata": {
            "temporal_info": {
                "date_string": "2023:09:26 13:24:48",
                "day_of_week": "Tuesday",
                "time_of_the_day": "Afternoon"
            },
            "location": {
                "gps": [
                    28.63755,
                    34.5760833333333
                ],
                "address": "جنوب سيناء, مصر",
                "country": "مصر",
                "zip": "جنوب سيناء"
            },
            "capture_method": "photo"
        },
        "content": {
            "caption": "A person standing in shallow, clear water at the beach with kite surfers in the background.",
            "objects": [
                "water",
                "beach",
                "kite surfers"
            ],
            "people": [
                {
                    "description": "A person wearing a blue and white tank top and blue shorts, standing in the water."
                }
            ],
            "activities": [
                "enjoying the beach",
                "standing in the water",
                "observing kite surfing"
            ],
            "text": ""
        }
    },
    {
        "filename": "IMG_051589.HEIC",
        "filepath": "images\\my_images\\IMG_051589.HEIC",
        "media_type": "image",
        "metadata": {
            "temporal_info": {
                "date_string": "2023:09:29 06:08:57",
                "day_of_week": "Friday",
                "time_of_the_day": "Morning"
            },
            "location": {
                "gps": [
                    28.4719611111111,
                    34.5064666666667
                ],
                "address": "شارع عباس العقاد, مدينه دهب, Medina, دهب, جنوب سيناء, 46617, مصر",
                "country": "مصر",
                "zip": "46617",
                "state": "جنوب سيناء",
                "county": "دهب",
                "city": "Medina"
            },
            "capture_method": "photo"
        },
        "content": {
            "caption": "A serene beach scene with mountains in the background.",
            "objects": [
                "beach",
                "sea",
                "mountains",
                "clouds"
            ],
            "people": [],
            "activities": [
                "photography",
                "relaxation"
            ],
            "text": ""
        }
    }
]

augmentContext = AugmentContext(memory_content_processed, debug=True)