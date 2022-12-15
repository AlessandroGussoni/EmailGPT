import random


class ChatBot:

    def __init__(self,
                 language_model_path,
                 class_mapping,
                 intents_path):

        self.language_model = ClassificationModel()
        self.class_mapping = class_mapping
        self.intents_path = intents_path

    def answer(self, text):
        intent = self.language_model.predict(text)
        text_intent = self.class_mapping[intent]
        for format_ in self.intents_path['intents']:
            if text_intent == format_['tag']:
                intent_data = format_.copy()
                break
        return random.choice(intent_data['responses'])