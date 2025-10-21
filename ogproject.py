import cv2
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageDraw
from customtkinter import CTkImage


# --------------------- Splash Video ---------------------
def play_video(video_path="C:/Users/HP/Downloads/creadlocklogo.mp4"):
    capture = cv2.VideoCapture(video_path)
    if not capture.isOpened():
        print("Error Opening video")
        return

    fps = capture.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30
    delay = int(1000 / fps)

    while capture.isOpened():
        ret, frame = capture.read()
        if ret:
            cv2.imshow("Credlock", frame)
            if cv2.waitKey(delay) & 0xFF == ord("q"):
                break
        else:
            break

    capture.release()
    cv2.destroyAllWindows()


# --------------------- Gradient Creation ---------------------
def create_gradient(width, height, start_color, end_color):
    gradient = Image.new("RGB", (width, height), color=0)
    draw = ImageDraw.Draw(gradient)
    for i in range(height):
        ratio = i / height
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    return gradient


# --------------------- Main App ---------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # hide root until login succeeds
        self.overrideredirect(True)  # stop flashing small window
        self.after(0, self.withdraw)

        self.screens = {}
        self.history = []
        self.history_index = -1

        # Storage
        self.data = {"wifi": [], "passkeys": [], "codes": []}
        self.deleted = {"usernames": [], "codes": []}

        self.protocol("WM_DELETE_WINDOW", self.close_app)

    # ---------------- Gradient Bar ----------------
    def gradient_bar(self, window, bar_height=120):
        bar_width = window.winfo_screenwidth()
        gradient_img = create_gradient(bar_width, bar_height, (0, 90, 200), (0, 150, 255))
        gradient_ctk = ctk.CTkImage(light_image=gradient_img, size=(bar_width, bar_height))
        top_bar = ctk.CTkLabel(window, image=gradient_ctk, text="")
        top_bar.image = gradient_ctk
        top_bar.pack(fill="x", side="top")

    # ---------------- Main Screen ----------------
    def main_screen(self):
        window = ctk.CTkToplevel(self)
        window.state("zoomed")
        window.configure(fg_color="white")
        window.title("Credlock - Main")
        window.protocol("WM_DELETE_WINDOW", self.close_app)

        # Gradient bar
        self.gradient_bar(window, 120)

        # Credtext image
        try:
            pil_img = Image.open("C:/Users/HP/Desktop/CredLock Project/credtext.jpg")
            img_obj = ctk.CTkImage(light_image=pil_img, size=(300, 100))
            img_label = ctk.CTkLabel(window, image=img_obj, text="")
            img_label.image = img_obj
            img_label.pack(anchor="w", padx=20, pady=(10, 20))
        except Exception as e:
            print("Image not found:", e)

        # Search bar
        search_frame = ctk.CTkFrame(window, fg_color="white")
        search_frame.pack(fill="x", pady=10)
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search...",
            width=400,
            height=35,
            font=("Arial", 14),
        )
        search_entry.pack(pady=5)

        # Buttons section
        button_section = ctk.CTkFrame(window, fg_color="white")
        button_section.pack(expand=True)
        button_section.grid_columnconfigure((0, 1, 2, 3), weight=1)
        buttons = []

        def add_button(col, image_path, text, target):
            try:
                pil_img = Image.open(image_path)
                img_obj = ctk.CTkImage(light_image=pil_img, size=(150, 120))
            except:
                img_obj = None
            btn = ctk.CTkButton(
                button_section,
                image=img_obj,
                text=text,
                compound="top",
                width=180,
                height=180,
                corner_radius=20,
                fg_color="white",
                hover_color="#f0f0f0",
                border_width=2,
                border_color="#cccccc",
                font=("Arial", 15, "bold"),
                text_color="black",
                command=lambda: self.open_screen(target),
            )
            btn.image = img_obj
            btn.grid(row=0, column=col, padx=30, pady=50, sticky="n")
            buttons.append((btn, text.lower()))

        # Add buttons
        add_button(0, "C:/Users/HP/Desktop/CredLock Project/passkeys.jpeg", "Passkeys", "passkeys")
        add_button(1, "C:/Users/HP/Desktop/CredLock Project/wifi.jpeg", "Wifi", "wifi")
        add_button(2, "C:/Users/HP/Desktop/CredLock Project/codes.jpeg", "Codes", "codes")
        add_button(3, "C:/Users/HP/Desktop/CredLock Project/deleted.jpeg", "Deleted", "deleted")

        # Search filter
        def filter_buttons(*args):
            query = search_entry.get().lower()
            col = 0
            for btn, label in buttons:
                if query in label:
                    btn.grid(row=0, column=col, padx=30, pady=50, sticky="n")
                    col += 1
                else:
                    btn.grid_forget()

        search_entry.bind("<KeyRelease>", filter_buttons)
        return window

    # ---------------- Sub Screens ----------------
    def sub_screen(self, name):
        window = ctk.CTkToplevel(self)
        window.state("zoomed")
        window.configure(fg_color="white")
        window.title(f"Credlock - {name.capitalize()}")
        window.protocol("WM_DELETE_WINDOW", self.close_app)

        # Gradient bar
        self.gradient_bar(window, 100)

        # Frame for Back and Create buttons
        button_frame = ctk.CTkFrame(window, fg_color="white")
        button_frame.pack(fill="x", pady=(10, 20), padx=20)

        # Back button
        back_btn = ctk.CTkButton(
            button_frame,
            text="←",
            width=50,
            height=35,
            corner_radius=15,
            fg_color="#e0e0e0",
            hover_color="#cfcfcf",
            text_color="black",
            font=("Arial", 18, "bold"),
            command=self.go_back,
        )
        back_btn.pack(side="left")

        # Create button
        if name in ["wifi", "passkeys", "codes"]:
            create_btn = ctk.CTkButton(
                button_frame,
                text="+ Create",
                width=130,
                height=40,
                corner_radius=20,
                fg_color="#0073e6",
                hover_color="#005bb5",
                text_color="white",
                font=("Arial", 16, "bold"),
                command=lambda n=name: self.create_page(n),
            )
            create_btn.pack(side="right")

        # Search bar
        search_frame = ctk.CTkFrame(window, fg_color="white")
        search_frame.pack(fill="x", pady=10)
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Search...",
            width=400,
            height=35,
            font=("Arial", 14),
        )
        search_entry.pack(pady=5)

        # Content frame
        content = ctk.CTkFrame(window, fg_color="white")
        content.pack(expand=True, fill="both", padx=20, pady=20)
        window.content = content
        window.search_entry = search_entry

        # Bind search
        search_entry.bind("<KeyRelease>", lambda e, cat=name: self.refresh_screen(cat))
        self.refresh_screen(name)
        return window

    # ---------------- Show No Pass Image ----------------
    def show_no_pass(self, parent):
        for w in parent.winfo_children():
            w.destroy()
        try:
            pil_img = Image.open("C:/Users/HP/Desktop/CredLock Project/nopass.jpg")
            img_obj = ctk.CTkImage(light_image=pil_img, size=(300, 300))
            img_label = ctk.CTkLabel(parent, image=img_obj, text="")
            img_label.image = img_obj
            img_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            print("No image found:", e)

    # ---------------- Create Popup ----------------
    def create_page(self, category):
        create_window = ctk.CTkToplevel(self)
        create_window.geometry("600x400+300+200")
        create_window.title("Create")
        create_window.configure(fg_color="white")
        create_window.grab_set()
        create_window.focus_force()
        create_window.lift()

        frm = ctk.CTkFrame(create_window, width=350, height=250, fg_color="white", corner_radius=10)
        frm.place(relx=0.5, rely=0.5, anchor="center")

        if category in ["wifi", "passkeys"]:
            hding = ctk.CTkLabel(frm, text=f"Create {category.capitalize()} User", text_color="black",
                                 font=("Microsoft Yahei UI Light", 23, "bold"))
            hding.place(relx=0.5, y=30, anchor="center")

            username_entry = ctk.CTkEntry(frm, width=220, placeholder_text="Enter Username")
            username_entry.place(relx=0.5, y=90, anchor="center")

            password_entry = ctk.CTkEntry(frm, width=220, placeholder_text="Enter Password", show="*")
            password_entry.place(relx=0.5, y=140, anchor="center")

            def save_action():
                u = username_entry.get().strip()
                p = password_entry.get().strip()
                if u and p:
                    self.data[category].append((u, p))
                    self.refresh_screen(category)
                    create_window.destroy()

            ctk.CTkButton(frm, text="Save", fg_color="yellow", text_color="black",
                          width=220, command=save_action).place(relx=0.5, y=180, anchor="center")

        elif category == "codes":
            hding = ctk.CTkLabel(frm, text="Create Code", text_color="black",
                                 font=("Microsoft Yahei UI Light", 23, "bold"))
            hding.place(relx=0.5, y=30, anchor="center")

            name_entry = ctk.CTkEntry(frm, width=220, placeholder_text="Enter Code Name")
            name_entry.place(relx=0.5, y=90, anchor="center")

            value_entry = ctk.CTkEntry(frm, width=220, placeholder_text="Enter Code Value")
            value_entry.place(relx=0.5, y=140, anchor="center")

            def save_action():
                n = name_entry.get().strip()
                v = value_entry.get().strip()
                if n and v:
                    self.data["codes"].append((n, v))
                    self.refresh_screen("codes")
                    create_window.destroy()

            ctk.CTkButton(frm, text="Save", fg_color="yellow", text_color="black",
                          width=220, command=save_action).place(relx=0.5, y=180, anchor="center")

    # ---------------- Refresh Screens ----------------
    def refresh_screen(self, category):
        if category not in self.screens:
            return
        window = self.screens[category]
        for w in window.content.winfo_children():
            w.destroy()

        query = window.search_entry.get().lower()
        items = []

        if category == "deleted":
            for u, p, src in self.deleted["usernames"]:
                if query in u.lower():
                    items.append(("user", u, p, src))
            for n, v in self.deleted["codes"]:
                if query in n.lower():
                    items.append(("code", n, v))
            if not items:
                self.show_no_pass(window.content)
                return

            for item in items:
                row = ctk.CTkFrame(window.content, fg_color="white")
                row.pack(fill="x", pady=5)
                if item[0] == "user":
                    u, p, src = item[1], item[2], item[3]
                    ctk.CTkLabel(row, text=u, anchor="w", font=("Arial", 14),
                                 text_color="black").pack(side="left", padx=10, fill="x", expand=True)
                    ctk.CTkButton(row, text="Restore", fg_color="green", text_color="white",
                                  command=lambda user=u, pw=p, s=src: self.restore_item(user, pw, s)).pack(side="right", padx=5)
                else:
                    n, v = item[1], item[2]
                    ctk.CTkLabel(row, text=f"{n}: {v}", anchor="w", font=("Arial", 14),
                                 text_color="black").pack(side="left", padx=10, fill="x", expand=True)
                    ctk.CTkButton(row, text="Restore", fg_color="green", text_color="white",
                                  command=lambda name=n, val=v: self.restore_code(name, val)).pack(side="right", padx=5)
            return

        for item in self.data[category]:
            name = item[0]
            if query in name.lower():
                items.append(item)

        if not items:
            self.show_no_pass(window.content)
            return

        for item in items:
            row = ctk.CTkFrame(window.content, fg_color="white")
            row.pack(fill="x", pady=5)
            if category in ["wifi", "passkeys"]:
                u, p = item
                ctk.CTkButton(row, text=u, anchor="w", font=("Arial", 14),
                              text_color="black", fg_color="#f8f8f8", hover_color="#e0e0e0",
                              command=lambda usr=u: print("Clicked", usr)).pack(side="left", padx=10, fill="x", expand=True)
                ctk.CTkButton(row, text="Delete", fg_color="red", text_color="white",
                              command=lambda usr=u, pw=p, cat=category: self.delete_item(usr, pw, cat)).pack(side="right", padx=5)
            elif category == "codes":
                n, v = item
                ctk.CTkLabel(row, text=f"{n}: {v}", anchor="w", font=("Arial", 14),
                             text_color="black").pack(side="left", padx=10, fill="x", expand=True)
                ctk.CTkButton(row, text="Delete", fg_color="red", text_color="white",
                              command=lambda name=n, val=v: self.delete_code(name, val)).pack(side="right", padx=5)

    # ---------------- Delete & Restore ----------------
    def delete_item(self, username, password, category):
        self.data[category] = [x for x in self.data[category] if x[0] != username]
        self.deleted["usernames"].append((username, password, category))
        self.refresh_screen(category)
        self.refresh_screen("deleted")

    def restore_item(self, username, password, category):
        self.deleted["usernames"] = [x for x in self.deleted["usernames"] if x[0] != username]
        self.data[category].append((username, password))
        self.refresh_screen(category)
        self.refresh_screen("deleted")

    def delete_code(self, name, value):
        self.data["codes"] = [x for x in self.data["codes"] if x[0] != name]
        self.deleted["codes"].append((name, value))
        self.refresh_screen("codes")
        self.refresh_screen("deleted")

    def restore_code(self, name, value):
        self.deleted["codes"] = [x for x in self.deleted["codes"] if x[0] != name]
        self.data["codes"].append((name, value))
        self.refresh_screen("codes")
        self.refresh_screen("deleted")

    # ---------------- Screen Management ----------------
    def open_screen(self, name):
        if self.history_index >= 0:
            current_name = self.history[self.history_index]
            if current_name in self.screens:
                self.screens[current_name].withdraw()

        if name not in self.screens:
            if name == "main":
                self.screens[name] = self.main_screen()
            elif name in ["wifi", "passkeys", "codes", "deleted"]:
                self.screens[name] = self.sub_screen(name)

        self.screens[name].deiconify()
        self.screens[name].state("zoomed")

        if self.history_index == -1 or self.history[self.history_index] != name:
            self.history = self.history[: self.history_index + 1]
            self.history.append(name)
            self.history_index += 1

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.open_screen(self.history[self.history_index])

    def close_app(self):
        for win in self.screens.values():
            win.destroy()
        self.destroy()


