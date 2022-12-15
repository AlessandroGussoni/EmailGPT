import threading
import tkinter
import tkinter.messagebox

import customtkinter
import speech_recognition
from PIL import Image

from audio.speech import record_audio, text_to_speech
from connections.gmail.functions import draft_email, get_connected_user
from connections.gmail.service import service
from engines.chatgpt import ChatGPT
from utils import control_state, load_config, dump_config

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    width = 1100
    height = 600
    USERNAME = 'alessandro.gussoni@hotmail.com'
    PASSWORD = 'Ale2996%'

    def __init__(self, chatgpt, use_gpt):
        super().__init__()

        # configure window
        self.chatgpt = chatgpt
        self.use_gpt = use_gpt

        self.loop = bool
        self.speech = False
        self.response = str
        self.active_email = str

        config = load_config()

        # set login page

        self.bg_image = customtkinter.CTkImage(Image.open("bg_gradient.jpg"),
                                               size=(self.width, self.height))
        self.bg_image_label = customtkinter.CTkLabel(self, image=self.bg_image)

        # create login frame
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Log in to OpenAI",
                                                  font=customtkinter.CTkFont(size=20, weight="bold"))
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=200, placeholder_text="username")
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=200, show="*",
                                                     placeholder_text="password")
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_event,
                                                    width=200)
        self.password_entry.bind("<Return>", command=self.login_event)

        self.title("EmailGPT")
        self.geometry(f"{1100}x{580}")

        # configure grid layout (4x4)

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame,
                                                 text="EmailGPT",
                                                 font=customtkinter.CTkFont(size=20, weight="bold"))

        # set start listening button
        self.start_listening = customtkinter.CTkButton(self.sidebar_frame,
                                                       text='Start listening',
                                                       command=self.start_conversation)

        # set stop listening button
        self.stop_listening = customtkinter.CTkButton(self.sidebar_frame,
                                                      text='Stop listening',
                                                      command=self.stop)

        # set stop listening button
        self.audio_check = customtkinter.CTkLabel(self.sidebar_frame,
                                                  text='🤖',
                                                  font=('Arial', 120, 'bold'))

        # set text to speech button
        self.text_to_speech_button = customtkinter.CTkButton(self.sidebar_frame,
                                                             text='Text to speech',
                                                             command=self.text_to_speech,
                                                             fg_color='red')

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)

        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")

        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                               values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")

        self.entry.bind("<Return>", command=self.send_message)

        self.main_button_1 = customtkinter.CTkButton(master=self,
                                                     text='send',
                                                     fg_color="transparent",
                                                     border_width=2,
                                                     text_color=("gray10", "#DCE4EE"),
                                                     command=self.send_message)

        self.main_button_2 = customtkinter.CTkButton(master=self,
                                                     text='Reset thread',
                                                     width=120,
                                                     height=10,
                                                     fg_color="transparent",
                                                     border_width=2,
                                                     text_color=("gray10", "#DCE4EE"),
                                                     command=self.reset_thread)

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)

        # create connections tabview
        self.tabview = customtkinter.CTkTabview(self, width=250)

        self.tabview.add("Gmail")
        self.tabview.add("Outlook")
        self.tabview.add("OpenAI")
        self.tabview.tab("Gmail").grid_columnconfigure(0, weight=1)  # configure grid of individual tabs
        self.tabview.tab("Outlook").grid_columnconfigure(0, weight=1)

        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("Gmail"), dynamic_resizing=False,
                                                        values=["Value 1", "Value 2", "Value Long Long Long"])

        # get current user
        address = get_connected_user(self, service)

        self.gmail_address = customtkinter.CTkLabel(self.tabview.tab("Gmail"),
                                                    text='Connected to: ' + address)

        self.combobox_1 = customtkinter.CTkButton(self.tabview.tab("Gmail"),
                                                  text='Set active',
                                                  command=lambda: self.set_active(self.gmail_address))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("Gmail"),
                                                           text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)

        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Outlook"),
                                                  text="CTkLabel on Tab 2")

        if config:
            self.openai = customtkinter.CTkLabel(self.tabview.tab("OpenAI"),
                                                 text='Connected to: \n' + config['username'])

        self.appearance_mode_optionemenu.set("Light")
        self.scaling_optionemenu.set("100%")
        self.textbox.insert("0.0",
                            "Dialogue\n\n")
        self.textbox.configure(state='disabled')

        if config:
            # setup connection to ChatGPT
            if self.use_gpt:
                self.chatgpt = chatgpt
                self.chatgpt.connect()
                self.chatgpt.login(config['username'], config['password'])

            self.show_components()
        else:
            # show input page
            self.bg_image_label.grid(row=0, column=0)
            self.login_frame.grid(row=0, column=0, sticky="ns")
            self.login_label.grid(row=0, column=0, padx=30, pady=(150, 15))
            self.username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
            self.password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))
            self.login_button.grid(row=3, column=0, padx=30, pady=(15, 15))

    def show_components(self):
        # show application
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.start_listening.grid(row=1, column=0, padx=20, pady=10)
        self.stop_listening.grid(row=2, column=0, padx=20, pady=10)
        self.audio_check.grid(row=4, column=0, padx=20, pady=10)
        self.text_to_speech_button.grid(row=3, column=0, padx=20, pady=10)
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.main_button_2.grid(row=2, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.grid(row=0, column=1, rowspan=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.grid(row=0, column=3, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.gmail_address.grid(row=3, column=0, padx=20, pady=(10, 10))
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        self.openai.grid(row=0, column=0, padx=20, pady=20)

    def login_event(self, event=None):
        print("Login pressed - username:", self.username_entry.get(), "password:", self.password_entry.get())

        config = {'username': self.username_entry.get(),
                  'password': self.password_entry.get()}

        if self.use_gpt:
            self.chatgpt.connect()
            try:
                self.chatgpt.login(config['username'], config['password'])
            except Exception as e:
                print(e)
                pass

        dump_config(config)
        self.openai = customtkinter.CTkLabel(self.tabview.tab("OpenAI"),
                                             text='Connected to: ' + config['username'])
        self.login_frame.grid_forget()  # remove login frame
        self.bg_image_label.forget()
        self.show_components()

    @control_state
    def update_textbox(self, text):
        self.textbox.insert(tkinter.END, '\n\n' + text)
        self.entry.delete(0, len(text) + 1)

    def route_question(self, text):
        self.update_textbox('You: ' + text)
        response = self.get_response(text)
        self.update_textbox('AI: ' + response)
        setattr(self, 'response', response)
        if self.speech:
            text_to_speech(self.response)

        if self.active_email == 'gmail':
            draft_email(self.gmail_service,
                        'test@gmail.com',
                        'ttt@gmail.com',
                        'test_draft',
                        response)

    def get_response(self, text):

        if self.use_gpt:
            return self.chatgpt(text)
        else:
            return 'Risposta esempio da GPT'

    def send_message(self, event=None):
        text = self.entry.get()
        self.route_question(text)

    def open_input_dialog_event(self):
        """dialog = customtkinter.CTkLabel(self,
                                        text="Type in a number:")
        dialog.grid(row=0, column=0)"""
        pass

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def record(self, recognizer):
        self.audio_check.configure(text_color='red')
        while self.loop:
            text = record_audio(recognizer)
            if 'stop' in text:
                self.stop()
            elif text != '':
                self.route_question(text)

    def stop(self):
        self.loop = False
        state = self.appearance_mode_optionemenu.get()
        color = 'black' if state == 'Light' else 'white'
        self.audio_check.configure(text_color=color)

    def start_conversation(self):
        self.loop = True
        thread = threading.Thread(target=self.record,
                                  args=(speech_recognition.Recognizer(),))
        thread.start()

    def text_to_speech(self):
        color_config = {True: 'green',
                        False: 'red'}

        self.speech = not self.speech
        self.text_to_speech_button.configure(fg_color=color_config[self.speech])

    def set_active(self, label_element):
        email = label_element.cget('text')
        self.active_email = 'gmail' if 'gmail' in email else 'outlook'
        label_element.configure(text=email + '\n\nStatus: Active')
        self.open_input_dialog_event()
        print(self.active_email)

    @control_state
    def reset_thread(self):
        self.chatgpt.reset_thread()
        self.textbox.delete('1.0', tkinter.END)
        self.textbox.insert("0.0",
                            "Dialogue\n\n")


if __name__ == "__main__":
    use_gpt = False
    if use_gpt:
        gpt = ChatGPT()
    else:
        gpt = None
    app = App(gpt, use_gpt=use_gpt)
    app.mainloop()
