import threading
import time
import tkinter as tk
from tkinter import ttk
import datetime as dt


class MainApp:
    def __init__(self, master):
        self.root = master
        self.root.title("Orders")

        self.main_labelframe = tk.LabelFrame(
            self.root, text="Waiting orders")
        self.main_labelframe.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.orders_treeview = ttk.Treeview(
            self.main_labelframe, show="headings",
            columns=("datetime", "product", "quantity"))
        self.orders_treeview.heading("#0", text="ID")
        self.orders_treeview.heading("datetime", text="Date & Time")
        self.orders_treeview.heading("product", text="Product")
        self.orders_treeview.heading("quantity", text="Quantity")
        self.orders_treeview.grid(column=0, row=0, sticky=tk.NSEW)
        self.main_labelframe.columnconfigure(0, weight=1)
        self.main_labelframe.rowconfigure(0, weight=1)

        self.buttons_frame = tk.Frame(self.root)
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

        self.status_bar = tk.Label(
            self.root, text="Ready...", relief=tk.SUNKEN,
            justify=tk.LEFT, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, anchor=tk.S)

        self.on_load()
        threading.Thread(target=self.update_daemon, daemon=tk.TRUE).start()

    def send_orders(self):
        self.set_status("Sending orders...")
        orders = []
        for child in self.orders_treeview.get_children():
            orders.append(self.orders_treeview.item(child)["values"])
        print(orders)

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
        self.set_status("Inserting order...")
        orders_win = tk.Toplevel(master=self.root)
        orders_win.title("Insert order")
        product_lbl = tk.Label(orders_win, text="Product: ")
        product_lbl.grid(column=0, row=0)
        product_entry = tk.Entry(orders_win)
        product_entry.grid(column=1, row=0, sticky=tk.EW)
        quantity_lbl = tk.Label(orders_win, text="Quantity: ")
        quantity_lbl.grid(column=0, row=1)
        quantity_entry = ttk.Spinbox(orders_win, from_=1, to=10)
        quantity_entry.set(1)
        quantity_entry.grid(column=1, row=1)

        def insert():
            if product_entry.get() != "":
                order = (dt.datetime.now().strftime("%d/%m/%Y - %H:%M"),
                         product_entry.get(),
                         quantity_entry.get())
                self.orders_treeview.insert("", tk.END, values=order)
                orders_win.destroy()
                self.set_status("Order inserted")

        button_frame = tk.Frame(orders_win)
        button_frame.grid(column=0, row=2, columnspan=2)
        insert_order_btn = tk.Button(
            button_frame, text="Insert order", command=insert)
        insert_order_btn.grid(column=0, row=0)

        orders_win.columnconfigure(1, weight=1)

    def set_status(self, string: str):
        self.status_bar.configure(text=string)


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
