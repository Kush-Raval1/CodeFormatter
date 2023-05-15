from pygments import highlight, styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters import ImageFormatter, HtmlFormatter
from tkinter import Tk, Text, Button, Label, StringVar, messagebox, END
from tkinter.ttk import Combobox
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor
import re
import os


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Code to Image Renderer")

        # Initialize the language input
        self.lang_label = Label(root, text="Programming Language:")
        self.lang_label.pack()

        self.lang_entry = Text(root, height=1, width=30)
        self.lang_entry.pack()

        # Initialize the code input
        self.code_label = Label(root, text="Code:")
        self.code_label.pack()

        self.code_input = ScrolledText(root, height=10, width=70)
        self.code_input.pack()

        # Initialize the theme selection
        self.theme_label = Label(root, text="Theme:")
        self.theme_label.pack()

        self.theme_names = list(styles.get_all_styles())
        self.theme_combobox = Combobox(root, values=self.theme_names)
        self.theme_combobox.pack()

        # Initialize the submit button
        self.submit_button = Button(root, text="Submit", command=self.submit)
        self.submit_button.pack()

    def submit(self):
        lang = self.lang_entry.get("1.0", END).strip()  # get language
        code = self.code_input.get("1.0", END)  # get code
        theme = self.theme_combobox.get()  # get theme

        if not lang or not code or not theme:
            messagebox.showerror("Error", "Please provide language, code, and theme!")
        else:
            self.code_to_image(lang, code, theme)

class ChromaScript(App):
    def __init__(self, root):
        super().__init__(root)
        self.extension_mapping = {"Python": "py", "JavaScript": "js", "Java": "java", "C": "c", "C++": "cpp"}

    def get_theme_colors(self, theme):
        style = styles.get_style_by_name(theme)
        formatter = HtmlFormatter(style=style)
        css = formatter.get_style_defs('.highlight')

        # Extract background color
        background_match = re.search(r'background:(.*?);', css)
        if background_match:
            background_color = background_match.group(1).strip()
            return background_color, background_color

        return None, None

    def draw_macos_buttons(self, draw, button_colors):
        y = 10
        x = 10
        for color in button_colors:
            draw.ellipse([x, y, x+12, y+12], fill=color)
            x += 20  # space between buttons
        return x  # return final x position

    def code_to_image(self, lang, code, theme):
        # Syntax highlighting
        try:
            lexer = get_lexer_by_name(lang)
            style = styles.get_style_by_name(theme)
        except ValueError:
            messagebox.showerror("Error", f"No such language or theme: {lang}, {theme}")
            return

        formatter = ImageFormatter(font_name="DejaVu Sans Mono", line_numbers=False, style=style)
        code_bytes = highlight(code, lexer, formatter)

        # Save the highlighted code as an image
        with open("temp.png", "wb") as temp_file:
            temp_file.write(code_bytes)

        # Open the saved image as a PIL Image object
        code_image = Image.open("temp.png")

        # Create a new image with padding for the MacOS buttons
        width, height = code_image.size

        # Extract the theme colors
        background_color, text_color = self.get_theme_colors(theme)
        new_image = Image.new("RGBA", (width, height + 30), background_color)  # Increased height for padding

        # Draw MacOS buttons on the new image
        draw = ImageDraw.Draw(new_image)
        button_colors = ["#ff5e56", "#febd2c", "#26c83f"]
        final_x = self.draw_macos_buttons(draw, button_colors)

        # Draw window title
        title_font = ImageFont.truetype("font/appleFont.ttf", 15)  # Use SF Pro font for title
        file_extension = self.extension_mapping.get(lang, lang)  # Use the mapping to get the correct file extension
        draw.text((final_x + 10, 10), f"main.{file_extension}", fill=text_color, font=title_font)  # Adjusted position

        # Paste the code image onto the new image, shifted by the padding size
        new_image.paste(code_image, (0, 30))  # Shifted down by 30 pixels

        # Save the final image with higher resolution and quality
        dpi = 1000  # Set the desired DPI value
        output_image_path = "output.png"
        new_image.save(output_image_path, dpi=(dpi, dpi), quality="maximum", subsampling=0)
        #Rounnd the image's corners by 2px

        corner_radius = 10
        rounded_image = Image.new("RGBA", new_image.size)
        mask = Image.new("L", rounded_image.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), rounded_image.size], corner_radius, fill=255)
        rounded_image.paste(new_image, (0, 0), mask=mask)

        # Save the rounded image
        output_image_path = "output.png"
        rounded_image.save(output_image_path, dpi=(dpi, dpi), quality="maximum", subsampling=0)
        os.remove('temp.png')
        rounded_image.show()

if __name__ == "__main__":
    root = Tk()
    app = ChromaScript(root)
    root.mainloop()
