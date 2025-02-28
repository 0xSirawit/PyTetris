from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class MyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        btn1 = Button(text="กดฉันสิ!", font_size=24, on_press=self.on_button_click)
        btn2 = Button(text="ปุ่มที่สอง", font_size=24)

        layout.add_widget(btn1)
        layout.add_widget(btn2)

        return layout

    def on_button_click(self, instance):
        instance.text = "กดแล้ว!"

if __name__ == "__main__":
    MyApp().run()
