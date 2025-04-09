# Model Component - Personal Memory QA  

This module handles **metadata extraction, query processing, and LLM-based question answering** for the **Personal Memory QA** system.  

## Project Structure  

```plaintext
Model/
│── data/                 # Stores outout of preprocessing processed data & vector database
│   ├── processed/        # Preprocessed extracted metadata
│   ├── vector_db/        # Stores vectorized embeddings for search
│── LLM/                  # Large Language Model (LLM) integration
│   ├── llm.py            # Main LLM interaction logic
│   └── prompt_templates.py  # Predefined prompts for better query handling
│── Preprocess/           # Data preprocessing components
│   ├── augment.py        # Augmentation techniques for better memory representation
│   ├── memory.py         # Processes and structures memory data
│   ├── metadata_extractor.py  # Extracts metadata (timestamps, location, capture method)
│   └── ProcessMemoryContent.py  # Converts media into structured memory representations
│── Query/                # Query processing logic
│   ├── query.py          # Core logic for answering user queries
│   └── query_augment.py  # Enhances queries using context from extracted metadata
│── Testing_Dataset/      # Scripts for dataset-based testing (Memex Dataset)
│   ├── downloader.py     # Dowloads sample images for users from Memex dataset for testing
│   └── processor.py      # Processes test datasets and get users photos and questions
│── api.py                # FastAPI-based API to serve the model
│── main.py               # Entry point to try the model service
│── ocr.py                # OCR-based text extraction from images
│── requirements.txt      # Dependencies for the model
│── test_api.py           # API endpoint testing
│── tester.py             # Running code on Memex dataset
│── utils.py              # Helper functions
│── README.md             # (This file)
```

---

## How to Run the Model  

You can run the model in different modes depending on your needs.  

### (1️) **Run as an API Server**  

This will start a FastAPI server to handle queries.  

```bash
cd Model
uvicorn api:app --reload
```
---

### (2️) **Run for Direct Question Answering**  

- Create a folder named `images` inside the `Model` directory.
- Place all images that need to be processed inside this folder.

If you want to interact with the model **without starting an API**, use:  

```bash
cd Model
python main.py
```

---

## How to Test the Model  

### **Test API Endpoints**  

Run API tests to verify functionality:  

```bash
python test_api.py
```

### **Test on Memex Dataset**  

To test on dataset make sure `dataset\all_users_photos.json` and `dataset/all_users_questions.json` exists if not use `Testing_Dataset/processor.py` to generate them:  

```bash
python tester.py
```

---

## Notes  

- Ensure `OPENAI_API_KEY` is set in `.env` before running LLM queries.  
- You can adjust prompt settings in **LLM/prompt_templates.py** for better responses.  
- The model uses **vector-based search** stored in `data/vector_db/`.  

---

This README provides a complete guide to understanding and using the model component effectively.

