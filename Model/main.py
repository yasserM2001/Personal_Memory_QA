from ProcessMemoryContent import ProcessMemoryContent
from augment import AugmentContext
from memory import Memory


# pass these if using memex dataset photos
## is_training_data=True,json_data_file_path=r"dataset\\photo_info.json"

memory = Memory(raw_folder="images", processed_folder=r"data\\processed")

memory.preprocess()
memory.augment()