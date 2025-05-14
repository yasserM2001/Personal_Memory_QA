from Preprocess.memory import Memory
from Query.query import QueryHandler
from Query.query_augment import QueryAugmentation
import json, os

# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder="images",
                processed_folder=os.path.join("data", "processed", "me"), 
                vector_db_folder=os.path.join("data", "vector_db", "me"),
                detect_faces=True,)

## if data was not processed and augmented before
memory.preprocess()
memory.augment()
# memory.load_processed_memory()
# memory.delete_face_tag("Person_3")
# memory.change_face_tag("Person_9", "Gom3aa")
query = QueryHandler(memory, detect_faces=True)
result = query.query_memory("Who participated in the redbull event?", topk=5, llm="gemini")

# # # or 
# result = query.query_rag("What funny thing did Dad wear?", topk=20, llm="gemini")

print("Result : ")
print(json.dumps(result, indent=4, ensure_ascii=False))