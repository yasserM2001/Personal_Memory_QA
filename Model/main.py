from memory import Memory
from Query.query import QueryHandler


# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder="images", processed_folder=r"data\\processed")

memory.preprocess()
memory.augment()


query = QueryHandler(memory, debug=True)

res = query.query_rag("When did i go to the beach?")

print(res)