# --------------------- Login Window ---------------------
def login_window(app: ctk.CTk):
    login = ctk.CTkToplevel(app)
    login.state("zoomed")
    login.title("Login")
    login.geometry("1000x500+300+200")
    login.resizable(False, False)
    login.configure(fg_color="white")
    login.grab_set()
    login.focus_force()
    login.lift()

    # Left image - replace with your path or skip if image not available
    try:
        original_img = Image.open("C:/Users/HP/Downloads/loginimg.jpg")
        bg_img = CTkImage(light_image=original_img, size=(500, 500))
        img_label = ctk.CTkLabel(login, image=bg_img, text="")
        img_label.place(x=300, y=200)
    except Exception as e:
        print("Image load error:", e)
        img_label = ctk.CTkLabel(login, text="Image failed to load", font=("Arial", 20))
        img_label.place(x=100, y=200)

    # Right side form
    form_frame = ctk.CTkFrame(login, width=1000, height=600, corner_radius=15, fg_color="white")
    form_frame.place(x=800, y=250)

    title_label = ctk.CTkLabel(form_frame, text="Enter Your Password", font=("Arial", 18, "bold"))
    title_label.pack(pady=(30, 20))

    subtitle_label = ctk.CTkLabel(
        form_frame,
        text="Enter the Master Password to start with credlock",
        wraplength=400,
        font=("Arial", 12)
    )
    subtitle_label.pack(pady=10)

    # Password input (8 boxes)
    password_vars = [ctk.StringVar() for _ in range(8)]
    entries = []

    def reset_entry_styles():
        for entry in entries:
            entry.configure(border_color="#d9d9d9")  # default light gray border

    def on_keypress(event, idx):
        entries[idx].configure(border_color="#d9d9d9")

        if event.char.isprintable() and len(event.char) == 1:
            password_vars[idx].set(event.char)
            if idx < len(entries) - 1:
                entries[idx + 1].focus_set()
            return "break"
        elif event.keysym == "BackSpace":
            password_vars[idx].set("")
            if idx > 0:
                entries[idx - 1].focus_set()
            return "break"

    password_frame = ctk.CTkFrame(form_frame, fg_color="white")
    password_frame.pack(pady=30)

    for i in range(8):
        entry = ctk.CTkEntry(
            password_frame,
            textvariable=password_vars[i],
            width=35,
            justify="center",
            font=("Arial", 20),
            show="*",
            border_width=2,
            border_color="#d9d9d9",
            corner_radius=5
        )
        entry.grid(row=0, column=i, padx=4)
        entry.bind("<KeyPress>", lambda e, idx=i: on_keypress(e, idx))
        entries.append(entry)

    entries[0].focus_set()

    def highlight_error():
        for var in password_vars:
            var.set("")
        for entry in entries:
            entry.configure(border_color="#e06666")  # mild red border
        entries[0].focus_set()

    def confirm_pin():
        password = "".join(var.get() for var in password_vars)
        reset_entry_styles()

        if len(password) != 8:
            highlight_error()
            messagebox.showerror("Error", "Password must be 8 characters long.")
            return

        # Example correct password
        if password == "A1@bcdef":
            login.destroy()
            app.deiconify()
            app.open_screen("main")
        else:
            highlight_error()
            messagebox.showerror("Error", "Incorrect Password. Please try again.")

    confirm_btn = ctk.CTkButton(
        form_frame,
        text="Confirm",
        width=200,
        height=40,
        fg_color="#0073e6",
        hover_color="#005bb5",
        text_color="white",
        font=("Arial", 16, "bold"),
        command=confirm_pin
    )
    confirm_btn.pack(pady=20)

    login.protocol("WM_DELETE_WINDOW", app.close_app)

# --------------------- Run ---------------------
if __name__ == "__main__":
    play_video()  # Splash video
    app = App()
    login_window(app)  # Login
    app.mainloop()
