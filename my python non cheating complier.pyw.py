import json
import os
import subprocess
import sys
import threading
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox

current_file = None
running_process = None
CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "app_config.json"
)


def update_status(message):
  file_name = os.path.basename(current_file) if current_file else "Untitled.py"
  status_label.config(text=f"  Python 3.15  |  {file_name}  |  {message}")


def save_file(event=None):
  global current_file
  if current_file:
    with open(current_file, "w", encoding="utf-8") as file:
      file.write(code_editor.get("1.0", tk.END))
    update_status("Saved! ✔")
  else:
    save_as_file()
  return "break"


def save_as_file():
  global current_file
  file_path = filedialog.asksaveasfilename(
      defaultextension=".py",
      filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
  )
  if file_path:
    current_file = file_path
    with open(current_file, "w", encoding="utf-8") as file:
      file.write(code_editor.get("1.0", tk.END))
    window.title(f"Mini-VS Code Pro - {os.path.basename(current_file)}")
    update_status("Saved new file! ✔")


def open_file(event=None):
  global current_file
  file_path = filedialog.askopenfilename(
      filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
  )
  if file_path:
    current_file = file_path
    with open(current_file, "r", encoding="utf-8") as file:
      code_editor.delete("1.0", tk.END)
      code_editor.insert("1.0", file.read())
    window.title(f"Mini-VS Code Pro - {os.path.basename(current_file)}")
    update_status("File loaded")
  return "break"


def write_to_terminal(text):
  terminal.config(state=tk.NORMAL)
  terminal.insert(tk.END, text)
  terminal.see(tk.END)
  terminal.config(state=tk.DISABLED)


def read_stream(stream):
  while True:
    char = stream.read(1)
    if not char:
      break
    window.after(0, write_to_terminal, char)


def run_interactive(event=None):
  global running_process

  if not current_file:
    messagebox.showwarning(
        "Save Required",
        "Please save your Python file first before running!",
    )
    save_as_file()
    if not current_file:
      update_status("Run cancelled (file not saved)")
      return "break"

  if running_process and running_process.poll() is None:
    running_process.kill()

  save_file()
  update_status("Saved & Running... ⚡")

  terminal.config(state=tk.NORMAL)
  terminal.delete("1.0", tk.END)
  terminal.config(state=tk.DISABLED)

  running_process = subprocess.Popen(
      [sys.executable, "-u", current_file],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
      bufsize=0,
  )

  threading.Thread(
      target=read_stream, args=(running_process.stdout,), daemon=True
  ).start()
  threading.Thread(
      target=read_stream, args=(running_process.stderr,), daemon=True
  ).start()

  cmd_entry.focus()
  return "break"


def send_input(event=None):
  global running_process
  user_text = cmd_entry.get()
  cmd_entry.delete(0, tk.END)

  write_to_terminal(user_text + "\n")

  if running_process and running_process.poll() is None:
    running_process.stdin.write(user_text + "\n")
    running_process.stdin.flush()


def clear_terminal():
  terminal.config(state=tk.NORMAL)
  terminal.delete("1.0", tk.END)
  terminal.config(state=tk.DISABLED)
  update_status("Terminal cleared")


def insert_spaces(event):
  code_editor.insert(tk.INSERT, "    ")
  return "break"


