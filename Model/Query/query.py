import numpy as np
from memory import Memory
from LLM.llm import OpenAIWrapper


class QueryHandler():
    def __init__(self,memory: Memory, debug: bool = False):
        self.memory = memory
        self.llm = OpenAIWrapper()
        self.cost = 0
        self.debug = debug
        if debug: 
            print('*'* 100)
            print("Started Handling Query")
            print('*'* 100)
        self._load_augmented_memory(memory)

    def _load_augmented_memory(self, memory: Memory):
        self.memory_to_query = memory.memory_content_processed.copy()

        augmented_context = memory.augment_context

        self.caption = augmented_context.caption_list
        self.caption_vector = augmented_context.caption_vector_db

        self.text = augmented_context.text_list
        self.text_vector = augmented_context.text_vector_db

        self.objects = augmented_context.objects_list
        self.objects_vector = augmented_context.objects_vector

        self.people = augmented_context.people_list
        self.people_vector = augmented_context.people_vector

        self.activities = augmented_context.activities_list
        self.activities_vector = augmented_context.activities_vector

        self.composite_context = augmented_context.composite_context
        self.composite_context_vector = augmented_context.composite_context_embeddings

        self.knowledge = memory.augment_context.knowledge
        self.knowledge_vector = memory.augment_context.knowledge_embeddings

        self.rag = augmented_context.vector_db_list
        self.rag_vector = augmented_context.vector_db_rag

        self.location_list = augmented_context.location_list
        self.location_vector = augmented_context.location_vector_db

    ## baseline model
    def query_rag(self, query, topk=25):
        query_emb = self.llm.calculate_embeddings(query)
        query_emb = np.array(query_emb).reshape(-1, 1)
        similarities = np.matmul(self.rag_vector, query_emb).flatten()
        
        top_k = np.argsort(similarities)[-topk:][::-1] if len(similarities) > topk else np.argsort(similarities)[::-1]
        
        retrieved_rag = []
        for index in top_k:
            if index < len(self.rag):
                retrieved_rag.append(self.rag[index])

        if self.debug:
            print(f"len(self.rag) = {len(self.rag)}")
            print("Similarities:")
            print(similarities)
            print(f"len Similarities: {len(similarities)}")
            print("Top K")
            print('-------')
            print(f"Top K indices : {top_k}")
            print(f"len Top K: {len(retrieved_rag)}")

        prompt = ""
        for rag in retrieved_rag:
            # prompt += f'memory_id: {rag['memory_ids']}'
            memory_id = rag['memory_ids']
            prompt += f'memory_id: {memory_id} '
            prompt += f'memory: {rag["memory"]}\n'

        response, result, cost = self.llm.query_rag(query, prompt)

        print("RAG API cost: ", cost)
        return result

        
        