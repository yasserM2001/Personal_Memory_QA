from LLM.llm import OpenAIWrapper
from datetime import datetime

class QueryAugmentation():
    def __init__(self,
                 query,
                 detect_faces=False) -> None:
        self.query = query
        self.detect_faces = detect_faces

        self.llm = OpenAIWrapper()

    def augment(self, specified_date=""):
        # parse temporal info
        if specified_date:
            today = specified_date    
        else:
            today = datetime.today()
            today = today.strftime("%Y-%m-%d")

        result, cost = self.llm.augment_query(self.query, today, self.detect_faces)

        return result, cost