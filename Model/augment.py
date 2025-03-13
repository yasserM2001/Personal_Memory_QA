import numpy as np
import json
import os

from datetime import datetime
from tqdm import tqdm

from LLM.llm import OpenAIWrapper

from utils import parse_memory_to_string

class AugmentContext():
    def __init__(
            self,
            memory_content_processed: list,
            debug = False,
    ) -> None:
        self.memory_content_processed = memory_content_processed

        self.composite_context = []
        self.composite_context_embeddings = None

        self.knowledge = []
        self.knowledge_embeddings = None

        self.llm = OpenAIWrapper()
        self.cost = 0
        
        self.caption_list = []
        self.location_list = []

        self.debug = debug

        self.augment()

    def update_vector_db_and_list(self, category, new_element, memory_id):
        print("*"*50)
        print(f"Category : {category}")
        print(f"New Element : {new_element}")
        print(f"ID : {memory_id}")
        new_emb = self.llm.calculate_embeddings(new_element)
        if new_emb is None:
            return
        
        if category == 'objects':
            vector_db = self.objects_vector
            element_list = self.objects_list
        elif category == 'people':
            vector_db = self.people_vector
            element_list = self.people_list
        elif category == 'activities':
            vector_db = self.activities_vector
            element_list = self.activities_list
        else:
            return
        
        if vector_db is None or len(vector_db) == 0:
            vector_db = np.array(new_emb).reshape(1, -1)
            element_dict = {f'{category}': new_element, 'memory_ids': [memory_id]}
            element_list.append(element_dict)
            print(f"Element List : \n {element_list}")
            if category == 'objects':
                self.objects_vector = vector_db
                self.objects_list = element_list
            elif category == 'people':
                self.people_vector = vector_db
                self.people_list = element_list
            elif category == 'activities':
                self.activities_vector = vector_db
                self.activities_list = element_list
            return vector_db, element_list
        
        emb_vertical = np.array(new_emb).reshape(-1, 1)
        similarities = np.matmul(vector_db, emb_vertical)  ## Cosine similarity
        similarities = similarities.flatten()

        if self.debug : 
            for element in element_list:
                print(element[category], end=" , ")
            print()
            print("************")
            print(similarities)
            print(element_list)


        max_similarity = max(similarities)
        if max_similarity > 0.8:
            index = np.argmax(similarities)
            combined_memory_ids = list(set(element_list[index]['memory_ids'] + [memory_id]))
            element_list[index]['memory_ids'] = combined_memory_ids
        else:
            element_dict = {f'{category}': new_element, 'memory_ids': [memory_id]}
            element_list.append(element_dict)
            vector_db = np.vstack([vector_db, new_emb])

        if category == 'objects':
            self.objects_vector = vector_db
            self.objects_list = element_list
        elif category == 'people':
            self.people_vector = vector_db
            self.people_list = element_list
        elif category == 'activities':
            self.activities_vector = vector_db
            self.activities_list = element_list

    def augment_atomic_context(self):
        # TODO 
        # merge similar object / people / activities and save them in a vector database

        if not os.path.exists('data/vector_db'):
            os.makedirs('data/vector_db')

        objects_vector_db_path = 'data/vector_db/objects_vector_db.npy'
        people_vector_db_path = 'data/vector_db/people_vector_db.npy'
        activities_vector_db_path = 'data/vector_db/activities_vector_db.npy'

        objects_list_path = 'data/vector_db/objects_list.json'
        people_list_path = 'data/vector_db/people_list.json'
        activities_list_path = 'data/vector_db/activities_list.json'

        if os.path.exists(objects_vector_db_path):
            self.objects_vector = np.load(objects_vector_db_path)
            self.people_vector = np.load(people_vector_db_path)
            self.activities_vector = np.load(activities_vector_db_path)

            with open(objects_list_path, 'r') as f:
                self.objects_list = json.load(f)
            with open(people_list_path, 'r') as f:
                self.people_list = json.load(f)
            with open(activities_list_path, 'r') as f:
                self.activities_list = json.load(f)
            return

        self.objects_vector = None
        self.people_vector = None
        self.activities_vector = None

        self.objects_list = []
        self.people_list = []
        self.activities_list = []

        for memory in tqdm(self.memory_content_processed[:]):
            memory_id = memory['filename']
            objects = memory['content']['objects']
            people = memory['content']['people']
            activities = memory['content']['activities']

            if isinstance(objects, list):
                for obj in objects:
                    self.update_vector_db_and_list('objects', obj, memory_id)
            elif isinstance(objects, str):
                self.update_vector_db_and_list('objects', objects, memory_id)

            if isinstance(people, list):
                for person in people:
                    if isinstance(person, dict):
                        person = person.get('description', '')
                    self.update_vector_db_and_list('people', person, memory_id)
            elif isinstance(people, str):
                self.update_vector_db_and_list('people', people, memory_id)

            if isinstance(activities, list):
                for activitiy in activities:
                    self.update_vector_db_and_list('activities', activitiy, memory_id)
            elif isinstance(activities, str):
                self.update_vector_db_and_list('activities', activities, memory_id)
        # save

        np.save(objects_vector_db_path, self.objects_vector)
        np.save(people_vector_db_path, self.people_vector)
        np.save(activities_vector_db_path, self.activities_vector)

        with open(objects_list_path, 'w') as f:
            json.dump(self.objects_list, f, indent=4)
        with open(people_list_path, 'w') as f:
            json.dump(self.people_list, f, indent=4)
        with open(activities_list_path, 'w') as f:
            json.dump(self.activities_list, f, indent=4)

    def augment_location(self):
        location_vector_db_path = 'data/vector_db/location_vector_db.npy'
        location_list_path = 'data/vector_db/location_list.json'

        if os.path.exists(location_vector_db_path):
            self.location_vector_db = np.load(location_vector_db_path)
            with open(location_list_path, 'r') as f:
                self.location_list = json.load(f)
            return
        
        self.location_vector_db = None
        self.location_list = []

        for memory in tqdm(self.memory_content_processed[:]):
            memory_id = memory['filename']
            location = memory['metadata']['location'].get('address', '')

            if not location or location == '':
                continue

            emb = self.llm.calculate_embeddings(location)
            if emb is None:
                continue

            if self.location_vector_db is None:
                self.location_vector_db = np.array(emb).reshape(1, -1)
                self.location_list = [{'location': location, 'memory_ids': [memory_id]}]

            # update location list
            emb_vertical = np.array(emb).reshape(-1, 1)
            similarities = np.matmul(self.location_vector_db, emb_vertical)
            similarities = similarities.flatten()

            max_similarity = max(similarities)
            if max_similarity > 0.8:
                index = np.argmax(similarities)
                combined_memory_ids = list(set(self.location_list[index]['memory_ids'] + [memory_id]))
                self.location_list[index]['memory_ids'] = combined_memory_ids
            else:
                self.location_list.append({'location': location, 'memory_ids': [memory_id]})
                self.location_vector_db = np.vstack([self.location_vector_db, emb])
            
        # save
        np.save(location_vector_db_path, self.location_vector_db)
        with open(location_list_path, 'w') as f:
            json.dump(self.location_list, f, indent=4)
    
    def augment_text_and_speech(self):
        if not os.path.exists('data/vector_db'):
            os.makedirs('data/vector_db')
        
        text_vector_db_path = 'data/vector_db/text_vector_db.npy'
        text_list_path = 'data/vector_db/text_list.json'

        if os.path.exists(text_vector_db_path):
            self.text_vector_db = np.load(text_vector_db_path)
            with open(text_list_path, 'r') as f:
                self.text_list = json.load(f)
            return
        
        self.text_vector_db = None
        self.text_list = []

        for memory in tqdm(self.memory_content_processed[:]):
            memory_id = memory['filename']
            memory_content = memory['content']
            text = memory_content.get('text', '')
            speech = memory_content.get('speech', '')

            if text and text != '':
                try:
                    emb = self.llm.calculate_embeddings(text)
                    if emb is not None:
                        if self.text_vector_db is None:
                            self.text_vector_db = np.array(emb).reshape(1, -1)
                            self.text_list.append({'text': text, 'memory_ids': [memory_id]})
                        else:
                            self.text_vector_db = np.vstack([self.text_vector_db, emb])
                            self.text_list.append({'text': text, 'memory_ids': [memory_id]})
                except:
                    # the text might be too long, exceed the token limit
                    # chunk the text first
                    texts = self.llm.chunking_text(text)
                    texts = texts.get('chunks', [])
                    for t in texts:
                        emb = self.llm.calculate_embeddings(t)
                        if emb is not None:
                            if self.text_vector_db is None:
                                self.text_vector_db = np.array(emb).reshape(1, -1)
                                self.text_list.append({'text': t, 'memory_ids': [memory_id]})
                            else:
                                self.text_vector_db = np.vstack([self.text_vector_db, emb])
                                self.text_list.append({'text': t, 'memory_ids': [memory_id]})

            if speech and speech != '':
                emb = self.llm.calculate_embeddings(speech)
                if emb is not None:
                    if self.text_vector_db is None:
                        self.text_vector_db = np.array(emb).reshape(1, -1)
                        self.text_list.append({'text': speech, 'memory_ids': [memory_id]})
                    else:
                        self.text_vector_db = np.vstack([self.text_vector_db, emb])
                        self.text_list.append({'text': speech, 'memory_ids': [memory_id]})

        # save
        np.save(text_vector_db_path, self.text_vector_db)
        with open(text_list_path, 'w') as f:
            json.dump(self.text_list, f, indent=4)


    def augment(self):
        print("Indexing atomic context...")
        self.augment_atomic_context()
        self.augment_location()

        print("Indexing text and speech...")
        self.augment_text_and_speech()
        
        print("Indexing captions...")
        self.generate_caption_vector_db()

        # print("Inferring composite context...")
        # self.augment_slide_window()

        # print("Indexing whole memory for RAG...")
        # self.generate_vector_db_for_rag()

        # embeddings (vector db) will be saved in /vector_db folder
        # all other processed context and knowledge will be saved in the context.json file in /processed folder