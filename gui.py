import tkinter as tk
from tkinter import messagebox
import sqlcipher3

from create_open_database import (
    get_connection,
    generate_password,
    save_password,
    fetch_all_passwords,
    delete_entry
)


def launch_main_app(conn, login_window: tk.Tk) -> None:
    login_window.destroy()

    window = tk.Tk()
    window.title("Private Password Manager")
    window.geometry("500x580")
    window.configure(bg="#34344b")

    tk.Label(window, text="Private Password Manager", font=("Red Hat Mono", 18, "bold"), bg="#34344b", fg="white").pack(pady=20)

    tk.Label(window, text="Website:", font=("Red Hat Mono", 12), bg="#34344b", fg="white").pack()
    entry_website = tk.Entry(window, width=40, font=("Red Hat Mono", 12))
    entry_website.pack(pady=5)

    tk.Label(window, text="Username:", font=("Red Hat Mono", 12), bg="#34344b", fg="white").pack()
    entry_user = tk.Entry(window, width=40, font=("Red Hat Mono", 12))
    entry_user.pack(pady=5)

    tk.Label(window, text="Email:", font=("Red Hat Mono", 12), bg="#34344b", fg="white").pack()
    entry_email = tk.Entry(window, width=40, font=("Red Hat Mono", 12))
    entry_email.pack(pady=5)

    tk.Label(window, text="Password:", font=("Red Hat Mono", 12), bg="#34344b", fg="white").pack()
    entry_pass = tk.Entry(window, width=40, font=("Red Hat Mono", 12), show="*")
    entry_pass.pack(pady=5)


    def on_generate():
        password = generate_password()
        entry_pass.delete(0, tk.END)
        entry_pass.insert(0, password)

    def on_save():
        website  = entry_website.get().strip()
        user     = entry_user.get().strip()
        email    = entry_email.get().strip()
        password = entry_pass.get().strip()

        if not website or not user or not email or not password:
            messagebox.showwarning("Missing Info", "Please fill all 4 fields!")
            return

        try:
            save_password(conn, website, user, email, password)
            messagebox.showinfo("Saved", f"Saved entry for {website}!")
            entry_website.delete(0, tk.END)
            entry_user.delete(0, tk.END)
            entry_email.delete(0, tk.END)
            entry_pass.delete(0, tk.END)
        except sqlcipher3.IntegrityError:
            messagebox.showerror("Duplicate", f"An entry with email '{email}' already exists!")
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
        show_window.geometry("600x600")
        show_window.configure(bg="#34344b")

        text_area = tk.Text(show_window, font=("Red Hat Mono", 11), wrap="word", bg="black", fg="white")
        text_area.pack(padx=10, pady=10, fill="both", expand=True)

        for row in rows:
            text_area.insert(tk.END, f"ID:       {row[0]}\n")
            text_area.insert(tk.END, f"Website:  {row[1]}\n")
            text_area.insert(tk.END, f"Username: {row[2]}\n")
            text_area.insert(tk.END, f"Email:    {row[3]}\n")
            text_area.insert(tk.END, f"Password: {row[4]}\n")
            text_area.insert(tk.END, f"Date:     {row[5]}\n")
            text_area.insert(tk.END, "-" * 50 + "\n\n")

        text_area.config(state="disabled")

        delete_frame = tk.Frame(show_window, bg="#34344b")
        delete_frame.pack(pady=8)

        tk.Label(delete_frame, text="Delete Entry ID:", font=("Red Hat Mono", 11),
                 bg="#34344b", fg="white").pack(side=tk.LEFT, padx=(10, 5))

        entry_delete_id = tk.Entry(delete_frame, width=6, font=("Red Hat Mono", 11))
        entry_delete_id.pack(side=tk.LEFT, padx=5)

        def on_delete():
            raw = entry_delete_id.get().strip()
            if not raw.isdigit():
                messagebox.showwarning("Invalid", "Please enter a valid numeric ID.", parent=show_window)
                return
            entry_id = int(raw)
            confirm = messagebox.askyesno("Confirm", f"Delete entry with ID {entry_id}?", parent=show_window)
            if not confirm:
                return
            deleted = delete_entry(conn, entry_id)
            if deleted:
                messagebox.showinfo("Deleted", f"Entry {entry_id} deleted.", parent=show_window)
                show_window.destroy()
            else:
                messagebox.showerror("Not Found", f"No entry with ID {entry_id}.", parent=show_window)

        tk.Button(delete_frame, text="Delete", command=on_delete,
                  font=("Red Hat Mono", 11), bg="#cc4444", fg="white", width=8).pack(side=tk.LEFT, padx=5)

    def on_close():
        conn.close()
        window.destroy()

    tk.Button(window, text="Generate Random Password", command=on_generate,
              font=("Red Hat Mono", 12), bg="#666699", fg="white", width=25).pack(pady=10)

    tk.Button(window, text="Save This Entry", command=on_save,
              font=("Red Hat Mono", 12), bg="#666699", fg="white", width=25).pack(pady=5)

    tk.Button(window, text="Show All Saved", command=on_show_all,
              font=("Red Hat Mono", 12), bg="#666699", fg="white", width=25).pack(pady=10)

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()

def launch_login() -> None:
    login_window = tk.Tk()
    login_window.title("Enter Master Password")
    login_window.geometry("350x200")
    login_window.configure(bg="#34344b")

    tk.Label(login_window, text="Master Password", font=("Red Hat Mono", 16, "bold"), bg="#34344b", fg="white").pack(pady=20)
    tk.Label(login_window, text="Enter your database password:", font=("Red Hat Mono", 11), bg="#34344b", fg="white").pack()

    entry_master = tk.Entry(login_window, width=30, font=("Red Hat Mono", 12), show="*")
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
        login_window, text="Unlock", font=("Red Hat Mono", 12),
        bg="#666699", fg="white", width=15,
        command=on_unlock
    ).pack(pady=10)

    entry_master.bind("<Return>", lambda e: on_unlock())
    login_window.mainloop()