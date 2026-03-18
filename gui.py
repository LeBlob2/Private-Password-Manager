import tkinter as tk
from tkinter import messagebox
import sqlcipher3

from create_open_database import (
    get_connection,
    generate_password,
    save_password,
    fetch_all_passwords,
    delete_password_by_id,
    change_master_password,
    list_databases,
    resolve_db_path,
    db_path
)

font = "red_button Hat Mono"
background   = "#34344b"
button  = "#666699"
red_button  = "#8b4444"

def launch_main_app(conn, login_window: tk.Tk, selected_db_path: str) -> None:
    login_window.destroy()

    window = tk.Tk()
    window.title(f"Private Password Manager — {selected_db_path.split('/')[-1]}")
    window.geometry("500x640")
    window.configure(background=background)

    tk.Label(window, text="Private Password Manager", font=(font, 18, "bold"), background=background, fg="white").pack(pady=20)

    tk.Label(window, text="Website:", font=(font, 12), background=background, fg="white").pack()
    entry_website = tk.Entry(window, width=40, font=(font, 12))
    entry_website.pack(pady=5)

    tk.Label(window, text="Username:", font=(font, 12), background=background, fg="white").pack()
    entry_user = tk.Entry(window, width=40, font=(font, 12))
    entry_user.pack(pady=5)

    tk.Label(window, text="Email:", font=(font, 12), background=background, fg="white").pack()
    entry_email = tk.Entry(window, width=40, font=(font, 12))
    entry_email.pack(pady=5)

    tk.Label(window, text="Password:", font=(font, 12), background=background, fg="white").pack()
    entry_pass = tk.Entry(window, width=40, font=(font, 12), show="*")
    entry_pass.pack(pady=5)

    def on_generate():
        entry_pass.delete(0, tk.END)
        entry_pass.insert(0, generate_password())

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
        show_window.geometry("600x500")
        show_window.configure(background=background)

        text_area = tk.Text(show_window, font=(font, 11), wrap="word", background="black", fg="white")
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

        delete_frame = tk.Frame(show_window, background=background)
        delete_frame.pack(pady=8)

        tk.Label(delete_frame, text="Delete Entry ID:", font=(font, 11),
                 background=background, fg="white").pack(side=tk.LEFT, padx=(10, 5))

        entry_delete_id = tk.Entry(delete_frame, width=6, font=(font, 11))
        entry_delete_id.pack(side=tk.LEFT, padx=5)

        def on_delete():
            raw = entry_delete_id.get().strip()
            if not raw.isdigit():
                messagebox.showwarning("Invalid", "Please enter a valid numeric ID.", parent=show_window)
                return
            entry_id = int(raw)
            if not messagebox.askyesno("Confirm", f"Delete entry with ID {entry_id}?", parent=show_window):
                return
            if delete_password_by_id(conn, entry_id):
                messagebox.showinfo("Deleted", f"Entry {entry_id} deleted.", parent=show_window)
                show_window.destroy()
            else:
                messagebox.showerror("Not Found", f"No entry with ID {entry_id}.", parent=show_window)

        tk.Button(delete_frame, text="Delete", command=on_delete,
                  font=(font, 11), background="#cc4444", fg="white", width=8).pack(side=tk.LEFT, padx=5)

    def on_change_master_password():
        chg_window = tk.Toplevel(window)
        chg_window.title("Change Master Password")
        chg_window.geometry("400x280")
        chg_window.configure(background=background)
        chg_window.resizable(False, False)

        tk.Label(chg_window, text="Change Master Password", font=(font, 14, "bold"),
                 background=background, fg="white").pack(pady=15)

        tk.Label(chg_window, text="Current Password:", font=(font, 11), background=background, fg="white").pack()
        entry_current = tk.Entry(chg_window, width=32, font=(font, 11), show="*")
        entry_current.pack(pady=5)

        tk.Label(chg_window, text="New Password:", font=(font, 11), background=background, fg="white").pack()
        entry_new = tk.Entry(chg_window, width=32, font=(font, 11), show="*")
        entry_new.pack(pady=5)

        tk.Label(chg_window, text="Confirm New Password:", font=(font, 11), background=background, fg="white").pack()
        entry_confirm = tk.Entry(chg_window, width=32, font=(font, 11), show="*")
        entry_confirm.pack(pady=5)

        def on_confirm_change():
            current = entry_current.get().strip()
            new_pw  = entry_new.get().strip()
            confirm = entry_confirm.get().strip()

            if not current or not new_pw or not confirm:
                messagebox.showwarning("Missing Info", "Please fill all fields.", parent=chg_window)
                return
            if new_pw != confirm:
                messagebox.showerror("Mismatch", "New passwords do not match.", parent=chg_window)
                return
            if new_pw == current:
                messagebox.showwarning("Same Password", "New password must differ from current.", parent=chg_window)
                return
            try:
                change_master_password(selected_db_path, current, new_pw)
                messagebox.showinfo("Success", "Master password changed!\nPlease log in again.", parent=chg_window)
                chg_window.destroy()
                conn.close()
                window.destroy()
                launch_login()
            except ValueError:
                messagebox.showerror("Wrong Password", "Current password is incorrect.", parent=chg_window)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=chg_window)

        tk.Button(chg_window, text="Change Password", command=on_confirm_change,
                  font=(font, 11), background="#cc4444", fg="white", width=20).pack(pady=15)

    def on_close():
        conn.close()
        window.destroy()

    def on_logout():
        conn.close()
        window.destroy()
        launch_login()

    tk.Button(window, text="Generate Random Password", command=on_generate,
              font=(font, 12), background=button, fg="white", width=25).pack(pady=10)

    tk.Button(window, text="Save This Password", command=on_save,
              font=(font, 12), background=button, fg="white", width=25).pack(pady=5)

    tk.Button(window, text="Show All Saved", command=on_show_all,
              font=(font, 12), background=button, fg="white", width=25).pack(pady=10)

    tk.Button(window, text="Change Master Password", command=on_change_master_password,
              font=(font, 12), background=red_button, fg="white", width=25).pack(pady=5)

    tk.Button(window, text="Logout", command=on_logout,
              font=(font, 12), background=red_button, fg="white", width=25).pack(pady=5)

    window.protocol("WM_DELETE_WINDOW", on_close)
    window.mainloop()

