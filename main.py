from PIL import Image

from ProcessMemoryContent import ProcessMemoryContent

pmc = ProcessMemoryContent(raw_data_folder=r"images\\dataset_sample",
                            processed_folder=r"data\\processed",
                            ## pass these if using memex dataset photos
                            is_training_data=True,
                            json_data_file_path=r"dataset\\photo_info.json")
pmc.process()

# from transformers import BlipProcessor, BlipForConditionalGeneration

# # Load the processor and model
# processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
# model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

# # Load and preprocess the image
# image = Image.open(r"images\\dataset_sample\\7627277724.jpg").convert("RGB")
# inputs = processor(image, return_tensors="pt")

# # Generate caption
# out = model.generate(**inputs)
# print(out)

# # Decode the output tokens to text
# caption = processor.decode(out[0], skip_special_tokens=True)
# print("Generated Caption:", caption)