# from deepface import DeepFace
import os
import shutil
from facenet_pytorch import InceptionResnetV1
import torch
import torchvision.transforms as transforms
from PIL import Image
import numpy as np
import json
import pickle
import matplotlib.pyplot as plt

JSON_FILE = "grouped_faces.json"
EMBEDDINGS_FILE = "embeddings.pkl"
GROUP_TO_IMAGES_FILE = "group_to_images.json"

class FaceGrouper:
    def __init__(self, face_to_image_map, 
                 face_folder="extracted_faces", 
                 output_folder="grouped_faces", 
                 images_folder="images",
                 detection_faces=None):
        
        if detection_faces is None:
            detection_faces = []
            for filename in os.listdir(face_folder):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    detection_faces.append(filename)
        
        self.face_to_image_map = face_to_image_map if face_to_image_map else {}

        self.detection_faces = detection_faces
        self.face_folder = face_folder
        self.output_folder = output_folder
        self.images_folder = images_folder
        os.makedirs(self.output_folder, exist_ok=True)

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)
        self.target_size = (160, 160)
        self.transform = transforms.Compose([
                        transforms.Resize(self.target_size),
                        transforms.ToTensor(),
                        transforms.Normalize([0.5], [0.5])
                    ])
        
        self.faces_embeddings = {}
        self.grouped_faces = {}
        self.group_to_images = {}
        self.load_group_data()

    def load_group_data(self):
        grouped_json_path = os.path.join(self.output_folder, JSON_FILE)
        embeddings_path = os.path.join(self.output_folder, EMBEDDINGS_FILE)
        group_to_images_path = os.path.join(self.output_folder, GROUP_TO_IMAGES_FILE)

        if os.path.exists(grouped_json_path):
            with open(grouped_json_path, "r") as f:
                self.grouped_faces = json.load(f)
            print(f"Loaded grouped faces from {grouped_json_path}")

        if os.path.exists(embeddings_path):
            with open(embeddings_path, "rb") as f:
                self.faces_embeddings = pickle.load(f)
            print(f"Loaded embeddings from {embeddings_path}")
        
        if os.path.exists(group_to_images_path):
            with open(group_to_images_path, "r") as f:
                self.group_to_images = json.load(f)
            print(f"Loaded group to images from {group_to_images_path}")
    
    def group_faces(self):
        if self.group_faces and self.faces_embeddings and self.group_to_images:
            print("Faces already grouped.")
            return
        
        group_id_counter = 0

        for face in self.detection_faces:
            face_path = os.path.join(self.face_folder, face)

            try:
                face_embedding = self.get_face_embedding(face_path)
                group_id = self.find_group(face_embedding)

                if group_id is None:
                    person_i = f"Person_{group_id_counter}"
                    group_id = person_i
                    group_id_counter += 1
                    self.faces_embeddings[group_id] = []
                    self.grouped_faces[group_id] = []

                self.faces_embeddings[group_id].append(face_embedding)
                self.grouped_faces[group_id].append(face)

                original_image = self.face_to_image_map.get(face, "")

                if original_image:
                    if group_id not in self.group_to_images:
                        self.group_to_images[group_id] = set()
                    self.group_to_images[group_id].add(original_image)

            except Exception as e:
                print(f"Error processing {face}: {e}")

        self.save_all()

    def get_face_embedding(self, face_path):
        img = self.transform(Image.open(face_path)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            embedding = self.model(img).cpu().numpy()
        return embedding
    
    def cosine_similarity(self, a, b):
        a = a.flatten()
        b = b.flatten()
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
    def find_group(self, face_embedding, threshold=0.6):
        for group_id, embeddings in self.faces_embeddings.items():
            for existing_emb in embeddings:
                # Compute cosine similarity
                sim = self.cosine_similarity(existing_emb, face_embedding)
                if sim > threshold:
                    return group_id
        return None
    
    def change_group_name(self, old_group_name, new_group_name):
        ## For now, it's case sensitive
        if old_group_name in self.grouped_faces and old_group_name in self.group_to_images:
            if new_group_name in self.grouped_faces and new_group_name in self.group_to_images:
                self.grouped_faces[new_group_name].extend(self.grouped_faces.pop(old_group_name))
                self.faces_embeddings[new_group_name].extend(self.faces_embeddings.pop(old_group_name))
                self.group_to_images[new_group_name].update(self.group_to_images.pop(old_group_name))
            else:
                self.grouped_faces[new_group_name] = self.grouped_faces.pop(old_group_name)
                self.faces_embeddings[new_group_name] = self.faces_embeddings.pop(old_group_name)
                self.group_to_images[new_group_name] = self.group_to_images.pop(old_group_name)
                
            print(f"Group name changed from {old_group_name} to {new_group_name}.")
        else:
            print(f"Group {old_group_name} does not exist.")
    
        self.save_group_data()
        self.save_embeddings_data()

    def save_group_data(self):
        output_json_path = os.path.join(self.output_folder, JSON_FILE)
        with open(output_json_path, "w") as f:
            json.dump(self.grouped_faces, f, indent=4)
        print(f"Grouped faces saved to {output_json_path}")

    def save_embeddings_data(self):
        output_embeddings_path = os.path.join(self.output_folder, EMBEDDINGS_FILE)
        with open(output_embeddings_path, "wb") as f:
            pickle.dump(self.faces_embeddings, f)
        print(f"Embeddings saved to {output_embeddings_path}")

    def save_group_to_images(self):
        json_path = os.path.join(self.output_folder, GROUP_TO_IMAGES_FILE)
        with open(json_path, "w") as f:
            json.dump({k: list(v) for k, v in self.group_to_images.items()}, f, indent=4)
        print(f"Group to image map saved to {json_path}")

    def save_all(self):
        self.save_group_data()
        self.save_embeddings_data() 
        self.save_group_to_images()
        print("All data saved.")

    def show_grouped_faces(self, group_id):
        if group_id in self.grouped_faces:
            faces = self.grouped_faces[group_id]
            num_faces = len(faces)
            cols = min(3, num_faces)
            rows = (num_faces + cols - 1) // cols  

            plt.figure(figsize=(12, rows * 3))
            for i, face in enumerate(faces):
                path = os.path.join(self.face_folder, face)
                if not os.path.exists(path):
                    print(f"File {path} does not exist.")
                    continue
                img = Image.open(path)
                plt.subplot(rows, cols, i + 1)
                plt.imshow(img)
                plt.axis("off")
            plt.suptitle(f"Group: {group_id}", fontsize=16)
            plt.tight_layout()  
            plt.show()
        else:
            print(f"Group {group_id} does not exist.")