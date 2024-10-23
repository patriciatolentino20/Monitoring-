import hashlib
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from matplotlib import pyplot as plt, table
import datetime
from time import strftime
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry
import re
from matplotlib.font_manager import FontProperties

connect = sqlite3.connect("members.db")
cursor = connect.cursor()

tourists_add = 0

def login():
    username = username_entry.get()
    password = password_entry.get()

    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Login Successful", "Welcome, " + username)
        open_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def open_dashboard():
    login_window.withdraw()
    username = username_entry.get()
    dashboard_window = tk.Toplevel(login_window)
    dashboard_window.title("Matictic Entrance Monitoring System")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Microsoft New Tai Lue", 12, "bold"))
    style.configure("Treeview", font=("Microsoft New Tai Lue", 12))


    first_display = False
    def first():
        Head.config(text="Welcome!")
        add_frame.pack_forget()
        payment_frame.pack_forget()
        content_frame.pack_forget()
        profileframe.pack_forget()
        addAccountFrame.pack_forget()
        Firstframe.pack()

        nonlocal first_display
        if first_display:
            return
        first_display = True
        def display():
            image_path = "background.jpg"  # Replace with the path to your image file
            image = Image.open(image_path)
            photo = ImageTk.PhotoImage(image)

            # Update the label to display the image
            image_label.config(image=photo)
            image_label.image = photo

        image_label = tk.Label(Firstframe)
        image_label.pack()
        display()

    content_displayed = False

    def open_page():
        Head.config(text="Overview")
        add_frame.pack_forget()
        payment_frame.pack_forget()
        content_frame.pack()
        Firstframe.pack_forget()
        addAccountFrame.pack_forget()
        profileframe.pack_forget()
        nonlocal content_displayed
        if content_displayed:
            return
        content_displayed = True

        listbox_frame = tk.Frame(content_frame)
        listbox_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=90, padx=10)

        List = tk.Label(listbox_frame, text="Records of Tourists", font=("Microsoft New Tai Lue", 16, 'bold'), fg="#000000")
        List.pack()

        columns = ("Name", "Address", "Contact No.")
        table = ttk.Treeview(listbox_frame, columns=columns, show="headings", height=100)

        # Create a style and configure it with the desired font
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft New Tai Lue", 12, "bold"))

        for col in columns:
            table.heading(col, text=col)

        table.pack()


        def search_members(search_term):
            cursor.execute("SELECT * FROM members WHERE name LIKE ? OR address LIKE ? OR contact LIKE ?",
                           ('%' + search_term + '%', '%' + search_term + '%', '%' + search_term + '%'))
            data = cursor.fetchall()
            table.delete(*table.get_children())
            for row in data:
                table.insert('', 'end', values=(row[0], row[1], row[2]))
            if not search_term:
                update_listbox()
            dashboard_window.after(500000, update_listbox)

        # Add this function where it makes sense in your code, for example, you can bind it to a button or an entry widget for user input.
        # For example, you can add a search button and call the search_members function when the button is clicked.


        # Also, you might want to add an entry widget for the user to input the search term.
        search_entry = tk.Entry(content_frame, font=("Microsoft New Tai Lue", 12))
        search_entry.pack(pady=10,padx=100)

        search_button = tk.Button(content_frame, text="Search Tourist", command=lambda: search_members(search_entry.get()),font=("Microsoft New Tai Lue", 12,'bold'),bg="#b4b4b4")
        search_button.pack(pady=10,padx=100)

        def update_listbox():
            cursor.execute("SELECT * FROM members")
            data = cursor.fetchall()
            table.delete(*table.get_children())
            for row in data:
                table.insert('', 'end', values=(row[0], row[1], row[2]))
            dashboard_window.after(500000, update_listbox)

        update_listbox()
        graph_frame = tk.Frame(content_frame,height=100)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=70, padx=10)

        if position[0] == "Monitoring_Station_Clerk":
            graph_frame.pack_forget()
        else:
            graph_frame.pack()

        graph_displayed = False
        def show_fee_chart():
            nonlocal graph_displayed
            if graph_displayed:
                return
            graph_displayed = True

            cursor.execute(
                "SELECT strftime('%m', timestamp) as month, sum(fee_amount) as total_fee FROM entrance_fees GROUP BY month")
            results = cursor.fetchall()
            months = [str(i).zfill(2) for i in range(1, 13)]
            total_fees = [0] * 12

            for result in results:
                index = int(result[0]) - 1
                total_fees[index] = result[1]

            fig = plt.figure(figsize=(5, 4))

            ax = fig.add_subplot(111)
            ax.bar(months, total_fees, tick_label=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
            font_props = FontProperties(family='Microsoft New Tai Lue', weight='bold', size=10)
            ax.set_xlabel('Month', fontproperties=font_props)
            ax.set_ylabel('Total Fees', fontproperties=font_props)
            ax.set_title('Matictic River Entrance Fee Chart', fontproperties=font_props)

            canvas = FigureCanvasTkAgg(fig, master=graph_frame)
            canvas.get_tk_widget().pack()

            dashboard_window.after(5000, show_fee_chart)

        show_fee_chart()
        update_listbox()

    def create_add_page():
        Head.config(text="Add Tourist")
        content_frame.pack_forget()
        add_frame.pack()
        addAccountFrame.pack_forget()
        Firstframe.pack_forget()
        profileframe.pack_forget()
        payment_frame.pack_forget()

        cursor.execute("DELETE from daily")
        connect.commit()
        def update_touris():
            cursor.execute("SELECT name, address FROM daily")
            tourists = cursor.fetchall()
            tourists_listbox.delete(0, tk.END)
            for tour in tourists:
                tourists_listbox.insert(tk.END, f" {tour[0]}                {tour[1]}")
            tourists_count_label.config(text=f"Tourists Count: {len(tourists)}")
            if len(tourists) >= 2000:
                add_button1.config(state=tk.DISABLED)
            else:
                add_button1.config(state=tk.NORMAL)

        def add_member():
            name = tourists_name_entry.get()
            address = tourists_address_entry.get()
            contact = tourists_cellno_entry.get()

            if name and re.match(r'^\+63\d{10}$|^\d{11}$', contact) and re.match(r'^[A-Za-z\s\.\'\-]*$', name):

                global tourists_add
                tourists_add += 1
                cursor.execute("INSERT INTO members (name, address, contact) VALUES (?, ?, ?)", (name, address, contact))
                cursor.execute("INSERT INTO daily (Name, Address, Contact) VALUES (?, ?, ?)", (name, address, contact))
                connect.commit()
                tourists_name_entry.delete(0, tk.END)
                tourists_cellno_entry.delete(0, tk.END)
                update_touris()
                error_label.pack_forget()
                fee_entry.delete(0, tk.END)
                fee_entry.insert(0, str(tourists_add))
            else:
                error_label.config(text="Fill in the empty fields. Check your Contact No.")

        def reset_daily_limitation():
            cursor.execute("DELETE FROM members WHERE id > 0")
            connect.commit()
            update_touris()

        def reset_daily():
            current_time = datetime.datetime.now().time()
            reset_time = datetime.time(0, 0)
            if current_time.hour == reset_time.hour and current_time.minute == reset_time.minute:
                reset_daily_limitation()
            add_frame.after(60000, reset_daily)

        reset_daily()

        def reset_add_member():
            global tourists_add
            tourists_name_entry.delete(0, tk.END)
            tourists_address_entry.delete(0, tk.END)
            tourists_cellno_entry.delete(0, tk.END)
            tourists_listbox.delete(0, tk.END)
            error_label.config(text="")
            tourists_add = 0
            fee_entry.delete(0, tk.END)
            fee_entry.insert(0, str(tourists_add))

        def add_fee_record():
            user = Username.cget("text")
            position = Position.cget("text")
            fee_amount = fee_entry.get()
            fee_amount = float(fee_amount) * 20
            if not fee_amount:
                messagebox.showerror("Error", "Please add tourists.")
                return

            current_date = datetime.datetime.now().date()
            current_time = strftime('%H:%M:%S')
            cursor.execute("INSERT INTO entrance_fees (fee_amount, timestamp, ExactTime, Username, Position) VALUES (?, ?, ?, ?, ?)",
                           (float(fee_amount), current_date, current_time, user, position))
            cursor.execute("DELETE from daily")

            connect.commit()

            messagebox.showinfo("Add Transaction", f"Total Fee: Php {fee_amount}")
            error_label.pack_forget()

            # Reset fee_entry to zero
            fee_entry.delete(0, tk.END)
            fee_entry.insert(0, "0")

            # Reset the "Add Member" input fields and tourists_add count
            reset_add_member()


        tourists_name_label = tk.Label(add_frame, text="Enter Name:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
        tourists_name_label.grid(row=2, column=0, pady=10)

        tourists_name_entry = tk.Entry(add_frame,font=("Microsoft New Tai Lue", 12,))
        tourists_name_entry.grid(row=2, column=1, pady=10)

        tourists_address_label = tk.Label(add_frame, text="Enter Address:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
        tourists_address_label.grid(row=4, column=0, pady=10)

        tourists_address_entry = tk.Entry(add_frame,font=("Microsoft New Tai Lue", 12,))
        tourists_address_entry.grid(row=4, column=1, pady=10)

        tourists_cellno_label = tk.Label(add_frame, text="Enter CellNo:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
        tourists_cellno_label.grid(row=6, column=0, pady=10)

        tourists_cellno_entry = tk.Entry(add_frame,font=("Microsoft New Tai Lue", 12,))
        tourists_cellno_entry.grid(row=6, column=1)

        add_button1 = tk.Button(add_frame, text="Add Tourist", command=add_member,font=("Microsoft New Tai Lue", 12,'bold'),fg="#ffffff",bg="#03254c")
        add_button1.grid(row=8, column=1, columnspan=2, pady=0)

        error_label = tk.Label(add_frame, text="", fg="red",font=("Microsoft New Tai Lue", 12,'bold'))
        error_label.grid(row=9, column=0, columnspan=2)

        listbox_frame = ttk.Frame(add_frame)
        listbox_frame.grid(row=10, column=0, columnspan=2)
        tourists_listbox = tk.Listbox(listbox_frame, width=70, font=("Microsoft New Tai Lue", 10))
        tourists_listbox.pack()

        tourists_count_label = tk.Label(add_frame, text="Tourists Count: 0",font=("Microsoft New Tai Lue", 12,'bold'),fg="#000000")
        tourists_count_label.grid(row=11, column=0, columnspan=2)

        fee_label = tk.Label(add_frame, text="Number of tourists:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#000000")
        fee_label.grid(row=13, column=0, pady=10)

        fee_entry = tk.Entry(add_frame,bg="#f0f0f0", borderwidth=0,font=("Microsoft New Tai Lue", 12,'bold'))
        fee_entry.grid(row=13, column=1, pady=10)

        add_button = tk.Button(add_frame, text="Add Record", command=add_fee_record,font=("Microsoft New Tai Lue", 12,'bold'),fg="#ffffff",bg="#03254c")
        add_button.grid(row=15, column=0, columnspan=2, pady=10)

    add_account = False
    def addAccount():
        Head.config(text="Add Account")
        content_frame.pack_forget()
        add_frame.pack_forget()
        profileframe.pack_forget()
        Firstframe.pack_forget()
        payment_frame.pack_forget()
        addAccountFrame.pack()

        nonlocal add_account

        if add_account:
            return
        add_account = True

        def on_add_button_click():
            # Retrieve data from entry widgets
            username = username_entry.get()
            password = password_entry.get()
            position = position_combobox.get()
            image_path = "profile.jpg"



            pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
            result = re.findall(pattern, password)

            if result:
                messagebox.showinfo("Successful", username + " is added successfully")
                cursor.execute("INSERT INTO users (username, password, position, path) VALUES (?, ?, ?, ?)",
                               (username, password, position, image_path))
                connect.commit()
                update_listbox()
            else:
                messagebox.showinfo("Registration unsuccessful", "Password not strong")


            username_entry.delete(0, tk.END)
            password_entry.delete(0, tk.END)
            position_combobox.set('Select a position')

            update_listbox()

        def on_combobox_select(event):
            selected_position = position_combobox.get()
            print(f"Selected position: {selected_position}")

        # Create entry widgets for username and password
        frame = ttk.Frame(addAccountFrame)
        frame.grid(row=0, column=0, padx=30, pady=100)

        tk.Label(frame, text="User Name:", font=("Microsoft New Tai Lue", 12, 'bold'), fg="#03254c").pack(pady=0)
        username_entry = tk.Entry(frame, font=("Microsoft New Tai Lue", 12,))
        username_entry.pack(pady=0)

        tk.Label(frame, text="", font=("Microsoft New Tai Lue", 12, 'bold'), fg="#03254c").pack(pady=10)
        tk.Label(frame, text="Password:", font=("Microsoft New Tai Lue", 12, 'bold'), fg="#03254c").pack(pady=5)
        password_entry = tk.Entry(frame,font=("Microsoft New Tai Lue", 12,))  # Show '*' for password
        password_entry.pack(pady=5)

        tk.Label(frame, text="", font=("Microsoft New Tai Lue", 12, 'bold'), fg="#03254c").pack(pady=10)
        tk.Label(frame, text="Position:", font=("Microsoft New Tai Lue", 12, 'bold'), fg="#03254c").pack(pady=0)
        positions = ('Barangay_Matictic_Official', 'Monitoring_Station_Clerk')  # Sample positions
        position_combobox = ttk.Combobox(frame, values=positions, font=("Microsoft New Tai Lue", 10, 'bold'))
        position_combobox.bind("<<ComboboxSelected>>", on_combobox_select)
        position_combobox.set('Select a position')
        position_combobox.pack(pady=5)

        add_button = tk.Button(frame, text="Add Account", command=on_add_button_click,
                               font=("Microsoft New Tai Lue", 10, 'bold'),
                               fg="#ffffff", bg="#03254c")
        add_button.pack(pady=10)

        # Move the listbox to t he right
        listbox_listPaymentframe = tk.Frame(addAccountFrame)
        listbox_listPaymentframe.grid(row=0, column=1, sticky="nsew", padx=10, pady=50)

        def on_delete_button_click(username):
            confirmation = tk.messagebox.askyesno("Confirm Deletion", f"Do you want to delete the user '{username}'?")
            if confirmation:
                # Perform the deletion in the database
                cursor.execute("DELETE FROM users WHERE username=?", (username,))
                connect.commit()
                # Update the Treeview
                update_listbox()

        def update_listbox():
            cursor.execute("SELECT id, username, password, position FROM users")
            data = cursor.fetchall()

            # Clear the existing items in the table
            for widget in listbox_listPaymentframe.winfo_children():
                widget.destroy()

            for col, column_name in enumerate(("ID", "Username", "Password (MD5)", "Position", "Delete")):
                header_label = tk.Label(listbox_listPaymentframe, text=column_name,
                                        font=("Microsoft New Tai Lue", 12, "bold"))
                header_label.grid(row=0, column=col, padx=5, pady=5)

            # Display the data
            for row_index, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    if col == 2:  # Check if it is the password column
                        # Display MD5 hash of the password
                        md5_hash = hashlib.md5(value.encode()).hexdigest()
                        label = tk.Label(listbox_listPaymentframe, text=md5_hash, font=("Microsoft New Tai Lue", 10))
                    else:
                        label = tk.Label(listbox_listPaymentframe, text=str(value), font=("Microsoft New Tai Lue", 10))
                    label.grid(row=row_index + 1, column=col, padx=5, pady=5)

                # Add a delete button
                delete_button_style = ttk.Style()

                # Configure the background color for the new style
                delete_button_style.configure("Delete.TButton", background="red", foreground="red")

                delete_button = ttk.Button(
                    listbox_listPaymentframe,
                    text='Delete',
                    command=lambda r=row_data[1]: on_delete_button_click(r),
                    style="Delete.TButton"  # Apply the new style to the button
                )

                delete_button.grid(row=row_index + 1, column=len(row_data), padx=5, pady=5, sticky="w")

            addAccountFrame.after(5000, update_listbox)

        # Create a Treeview with the correct column identifiers
        columns = ("Username", "Password", "Position", "Delete")
        table = ttk.Treeview(listbox_listPaymentframe, columns=columns, show="headings")

        # Set column headers
        for col in columns:
            table.heading(col, text=col)

        # Display the Treeview
        table.pack(fill=tk.BOTH, expand=True)

        # Call the update_listbox function to populate the Treeview
        update_listbox()

    profile_display = False

    def Profile():
        Head.config(text="Profile")
        content_frame.pack_forget()
        add_frame.pack_forget()
        addAccountFrame.pack_forget()
        payment_frame.pack_forget()
        profileframe.pack()
        Firstframe.pack_forget()
        nonlocal profile_display

        if profile_display:
            return
        profile_display = True

        def load_image():
            cursor.execute('SELECT path FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            if row:
                image_path = row[0]
                image = Image.open(image_path)

                image.thumbnail((150, 150))

                photo = ImageTk.PhotoImage(image)

                image_label.config(image=photo)
                image_label.image = photo

        def upload_image():
            name = Username.cget("text")
            file_path = filedialog.askopenfilename(
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.ppm *.pgm *.tif *.tiff")])
            if file_path:
                cursor.execute('Update users set path = (?) where username = (?)', (file_path, name))
                connect.commit()
                image_id.set(Username.cget("text"))
                load_image()
                Picutre()

        def changePassword():
            passwordFrame.pack()

            def changeOldPassword():
                oldpassword = oldPassEntry.get()
                newpassword = newPassEntry.get()
                name = Username.cget("text")


                cursor.execute('SELECT username FROM users WHERE password = ?', (oldpassword,))
                row = cursor.fetchone()

                if row:
                    pattern = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"
                    result = re.findall(pattern, newpassword)
                    if result:
                        messagebox.showinfo("Successful","Password Changed")
                        cursor.execute('Update users set password = (?) where username = (?)', (newpassword, name))
                        connect.commit()
                        passwordFrame.pack_forget()
                    else:
                        messagebox.showinfo("Unsuccessful","Password not strong")
                else:
                    messagebox.showinfo("Unsuccessful","Incorrect Password. Try Again")


            def toggle_password_visibility():
                confirmPassword.config(show="" if show_password_var.get() else "*")
                newPassEntry.config(show="" if show_password_var.get() else "*")
                oldPassEntry.config(show="" if show_password_var.get() else "*")

            show_password_var = tk.BooleanVar()

            # Create a Checkbox



            Pad2 = tk.Label(passwordFrame, text="", font=("Microsoft New Tai Lue", 12, 'bold'),
                            fg="#03254c")
            Pad2.grid(row=2, column=0, pady=10)

            oldPassLabel = tk.Label(passwordFrame, text="Old Password:", font=("Microsoft New Tai Lue", 12, 'bold'),
                                    fg="#03254c")
            oldPassLabel.grid(row=4, column=0, pady=0)

            oldPassEntry = tk.Entry(passwordFrame, show="*", font=("Microsoft New Tai Lue", 12,))
            oldPassEntry.grid(row=4, column=1, pady=0)

            newPassLabel = tk.Label(passwordFrame, text="New Password:", font=("Microsoft New Tai Lue", 12, 'bold'),
                                        fg="#03254c")
            newPassLabel.grid(row=6, column=0, pady=0)

            newPassEntry = tk.Entry(passwordFrame, show="*", font=("Microsoft New Tai Lue", 12,))
            newPassEntry.grid(row=6, column=1, pady=0)

            confirmPass = tk.Label(passwordFrame, text="Confirm Password:", font=("Microsoft New Tai Lue", 12, 'bold'),
                                    fg="#03254c")
            confirmPass.grid(row=10, column=0, pady=0)

            confirmPassword = tk.Entry(passwordFrame, show="*", font=("Microsoft New Tai Lue", 12,))
            confirmPassword.grid(row=10, column=1, pady=0)

            ChangeBtn = tk.Button(passwordFrame, text="Save", command=changeOldPassword,
                                      font=("Microsoft New Tai Lue", 12, 'bold'), fg="#ffffff", bg="#03254c")
            ChangeBtn.grid(row=12, column=1, columnspan=2, pady=20)

        frame = ttk.Frame(profileframe)
        frame.pack(padx=10, pady=10)

        # Label to display the image
        image_label = ttk.Label(frame)
        image_label.grid(row=0, column=0)

        upload_button = ttk.Button(frame, text="Change Profile", command=upload_image)
        upload_button.grid(row=1, column=0)

        image_id = tk.StringVar()
        image_id.set(Username.cget("text"))
        image_id_entry = ttk.Label(frame, textvariable=image_id, font=("Arial", 12, "bold"))
        image_id_entry.grid(row=25, column=0)

        cursor.execute('Select position from users WHERE username = ?', (username,))
        position = cursor.fetchone()

        pofitionUser = ttk.Label(frame, text=position, font=("Arial", 10, "bold"))
        pofitionUser.grid(row=26, column=0)

        changePass = ttk.Button(frame, text="Change Password", command=changePassword)
        changePass.grid(row=27, column=0, pady=20)

        passwordFrame = ttk.Frame(profileframe,)
        passwordFrame.pack(padx=10, pady=10)

        load_image()
        Picutre()
        passwordFrame.pack_forget()

    payment_displayed = False

    def History():
        Head.config(text="Transactions")
        content_frame.pack_forget()
        add_frame.pack_forget()
        addAccountFrame.pack_forget()
        profileframe.pack_forget()
        Firstframe.pack_forget()
        payment_frame.pack()

        nonlocal payment_displayed

        if payment_displayed:
            return
        payment_displayed = True

        def filter_history(table):
            date_from = date_picker_from.get_date()
            date_to = date_picker_to.get_date()

            cursor.execute("SELECT * FROM entrance_fees WHERE timestamp BETWEEN ? AND ?", (date_from, date_to))
            data = cursor.fetchall()
            table.delete(*table.get_children())

            total_amount = 0

            for row in data:

                total_amount += row[1]

                table.insert('', 'end', values=(row[1], row[2], row[3], row[4]))

            messagebox.showinfo("Transaction Checked", f"Total Amount: Php {total_amount}")


        label_from = tk.Label(payment_frame, text="", font=("Microsoft New Tai Lue", 12, 'bold'))
        label_from.pack(pady=10)

        label_from = tk.Label(payment_frame, text="From:", font=("Microsoft New Tai Lue", 12, 'bold'))
        label_from.pack(pady=0)

        date_picker_from = DateEntry(payment_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                     font=("Microsoft New Tai Lue", 12,))
        date_picker_from.pack(pady=0)

        tk.Label(payment_frame, text="", font=("Microsoft New Tai Lue", 12, 'bold')).pack(pady=5)


        label_to = tk.Label(payment_frame, text="To:", font=("Microsoft New Tai Lue", 12, 'bold'))
        label_to.pack(pady=0)

        date_picker_to = DateEntry(payment_frame, width=12, background='darkblue', foreground='white', borderwidth=2,
                                   font=("Microsoft New Tai Lue", 12,))
        date_picker_to.pack(pady=0)

        filter_button = tk.Button(payment_frame, text="Check Transactions", command=lambda: filter_history(table),font=("Microsoft New Tai Lue", 12,'bold'),fg="#ffffff",bg="#03254c")
        filter_button.pack(pady=10)

        listbox_listPaymentframe = tk.Frame(payment_frame)
        listbox_listPaymentframe.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, pady=50, padx=40)

        columns = ("Amount", "Date", "User", "Position")
        table = ttk.Treeview(listbox_listPaymentframe, columns=columns, show="headings", height=100)
        for col in columns:
            table.heading(col, text=col)
        table.pack()

        def update_listbox():
            cursor.execute("SELECT * FROM entrance_fees")
            data = cursor.fetchall()
            table.delete(*table.get_children())
            for row in data:
                table.insert('', 'end', values=(row[1], row[2], row[3], row[4]))
            payment_frame.after(5000, update_listbox)

        update_listbox()

    def reset_login():
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)

    def logout():
        messagebox.askokcancel("Logout", "Are you sure?")
        reset_login()
        dashboard_window.withdraw()
        login_window.deiconify()

    def Picutre():
        cursor.execute('SELECT path FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        if row:
            image_path = row[0]
            image = Image.open(image_path)

            image.thumbnail((150, 150))

            photo = ImageTk.PhotoImage(image)

            image_label.config(image=photo)
            image_label.image = photo


    sidebar_frame = tk.Frame(dashboard_window, bg="#d4d4d4", width=200)
    sidebar_frame.pack(fill=tk.Y, side=tk.LEFT)

    image_frame = tk.Frame(sidebar_frame, bg="#b4b4b4")
    image_frame.pack()

    image_label = tk.Label(image_frame, width=150, bg="#b4b4b4")
    image_label.pack(pady=10)
    Picutre()

    Username = tk.Label(image_frame, text=username, width=20, font=("Microsoft New Tai Lue", 12, 'bold'), bg="#b4b4b4")
    Username.pack(pady=0)

    cursor.execute('Select position from users WHERE username = ?', (username,))
    position = cursor.fetchone()

    Position = tk.Label(image_frame, text=position, width=20, font=("Microsoft New Tai Lue", 8, 'bold'), bg="#b4b4b4")
    Position.pack(pady=0)

    top_nav_frame = tk.Frame(dashboard_window, bg="#d4d4d4", height=80)
    top_nav_frame.pack(fill=tk.X)

    Head = tk.Label(top_nav_frame,text="Dashboard", font=("Microsoft New Tai Lue", 18, 'bold'),bg="#d4d4d4")
    Head.grid(row=10)
    Head.pack(pady=30,padx=5, side=tk.LEFT)

    content_frame = tk.Frame(dashboard_window)
    content_frame.pack(fill=tk.BOTH, expand=True)

    add_frame = tk.Frame(dashboard_window)
    add_frame.pack(fill=tk.BOTH, expand=True)

    payment_frame = tk.Frame(dashboard_window)
    payment_frame.pack(fill=tk.BOTH, expand=True)

    addAccountFrame = tk.Frame(dashboard_window)
    addAccountFrame.pack(fill=tk.BOTH, expand=True)

    profileframe = tk.Frame(dashboard_window )
    profileframe.pack(fill=tk.BOTH, expand=True)

    Firstframe = tk.Frame(dashboard_window)
    Firstframe.pack(fill=tk.BOTH, expand=True)

    overviewButton = tk.Button(sidebar_frame, text="Overview", width=20, command=open_page, bg="#b4b4b4", border=0,font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    overviewButton.pack(pady=15)



    addButton = tk.Button(sidebar_frame, text="Payment", width=20, command=create_add_page, bg="#b4b4b4", border=0,font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    addButton.pack(pady=15)

    if position[0] == "Barangay_Matictic_Official":
        addButton.pack_forget()
    else:
        addButton.config(state=tk.NORMAL)

    addAccountButton = tk.Button(sidebar_frame, text="Add Account", width=20, command=addAccount, bg="#b4b4b4", border=0,
                              font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    addAccountButton.pack(pady=15)

    if position[0] == "Monitoring_Station_Clerk":
        addAccountButton.pack_forget()
    else:
        addAccountButton.config(state=tk.NORMAL)

    profileButton = tk.Button(sidebar_frame, text="Profile", width=20, command=Profile, bg="#b4b4b4", border=0,font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    profileButton.pack(pady=15)

    historyButton = tk.Button(sidebar_frame, text="Records of Payment", width=20, command=History, bg="#b4b4b4", border=0,font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    historyButton.pack(pady=15)

    if position[0] == "Monitoring_Station_Clerk":
        historyButton.pack_forget()
    else:
        historyButton.config(state=tk.NORMAL)

    logoutButton = tk.Button(sidebar_frame, text="Logout", width=20, command=logout, bg="#b4b4b4", border=0,font=("Microsoft New Tai Lue", 14, 'bold'),fg="#03254c")
    logoutButton.pack(pady=50)

    first()
    dashboard_window.geometry("2000x1000")


def login_design():
    image_path = "Logo1.png"  # Replace with the path to your image file
    image = Image.open(image_path)
    image.thumbnail((300, 300))
    photo = ImageTk.PhotoImage(image)

    # Update the label to display the image
    image_label.config(image=photo)
    image_label.image = photo

login_window = tk.Tk()
login_window.title("Login")

sidebar_frame = tk.Frame(login_window, bg="#b4b4b4", width=600)
sidebar_frame.pack(fill=tk.Y, side=tk.LEFT)

image_frame = tk.Frame(sidebar_frame, bg="#b4b4b4")
image_frame.pack()

image_label = tk.Label(image_frame, width=600, bg="#b4b4b4")
image_label.pack(pady=50)
login_design()

Title = tk.Label(image_frame, text="Barangay Matictic\nMonitoring Station Portal", bg="#b4b4b4", font=("Microsoft New Tai Lue", 24, 'bold'),fg="#03254c")
Title.pack()

Panel = tk.Frame(login_window)
Panel.pack(fill=tk.BOTH, pady=200)

Pad2 = tk.Label(Panel, text="",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
Pad2.pack(pady=0)

username_label = tk.Label(Panel, text="User Name:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
username_label.pack(pady=0)
username_entry = tk.Entry(Panel, width=30,font=("Microsoft New Tai Lue", 14))
username_entry.focus_force()
username_entry.pack(pady=0, padx=10)

Pad = tk.Label(Panel, text="",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
Pad.pack(pady=0)

password_label = tk.Label(Panel, text="Password:",font=("Microsoft New Tai Lue", 12,'bold'),fg="#03254c")
password_label.pack(pady=0)
password_entry = tk.Entry(Panel, show="*", width=30,font=("Microsoft New Tai Lue", 14,))
password_entry.pack(pady=0, padx=10)

def toggle_password_visibility():
    password_entry.config(show="" if show_password_var.get() else "*")

show_password_var = tk.BooleanVar()

# Create a Checkbox
show_password_checkbox = tk.Checkbutton(Panel, text="Show Password", variable=show_password_var, command=toggle_password_visibility,font=("Microsoft New Tai Lue", 10))
show_password_checkbox.pack(pady=5)

login_button = tk.Button(Panel, text="Login",width=20, command=login,font=("Microsoft New Tai Lue", 12,'bold'),fg="#ffffff",bg="#03254c")
login_button.pack(pady=30)
login_window.geometry("2000x1000")
login_window.mainloop()
connect.close()