def launch_login() -> None:
    login_window = tk.Tk()
    login_window.title("Private Password Manager — Login")
    login_window.geometry("420x480")
    login_window.configure(background=background)
    login_window.resizable(False, False)

    tk.Label(login_window, text="Private Password Manager", font=(font, 15, "bold"),
             background=background, fg="white").pack(pady=(20, 5))

    selector_frame = tk.Frame(login_window, background=background)
    selector_frame.pack(pady=10, padx=20, fill="x")

    tk.Label(selector_frame, text="Database:", font=(font, 11), background=background, fg="white").pack(anchor="w")

    db_listbox = tk.Listbox(selector_frame, font=(font, 11), height=4,
                             background="#1e1e2e", fg="white", selectbackground=button,
                             selectforeground="white", activestyle="none")
    db_listbox.pack(fill="x", pady=(3, 0))

    # tracks which db names are pending creation (not yet on disk)
    pending_new = set()

    def refresh_db_list(select_name: str = None):
        db_listbox.delete(0, tk.END)
        dbs = list_databases()
        # also show any pending new databases
        all_names = dbs + [n for n in pending_new if n not in dbs]
        for name in all_names:
            label = f"+ {name}  [new]" if name in pending_new else name
            db_listbox.insert(tk.END, label)
        if select_name:
            for i, n in enumerate(all_names):
                if n == select_name:
                    db_listbox.selection_set(i)
                    db_listbox.activate(i)
                    break
        elif all_names:
            db_listbox.selection_set(0)
            db_listbox.activate(0)
        update_password_ui()

    new_frame = tk.Frame(login_window, background=background)
    new_frame.pack(pady=(5, 0), padx=20, fill="x")

    tk.Label(new_frame, text="New Database Name:", font=(font, 10), background=background, fg="white").pack(anchor="w")

    new_db_row = tk.Frame(new_frame, background=background)
    new_db_row.pack(fill="x")

    entry_new_db = tk.Entry(new_db_row, font=(font, 11), background="#1e1e2e", fg="white",
                             insertbackground="white", width=22)
    entry_new_db.pack(side=tk.LEFT, padx=(0, 8))

    def on_add_db():
        name = entry_new_db.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Enter a name for the new database.", parent=login_window)
            return
        safe = ''.join(c for c in name if c.isalnum() or c in ('_', '-'))
        if not safe:
            messagebox.showerror("Invalid Name", "Use only letters, numbers, _ or -", parent=login_window)
            return
        if safe in list_databases() or safe in pending_new:
            messagebox.showwarning("Exists", f'"{safe}" already exists.', parent=login_window)
            return
        pending_new.add(safe)
        entry_new_db.delete(0, tk.END)
        refresh_db_list(safe)

    tk.Button(new_db_row, text="Create New", font=(font, 10), background=button, fg="white",
              command=on_add_db, width=8).pack(side=tk.LEFT)
    #login and create screens are quite messy this is what i got
    pw_frame = tk.Frame(login_window, background=background)
    pw_frame.pack(pady=10, padx=20, fill="x")

    open_pw_frame = tk.Frame(pw_frame, background=background)
    tk.Label(open_pw_frame, text="Master Password:", font=(font, 11), background=background, fg="white").pack(anchor="w")
    entry_master = tk.Entry(open_pw_frame, width=34, font=(font, 12), show="*",
                             background="#1e1e2e", fg="white", insertbackground="white")
    entry_master.pack(pady=(3, 0), fill="x")

    new_pw_frame = tk.Frame(pw_frame, background=background)
    tk.Label(new_pw_frame, text="Set New Master Password:", font=(font, 11), background=background, fg="white").pack(anchor="w")
    entry_new_pw = tk.Entry(new_pw_frame, width=34, font=(font, 12), show="*",
                             background="#1e1e2e", fg="white", insertbackground="white")
    entry_new_pw.pack(pady=(3, 0), fill="x")
    tk.Label(new_pw_frame, text="Confirm Password:", font=(font, 11), background=background, fg="white").pack(anchor="w", pady=(8, 0))
    entry_confirm_pw = tk.Entry(new_pw_frame, width=34, font=(font, 12), show="*",
                                 background="#1e1e2e", fg="white", insertbackground="white")
    entry_confirm_pw.pack(pady=(3, 0), fill="x")

    def get_selected_name() -> str | None:
        sel = db_listbox.curselection()
        if not sel:
            return None
        raw = db_listbox.get(sel[0])
        # strip the "[new]" label if present
        return raw.replace("+ ", "").replace("  [new]", "").strip()

    def is_new_selected() -> bool:
        name = get_selected_name()
        return name in pending_new if name else False

    def update_password_ui(*_):
        """Show open or create password fields based on selection."""
        if is_new_selected():
            open_pw_frame.pack_forget()
            new_pw_frame.pack(fill="x")
            btn_unlock.config(text="Create & Unlock")
        else:
            new_pw_frame.pack_forget()
            open_pw_frame.pack(fill="x")
            btn_unlock.config(text="Unlock")

    db_listbox.bind("<<ListboxSelect>>", update_password_ui)

    def on_unlock():
        db_name = get_selected_name()
        if not db_name:
            messagebox.showwarning("No Database", "Select or create a database first.", parent=login_window)
            return

        selected_path = resolve_db_path(db_name)

        if is_new_selected():
            pw  = entry_new_pw.get()
            cpw = entry_confirm_pw.get()
            if not pw:
                messagebox.showwarning("Empty", "Please set a master password.", parent=login_window)
                return
            if pw != cpw:
                messagebox.showerror("Mismatch", "Passwords do not match.", parent=login_window)
                return
            try:
                conn = get_connection(pw, selected_path)
                pending_new.discard(db_name)
                launch_main_app(conn, login_window, selected_path)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=login_window)
        else:
            pw = entry_master.get()
            if not pw:
                messagebox.showwarning("Empty", "Please enter your master password.", parent=login_window)
                return
            try:
                conn = get_connection(pw, selected_path)
                launch_main_app(conn, login_window, selected_path)
            except ValueError:
                messagebox.showerror("Error", "Wrong master password!", parent=login_window)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=login_window)

    btn_unlock = tk.Button(login_window, text="Unlock", font=(font, 12), background=button, fg="white",
                            width=20, command=on_unlock)
    btn_unlock.pack(pady=12)

    entry_master.bind("<Return>", lambda e: on_unlock())
    entry_confirm_pw.bind("<Return>", lambda e: on_unlock())

    refresh_db_list()
    login_window.mainloop()
