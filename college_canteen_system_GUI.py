import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector as sql
from datetime import date

# ---------------- DATABASE CONNECTION -----------------
def connect_db():
    try:
        conn = sql.connect(
            host="localhost",
            user="root",
            password="thanvi1707",
            database="college_canteen"
        )
        return conn
    except Exception as e:
        messagebox.showerror("Error", f"Database Connection Failed!\n{e}")
        return None

# ---------------- GENERIC FUNCTIONS -----------------
def fetch_table(table_name, tree):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(f"SELECT * FROM {table_name}")
            cols = [i[0] for i in cur.description]
            tree["columns"] = cols
            tree["show"] = "headings"
            for col in cols:
                tree.heading(col, text=col)
                tree.column(col, width=120, anchor="center")
            rows = cur.fetchall()
            tree.delete(*tree.get_children())
            for row in rows:
                tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch {table_name}\n{e}")
        finally:
            conn.close()

def insert_record(table_name, entries, tree):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            columns = ', '.join(entries.keys())
            placeholders = ', '.join(['%s'] * len(entries))
            values = [e.get() for e in entries.values()]
            sql_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cur.execute(sql_query, values)
            conn.commit()
            messagebox.showinfo("Success", f"Record inserted into {table_name}!")
            for e in entries.values():
                e.delete(0, tk.END)
            fetch_table(table_name, tree)
        except Exception as e:
            messagebox.showerror("Insert Error", f"Failed to insert into {table_name}\n{e}")
        finally:
            conn.close()

