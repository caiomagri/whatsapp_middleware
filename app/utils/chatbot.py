import os
import requests


class Chatbot:
    @staticmethod
    def call(text: str):
        endpoint = os.environ["CHATBOT_ENDPOINT"]
        payload = {"question": text}
        response = requests.post(endpoint, json=payload)
        return response
