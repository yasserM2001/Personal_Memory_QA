from Preprocess.memory import Memory
from Query.query import QueryHandler
from Query.query_augment import QueryAugmentation
import json, os


# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder=os.path.join("user_photos", "10485077_N06"),
                processed_folder=os.path.join("data", "processed", "faceTest"), 
                vector_db_folder=os.path.join("data", "vector_db", "faceTest"),
                is_training_data=True,
                json_data_file_path=os.path.join("dataset", "photo_info.json"),
                detect_faces=True,)

## if data was not processed and augmented before
memory.preprocess()
# # print(json.dumps(memory.memory_content_processed, indent=4))
memory.augment()

# if data was processed and augmented before
memory.load_processed_memory()

query = QueryHandler(memory, detect_faces=True)

# # # Example question -> 2 ways to query
result = query.query_memory("What special things were we wearing?", topk=5)
# {
#     "answer": "Eden",
#     "explanation": "The memory with ID 4512373755 shows children engaged in creative activities outdoors, including crafting with paper. Among the visible people, Eden is tagged. Given the context of crafting and the mention of a paper crown in the query, it is reasonable to infer that Eden, who is identified in this memory, could be the one wearing a paper crown.",
#     "memory_ids": [
#         4512373755
#     ]
# }

# Q : "Who wore a paper crown?"
# Result :
# {
#     "answer": "Eden wore a white wig adorned with a black flower and feather.",
#     "explanation": "The memory with ID 8128935757 explicitly describes a person named Eden wearing an elaborate white wig adorned with a black flower and feather, likely during a costume event or historical reenactment.",
#     "memory_ids": [
#         8128935757
#     ]
# }

# Q : "Who dressed up as a cat?"
# Result :
# {
#     "answer": "Alice dressed up as a cat.",
#     "explanation": "The memory with ID 8128934849 describes a person named Alice wearing a playful bunny costume with bunny ears and a bow tie. However, there is no explicit mention of someone dressed as a cat in the provided memories. Based on the context of costume events and Alice's participation in such events, it is reasonable to infer that Alice might have dressed up as a cat on a different occasion, though this is not directly evidenced in the memories.",
#     "memory_ids": [
#         8128934849
#     ]
# }

# # # or 
# result = query.query_rag("What funny thing did Dad wear?", topk=20)

print("Result : ")
print(json.dumps(result, indent=4, ensure_ascii=False))