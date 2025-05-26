from openai import OpenAI
from io import BytesIO
import base64
import json
from google import genai

from .prompt_templates import merge_templates_to_dict
from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

gemini_api_key = os.getenv("GEMINI_API_KEY")

import re

class LLMWrapper():
    def __init__(self,
                 templates: dict = None,
                 ) -> None:
        self.templates = merge_templates_to_dict() if templates is None else templates

class OpenAIWrapper(LLMWrapper):
    def __init__(self,
                 templates: str = None,
                 model: str = 'gpt-3.5-turbo-0125',
                 ) -> None:
        super().__init__(templates)
        
        self.llm = OpenAI()
        # self.llm = OpenAI(base_url="https://models.inference.ai.azure.com")
        self.model = model


    def _generate_messages(self):
        pass

    def _restructure_result(self, result):
        print("Reformatting the JSON-like text into a correct JSON format.")
        system_prompt = "Reformat the JSON-like text into a correct JSON format. Output the json object."
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": result}]
        response, result, cost = self._call_api(messages, json_mode=True, model='gpt-4o-mini')
        return result, cost

    def _call_api(self, messages, json_mode=False, model=""):
        if model == "":
            model = self.model
        
        #############
        # model = 'gpt-4o'
        # model = 'gpt-3.5-turbo'
        print(f"================================== Calling model: {model} ===================================")

        if model == 'gpt-3.5-2024-08-06':
            max_tokens = 16384
        else:
            max_tokens = 4096

        if json_mode:
            response = self.llm.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        else:
            response = self.llm.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=max_tokens
            )

        if model == 'gpt-4o':
            rate = 0.000005
        elif model == 'gpt-3.5-turbo-0125':
            rate = 0.0000005
        elif model == 'gpt-4o-mini':
            rate = 0.00000015
        else:
            rate = 0.000005
        prompt_token = response.usage.prompt_tokens
        generation_token = response.usage.completion_tokens
        cost = prompt_token*rate + generation_token*rate*3
        result = response.choices[0].message.content

        return response, result, cost

    def generate_visual_content(self, image, face_tags=None):
        system_prompt = self.templates['prompt_visual_content']

        # def resize_image(image, max_size=(800, 800)):
        #         image.thumbnail(max_size)
        #         return image
        
        # image = resize_image(image, max_size=(800, 800))
        # create a base64 image
        buff = BytesIO()
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buff, format="JPEG")

        base64_img = base64.b64encode(buff.getvalue()).decode("utf-8")
        user_prompt = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "low"}}]
        
        # if face_tags is not None:
        #     people_info = f"People tagged in the image: {', '.join(face_tags)}"
        #     user_prompt.append({"type": "text", "content": people_info})
        #     user_prompt = json.dumps(user_prompt)
        
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        _, result, cost = self._call_api(messages, json_mode=True, model='gpt-4o-mini')
        result = json.loads(result)

        return result, cost
    
    def generate_visual_content_video(self, images, speech):
        system_prompt = f"Given frames of a video and the transcribed speech, generate the following information from the video: caption of the video describing the content, visible objects, list of description of visible people, inferred activities of the media owner. Output a JSON object with key: 'caption', 'objects', 'people', 'activities'."

        user_prompt = []
        speech_prompt = {"type": "text", "text": f"transcribed speech: {speech}"}
        user_prompt.append(speech_prompt)
        for image in images:
            buff = BytesIO()
            if image.mode == "RGBA":
                image = image.convert("RGB")
            image.save(buff, format="JPEG")
            base64_img = base64.b64encode(buff.getvalue()).decode("utf-8")

            entry = {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "low"}}
            
            user_prompt.append(entry)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
            ]

        _, result, cost = self._call_api(messages, json_mode=True)
        result = json.loads(result)

        return result, cost
    
    def chunking_text(self, text):
        system_prompt = "Given a long text, chunk the text into smaller segments. Output the list of chunks in a JSON object with the key 'chunks'."
        user_prompt = f"Text: {text}"
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
        response, result, cost = self._call_api(messages, json_mode=True)
        return result, cost

    def calculate_embeddings(self, text, model="text-embedding-3-small"):
        if text == "":
            return None
        return self.llm.embeddings.create(input = [text], model=model).data[0].embedding
    
    def generate_composite_context(self, memory_batch_text):
        system_prompt = self.templates['prompt_composite_context']

        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": memory_batch_text}]
        _, result, cost = self._call_api(messages, json_mode=True)
        try:
            result = json.loads(result)
        except:
            # use gpt-4o-mini to reprocess the result to be json
            result, _ = self._restructure_result(result)
            result = json.loads(result)

        return result, cost
    
    def generate_facts_and_knowledge(self, memory_batch_text):
        system_prompt = self.templates['prompt_facts_knowledge']
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": memory_batch_text}]

        _, result, cost = self._call_api(messages, json_mode=True)
        try:
            result = json.loads(result)
        except:
            # use gpt-4o-mini to reprocess the result to be json
            result, _ = self._restructure_result(result)
            result = json.loads(result)

        return result, cost
    
    def query_rag(self, query, memory_prompt, detect_faces=False, llm='openai'):
        if detect_faces:
            system_prompt = self.templates['prompt_query_rag_update']
        else:
            system_prompt = self.templates['prompt_query_rag']

        user_prompt = f"Query: {query}\n"
        user_prompt += memory_prompt

        if llm == 'gemini':
            print("Using Gemini LLM")
            system_prompt = system_prompt + "\nPlease provide concise and direct answers. Focus on answering the user's question clearly, using as few words as possible while preserving essential information. Avoid repeating details or including irrelevant context. When possible, summarize or infer briefly without listing every memory ID unless necessary for clarity. The memory ids should be the memories most relevant to the answer. If the answer is not in the memories, please say 'I don't know'."

            completed_prompt = f"{system_prompt}\n{user_prompt}"
            response = safe_generate_content(completed_prompt, model_name="gemini-2.0-flash")
            
            text = response.text.strip()
            try:
                result = safe_json_parse(text)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode JSON: {text}")
            
            return response, result, 0.000005 * len(response.text.split())
        elif llm == 'openai':
            print("Using OpenAI LLM")
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            response, result, cost = self._call_api(messages, json_mode=True)
            result = json.loads(result)
            return response, result, cost

    def augment_query(self, query, today, detect_faces=False, llm='openai'):
        if detect_faces:
            system_prompt = self.templates['prompt_augment_query_update']
        else:
            system_prompt = self.templates['prompt_augment_query']

        user_prompt = f"Query: {query}, Today: {today}"

        if llm == 'gemini':
            print("Using Gemini LLM")
            system_prompt = system_prompt + 'Please return all dates in ISO format: YYYY-MM-DD (e.g., 2011-12-01). Do not use formats like "December 1, 2011".'
            completed_prompt = f"{system_prompt}\n{user_prompt}"
            response = safe_generate_content(completed_prompt, model_name="gemini-2.0-flash")
            
            text = response.text.strip()

            try:
                result = safe_json_parse(text)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode JSON: {text}")
            
            return result, 0.000005 * len(response.text.split())
        
        elif llm == 'openai':
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            response, result, cost = self._call_api(messages, json_mode=True)
            result = json.loads(result)
            return result, cost
    
    def filter_related_composite_context(self, query, composite_context, llm='openai'):
        system_prompt = self.templates['prompt_filter_related_composite_context']

        user_prompt = ""
        for context in composite_context:
            event_name = context['event_name']
            context_str = f"event_name: '{event_name}'\n"
            user_prompt += context_str

        if llm == 'gemini':
            print("Using Gemini LLM")
            completed_prompt = f"{system_prompt}\n{user_prompt}\nQuery: {query}"
            response = safe_generate_content(completed_prompt, model_name="gemini-2.0-flash")
            
            text = response.text.strip()
            try:
                result = safe_json_parse(text)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode JSON: {text}")
            
            return result, 0.000005 * len(response.text.split())
        elif llm == 'openai':
            print("Using OpenAI LLM")
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            response, result, cost = self._call_api(messages, json_mode=True)
            result = json.loads(result)
            return result, cost
    
    def query_memory(self, query, memory_prompt, detect_faces=False, llm='openai'):
        if detect_faces:
            system_prompt = self.templates['prompt_query_memory_update']
        else:
            system_prompt = self.templates['prompt_query_memory']

        user_prompt = f"Query: {query}\n"
        user_prompt += memory_prompt

        if llm == 'gemini':
            print("Using Gemini LLM")
            system_prompt = system_prompt + "\nPlease provide concise and direct answers. Focus on answering the user's question clearly, using as few words as possible while preserving essential information. Avoid repeating details or including irrelevant context. When possible, summarize or infer briefly without listing every memory ID unless necessary for clarity. The memory ids should be the memories most relevant to the answer. If the answer is not in the memories, please say 'I don't know'."
            completed_prompt = f"{system_prompt}\n{user_prompt}"
            response = safe_generate_content(completed_prompt, model_name="gemini-2.0-flash")
           
            text = response.text.strip()
            try:
                result = safe_json_parse(text)
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode JSON: {text}")
           
            return response, result, 0.000005 * len(response.text.split())
        elif llm == 'openai':
            print("Using OpenAI LLM")
            messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]
            response, result, cost = self._call_api(messages, json_mode=True)
            result = json.loads(result)
            return response, result, cost
        else:
            raise ValueError("Invalid LLM type. Choose either 'openai' or 'gemini'.")
        
