import cv2
from face_grouping import FaceGrouper
import os
import torch
import uuid
from facenet_pytorch import MTCNN
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np


class FaceProcessor:
    def __init__(self, directory="extracted_faces") -> None:
        self.directory = directory
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.mtcnn = MTCNN(keep_all=True, device=self.device)

    def show_extracted_faces(self, faces, title="Extracted Faces"):
        num_faces = len(faces)
        cols = min(5, num_faces)
        rows = (num_faces + cols - 1) // cols  

        plt.figure(figsize=(15, rows * 3))
        for i, face in enumerate(faces):
            path = os.path.join(self.directory, face)
            if not os.path.exists(path):
                print(f"File {path} does not exist.")
                continue
            img = Image.open(path)
            plt.subplot(rows, cols, i + 1)
            plt.imshow(img)
            plt.axis("off")
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        plt.show()

    def extract_faces(self, image_path, confidence_threshold=0.9, count=0):
        os.makedirs(self.directory, exist_ok=True)

        image = Image.open(image_path)
        boxes, probs = self.mtcnn.detect(image)
        face_images = []
        if boxes is not None:
            for i, (box, prob) in enumerate(zip(boxes, probs)):
                # print(f"Box {i}: {box}, Probability: {prob}")
                if prob < confidence_threshold:
                    continue  # Skip low confidence

                left, top, right, bottom = map(int, box)
                face = image.crop((left, top, right, bottom))

                # face_id = str(uuid.uuid4())[:8]

                face_name = f"face_{count}.jpg"
                face_path = os.path.join(self.directory, face_name)
                face.save(face_path)
                face_images.append(face_name)
                count += 1

        return face_images
  
    def extract_all_faces(self, images_root_path, confidence_threshold=0.9):
        os.makedirs(self.directory, exist_ok=True)
        face_images = []
        for image_name in os.listdir(images_root_path):
            image_path = os.path.join(images_root_path, image_name)
            if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue
            faces = self.extract_faces(image_path, confidence_threshold, count=len(face_images))
            face_images.extend(faces)

        print(f"Extracted {len(face_images)} faces from {len(os.listdir(images_root_path))} images.")
        return face_images

    def extract_all_faces(self, images_root_path, confidence_threshold=0.9):
        os.makedirs(self.directory, exist_ok=True)
        
        face_images = []
        face_to_image_map = {}

        count = 0
        for image_name in os.listdir(images_root_path):
            if not image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            image_path = os.path.join(images_root_path, image_name)
            faces = self.extract_faces(image_path, confidence_threshold, count=count)

            for face_file in faces:
                face_to_image_map[face_file] = image_name
                count += 1

            face_images.extend(faces)

        print(f"Extracted {len(face_images)} faces from {len(os.listdir(images_root_path))} images.")
        return face_images, face_to_image_map



if __name__ == "__main__":
    face_processor = FaceProcessor()
    root_path = "images"
    detected_faces, detected_faces_map = face_processor.extract_all_faces(root_path, confidence_threshold=0.9)
    print(f"Detected faces: {detected_faces}")
    print()
    print(f"Detected faces map: {detected_faces_map}")
    face_processor.show_extracted_faces(detected_faces, title="Extracted Faces")

    face_grouping = FaceGrouper(face_to_image_map=detected_faces_map, detection_faces=detected_faces)
    face_grouping.group_faces()
    print("Faces grouped successfully.")
    print('*' * 50)

    face_grouping.show_grouped_faces('Person_8')
    new_name = input("Enter new name for group: ")
    face_grouping.change_group_name("Person_8", new_name)

    face_grouping.save_all()