def delete_record(table_name, tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showwarning("No Selection", "Please select a record to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?")
    if not confirm:
        return
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            columns = [tree.heading(col)["text"] for col in tree["columns"]]
            pk_col = columns[0]
            pk_val = tree.item(selected_item)["values"][0]
            cur.execute(f"DELETE FROM {table_name} WHERE {pk_col} = %s", (pk_val,))
            conn.commit()
            tree.delete(selected_item)
            messagebox.showinfo("Deleted", f"Record deleted from {table_name}.")
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete record\n{e}")
        finally:
            conn.close()

# ---------------- PROCEDURE & FUNCTION EXECUTION -----------------
def execute_procedure(proc_name, params, output_text):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            if proc_name == "calc_final_bill":
                cur.callproc(proc_name, [int(params[0].get()), 0])
                for result in cur.stored_results():
                    pass
                cur.execute("SELECT @_" + proc_name + "_1;")
                result = cur.fetchone()[0]
                output_text.insert(tk.END, f"Final Bill Amount: {result}\n")
            elif proc_name == "get_customer_orders":
                cur.callproc(proc_name, [int(params[0].get())])
                for result in cur.stored_results():
                    rows = result.fetchall()
                    output_text.insert(tk.END, f"Orders for Customer {params[0].get()}:\n")
                    for row in rows:
                        output_text.insert(tk.END, f"  {row}\n")
            elif proc_name == "GetTotalBill":
                cur.callproc(proc_name, [int(params[0].get())])
                for result in cur.stored_results():
                    rows = result.fetchall()
                    for row in rows:
                        output_text.insert(tk.END, f"Total Bill: {row[0]}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Procedure failed:\n{e}")
        finally:
            conn.close()

def execute_function(func_name, params, output_text):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            if func_name == "get_total_bill":
                cur.execute(f"SELECT get_total_bill({int(params[0].get())})")
            elif func_name == "full_name":
                cur.execute(f"SELECT full_name({int(params[0].get())})")
            elif func_name == "ApplyDiscount":
                cur.execute(f"SELECT ApplyDiscount({float(params[0].get())}, {float(params[1].get())})")
            result = cur.fetchone()
            output_text.insert(tk.END, f"{func_name} result: {result[0]}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Function execution failed:\n{e}")
        finally:
            conn.close()

# ---------------- MAIN APP -----------------
def open_main_app():
    root = tk.Tk()
    root.title("College Canteen Database Management")
    root.geometry("1500x850")
    root.configure(bg="#D6EAF8")

    # --- Left Sidebar ---
    sidebar = tk.Frame(root, width=200, bg="#0A174E")
    sidebar.pack(side="left", fill="y")

    # --- Right Content Frame ---
    content = tk.Frame(root, bg="#D6EAF8")
    content.pack(side="right", fill="both", expand=True)

    # --- Functions to display pages ---
    def clear_content():
        for widget in content.winfo_children():
            widget.destroy()

    def show_dashboard():
        clear_content()
        tk.Label(content, text="Welcome to College Canteen Database Dashboard",
                 font=("Arial", 24, "bold"), bg="#D6EAF8", fg="#0A174E").pack(pady=50)
        tk.Label(content, text="Use the sidebar to navigate between tables, procedures, and SQL runner.",
                 font=("Arial", 14), bg="#D6EAF8").pack(pady=10)

    def show_table(table_name, columns):
        clear_content()
        frame = tk.Frame(content)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        form_frame = tk.LabelFrame(frame, text="Add New Record", padx=10, pady=10, bg="#D4E6F0")
        form_frame.pack(side="left", fill="y", padx=10, pady=5)

        entries = {}
        for idx, col in enumerate(columns):
            tk.Label(form_frame, text=col, font=("Arial", 10, "bold"), bg="#E4E8EA").grid(row=idx, column=0, sticky="e", pady=4)
            entry = tk.Entry(form_frame, width=25)
            entry.grid(row=idx, column=1, padx=8, pady=4)
            entries[col] = entry

        table_frame = tk.Frame(frame)
        table_frame.pack(side="right", fill="both", expand=True, padx=10)

        tree = ttk.Treeview(table_frame)
        tree.pack(fill="both", expand=True)
        fetch_table(table_name, tree)

        btn_frame = tk.Frame(form_frame, bg="#f4f6f7")
        btn_frame.grid(row=len(columns), columnspan=2, pady=10)
        tk.Button(btn_frame, text="Add", bg="#137b2c", fg="white", width=12,
                  command=lambda: insert_record(table_name, entries, tree)).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete", bg="#dc3545", fg="white", width=12,
                  command=lambda: delete_record(table_name, tree)).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Refresh", bg="#175296", fg="white", width=12,
                  command=lambda: fetch_table(table_name, tree)).grid(row=0, column=2, padx=5)

    def show_procedure_page():
        clear_content()
        frame = tk.Frame(content)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        title = tk.Label(frame, text="Stored Procedures & Functions Executor",
                         font=("Arial", 16, "bold"), bg="#062D50", fg="white")
        title.pack(fill="x", pady=(0, 10))

        left = tk.Frame(frame, bg="#E4E8EA")
        left.pack(side="left", fill="y", padx=10, pady=10)

        tk.Label(left, text="Enter Parameter(s):", bg="#E4E8EA", font=("Arial", 11, "bold")).pack(pady=5)
        p1 = tk.Entry(left, width=20)
        p1.pack(pady=5)

        output_text = tk.Text(frame, height=25, width=90, bg="#FDFEFE", font=("Consolas", 10))
        output_text.pack(side="right", fill="both", expand=True, padx=10)

        tk.Button(left, text="Run get_customer_orders", bg="#007b00", fg="white",
                  command=lambda: execute_procedure("get_customer_orders", [p1], output_text)).pack(pady=5)
        tk.Button(left, text="Run GetTotalBill", bg="#8b0000", fg="white",
                  command=lambda: execute_procedure("GetTotalBill", [p1], output_text)).pack(pady=5)
        tk.Button(left, text="Run full_name()", bg="#802090", fg="white",
                  command=lambda: execute_function("full_name", [p1], output_text)).pack(pady=5)
        tk.Button(left, text="Clear Output", bg="#333333", fg="white",
                  command=lambda: output_text.delete(1.0, tk.END)).pack(pady=10)

    def show_sql_runner_page():
        clear_content()
        frame = tk.Frame(content, padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        title = tk.Label(frame, text="SQL Query Runner", font=("Arial", 16, "bold"),
                         bg="#30336b", fg="white")
        title.pack(fill="x", pady=10)

        sql_box = tk.Text(frame, height=8, font=("Consolas", 12))
        sql_box.pack(fill="x", padx=10)

        result_frame = tk.Frame(frame)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)

        def execute_sql():
            query = sql_box.get("1.0", tk.END).strip()
            if not query:
                messagebox.showwarning("Empty Query", "Please enter SQL query.")
                return
            conn = connect_db()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                cursor.execute(query)
                if cursor.description:
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    for w in result_frame.winfo_children():
                        w.destroy()
                    tree = ttk.Treeview(result_frame, columns=columns, show="headings")
                    tree.pack(fill="both", expand=True)
                    for col in columns:
                        tree.heading(col, text=col)
                        tree.column(col, width=150)
                    for row in rows:
                        tree.insert("", tk.END, values=row)
                else:
                    conn.commit()
                    messagebox.showinfo("Success", "Query executed successfully.")
            except Exception as e:
                messagebox.showerror("SQL Error", str(e))
            finally:
                cursor.close()
                conn.close()

        tk.Button(frame, text="Execute Query", font=("Arial", 12, "bold"),
                  bg="green", fg="white", command=execute_sql).pack(pady=5)

    # --- Sidebar Buttons ---
    tables = {
        "Food": ["F_item_no", "F_name", "F_type", "F_price"],
        "Customer": ["customer_id", "c_name", "ph_no", "address", "first_name", "middle_name", "last_name"],
        "Administrator": ["admin_id", "A_name", "address"],
        "Phone Numbers": ["admin_id", "ph_no"],
        "Orders": ["order_id", "order_date", "order_No", "user_id", "quantity", "customer_id", "admin_id"],
        "Item": ["item_id", "I_name", "description", "price", "order_id", "customer_id"],
        "Staff": ["staff_id", "staff_name", "order_id"],
        "Offer": ["offer_id", "offer_amt", "start_date", "end_date", "item_id", "staff_id"],
        "Bill": ["bill_id", "bill_amount", "bill_date", "customer_id", "order_id", "admin_id"],
        "Delivered": ["customer_id", "F_item_no"],
    }

    tk.Button(sidebar, text="Dashboard", bg="#0A174E", fg="white", width=25, command=show_dashboard).pack(pady=5)
    for t, c in tables.items():
        tk.Button(sidebar, text=t, bg="#0A174E", fg="white", width=25,
                  command=lambda t=t, c=c: show_table(t, c)).pack(pady=2)
    tk.Button(sidebar, text="Procedures / Functions", bg="#0A174E", fg="white", width=25,
              command=show_procedure_page).pack(pady=5)
    tk.Button(sidebar, text="SQL Runner", bg="#0A174E", fg="white", width=25,
              command=show_sql_runner_page).pack(pady=5)
    tk.Button(sidebar, text="Logout", bg="#8B0000", fg="white", width=25,
              command=lambda: (root.destroy(), login_window())).pack(side="bottom", pady=10)

    show_dashboard()
    root.mainloop()

# ---------------- LOGIN WINDOW -----------------
def login_window():
    login = tk.Tk()
    login.title("Login")
    login.geometry("550x550")
    login.configure(bg="#D3DAF2")

    tk.Label(login, text="College Canteen Login", font=("Arial",36, "bold"),
             fg="black", bg="#D3DAF2").pack(pady=20)
    tk.Label(login, text="Username:", font=("Arial",24, "bold"),fg="black", bg="#D3DAF2").pack()
    user_entry = tk.Entry(login, width=35)
    user_entry.pack(pady=20)
    tk.Label(login, text="Password:", fg="black",font=("Arial",24, "bold"), bg="#D3DAF2").pack()
    pass_entry = tk.Entry(login, width=35, show="*")
    pass_entry.pack(pady=20)

    def check_login():
        if user_entry.get() == "admin" and pass_entry.get() == "1234":
            login.destroy()
            open_main_app()
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password!")

    tk.Button(login, text="Login", bg="green", fg="white",
              width=15, command=check_login).pack(pady=15)
    login.mainloop()

# ---------------- START APP -----------------
login_window()
