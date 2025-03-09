from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle

SCREEN_RESOLUTION = (2880, 1800)
GRID_COLS, GRID_ROWS = 10, 20
WINDOW_BG_COLOR = (0.1, 0.1, 0.1, 1)
BASE_FONT_SIZE = SCREEN_RESOLUTION[1] * 0.04
LabelBase.register(name="Jersey10", fn_regular="./font/Jersey10-Regular.ttf")


class HowToPlayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = SCREEN_RESOLUTION

        main_layout = BoxLayout(orientation="vertical", size=SCREEN_RESOLUTION)
        main_layout.canvas.before.add(Color(*WINDOW_BG_COLOR))
        main_layout.canvas.before.add(
            Rectangle(size=SCREEN_RESOLUTION, pos=main_layout.pos)
        )

        button_width = SCREEN_RESOLUTION[0] * 0.15
        button_height = SCREEN_RESOLUTION[1] * 0.06
        padding = SCREEN_RESOLUTION[1] * 0.02

        top_layout = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=button_height + padding * 2,
            padding=(padding, padding),
        )

        back_button = Button(
            text="Back to Menu",
            size_hint=(None, None),
            size=(button_width, button_height),
            font_name="Jersey10",
            font_size=BASE_FONT_SIZE * 0.8,
        )
        back_button.bind(on_press=self.go_back)

        top_layout.add_widget(back_button)
        top_layout.add_widget(Label())

        vertical_layout = BoxLayout(orientation="vertical")

        top_spacer = Label(size_hint=(1, 0.1))
        vertical_layout.add_widget(top_spacer)

        content_layout = AnchorLayout(
            anchor_x="center",
            anchor_y="top",
            size_hint=(1, 0.7),
        )

        instructions_container = BoxLayout(
            orientation="vertical",
            size_hint=(None, None),
            width=SCREEN_RESOLUTION[0] * 0.6,
            height=SCREEN_RESOLUTION[1] * 0.5,
            spacing=SCREEN_RESOLUTION[1] * 0.025,
        )

        title_label = Label(
            text="Tetris Controls",
            font_size=BASE_FONT_SIZE * 2,
            font_name="Jersey10",
            halign="center",
            valign="middle",
            size_hint=(1, None),
            height=BASE_FONT_SIZE * 3,
        )
        title_label.text_size = (instructions_container.width, None)
        instructions_container.add_widget(title_label)

        spacer = Label(size_hint=(1, None), height=BASE_FONT_SIZE * 0.5)
        instructions_container.add_widget(spacer)

        instructions = [
            "W - Soft Drop",
            "A - Move Left",
            "D - Move Right",
            "Arrow Right - Rotate Clockwise",
            "Arrow Left - Rotate Counterclockwise",
        ]

        for text in instructions:
            label = Label(
                text=text,
                font_size=BASE_FONT_SIZE * 1.1,
                font_name="Jersey10",
                halign="center",
                valign="middle",
                size_hint=(1, None),
                height=BASE_FONT_SIZE * 1.5,
            )
            label.text_size = (instructions_container.width, None)
            instructions_container.add_widget(label)

        content_layout.add_widget(instructions_container)

        vertical_layout.add_widget(content_layout)

        bottom_spacer = Label(size_hint=(1, 0.2))
        vertical_layout.add_widget(bottom_spacer)

        main_layout.add_widget(top_layout)
        main_layout.add_widget(vertical_layout)

        self.add_widget(main_layout)

    def go_back(self, instance):
        self.manager.current = "menu_screen"
