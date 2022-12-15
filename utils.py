import pickle


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def control_state(f):
    def inner(self, *args, **kwargs):
        self.textbox.configure(state='normal')
        f(self, *args, **kwargs)
        self.textbox.configure(state='disabled')

    return inner


def load_config():
    try:
        with open('config.pickle', 'rb') as file:
            config = pickle.load(file)
            return config
    except FileNotFoundError:
        return {}


def dump_config(config):
    with open('config.pickle', 'wb') as file:
        pickle.dump(config, file)