# --- FIRST-LAUNCH TUTORIAL POPUP ---
def show_tutorial():
  tut_win = tk.Toplevel(window)
  tut_win.title("Welcome Guide")
  tut_win.geometry("460x280")
  tut_win.configure(bg="#252526")
  tut_win.resizable(False, False)
  tut_win.transient(window)
  tut_win.grab_set()

  steps = [
      (
          "Step 1 of 4: Pure Coding, No Distractions",
          "Welcome to your Python 3.15 workspace!\n\n"
          "There is NO annoying autocomplete here—so beginners and real "
          "programmers can write clean code from scratch.",
      ),
      (
          "Step 2 of 4: Toolbar Button Guide",
          "• Open (Ctrl+O): Load an existing .py file\n"
          "• Save (Ctrl+S): Save your code (Required first!)\n"
          "• ▶ Run (F5): Compile and run your saved code\n"
          "• Clear: Wipe the output screen clean\n"
          "• ? Guide: Reopen this tutorial anytime",
      ),
      (
          "Step 3 of 4: Always Save First!",
          "Your code must be saved as a .py file before running.\n\n"
          "If you forget, pressing ▶ Run (F5) will remind you and open the "
          "Save window automatically.",
      ),
      (
          "Step 4 of 4: Using the Bottom '>' Input Bar",
          "Look at the '>' box at the bottom of the app.\n\n"
          "Whenever your code uses input(), type your answer into that '>' "
          "box and press Enter!",
      ),
  ]

  step_state = {"index": 0}

  # Notice [0][0] and [0][1] — this fixes the squished text bug!
  title_lbl = tk.Label(
      tut_win,
      text=steps[0][0],
      fg="#569cd6",
      bg="#252526",
      font=("Segoe UI", 12, "bold"),
  )
  title_lbl.pack(pady=(20, 10), padx=22, anchor="w")

  body_lbl = tk.Label(
      tut_win,
      text=steps[0][1],
      fg="#d4d4d4",
      bg="#252526",
      font=("Segoe UI", 10),
      justify=tk.LEFT,
      wraplength=415,
  )
  body_lbl.pack(pady=5, padx=22, anchor="w")

  btn_frame = tk.Frame(tut_win, bg="#252526")
  btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=22, pady=18)

  def finish_tutorial():
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
      json.dump({"tutorial_seen": True}, f)
    tut_win.destroy()

  def update_slide():
    idx = step_state["index"]
    title_lbl.config(text=steps[idx][0])
    body_lbl.config(text=steps[idx][1])

    if idx == 0:
      back_btn.pack_forget()
    else:
      back_btn.pack(side=tk.LEFT)

    if idx == len(steps) - 1:
      next_btn.config(text="Start Coding! ✔", bg="#16825d")
    else:
      next_btn.config(text="Next →", bg="#007acc")

  def prev_step():
    if step_state["index"] > 0:
      step_state["index"] -= 1
      update_slide()

  def next_step():
    if step_state["index"] < len(steps) - 1:
      step_state["index"] += 1
      update_slide()
    else:
      finish_tutorial()

  back_btn = tk.Button(
      btn_frame,
      text="← Back",
      command=prev_step,
      bg="#3c3c3c",
      fg="#cccccc",
      relief=tk.FLAT,
      font=("Segoe UI", 9, "bold"),
      padx=12,
      pady=5,
      cursor="hand2",
  )

  next_btn = tk.Button(
      btn_frame,
      text="Next →",
      command=next_step,
      bg="#007acc",
      fg="white",
      relief=tk.FLAT,
      font=("Segoe UI", 9, "bold"),
      padx=14,
      pady=5,
      cursor="hand2",
  )
  next_btn.pack(side=tk.RIGHT)



# --- MAIN WINDOW (VS Code Dark+ Palette) ---
window = tk.Tk()
window.title("PyForge")
window.geometry("820x620")
window.configure(bg="#1e1e1e")
import ctypes

# 1. Tell Windows this is its own standalone app (fixes the taskbar icon!)
myappid = "mycompany.mypythonide.315"  # Any unique text string works
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


# 2. Helper function so the icon still loads after converting to an .exe
def get_resource_path(relative_path):
  if hasattr(sys, "_MEIPASS"):
    return os.path.join(sys._MEIPASS, relative_path)
  return os.path.join(
      os.path.dirname(os.path.abspath(__file__)), relative_path
  )


# 3. Apply your custom icon to the main window
icon_path = get_resource_path("my complier icon.ico")
if os.path.exists(icon_path):
  app_icon = ImageTk.PhotoImage(Image.open(icon_path))
  window.iconphoto(True, app_icon)


# Top Toolbar
toolbar = tk.Frame(window, bg="#2d2d2d", height=38)
toolbar.pack(fill=tk.X)

btn_style = {
    "bg": "#3c3c3c",
    "fg": "#ffffff",
    "relief": tk.FLAT,
    "font": ("Segoe UI", 9, "bold"),
    "padx": 10,
    "pady": 4,
    "cursor": "hand2",
}

