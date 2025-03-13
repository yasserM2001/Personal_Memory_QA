from openai import OpenAI
from io import BytesIO
import base64
import json

from .prompt_templates import merge_templates_to_dict
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

import re

def count_words(text):
    words = re.split(r'[ \n,.!?():"/;]+', text)
    word_count = len([word for word in words if word])
    
    return word_count


def parse_memory_to_string(memory: dict) -> str:
    filename = memory['filename']

    capture_method = memory['metadata']['capture_method']

    temporal = memory['metadata']['temporal_info']
    date_string = temporal['date_string']
    day_of_week = temporal['day_of_week']
    time_of_the_day = temporal['time_of_the_day']
    temporal_info = f'{date_string}, {day_of_week}, {time_of_the_day}'

    location = memory['metadata']['location']
    address = location.get('address', 'Unknown')

    content = memory['content']

    caption = content.get('caption', '')
    objects = content.get('objects', [])
    people = content.get('people', [])
    activities = content.get('activities', [])
    text = content.get('text', '')
    speech = content.get('speech', '')

    word_count = count_words(text)
    text_in_prompt = text if word_count < 100 else ""

    memory_string = f'''
memory_id: {filename}
capture method: {capture_method}
temporal info: {temporal_info}
location: {address}

Content: 
caption: {caption}
visible objects: {objects}
visible people: {people}
visible text: {text_in_prompt}
heard speech: {speech}
inferred activities: {activities}\n\n'''
    return memory_string


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
        model = 'gpt-4o'

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

    def generate_visual_content(self, image):
        system_prompt = self.templates['prompt_visual_content']

        # create a base64 image
        buff = BytesIO()
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buff, format="JPEG")

        base64_img = base64.b64encode(buff.getvalue()).decode("utf-8")
        user_prompt = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}", "detail": "low"}}]
        messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

        _, result, cost = self._call_api(messages, json_mode=True)
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
 