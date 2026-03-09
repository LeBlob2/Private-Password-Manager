import tkinter as tk
from tkinter import messagebox
import random
import string
import json
import os

# Main window
window = tk.Tk()
window.title("Password Manager - Simple Version")
window.geometry("500x500")
window.configure(bg="#f0f0f0")  # light gray background, looks cleaner

# Title
title_label = tk.Label(window, text="My Password Manager", font=("Arial", 18, "bold"), bg="#f0f0f0")
title_label.pack(pady=20)

# Website
tk.Label(window, text="Website / App Name:", font=("Arial", 12), bg="#f0f0f0").pack()
entry_website = tk.Entry(window, width=40, font=("Arial", 12))
entry_website.pack(pady=5)

# Username
tk.Label(window, text="Username / Email:", font=("Arial", 12), bg="#f0f0f0").pack()
entry_user = tk.Entry(window, width=40, font=("Arial", 12))
entry_user.pack(pady=5)

# Password
tk.Label(window, text="Password:", font=("Arial", 12), bg="#f0f0f0").pack()
entry_pass = tk.Entry(window, width=40, font=("Arial", 12), show="*")
entry_pass.pack(pady=5)

# Generate password function
def generate_password():
    length = 12
    chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    password = ''.join(random.choice(chars) for _ in range(length))
    
    entry_pass.delete(0, tk.END)
    entry_pass.insert(0, password)

# Save function
def save_password():
    website = entry_website.get().strip()
    user = entry_user.get().strip()
    password = entry_pass.get().strip()
    
    if not website or not user or not password:
        messagebox.showwarning("Missing Info", "Please fill all 3 fields lah!")
        return
    
    # Data to save
    new_data = {
        "website": website,
        "username": user,
        "password": password
    }
    
    file_name = "passwords.json"
    data = []
    
    # Read old data if file exists
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
        except:
            data = []  # if file broken, start fresh
    
    data.append(new_data)
    
    # Save
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)
    
    messagebox.showinfo("Success", f"Saved {website}!")
    
    # Clear boxes
    entry_website.delete(0, tk.END)
    entry_user.delete(0, tk.END)
    entry_pass.delete(0, tk.END)

# Show all passwords
def show_all():
    file_name = "passwords.json"
    if not os.path.exists(file_name):
        messagebox.showinfo("No Data", "Nothing saved yet bro.")
        return
    
    with open(file_name, "r") as file:
        try:
            data = json.load(file)
        except:
            messagebox.showerror("Error", "File broken lah.")
            return
    
    if not data:
        messagebox.showinfo("Empty", "No passwords saved.")
        return
    
    # New window to show list
    show_window = tk.Toplevel(window)
    show_window.title("Saved Passwords")
    show_window.geometry("600x400")
    show_window.configure(bg="#f0f0f0")
    
    text_area = tk.Text(show_window, font=("Arial", 11), wrap="word", bg="white")
    text_area.pack(padx=10, pady=10, fill="both", expand=True)
    
    for entry in data:
        text_area.insert(tk.END, f"Website: {entry['website']}\n")
        text_area.insert(tk.END, f"User:     {entry['username']}\n")
        text_area.insert(tk.END, f"Pass:     {entry['password']}\n")
        text_area.insert(tk.END, "-" * 50 + "\n\n")
    
    text_area.config(state="disabled")  # read only

# Buttons
btn_generate = tk.Button(window, text="Generate Random Password", command=generate_password,
                         font=("Arial", 12), bg="#4CAF50", fg="white", width=25)
btn_generate.pack(pady=10)

btn_save = tk.Button(window, text="Save This Password", command=save_password,
                     font=("Arial", 12), bg="#2196F3", fg="white", width=25)
btn_save.pack(pady=5)

btn_show = tk.Button(window, text="Show All Saved", command=show_all,
                     font=("Arial", 12), bg="#FF9800", fg="white", width=25)
btn_show.pack(pady=10)

# Start the app
window.mainloop()