tk.Button(toolbar, text="Open_ (Ctrl+O)", command=open_file, **btn_style).pack(
    side=tk.LEFT, padx=(8, 4), pady=5
)
tk.Button(toolbar, text="Save_ (Ctrl+S)", command=save_file, **btn_style).pack(
    side=tk.LEFT, padx=4, pady=5
)
tk.Button(toolbar, text="Save As_", command=save_as_file, **btn_style).pack(
    side=tk.LEFT, padx=4, pady=5
)
tk.Button(toolbar, text="Guide_?", command=show_tutorial, **btn_style).pack(
    side=tk.LEFT, padx=4, pady=5
)

tk.Button(toolbar, text="Clear", command=clear_terminal, **btn_style).pack(
    side=tk.RIGHT, padx=(4, 8), pady=5
)
tk.Button(
    toolbar,
    text="▶ Run (F5)",
    command=run_interactive,
    bg="#007acc",
    fg="white",
    relief=tk.FLAT,
    font=("Segoe UI", 9, "bold"),
    padx=12,
    pady=4,
    cursor="hand2",
).pack(side=tk.RIGHT, padx=4, pady=5)

# Code Editor Area
editor_frame = tk.Frame(window, bg="#1e1e1e")
editor_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=(6, 0))

editor_scroll = tk.Scrollbar(editor_frame)
editor_scroll.pack(side=tk.RIGHT, fill=tk.Y)

code_editor = tk.Text(
    editor_frame,
    height=15,
    bg="#1e1e1e",
    fg="#d4d4d4",
    insertbackground="#569cd6",
    selectbackground="#264f78",
    relief=tk.FLAT,
    font=("Consolas", 12),
    yscrollcommand=editor_scroll.set,
    undo=True,
)
code_editor.pack(fill=tk.BOTH, expand=True)
editor_scroll.config(command=code_editor.yview)

code_editor.insert(
    "1.0",
    'import time\nname = input("Enter your hacker name: ")\nprint("Connecting...")\ntime.sleep(1)\nprint(f"Access granted, {name}!")\n',
)

# Built-in Interactive Terminal Engine
term_header = tk.Frame(window, bg="#252526")
term_header.pack(fill=tk.X, padx=6, pady=(6, 0))
tk.Label(
    term_header,
    text="  TERMINAL_",
    fg="#cccccc",
    bg="#252526",
    font=("Segoe UI", 8, "bold"),
    pady=4,
).pack(side=tk.LEFT)

terminal = tk.Text(
    window,
    height=9,
    bg="#181818",
    fg="#4ec9b0",
    relief=tk.FLAT,
    font=("Consolas", 11),
    state=tk.DISABLED,
)
terminal.pack(fill=tk.BOTH, expand=True, padx=6)

# Interactive Input Bar right below the terminal
input_frame = tk.Frame(window, bg="#252526")
input_frame.pack(fill=tk.X, padx=6, pady=(0, 6))

tk.Label(
    input_frame,
    text=" > ",
    fg="#569cd6",
    bg="#252526",
    font=("Consolas", 12, "bold"),
).pack(side=tk.LEFT)

cmd_entry = tk.Entry(
    input_frame,
    bg="#252526",
    fg="white",
    insertbackground="white",
    relief=tk.FLAT,
    font=("Consolas", 11),
)
cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
cmd_entry.bind(chr(60) + "Return" + chr(62), send_input)

# Status Bar
status_bar = tk.Frame(window, bg="#007acc", height=24)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)
status_label = tk.Label(
status_bar,
text="  Python 3.15  |  Untitled.py  |  Ready",
fg="white",
bg="#007acc",
font=("Segoe UI", 9),
)
status_label.pack(side=tk.LEFT)

code_editor.bind(chr(60) + "Tab" + chr(62), insert_spaces)
window.bind(chr(60) + "Control-s" + chr(62), save_file)
window.bind(chr(60) + "Control-S" + chr(62), save_file)
window.bind(chr(60) + "Control-o" + chr(62), open_file)
window.bind(chr(60) + "Control-O" + chr(62), open_file)
window.bind(chr(60) + "F5" + chr(62), run_interactive)

if not os.path.exists(CONFIG_FILE):
  window.after(300, show_tutorial)
window.mainloop()