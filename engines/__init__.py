def check_attribute(*attrs):
    """
    check if class has input attrs, else raise error
    """

    mapping = {'_connected': 'connect()',
               '_logged': 'login(email, password)',
               '_first_call': '__call__(self, text)'}

    def outer(f):
        def inner(self, *args, **kwargs):

            for attr in attrs:
                if not hasattr(self, attr):
                    raise AttributeError(f'You must call {mapping[attr]} before')
                elif not getattr(self, attr):
                    raise AttributeError(
                        "ChatGPT has only a single try again for a given input prompt. Try sedning new text or reset the thread")

            output = f(self, *args, **kwargs)
            return output

        return inner

    return outer
