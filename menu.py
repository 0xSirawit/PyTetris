from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
import pygame

# เมนูเกม
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        title = Label(text="Tetris Game", font_size=32, size_hint=(1, 0.1))

        btn_start = Button(
            text="Start Game",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(0.2, 0.6, 1, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        btn_high_scores = Button(
            text="High Scores",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(0.1, 0.7, 0.3, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )
        btn_exit = Button(
            text="Exit",
            font_size=20,
            size_hint=(0.3, 0.1),
            background_color=(1, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5},
        )

        btn_start.bind(on_press=self.start_game)
        btn_high_scores.bind(on_press=self.show_high_scores)
        btn_exit.bind(on_press=lambda : App.get_running_app().stop())

        layout.add_widget(title)
        layout.add_widget(btn_start)
        layout.add_widget(btn_high_scores)
        layout.add_widget(btn_exit)
        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = 'game_screen'  # เปลี่ยนไปหน้าจอเกม

    def show_high_scores(self, instance):
        content = BoxLayout(orientation="vertical")
        content.add_widget(Label(
            text="High Scores:\n1. Player1 - 10000\n2. Player2 - 8000\n3. Player3 - 6000",
            font_size=24
        ))
        close_btn = Button(text="Close", size_hint=(1, 0.2))
        content.add_widget(close_btn)

        popup = Popup(title="High Scores", content=content, size_hint=(0.8, 0.8))
        close_btn.bind(on_press=popup.dismiss)
        popup.open()

# หน้าจอเกม
class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='Game is running!', font_size=24))
        self.add_widget(layout)

# แอปหลัก
class GameApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu_screen'))
        sm.add_widget(GameScreen(name='game_screen'))
        return sm

if __name__ == "__main__":
    app = GameApp()
    app.run()
