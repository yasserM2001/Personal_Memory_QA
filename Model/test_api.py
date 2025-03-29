import requests
from pathlib import Path
import json

url_upload = "http://127.0.0.1:8000/upload_images"
url_init = "http://127.0.0.1:8000/initialize_user_memory"
url_query = "http://127.0.0.1:8000/answer_query"

data = {"user_id": "test1"}

file_paths = [
    "images/IMG_051195.PNG",
    "images/IMG_051410.PNG",
    "images/IMG_051372.jpg",
    "images/IMG_051240.jpg",
    "images/IMG_054510.JPG"
]

# Function to determine the correct MIME type
def get_mime_type(file_path):
    ext = file_path.split(".")[-1].lower()
    if ext in {"jpg", "jpeg", "png"}:
        return "image/jpeg" if ext in {"jpg", "jpeg"} else "image/png"
    return "application/octet-stream"

# Open all files and prepare them for upload
files = [("files", (Path(fp).name, open(fp, "rb"), get_mime_type(fp))) for fp in file_paths]


### UPLOAD FILES
try:
    response = requests.post(url_upload, files=files, data=data)
    print(json.dumps(response.json(), indent=4))
finally:
    # Ensure all files are closed after upload
    for _, file_tuple in files:
        file_tuple[1].close()



### INITIALIZE MEMORY
response = requests.post(url_init, data=data)
print(json.dumps(response.json(), indent=4))


### QUERY PART
params = {
    "user_id": "test1",
    "query": "Where was the photo taken?",
    "method": "memory"
}
response = requests.post(url_query, params=params)
print(json.dumps(response.json(), indent=4))