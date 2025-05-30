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
        
        self.raw_folder = raw_folder
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
        
        if self.preprocess_memory.face_processor is None:
            face_processor = FaceProcessor(directory=os.path.join(self.processed_folder, "extracted_faces"),
                                            output_folder=os.path.join(self.processed_folder, "grouped_faces"))
            self.preprocess_memory.face_processor = face_processor
            self.preprocess_memory.face_processor.process_and_group_faces(self.raw_folder)

        self.preprocess_memory.face_processor.change_group_name(face_tag, new_face_tag)
        # Edit face tags in memory content
        if self.preprocess_memory.memory_content_processed is None:
            self.preprocess_memory.memory_content_processed = self.memory_content_processed
        self.preprocess_memory.add_face_tags()
        self.memory_content_processed = self.preprocess_memory.memory_content_processed
        # Edit Face List in vectorDB
        if self.augment_context.face_list:
            for face in self.augment_context.face_list:
                if face['face_tag'].lower() == face_tag.lower():
                    face['face_tag'] = new_face_tag
            
            # Save updated face list back to file
            face_list_path = os.path.join(self.vector_db_folder, 'face_list.json')
            with open(face_list_path, 'w', encoding='utf-8') as f:
                json.dump(self.augment_context.face_list, f, ensure_ascii=False, indent=4)

        print(f"Finished Updating {face_tag} to {new_face_tag}")
        return True
        
    def delete_face_tag(self, face_tag: str):
        """Delete a face group and all associated references."""
        if self.memory_content_processed is None:
            raise ValueError("Memory content is not processed yet.")
            return False

        if self.preprocess_memory.face_processor is None:
            face_processor = FaceProcessor(directory=os.path.join(self.processed_folder, "extracted_faces"),
                                        output_folder=os.path.join(self.processed_folder, "grouped_faces"))
            self.preprocess_memory.face_processor = face_processor
            self.preprocess_memory.face_processor.process_and_group_faces(self.raw_folder)

        # Step 1: Delete the face group folder
        self.preprocess_memory.face_processor.delete_group(face_tag)

        # Step 2: Remove from face_list
        if self.augment_context.face_list:
            original_count = len(self.augment_context.face_list)
            self.augment_context.face_list = [
                face for face in self.augment_context.face_list if face['face_tag'].lower() != face_tag.lower()
            ]
            removed_count = original_count - len(self.augment_context.face_list)

            # Save updated face list
            face_list_path = os.path.join(self.vector_db_folder, 'face_list.json')
            with open(face_list_path, 'w', encoding='utf-8') as f:
                json.dump(self.augment_context.face_list, f, ensure_ascii=False, indent=4)

        # Step 3: Remove tags from memory content
        for item in self.memory_content_processed:
            if 'content' in item and 'face_tags' in item['content'] and face_tag in item['content']['face_tags']:
                item['content']['face_tags'].remove(face_tag)
        self.augment_context.memory_content_processed = self.memory_content_processed
        self.preprocess_memory.memory_content_processed = self.memory_content_processed

        # Save updated memory content
        memory_file = os.path.join(self.processed_folder, "memory_content_processed.json")
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_content_processed, f, ensure_ascii=False, indent=4)

        print(f"Deleted face tag '{face_tag}' and removed {removed_count} associated faces.")
        return True


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
