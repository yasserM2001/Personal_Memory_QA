from .ProcessMemoryContent import ProcessMemoryContent
from .augment import AugmentContext
import os
import json
import numpy as np
from Face_Processing.face_extraction import FaceProcessor


class Memory():
    def __init__(self,raw_folder,
                 processed_folder=r"data\\processed", 
                 vector_db_folder=r"data\\vector_db", 
                is_training_data: bool = False, 
                json_data_file_path: str = None,
                detect_faces: bool = False) -> None:
        
        self.processed_folder = processed_folder
        self.vector_db_folder = vector_db_folder

        self.detect_faces = detect_faces
        
        self.preprocess_memory = ProcessMemoryContent(
            raw_data_folder=raw_folder,
            processed_folder=processed_folder,
            is_training_data=is_training_data,
            json_data_file_path=json_data_file_path
            )
                
    def preprocess(self):
        self.preprocess_memory.process(self.detect_faces)
        self.memory_content_processed = self.preprocess_memory.memory_content_processed

    def augment(self):
        if self.memory_content_processed is None:
            raise ValueError("Memory content is not processed yet.")
        self.augment_context = AugmentContext(
            memory_content_processed=self.memory_content_processed,
            processed_folder=self.processed_folder,
            vector_db_folder=self.vector_db_folder,
            detect_faces=self.detect_faces
        )
        self.augment_context.augment()

    def change_face_tag(self, face_tag: str, new_face_tag: str):
        """Change the face tag in the memory content."""
        if self.memory_content_processed is None:
            raise ValueError("Memory content is not processed yet.")
        
        if self.preprocess_memory.memory_content_processed is None:
            self.preprocess_memory.memory_content_processed = self.memory_content_processed

        if self.preprocess_memory.face_processor is None:
            face_processor = FaceProcessor(directory=os.path.join(self.processed_folder, "extracted_faces"),
                                            output_folder=os.path.join(self.processed_folder, "grouped_faces"))
            self.preprocess_memory.face_processor = face_processor

        self.preprocess_memory.face_processor.change_group_name(face_tag, new_face_tag)
        self.preprocess_memory.add_face_tags()


    def load_processed_memory(self):
        """Load the already processed memory content from saved JSON and vector files."""
        memory_file = os.path.join(self.processed_folder, "memory_content_processed.json")

        if not os.path.exists(memory_file):
            raise FileNotFoundError(f"Processed memory file not found: {memory_file}")

        with open(memory_file, "r", encoding="utf-8") as f:
            self.memory_content_processed = json.load(f)

        # Load vector DB
        self.augment_context = AugmentContext(memory_content_processed=self.memory_content_processed)
        self.augment_context.caption_list = self._load_json("caption_list.json")
        self.augment_context.caption_vector_db = self._load_npy("caption_vector_db.npy")

        self.augment_context.text_list = self._load_json("text_list.json")
        self.augment_context.text_vector_db = self._load_npy("text_vector_db.npy")

        self.augment_context.objects_list = self._load_json("objects_list.json")
        self.augment_context.objects_vector = self._load_npy("objects_vector_db.npy")

        self.augment_context.people_list = self._load_json("people_list.json")
        self.augment_context.people_vector = self._load_npy("people_vector_db.npy")

        self.augment_context.activities_list = self._load_json("activities_list.json")
        self.augment_context.activities_vector = self._load_npy("activities_vector_db.npy")

        self.augment_context.composite_context = self._load_json("composite_list.json")
        self.augment_context.composite_context_embeddings = self._load_npy("composite_vector_db.npy")

        self.augment_context.knowledge = self._load_json("knowledge_list.json")
        self.augment_context.knowledge_embeddings = self._load_npy("knowledge_vector_db.npy")

        self.augment_context.vector_db_list = self._load_json("vector_db_list.json")
        self.augment_context.vector_db_rag = self._load_npy("vector_db_rag.npy")

        self.augment_context.location_list = self._load_json("location_list.json")
        self.augment_context.location_vector_db = self._load_npy("location_vector_db.npy")

        self.augment_context.face_list = self._load_json('face_list.json')

    def _load_json(self, filename):
        """Helper function to load JSON files."""
        file_path = os.path.join(self.vector_db_folder, filename)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _load_npy(self, filename):
        """Helper function to load NumPy vector files."""
        file_path = os.path.join(self.vector_db_folder, filename)
        if os.path.exists(file_path):
            return np.load(file_path, allow_pickle=True)
        return None
