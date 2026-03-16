import tkinter as tk
from tkinter import messagebox
import sqlcipher3

from create_open_database import (
    get_connection,
    generate_password,
    save_password,
    fetch_all_passwords
)



def launch_main_app(conn, login_window: tk.Tk) -> None:
    login_window.destroy()

    window = tk.Tk()
    window.title("Password Manager")
    window.geometry("500x520")
    window.configure(bg="#f0f0f0")

    tk.Label(window, text="My Password Manager", font=("Hack", 18, "bold"), bg="#f0f0f0").pack(pady=20)

    tk.Label(window, text="Website:", font=("Hack", 12), bg="#f0f0f0").pack()
    entry_website = tk.Entry(window, width=40, font=("Hack", 12))
    entry_website.pack(pady=5)

    tk.Label(window, text="Username:", font=("Hack", 12), bg="#f0f0f0").pack()
    entry_user = tk.Entry(window, width=40, font=("Hack", 12))
    entry_user.pack(pady=5)


    tk.Label(window, text="Email:", font=("Hack", 12), bg="#f0f0f0").pack()
    entry_email = tk.Entry(window, width=40, font=("Hack", 12))
    entry_email.pack(pady=5)

    tk.Label(window, text="Password:", font=("Hack", 12), bg="#f0f0f0").pack()
    entry_pass = tk.Entry(window, width=40, font=("Hack", 12), show="*")
    entry_pass.pack(pady=5)


    def on_generate():
        password = generate_password()
        entry_pass.delete(0, tk.END)
        entry_pass.insert(0, password)

    def on_save():
        website = entry_website.get().strip()
        user = entry_user.get().strip()
        password = entry_pass.get().strip()

        if not website or not user or not password:
            messagebox.showwarning("Missing Info", "Please fill all 3 fields!")
            return

        try:
            save_password(conn, website, user, password)
            messagebox.showinfo("Saved", f"Saved entry for {website}!")
            entry_website.delete(0, tk.END)
            entry_user.delete(0, tk.END)
            entry_pass.delete(0, tk.END)
        except sqlcipher3.IntegrityError:
            messagebox.showerror("Duplicate", f"An entry with email '{user}' already exists!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_show_all():
        try:
            rows = fetch_all_passwords(conn)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        if not rows:
            messagebox.showinfo("Empty", "No passwords saved yet.")
            return

        show_window = tk.Toplevel(window)
        show_window.title("Saved Passwords")
        show_window.geometry("600x400")
        show_window.configure(bg="#f0f0f0")

        text_area = tk.Text(show_window, font=("Hack", 11), wrap="word", bg="white")
        text_area.pack(padx=10, pady=10, fill="both", expand=True)

        for row in rows:
            text_area.insert(tk.END, f"Website:  {row[0]}\n")
            text_area.insert(tk.END, f"Email:    {row[1]}\n")
            text_area.insert(tk.END, f"Password: {row[2]}\n")
            text_area.insert(tk.END, f"Saved:    {row[3]}\n")
            text_area.insert(tk.END, "-" * 50 + "\n\n")

        text_area.config(state="disabled")

    def on_close():
        conn.close()
        window.destroy()


    tk.Button(window, text="Generate Random Password", command=on_generate,
              font=("Hack", 12), bg="#4CAF50", fg="white", width=25).pack(pady=10)

    tk.Button(window, text="Save This Password", command=on_save,
              font=("Hack", 12), bg="#2196F3", fg="white", width=25).pack(pady=5)

    tk.Button(window, text="Show All Saved", command=on_show_all,
              font=("Hack", 12), bg="#FF9800", fg="white", width=25).pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()



def launch_login() -> None:
    login_window = tk.Tk()
    login_window.title("Enter Master Password")
    login_window.geometry("350x200")
    login_window.configure(bg="#f0f0f0")

    tk.Label(login_window, text="Master Password", font=("Hack", 16, "bold"), bg="#f0f0f0").pack(pady=20)
    tk.Label(login_window, text="Enter your database password:", font=("Hack", 11), bg="#f0f0f0").pack()

    entry_master = tk.Entry(login_window, width=30, font=("Hack", 12), show="*")
    entry_master.pack(pady=8)

    def on_unlock():
        db_password = entry_master.get()
        if not db_password:
            messagebox.showwarning("Empty", "Please enter your master password.")
            return
        try:
            conn = get_connection(db_password)
            launch_main_app(conn, login_window)
        except ValueError:
            messagebox.showerror("Error", "Wrong master password!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    tk.Button(
        login_window, text="Unlock", font=("Hack", 12),
        bg="#2196F3", fg="white", width=15,
        command=on_unlock
    ).pack(pady=10)

    entry_master.bind("<Return>", lambda e: on_unlock())
    login_window.mainloop()
