import cv2
from face_grouping import FaceGrouper
import os
import torch
import uuid
from facenet_pytorch import MTCNN
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import shutil

class FaceProcessor:
    def __init__(self, directory="extracted_faces", output_folder="grouped_faces") -> None:
        self.directory = directory
        self.output_folder = output_folder

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.face_grouper = None

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

        image = Image.open(image_path).convert("RGB")
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
    
    def process_and_group_faces(self, images_root_path, confidence_threshold=0.9):
        UP_TO_DATE_FLAG = False

        if os.path.exists(self.output_folder):
            images_time = os.path.getmtime(images_root_path)
            output_time = os.path.getmtime(self.output_folder)
            if images_time < output_time:
                UP_TO_DATE_FLAG = True

        if UP_TO_DATE_FLAG:
            print("Output folder is up to date. No need to process images.")
            self.face_grouper = FaceGrouper(face_folder=self.directory,
                                        output_folder=self.output_folder,
                                        images_folder=images_root_path)
        else:
            print("Output folder is outdated. Processing images.")
            if os.path.exists(self.output_folder):
                shutil.rmtree(self.output_folder)
                print(f"[INFO] Deleted existing output folder: {self.output_folder}")
            if os.path.exists(self.directory):
                shutil.rmtree(self.directory)
                print(f"[INFO] Deleted existing face folder: {self.directory}")

            face_images, face_to_image_map = self.extract_all_faces(images_root_path, confidence_threshold)
            self.face_grouper = FaceGrouper(face_to_image_map=face_to_image_map, 
                                            detection_faces=face_images, 
                                            face_folder=self.directory, 
                                            output_folder=self.output_folder, 
                                            images_folder=images_root_path)
            
            self.face_grouper.group_faces()

        return self.face_grouper
    
    def change_group_name(self, old_name, new_name, debug=False):
        if self.face_grouper:
            done = self.face_grouper.change_group_name(old_name, new_name)
            if debug:
                self.face_grouper.show_grouped_faces(new_name)
            self.face_grouper.save_all() if done else None
        else:
            print("Face grouper not initialized. Please run process_and_group_faces first.")

if __name__ == "__main__":
    face_processor = FaceProcessor(directory="Face_Processing/extracted_faces", 
                                   output_folder="Face_Processing/grouped_faces")
    
    root_path = "images"
    face_processor.process_and_group_faces(root_path, confidence_threshold=0.9)
    face_processor.change_group_name("Person_0", "Yasser")
    face_processor.change_group_name("Person_1", "Morsy")
    face_processor.change_group_name("Person_2", "Mira")
    face_processor.change_group_name("Person_5", "Yasser", debug=True)