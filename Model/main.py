from memory import Memory
from Query.query import QueryHandler
import json


# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder="images", processed_folder=r"data\\processed")

memory.preprocess()
memory.augment()


query = QueryHandler(memory, debug=True)

result = query.query_memory("When did i go to the beach?")
# or 
# result = query.query_rag("When did i go to the beach?")

print("Result : ")
print(json.dumps(result, indent=4, ensure_ascii=False))