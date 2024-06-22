import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GroceryBillingSystem(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced Grocery Shop Billing System")
        self.geometry("900x700")
        self.configure(bg="#2e2e2e")
        self.cashier_name = "S M Abu Haider"
        self.category_var = tk.StringVar()
        self.item_var = tk.StringVar()
        self.create_widgets()
        self.setup_database()
        self.populate_categories_and_items()

    def create_widgets(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background="#2e2e2e")
        style.configure("TLabel", background="#2e2e2e", foreground="white", font=("Helvetica", 12))
        style.configure("TButton", background="#5e5e5e", foreground="white", font=("Helvetica", 12), padding=5)
        style.configure("TCombobox", fieldbackground="#4e4e4e", background="#4e4e4e", foreground="white")
        style.configure("TEntry", fieldbackground="#4e4e4e", foreground="white")

        # Header
        self.header_frame = ttk.Frame(self)
        self.header_frame.pack(fill=tk.X)
        self.header_label = ttk.Label(self.header_frame, text="Grocery Shop Billing System", font=("Helvetica", 24, "bold"), anchor="center")
        self.header_label.pack(pady=10, fill=tk.X)

        # Category and Item Selection
        self.selection_frame = ttk.Frame(self)
        self.selection_frame.pack(pady=20)

        self.category_label = ttk.Label(self.selection_frame, text="Category:", font=("Helvetica", 12))
        self.category_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.category_menu = ttk.Combobox(self.selection_frame, textvariable=self.category_var, state="readonly", font=("Helvetica", 12))
        self.category_menu.grid(row=0, column=1, padx=5, pady=5)
        self.category_menu.bind("<<ComboboxSelected>>", self.update_item_menu)

        self.item_label = ttk.Label(self.selection_frame, text="Item:", font=("Helvetica", 12))
        self.item_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.item_menu = ttk.Combobox(self.selection_frame, textvariable=self.item_var, state="readonly", font=("Helvetica", 12))
        self.item_menu.grid(row=0, column=3, padx=5, pady=5)

        self.quantity_label = ttk.Label(self.selection_frame, text="Quantity:", font=("Helvetica", 12))
        self.quantity_label.grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.quantity_entry = ttk.Entry(self.selection_frame, font=("Helvetica", 12))
        self.quantity_entry.grid(row=0, column=5, padx=5, pady=5)

        self.add_button = ttk.Button(self.selection_frame, text="Add to Bill", command=self.add_to_bill)
        self.add_button.grid(row=0, column=6, padx=5, pady=5)

        self.add_item_button = ttk.Button(self.selection_frame, text="Add Item to Stock", command=self.open_password_prompt)
        self.add_item_button.grid(row=0, column=7, padx=5, pady=5)

        # Bill Area
        self.bill_frame = ttk.Frame(self)
        self.bill_frame.pack(pady=20)

        self.bill_text = tk.Text(self.bill_frame, height=15, font=("Helvetica", 12), bg="#1e1e1e", fg="white")
        self.bill_text.pack(pady=10)

        # Total and Checkout
        self.total_frame = ttk.Frame(self)
        self.total_frame.pack(pady=20)

        self.total_label = ttk.Label(self.total_frame, text="Total: $", font=("Helvetica", 12))
        self.total_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.total_value = ttk.Label(self.total_frame, text="0", font=("Helvetica", 12))
        self.total_value.grid(row=0, column=1, padx=5, pady=5)

        self.checkout_button = ttk.Button(self.total_frame, text="Checkout", command=self.checkout)
        self.checkout_button.grid(row=0, column=2, padx=5, pady=5)

    def setup_database(self):
        self.conn = sqlite3.connect('grocery_shop.db')
        self.cursor = self.conn.cursor()

        # Drop existing stock table and create a new one with category column
        self.cursor.execute('''
            DROP TABLE IF EXISTS stock
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                item TEXT PRIMARY KEY,
                category TEXT,
                price REAL,
                quantity INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY,
                item TEXT,
                price REAL,
                quantity INTEGER,
                total REAL
            )
        ''')
        self.conn.commit()

    def populate_categories_and_items(self):
        categories = {
            "Beverages": [("Coke", 1.5, 50), ("Pepsi", 1.5, 60), ("Sprite", 1.5, 40)],
            "Fruits": [("Apple", 1.2, 50), ("Banana", 0.5, 100), ("Orange", 1.0, 75)],
            "Dairy": [("Milk", 2.0, 30), ("Cheese", 3.0, 20), ("Yogurt", 1.0, 25)],
            "Bakery": [("Bread", 1.5, 40), ("Cake", 5.0, 10), ("Muffin", 2.0, 30)],
            "Vegetables": [("Carrot", 0.8, 60), ("Broccoli", 1.5, 40), ("Spinach", 1.0, 50)],
            "Snacks": [("Chips", 1.2, 70), ("Cookies", 2.0, 50), ("Popcorn", 1.0, 40)],
            "Meat": [("Chicken", 5.0, 20), ("Beef", 7.0, 15), ("Pork", 6.0, 10)],
            "Seafood": [("Salmon", 8.0, 10), ("Shrimp", 10.0, 15), ("Crab", 12.0, 8)],
            "Frozen": [("Pizza", 7.0, 10), ("Ice Cream", 4.0, 20), ("Fries", 3.0, 30)],
            "Grains": [("Rice", 1.0, 100), ("Wheat", 1.2, 80), ("Oats", 1.5, 60)]
        }

        for category, items in categories.items():
            for item, price, quantity in items:
                self.cursor.execute("INSERT OR IGNORE INTO stock (item, category, price, quantity) VALUES (?, ?, ?, ?)", (item, category, price, quantity))

        self.conn.commit()
        self.update_category_menu()

    def update_category_menu(self):
        self.cursor.execute("SELECT DISTINCT category FROM stock")
        categories = [row[0] for row in self.cursor.fetchall()]
        self.category_menu['values'] = categories
        if categories:
            self.category_var.set(categories[0])
            self.update_item_menu()

    def update_item_menu(self, event=None):
        selected_category = self.category_var.get()
        self.cursor.execute("SELECT item, price FROM stock WHERE category=? AND quantity > 0", (selected_category,))
        items = [f"{row[0]} - ${row[1]}" for row in self.cursor.fetchall()]
        self.item_menu['values'] = items
        if items:
            self.item_var.set(items[0])

    def add_to_bill(self):
        item_info = self.item_var.get().split(" - $")
        item = item_info[0]
        price = float(item_info[1])
        quantity = int(self.quantity_entry.get())

        self.cursor.execute("SELECT quantity FROM stock WHERE item=?", (item,))
        stock_quantity = self.cursor.fetchone()[0]
        if quantity > stock_quantity:
            messagebox.showerror("Error", "Insufficient stock for this item.")
            return

        total = price * quantity
        self.bill_text.insert(tk.END, f'{item} - ${price} x {quantity} = ${total}\n')

        current_total = float(self.total_value.cget("text"))
        new_total = current_total + total
        self.total_value.config(text=str(new_total))

        self.cursor.execute("UPDATE stock SET quantity=quantity-? WHERE item=?", (quantity, item))
        self.conn.commit()

    def checkout(self):
        total_amount = float(self.total_value.cget("text"))
        if self.detect_fraud(total_amount):
            self.send_email(f"Fraudulent purchase detected. Total amount: ${total_amount}\nCashier: {self.cashier_name}")
            messagebox.showerror("Error", "Fraudulent purchase detected!")
        else:
            self.send_email(f"Purchase completed. Total amount: ${total_amount}\nCashier: {self.cashier_name}")
            messagebox.showinfo("Purchase Complete", f"Total amount to be paid: ${total_amount}")
        self.reset_bill()

    def detect_fraud(self, total_amount):
        # Simple fraud detection logic
        if total_amount > 1000:  # Example condition for fraud
            return True
        return False

    def send_email(self, message):
        sender = "mail server name goes here"
        recipient = "owner_email@example.com"  # Replace with actual owner's email
        subject = "Purchase Notification"
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = recipient
        body = MIMEText(message)
        msg.attach(body)

        try:
            with smtplib.SMTP('smtp.mailersend.net', 587) as server:
                server.starttls()
                server.login(sender, "dRf1STdychWC3B5Y")
                server.sendmail(sender, recipient, msg.as_string())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")

    def reset_bill(self):
        self.bill_text.delete('1.0', tk.END)
        self.total_value.config(text="0")
        self.quantity_entry.delete(0, tk.END)
        self.update_item_menu()

    def open_password_prompt(self):
        password_window = tk.Toplevel(self)
        password_window.title("Password Entry")
        password_window.geometry("300x150")
        password_window.configure(bg="#2e2e2e")

        password_label = ttk.Label(password_window, text="Enter Password:", font=("Helvetica", 12))
        password_label.pack(pady=10)
        self.password_entry = ttk.Entry(password_window, show='*', font=("Helvetica", 12))
        self.password_entry.pack(pady=5)

        submit_button = ttk.Button(password_window, text="Submit", command=lambda: self.check_password(password_window))
        submit_button.pack(pady=10)

    def check_password(self, window):
        password = self.password_entry.get()
        if password == "admin123":  # Replace with a secure password check method
            window.destroy()
            self.open_add_item_window()
        else:
            messagebox.showerror("Error", "Incorrect Password")

    def open_add_item_window(self):
        add_item_window = tk.Toplevel(self)
        add_item_window.title("Add New Item to Stock")
        add_item_window.geometry("400x300")
        add_item_window.configure(bg="#2e2e2e")

        category_label = ttk.Label(add_item_window, text="Category:", font=("Helvetica", 12))
        category_label.pack(pady=5)
        self.new_item_category_entry = ttk.Entry(add_item_window, font=("Helvetica", 12))
        self.new_item_category_entry.pack(pady=5)

        item_name_label = ttk.Label(add_item_window, text="Item Name:", font=("Helvetica", 12))
        item_name_label.pack(pady=5)
        self.new_item_name_entry = ttk.Entry(add_item_window, font=("Helvetica", 12))
        self.new_item_name_entry.pack(pady=5)

        item_price_label = ttk.Label(add_item_window, text="Item Price:", font=("Helvetica", 12))
        item_price_label.pack(pady=5)
        self.new_item_price_entry = ttk.Entry(add_item_window, font=("Helvetica", 12))
        self.new_item_price_entry.pack(pady=5)

        item_quantity_label = ttk.Label(add_item_window, text="Item Quantity:", font=("Helvetica", 12))
        item_quantity_label.pack(pady=5)
        self.new_item_quantity_entry = ttk.Entry(add_item_window, font=("Helvetica", 12))
        self.new_item_quantity_entry.pack(pady=5)

        add_button = ttk.Button(add_item_window, text="Add Item", command=self.add_new_item)
        add_button.pack(pady=20)

    def add_new_item(self):
        category = self.new_item_category_entry.get()
        item_name = self.new_item_name_entry.get()
        item_price = float(self.new_item_price_entry.get())
        item_quantity = int(self.new_item_quantity_entry.get())

        self.cursor.execute("INSERT OR IGNORE INTO stock (item, category, price, quantity) VALUES (?, ?, ?, ?)", (item_name, category, item_price, item_quantity))
        self.conn.commit()
        self.update_category_menu()
        self.send_email(f"New item added to stock.\nCategory: {category}\nItem: {item_name}\nPrice: ${item_price}\nQuantity: {item_quantity}\nCashier: {self.cashier_name}")

        messagebox.showinfo("Success", f"Item '{item_name}' added to stock.")
        self.new_item_category_entry.delete(0, tk.END)
        self.new_item_name_entry.delete(0, tk.END)
        self.new_item_price_entry.delete(0, tk.END)
        self.new_item_quantity_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = GroceryBillingSystem()
    app.mainloop()
