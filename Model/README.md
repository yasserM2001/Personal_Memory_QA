# Personal Memory QA

A question-answering system for personal memories that utilizes metadata extraction and natural language processing to answer questions about your personal history and experiences.

## Features

- Extract metadata from personal files (images, videos)
- Natural language processing for question understanding
- Context-based answer generation

## Installation

### Prerequisites

- Python 3.8 or higher
- Git
- OpenAI API key
- ExifTool (for metadata extraction)

### Setup Instructions

1. **Clone the repository**
    ```bash
    git clone https://github.com/yasserM2001/Personal_Memory_QA.git
    cd Personal_Memory_QA/Model
    ```

2. **Install the required dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Install ExifTool for extracting metadata from media**

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

4. **Set up the environment variables**
    - Create a new file named `.env` in the Model directory of the project.
    - Add your OpenAI API key to the `.env` file as follows:
      ```bash
      OPENAI_API_KEY=your_openai_api_key_here
      ```

5. **Prepare your media files**
    - Create a folder named `images` inside the project directory.
    - Place all images that need to be processed inside this folder.

## Usage

After setting up the project, you can run the application from Model directory using:
```bash
python main.py
```

This will start the system, allowing you to process images and ask questions based on the extracted metadata.

