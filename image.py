import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import ctypes
import keyboard

def enable_clickthrough(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles | 0x80000 | 0x20)

def disable_clickthrough(window):
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    styles = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
    ctypes.windll.user32.SetWindowLongW(hwnd, -20, styles & ~0x20)

current_size = 300
opacity_level = 0.7
can_move = False
tk_image = None
pil_image = None
menu_window = None
slider_window = None

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", opacity_level)

image_label = tk.Label(root, bd=0)
image_label.pack()

def upload_image():
    global tk_image, pil_image, start_window
    path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
    )
    if path:
        pil_image = Image.open(path)
        pil_image = pil_image.resize((current_size, current_size))
        tk_image = ImageTk.PhotoImage(pil_image)
        image_label.config(image=tk_image)
        start_window.destroy()

def toggle_move():
    global can_move
    can_move = not can_move
    if can_move:
        disable_clickthrough(root)
    else:
        enable_clickthrough(root)

def start_move(event):
    if can_move:
        image_label.startX = event.x
        image_label.startY = event.y

def do_move(event):
    if can_move:
        x = root.winfo_x() + event.x - image_label.startX
        y = root.winfo_y() + event.y - image_label.startY
        root.geometry(f"+{x}+{y}")

def open_slider(slider_type):
    global slider_window, current_size, opacity_level, tk_image, pil_image

    if slider_window and slider_window.winfo_exists():
        slider_window.destroy()

    slider_window = tk.Toplevel(root)
    slider_window.overrideredirect(True)
    slider_window.geometry("320x120")
    slider_window.configure(bg="black")
    slider_window.attributes("-topmost", True)

    if slider_type == "zoom":
        tk.Label(slider_window, text="Zoom", fg="white", bg="black", font=("Arial", 12, "bold")).pack(pady=(5,0))
        zoom_slider = tk.Scale(slider_window, from_=50, to=1000, orient="horizontal", length=280,
                               bg="black", fg="white", troughcolor="white", sliderlength=30, highlightthickness=0)
        zoom_slider.set(current_size)
        zoom_slider.pack()

        def update_zoom(val):
            global current_size, tk_image, pil_image
            current_size = int(float(val))
            if pil_image:
                resized = pil_image.resize((current_size, current_size))
                tk_image = ImageTk.PhotoImage(resized)
                image_label.config(image=tk_image)

        zoom_slider.config(command=update_zoom)

    elif slider_type == "opacity":
        tk.Label(slider_window, text="Opacity", fg="white", bg="black", font=("Arial", 12, "bold")).pack(pady=(5,0))
        opacity_slider = tk.Scale(slider_window, from_=0, to=1, resolution=0.01, orient="horizontal", length=280,
                                  bg="black", fg="white", troughcolor="white", sliderlength=30, highlightthickness=0)
        opacity_slider.set(opacity_level)
        opacity_slider.pack()

        def update_opacity(val):
            global opacity_level
            opacity_level = float(val)
            root.attributes("-alpha", opacity_level)

        opacity_slider.config(command=update_opacity)

    tk.Button(slider_window, text="Done", width=10, bg="black", fg="white", font=("Arial", 10, "bold"),
              relief="raised", bd=3, command=slider_window.destroy).pack(pady=5)

def show_menu():
    global menu_window
    if menu_window and menu_window.winfo_exists():
        menu_window.destroy()
        menu_window = None
        return

    menu_window = tk.Toplevel(root)
    menu_window.overrideredirect(True)
    menu_window.geometry("250x300+400+200")
    menu_window.attributes("-topmost", True)
    menu_window.configure(bg="black")

    buttons = [
        ("Move Toggle", toggle_move),
        ("Zoom", lambda: open_slider("zoom")),
        ("Opacity", lambda: open_slider("opacity")),
        ("Quit", root.destroy)
    ]

    for text, cmd in buttons:
        fg_color = "#FF0000" if text == "Quit" else "white"
        tk.Button(menu_window, text=text, width=18, height=2, bg="black", fg=fg_color,
                  font=("Arial", 11, "bold"), relief="raised", bd=3, command=cmd).pack(pady=10)

image_label.bind("<Button-1>", start_move)
image_label.bind("<B1-Motion>", do_move)

start_window = tk.Toplevel(root)
start_window.overrideredirect(True)
width, height = 400, 200
x_pos = (root.winfo_screenwidth() - width) // 2
y_pos = (root.winfo_screenheight() - height) // 2
start_window.geometry(f"{width}x{height}+{x_pos}+{y_pos}")
start_window.attributes("-topmost", True)
start_window.configure(bg="black")

tk.Button(start_window, text="Upload Image", width=20, height=2, bg="black", fg="white",
          font=("Arial", 12, "bold"), relief="raised", bd=3, command=upload_image).pack(pady=20)

tk.Label(start_window, text='After uploading image, press "CTRL+M" to open/close menu',
         fg="white", bg="black", font=("Arial", 9, "italic")).pack(pady=15)

root.update_idletasks()
enable_clickthrough(root)
keyboard.add_hotkey('ctrl+m', show_menu)

root.mainloop()
