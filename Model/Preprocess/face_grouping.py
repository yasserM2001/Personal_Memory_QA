from deepface import DeepFace
import os

class FaceGrouper:
    def __init__(self, face_folder="detected_faces", output_folder="grouped_faces"):
        self.face_folder = face_folder
        self.output_folder = output_folder
        os.makedirs(self.output_folder, exist_ok=True)

    def group_faces(self):
        faces = os.listdir(self.face_folder)
        grouped_faces = {}
        for face in faces:
            face_path = os.path.join(self.face_folder, face)
            try:
                result = DeepFace.find(img_path=face_path, db_path=self.output_folder, enforce_detection=False)
                if not result.empty:
                    group_id = result['identity'][0].split('/')[-2]
                    if group_id not in grouped_faces:
                        grouped_faces[group_id] = []
                    grouped_faces[group_id].append(face)
                else:
                    group_id = len(grouped_faces)
                    os.makedirs(os.path.join(self.output_folder, str(group_id)), exist_ok=True)
                    shutil.copy(face_path, os.path.join(self.output_folder, str(group_id), face))
                    grouped_faces[group_id] = [face]
            except Exception as e:
                print(f"Error processing {face}: {e}")
        return grouped_faces