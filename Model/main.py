from Preprocess.memory import Memory
from Query.query import QueryHandler
import json, os


# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder="images", 
                processed_folder=os.path.join("data", "processed", "me"), 
                vector_db_folder=os.path.join("data", "vector_db", "me"),)

## if data was not processed and augmented before
# memory.preprocess()
# memory.augment()

# if data was processed and augmented before
memory.load_processed_memory()

query = QueryHandler(memory)

# Example question -> 2 ways to query
# result = query.query_memory("When did i go to the beach?")
# or 
result = query.query_rag("When did i go to the beach?")

print("Result : ")
print(json.dumps(result, indent=4, ensure_ascii=False))