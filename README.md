# Personal Memory QA

A **question-answering system** that processes personal images and videos, extracts metadata, and answers questions based on memories.

## Features

- Extracts metadata (timestamps, locations, texts, objects) from images/videos
- Uses NLP to process and understand user queries
- Provides context-based answers from extracted memory data
- API-based architecture for easy integration with other platforms

## Project Structure

```plaintext
Personal_Memory_QA/
│── Backend/       # Handles user authentication, query routing
│── Frontend/      # User interface for uploading images & asking questions
│── Model/         # AI processing, metadata extraction, and question answering
│── .gitignore      
│── README.md      # (This file)
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key
- ExifTool (for metadata extraction)
- FastApi (for integeraation with backend)

### Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yasserM2001/Personal_Memory_QA.git
cd Personal_Memory_QA
```

### 2. Set Up and Run Each Component

#### Model
The model is responsible for processing media files and answering queries.
1. **Install the required dependencies**

    ```bash
    cd Model
    pip install -r requirements.txt
    ```

2. **Install ExifTool for extracting metadata from media**

    #### Windows Installation:
    - Download ExifTool from [exiftool.org](https://exiftool.org/).
    - Unzip the downloaded file.
    - Rename `exiftool(-k).exe` to `exiftool.exe`.
    - Add ExifTool to the system PATH:
        1. Open the Start Menu and search for "Edit the system environment variables".
        2. In the System Properties window, click on the "Environment Variables" button.
        3. Under "System variables", find the `Path` variable and click "Edit".
        4. Click "New" and add the path to the directory where `exiftool.exe` is located (e.g., `C:\Tools\ExifTool`).
        5. Click "OK" to save the changes.
    - Verify installation with:
    
      ```bash
      exiftool -ver
      ```

3. **Set up the environment variables**
    - Create a new file named `.env` in the Model directory of the project.
    - Add your OpenAI API key to the `.env` file as follows:
      ```bash
      OPENAI_API_KEY=your_openai_api_key_here
      ```

### Backend

### Frontend


## How to Run the Project

Run the system in this order:

### 1. Start the Model API
Navigate to the `Model` folder and follow its [README.md](Model/README.md) to set up and start the model server:

```bash
cd Model
# python main.py
```

### 2. Start the Backend
In the `Backend` folder, start the API that connects the model with the frontend:

```bash
cd ../Backend
# python app.py  # Adjust based on your backend framework
```

### 3. Start the Frontend
Finally, launch the frontend UI:

```bash
cd ../Frontend
# npm install  # If using React/Angular
# npm start
```

## How to Use

1. **Upload images/videos** via the frontend.
2. **Ask questions** about the uploaded media.
3. **Receive answers** based on extracted metadata and AI processing.

---

For detailed installation instructions and dependencies, see the `README.md` in each folder (Model, Backend, Frontend).