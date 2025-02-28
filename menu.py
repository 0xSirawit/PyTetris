from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        title = Label(text="Tetris Game", font_size=32, size_hint=(1, 0.2))
        btn_start = Button(text="Start Game", font_size=24, on_press=self.start_game)
        btn_high_scores = Button(text="High Scores", font_size=24, on_press=self.show_high_scores)
        btn_exit = Button(text="Exit", font_size=24, on_press=self.stop)

        layout.add_widget(title)
        layout.add_widget(btn_start)
        layout.add_widget(btn_high_scores)
        layout.add_widget(btn_exit)
        return layout

    def start_game(self, instance):
               instance.text = "Starting Game..."
       

    def show_high_scores(self, instance):
      
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text="High Scores:\n1. Player1 - 10000\n2. Player2 - 8000\n3. Player3 - 6000", font_size=24))
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        content.add_widget(close_btn)

        popup = Popup(title='High Scores', content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == "__main__":
    MyApp().run()
