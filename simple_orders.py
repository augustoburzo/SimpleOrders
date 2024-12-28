import configparser
import datetime
import threading
import time
import tkinter as tk
import tkinter.messagebox
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import ttkbootstrap as ttk
import datetime as dt

from email_sender import send_mail


class MainApp(ttk.Window):
    def __init__(self, *args, **kwargs):
        ttk.Window.__init__(self, *args, **kwargs, themename="darkly")
        self.selected_item = ""
        self.configs = configparser.ConfigParser()
        self.configs.read(filenames="config.ini")
        self.title("Orders")
        self.resizable(tk.FALSE,tk.FALSE)
        self.icon = tk.PhotoImage(file="assets/icon.png")
        self.iconphoto(tk.FALSE, self.icon)
        self.popup = tk.Menu(self, tearoff=0)
        self.popup.add_command(label="Delete", command=self.delete_row)
        # Main labelframe containing the orders treeview
        self.main_labelframe = tk.LabelFrame(
            self, text="Waiting orders")
        self.main_labelframe.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.orders_treeview = ttk.Treeview(
            self.main_labelframe, show="headings",
            columns=("datetime", "product", "quantity"))
        self.orders_treeview.grid(column=0, row=0, sticky=tk.NSEW)
        self.orders_treeview.bind("<Button-3>", self.popup_menu)
        # Loads treeview's headings
        self.load_headings()

        self.main_labelframe.columnconfigure(0, weight=1)
        self.main_labelframe.rowconfigure(0, weight=1)
        # Frame containing the control buttons for the GUI
        self.buttons_frame = tk.Frame(self)
        self.buttons_frame.pack(fill=tk.X)
        self.send_order_btn = tk.Button(
            self.buttons_frame, text="Send orders", command=self.send_orders)
        self.send_order_btn.grid(column=0, row=0)
        self.clean_orders_btn = tk.Button(
            self.buttons_frame, text="Clean orders table",
            command=self.clean_orders)
        self.clean_orders_btn.grid(column=1, row=0)
        self.insert_order_btn = tk.Button(
            self.buttons_frame, text="Insert order", command=self.insert_order)
        self.insert_order_btn.grid(column=3, row=0)

        self.buttons_frame.columnconfigure(2, weight=1)

        # Simple status bar
        self.status_bar = tk.Label(
            self, text="Ready...", relief=tk.SUNKEN,
            justify=tk.LEFT, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, anchor=tk.S)

        self.initialize_menu()
        self.on_load() # Loads the current CSV file containing the products in order
        threading.Thread(target=self.update_daemon, daemon=tk.TRUE).start() # Starts the update daemon

    def initialize_menu(self):
        self.main_menu = tk.Menu(self, tearoff=tk.FALSE)
        self.file_menu = tk.Menu(self.main_menu, tearoff=tk.FALSE)
        self.about_menu = tk.Menu(self.main_menu, tearoff=tk.FALSE)
        self.file_menu.add_command(label="Configure", command=self.config_window)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.destroy)
        self.about_menu.add_command(label="About", command=self.about)
        self.main_menu.add_cascade(menu=self.file_menu, label="File")
        self.main_menu.add_cascade(menu=self.about_menu, label="?")
        self.configure(menu=self.main_menu)

    def about(self):
        about_win = tk.messagebox.showinfo(title="About", message="""
©2024 Augusto Burzo
____________________________________
Released under MIT License
""")

    def load_headings(self):
        self.orders_treeview.heading("#0", text="ID")
        self.orders_treeview.heading("datetime", text="Date & Time")
        self.orders_treeview.heading("product", text="Product")
        self.orders_treeview.heading("quantity", text="Quantity")

    def send_orders(self):
        orders_check = self.orders_treeview.get_children()
        if orders_check != ():
            check = tkinter.messagebox.askyesno("Are you sure?", "Do you really want to send this order?")
            if check:
                self.set_status("Sending orders...")
                msg = MIMEMultipart()
                msg["From"] = self.configs["Mail server"]["email"]
                msg["To"] = self.configs["Mail server"]["receiver"]
                msg["Subject"] = f"Order {datetime.datetime.now().strftime('%d/%m/%Y - %H:%M')}"
                table = MIMEText("""
<html>
<table style="border-collapse: collapse; width: 100%; border-color: #34495E; border-style: solid;" border="1">
    <tbody>
        <tr>
            <td style="width: 40%;"><span style="color: #236fa1;"><strong>Date &amp; Time</strong></span></td>
            <td style="width: 40%;"><span style="color: #236fa1;"><strong>Product</strong></span></td>
            <td style="width: 20%;"><span style="color: #236fa1;"><strong>Quantity</strong></span></td>
        </tr>

""", "html")
                msg.attach(table)
                for child in self.orders_treeview.get_children():
                    row = MIMEText(f"""
<tr>
    <td style="width: 40%;"><span style="color: #236fa1;">{self.orders_treeview.item(child)['values'][0]}<strong><br /></strong></span></td>
    <td style="width: 40%;"><span style="color: #236fa1;">{self.orders_treeview.item(child)['values'][1]}<strong><br /></strong></span></td>
    <td style="width: 20%;"><span style="color: #236fa1;">{self.orders_treeview.item(child)['values'][2]}<strong><br /></strong></span></td>
</tr>
""", "html")
                    msg.attach(row)
                ending = MIMEText(f"""
</tbody>
</table>
<p>
<p>This message was automatically generated.</p>
</html>""", "html")
                msg.attach(ending)
                message = msg.as_string()
                send_mail(message=message)
                new_orders = []
                for child in self.orders_treeview.get_children():
                    new_orders.append(self.orders_treeview.item(child)["values"])

                with open(f"order{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}.csv", "w+") as f:
                    f.truncate(0)
                    f.writelines("Date & Time, Product, Quantity\n")
                    for order in new_orders:
                        line = f"{order[0]},{order[1]},{order[2]}\n"
                        f.writelines(line)
                self.clean_orders()
                self.set_status("Order sent!")
        else:
            tk.messagebox.showinfo(title="No products", message="There's no product to send")

    def update_daemon(self):
        print("daemon")
        while True:
            orders = []
            for child in self.orders_treeview.get_children():
                orders.append(self.orders_treeview.item(child)["values"])
            time.sleep(2)
            new_orders = []
            for child in self.orders_treeview.get_children():
                new_orders.append(self.orders_treeview.item(child)["values"])

            if orders != new_orders:
                with open("orders.csv", "w+") as f:
                    f.truncate(0)
                    f.writelines("Date & Time, Product, Quantity\n")
                    for order in new_orders:
                        line = f"{order[0]},{order[1]},{order[2]}\n"
                        f.writelines(line)

    def on_load(self):
        with open("orders.csv", "r+") as f:
            lines = f.readlines()
            lines = lines[1:]
        for line in lines:
            line = line.split(",")
            self.orders_treeview.insert("", tk.END, values=line)


    def clean_orders(self):
        for child in self.orders_treeview.get_children():
            self.orders_treeview.delete(child)

    def insert_order(self):
        self.set_status("Adding order...")
        orders_win = tk.Toplevel(master=self)
        orders_win.title("Add order")
        product_lbl = tk.Label(orders_win, text="Product: ")
        product_lbl.grid(column=0, row=0)
        product_entry = tk.Entry(orders_win)
        product_entry.grid(column=1, row=0, sticky=tk.EW)
        quantity_lbl = tk.Label(orders_win, text="Quantity: ")
        quantity_lbl.grid(column=0, row=1)
        quantity_entry = ttk.Spinbox(orders_win, from_=1, to=10)
        quantity_entry.set(1)
        quantity_entry.grid(column=1, row=1)

        def insert(event=None):
            if product_entry.get() != "":
                order = (dt.datetime.now().strftime("%d/%m/%Y - %H:%M"),
                         product_entry.get(),
                         quantity_entry.get())
                self.orders_treeview.insert("", tk.END, values=order)
                orders_win.destroy()
                self.set_status("Order added")

        button_frame = tk.Frame(orders_win)
        button_frame.grid(column=0, row=2, columnspan=2)
        insert_order_btn = tk.Button(
            button_frame, text="Add", command=insert)
        insert_order_btn.grid(column=0, row=0)

        orders_win.columnconfigure(1, weight=1)
        product_entry.focus_set()
        product_entry.bind("<Return>", insert)
        quantity_entry.bind("<Return>", insert)

    def set_status(self, string: str):
        self.status_bar.configure(text=string)

    def config_window(self):
        config = configparser.ConfigParser()
        window = tk.Toplevel(master=self)
        window.title("Configure")
        email_lbl = tk.Label(window, text="Email:")
        email_lbl.pack(fill=tk.X)
        email_entry = tk.Entry(window)
        email_entry.pack(fill=tk.X)
        pwd_lbl = tk.Label(window, text="Password:")
        pwd_lbl.pack(fill=tk.X)
        pwd_entry = tk.Entry(window, show="*")
        pwd_entry.pack(fill=tk.X)
        smtp_lbl = tk.Label(window, text="SMTP Server:")
        smtp_lbl.pack(fill=tk.X)
        smtp_entry = tk.Entry(window)
        smtp_entry.pack(fill=tk.X)
        receiver_lbl = tk.Label(window, text="Recipient:")
        receiver_lbl.pack(fill=tk.X)
        receiver_entry = tk.Entry(window)
        receiver_entry.pack(fill=tk.X)
        def save_config():
            config["Mail server"] = {
                "smtp":smtp_entry.get(),
                "email":email_entry.get(),
                "password":pwd_entry.get(),
                "receiver":receiver_entry.get()}

            with open("config.ini", 'w') as configfile:
                config.write(configfile)

            window.destroy()

        save_btn = tk.Button(window, text="Save configuration", command=save_config)
        save_btn.pack(fill=tk.X)
        config.read("config.ini")
        email_entry.insert(0, config["Mail server"]["email"])
        pwd_entry.insert(0, config["Mail server"]["password"])
        smtp_entry.insert(0, config["Mail server"]["smtp"])
        receiver_entry.insert(0, config["Mail server"]["receiver"])

    def popup_menu(self, event):
        item = self.orders_treeview.identify_row(event.y)
        self.selected_item = item
        try:
            self.popup.tk_popup(event.x_root+1, event.y_root+1, 0)
        finally:
            self.popup.grab_release()

    def delete_row(self):
        self.orders_treeview.delete(self.selected_item)


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