from google.genai.errors import ServerError
import random
import time

def safe_generate_content(prompt, model_name="gemini-2.0-flash", retries=4):
    client = genai.Client(api_key=gemini_api_key)

    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=model_name, contents=prompt)
            return response
        except ServerError as e:
            # print(f"⚠️ Server overloaded (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                wait_time = 2 ** attempt + random.uniform(0, 1)
                # print(f"Retrying in {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            else:
                raise ValueError("Max retries reached. Unable to generate content.")
        except Exception as e:
            # Generic catch for quota or unknown issues
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("⚠️ Quota exceeded. Backing off and retrying...")
                time.sleep(30)
            else:
                raise e
            

def extract_json_block(text):
    # Extract the content inside the first ```json ... ``` block
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        return text.strip()

def clean_and_fix_json(text):
    text = extract_json_block(text)
    # # Step 0: Remove any content before ```json
    # json_start = re.search(r"```json", text)
    # if json_start:
    #     text = text[json_start.end():]  # Skip past ```json

    # Step 1: Remove markdown-style ```json ... ```
    text = re.sub(r"^```json\s*|\s*```$", "", text.strip())

    # Step 2: Convert single quotes to double quotes (only outside lists or numerics)
    # Naively replace single quotes if double quotes not used (Gemini often returns Python-like dicts)
    if "'" in text and '"' not in text:
        text = text.replace("'", '"')

    # Step 3: Remove trailing commas before closing } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Step 4: Replace smart quotes and bad apostrophes
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")

    # Step 3: Fix single-quoted keys: {'key': → {"key":
    text = re.sub(r"([{,]\s*)'([^']+?)'\s*:", r'\1"\2":', text)

    # Step 5: Escape unescaped double quotes inside string values
    def escape_inner_quotes(match):
        content = match.group(0)
        key_value = content.split(":", 1)
        if len(key_value) == 2:
            key, val = key_value
            val = val.strip()
            if val.startswith('"') and val.endswith('"'):
                inner = val[1:-1]
                inner = inner.replace('\\"', 'ESCAPED_QUOTE')
                inner = inner.replace('"', '\\"')
                inner = inner.replace('ESCAPED_QUOTE', '\\"')
                return f'{key}: "{inner}"'
        return content

    text = re.sub(r'"[^"]*"\s*:\s*".*?"', escape_inner_quotes, text)

    return text

def safe_json_parse(text):
    fixed = clean_and_fix_json(text)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode JSON after fixing: \n{fixed}\n{e}") from e

# def safe_json_parse(text, retry_fix=False, original_prompt=None):
#     try:
#         # Basic fix attempt
#         fixed = text.replace("'", '"')
#         fixed = re.sub(r",\s*}", "}", fixed)
#         fixed = re.sub(r",\s*]", "]", fixed)
#         return json.loads(fixed)

#     except json.JSONDecodeError as e:
#         print("❌ Failed to decode JSON. Trying to fix via re-prompt..." if retry_fix else "❌ Failed to decode JSON.")

#         if retry_fix and original_prompt:
#             # Append an instruction to the original prompt to get properly formatted JSON
#             new_prompt = original_prompt + "\n\nPlease reformat your answer strictly as a JSON object using double quotes and no trailing commas."
#             response = safe_generate_content(new_prompt)
#             new_text = response.text if hasattr(response, 'text') else response.candidates[0].content.parts[0].text
#             return safe_json_parse(new_text, retry_fix=False)  # one retry only

#         raise ValueError(f"Failed to decode JSON after fixing: {text}") from e
