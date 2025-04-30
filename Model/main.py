from Preprocess.memory import Memory
from Query.query import QueryHandler
from Query.query_augment import QueryAugmentation
import json, os
import re

# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

# memory = Memory(raw_folder=os.path.join("user_photos", "10485077_N06"),
#                 processed_folder=os.path.join("data", "processed", "faceTest"), 
#                 vector_db_folder=os.path.join("data", "vector_db", "faceTest"),
#                 is_training_data=True,
#                 json_data_file_path=os.path.join("dataset", "photo_info.json"),
#                 detect_faces=True,)
memory = Memory(raw_folder="images",
                processed_folder=os.path.join("data", "processed", "me"), 
                vector_db_folder=os.path.join("data", "vector_db", "me"),
                detect_faces=True,)

## if data was not processed and augmented before
memory.preprocess()
memory.augment()

query = QueryHandler(memory, detect_faces=True)
result = query.query_memory("Who participated in the redbull event?", topk=5)

# query_memory
# Result : 
# {
#     "answer": "The participants in the Red Bull event included Yasser, Peter, Ali, Person_7, and Person_9.",
#     "explanation": "The Red Bull event, which took place on February 19-20, 2024, involved activities such as soccer and basketball games. A photo from the event shows a group of young men posing with a soccer ball in front of a colorful wall, and the face tags identify some of the participants as Yasser, Peter, Ali, Person_7, and Person_9.",
#     "memory_ids": [
#         "IMG_055555.JPG"
#     ]
# }

# query_rag
# Result : 
# {
#     "answer": "Two people participated in the Red Bull event.",
#     "explanation": "The memory with ID 'IMG_055565.JPG' shows an outdoor basketball court with Red Bull branding and mentions two people standing near the basketball court. This suggests their participation in the event.",
#     "memory_ids": [
#         "IMG_055565.JPG"
#     ]
# }

# # # or 
# result = query.query_rag("What funny thing did Dad wear?", topk=20)

print("Result : ")
print(json.dumps(result, indent=4, ensure_ascii=False))