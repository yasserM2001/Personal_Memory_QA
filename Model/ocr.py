from paddleocr import PaddleOCR

# print("Result : \n")
# print(f"Result[0] : {result[0]}")
# print(f"Result[0][0] : {result[0][0]}")
# print(f"Result[0][0][0] (Word Box) : {result[0][0][0]}")
# print(f"Result[0][0][1] (Word itself) : {result[0][0][1]}")

class OCR:
    def __init__(self, confidence_threshold=0.85, debug=False):
        # Initialize the PaddleOCR model
        self.model = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        self.confidence_threshold = confidence_threshold
        self.debug = debug

    def detect_text(self,image_path):
        # Perform OCR on an image
        # cls for Handling Rotated Text
        model_result = self.model.ocr(image_path, cls=True)

        result = []

        if model_result[0] : # if ! [None] 
            # Print the detected text and confidence scores
            for line in model_result:
                for word in line:
                    text = word[1][0]  # Recognized text
                    confidence = word[1][1]  # Confidence score
                    bounding_box = word[0]  # Bounding box coordinates

                    # print(f"Text: {text}, Confidence: {confidence}")
                    if confidence >= self.confidence_threshold:
                        # vertices of box
                        vertices = [
                            {"x": int(point[0]), "y": int(point[1])} for point in bounding_box
                        ]

                        # Add the text and bounding box to the result
                        result.append({
                            "description": text,
                            "bounding_poly": {
                                "vertices": vertices
                            },
                            "confidence": confidence
                        })

        if result:
            return"\n".join([item["description"] for item in result])
        else:
            return ''