# TODO: fix the bug in headless mode
# TODO: Format text in textbox
# TODO: add waiting text when calling chatgpt

import json
import logging

import pandas as pd
from simpletransformers.classification import ClassificationModel, ClassificationArgs

with open(r'/engines/chatbot/intents.json', 'rb') as file:
    intents = json.load(file)


def preprocess_intents(intents_):
    data = {'text': [], 'labels': []}
    for i, elem in enumerate(intents_['intents']):
        for p in elem['patterns']:
            data['text'].append(p)
            data['labels'].append(elem['tag'])
    data = pd.DataFrame(data)
    labels_to_int = {label: i for i, label in enumerate(data.labels.unique())}
    data.labels = data.labels.map(labels_to_int)
    data = data.sample(frac=1)
    int_to_labels = {value: key for key, value in labels_to_int.items()}
    return data, int_to_labels


def split_data(df, eval_frac):
    n_rows = int(len(df) * eval_frac)
    return df.iloc[:-n_rows], df.iloc[-n_rows:]


def train_model():
    logging.basicConfig(level=logging.INFO)
    transformers_logger = logging.getLogger("transformers")
    transformers_logger.setLevel(logging.WARNING)

    data, int_to_labels = preprocess_intents(intents)
    train_df, eval_df = split_data(data, eval_frac=0.3)

    model_args = ClassificationArgs(num_train_epochs=3)

    # Create a ClassificationModel
    model = ClassificationModel(
        'bert',
        'dbmdz/bert-base-italian-uncased',
        num_labels=len(int_to_labels),
        args=model_args,
        use_cuda=False
    )
    model.train_model(train_df)

    # Evaluate the model
    result, model_outputs, wrong_predictions = model.eval_model(eval_df)

    model.save_model('bert')

    return result, model_outputs, wrong_predictions


if __name__ == '__main__':
    result, model_outputs, wrong_predictions = train_model()
    print(result)
