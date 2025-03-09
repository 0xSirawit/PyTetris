from kivy.app import App 
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

FONT_PATH = "font/Jersey10-Regular.ttf"  

class HowToPlayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        instructions = [
            "\nTetris Controls:\n",
            "W - Soft Drop",
            "A - Move Left",
            "D - Move Right",
            "Arrow Right - Rotate Clockwise",
            "Arrow Left - Rotate Counterclockwise"
        ]
        
        for text in instructions:
            layout.add_widget(Label(text=text, font_size='20sp', font_name=FONT_PATH))  
        
        back_button = Button(text='Back to Menu', size_hint=(None, None), size=(200, 50), font_name=FONT_PATH)
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def go_back(self, instance):
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        title = Label(text='Tetris Game', font_size='30sp', font_name=FONT_PATH) 
        how_to_play_button = Button(text='How to Play', size_hint=(None, None), size=(200, 50), font_name=FONT_PATH)
        how_to_play_button.bind(on_press=self.go_to_how_to_play)
        
        layout.add_widget(title)
        layout.add_widget(how_to_play_button)
        self.add_widget(layout)
    
    def go_to_how_to_play(self, instance):
        self.manager.current = 'how_to_play'

class TetrisApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(HowToPlayScreen(name='how_to_play'))
        return sm

if __name__ == '__main__':
    TetrisApp().run()
