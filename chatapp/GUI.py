import tkinter as tk
import threading
import os

root = tk.Tk()
root.title("KeyChat")
root.geometry("600x800")
root.configure(bg="#d8d4d4")

button_frame = tk.Frame(root, bg="#d8d4d4")
button_frame.pack(expand=True)

def run_server():
    import server as server
    btnclient.pack_forget()
    btnhost.pack_forget()

    tk.Label(root, text=f"Server hosted on \n {server.SERVER}", font=('Arial', 20), bg="#d8d4d4").place(x=300, y=400, anchor='center')
    threading.Thread(target=lambda: server.start(lambda: root.after(0, chat_room_host)), daemon=True).start()

def run_client():
    import client as client
    btnclient.pack_forget()
    btnhost.pack_forget()

    tk.Label(root, text=f"Searching for Host on \n {client.SERVER}", font=('Arial', 20), bg="#d8d4d4").place(x=300, y=400, anchor='center')
    threading.Thread(target=lambda: client.connect(lambda: root.after(0, chat_room_client)), daemon=True).start()

def chat_room_host():
    import server as server

    for widget in root.winfo_children():
        widget.destroy()

    entrybox = tk.Entry(root, font=('Arial', 20), bg="#575A5A", width=30)
    chatlog = tk.Text(root, bg='white', state="disabled", font=('Arial', 14))

    def update_chat_log(msg):
        chatlog.config(state='normal')
        chatlog.insert(tk.END, msg)
        chatlog.config(state="disabled")

    server.chatlog_update_func = update_chat_log

    entrybox.pack(side='bottom', fill='x',padx=5)
    chatlog.pack(side='top', fill='both', expand=True, padx=5, pady=5)

    def on_enter(event):
        message = entrybox.get()
        server.send(message)
        update_chat_log(f"You: {message}\n")
        entrybox.delete(0, tk.END)

    root.bind('<Return>', on_enter)

def chat_room_client():
    import client as client

    for widget in root.winfo_children():
        widget.destroy()

    entrybox = tk.Entry(root, font=('Arial', 20), bg="#575A5A", width=30)
    chatlog = tk.Text(root, bg='white', state="disabled", font=('Arial', 14))

    def update_chat_log(msg):
        chatlog.config(state='normal')
        chatlog.insert(tk.END, msg)
        chatlog.config(state="disabled")

    client.chatlog_update_func = update_chat_log

    entrybox.pack(side='bottom', fill='x',padx=5)
    chatlog.pack(side='top', fill='both', expand=True, padx=5, pady=5)

    def on_enter(event):
        message = entrybox.get()
        client.send(message)
        update_chat_log(f"You: {message}\n")
        entrybox.delete(0, tk.END)

    root.bind('<Return>', on_enter)

# Host Button
btnhost = tk.Button(button_frame, text="Host", command=run_server, font=("Arial", 16, "bold"),
                    bg="#D84646", fg="white", activebackground="#eb8e8e", activeforeground="white",
                    relief="flat", bd=5, padx=100, pady=10)
btnhost.pack(pady=20)

# Join Button
btnclient = tk.Button(button_frame, text="Join", command=run_client, font=("Arial", 16, "bold"),
                      bg="#D84646", fg="white", activebackground="#eb8e8e", activeforeground="white",
                      relief="flat", bd=5, padx=100, pady=10)
btnclient.pack(pady=20)

def on_close():
    print("Window Closed. Exiting...")
    os._exit(0)


root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()
