"""
ClassChat Client
With conversation threading, io_multiplexer, message filtering, encryption
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import socket
import threading
import json
import select
import base64
import os
import sys
import config
from protocol import Message
from encryption import MessageEncryption
from io_multiplexer import IOMultiplexer


class ClassChatClient:
    """Chat client with conversation threading"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClassChat")
        self.root.geometry("900x700")
        self.root.configure(bg='#2c3e50')

        self.socket = None
        self.connected = False
        self.username = None
        self.encryption = MessageEncryption()
        self.receive_thread = None

        # I/O MULTIPLEXING - Auto-detect best method
        # Priority: epoll (Linux) > poll (Unix) > select (All platforms)
        if hasattr(select, 'epoll'):
            self.io_method = 'epoll'
        elif hasattr(select, 'poll'):
            self.io_method = 'poll'
        else:
            self.io_method = 'select'

        self.io_multiplexer = None  # Will be created after socket connection
        print(f"[CLIENT] Using I/O multiplexing method: {self.io_method}")

        # CONVERSATION THREADING
        self.current_recipient = None
        self.current_chat_type = None  # 'private' or 'group'
        self.file_to_send = None

        self.create_login_screen()

    def create_login_screen(self):
        """Create login interface"""
        for widget in self.root.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(expand=True)

        tk.Label(main_frame, text="ClassChat", font=('Arial', 32, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=20)
        tk.Label(main_frame, text="Connect with your classmates", font=('Arial', 12),
                 bg='#2c3e50', fg='#ecf0f1').pack(pady=10)
        tk.Label(main_frame, text="🔒 ENCRYPTED COMMUNICATION", font=('Arial', 10, 'bold'),
                 bg='#2c3e50', fg='#27ae60').pack(pady=10)

        tk.Label(main_frame, text="Username:", font=('Arial', 11),
                 bg='#2c3e50', fg='white').pack(pady=(20, 5))
        self.username_entry = tk.Entry(main_frame, font=('Arial', 11), width=30)
        self.username_entry.pack(pady=5)

        tk.Label(main_frame, text="Server:", font=('Arial', 11),
                 bg='#2c3e50', fg='white').pack(pady=(10, 5))
        self.server_entry = tk.Entry(main_frame, font=('Arial', 11), width=30)
        self.server_entry.insert(0, f"{config.SERVER_HOST}:{config.SERVER_PORT}")
        self.server_entry.pack(pady=5)

        self.connect_btn = tk.Button(main_frame, text="Connect", font=('Arial', 12, 'bold'),
                                     bg='#3498db', fg='white', width=20, height=2,
                                     command=self.connect_to_server, cursor='hand2')
        self.connect_btn.pack(pady=20)

        self.status_label = tk.Label(main_frame, text="", font=('Arial', 10),
                                     bg='#2c3e50', fg='#e74c3c')
        self.status_label.pack(pady=10)

        self.username_entry.bind('<Return>', lambda e: self.connect_to_server())

    def connect_to_server(self):
        """Connect to server with encryption key exchange"""
        username = self.username_entry.get().strip()
        server_info = self.server_entry.get().strip()

        if not username:
            self.status_label.config(text="Please enter a username")
            return

        try:
            if ':' in server_info:
                host, port = server_info.split(':')
                port = int(port)
            else:
                host = server_info
                port = config.SERVER_PORT

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.username = username

            connect_msg = Message.create_connect_message(username)
            self.socket.send(connect_msg.encode())

            response_data = self.socket.recv(config.BUFFER_SIZE)
            response = Message.parse_message(response_data.decode('utf-8'))

            if response and response.get('type') == config.MSG_SUCCESS:
                self.connected = True
                
                # ENCRYPTION KEY EXCHANGE
                if config.USE_ENCRYPTION:
                    print("[CLIENT] Starting encryption key exchange...")
                    
                    # Receive server's RSA public key
                    key_data = self.socket.recv(config.BUFFER_SIZE)
                    key_message = Message.parse_message(key_data.decode('utf-8'))
                    
                    if key_message and key_message.get('type') == config.MSG_KEY_EXCHANGE:
                        public_key_pem = key_message.get('data', {}).get('public_key')
                        
                        if public_key_pem:
                            # Load server's public key
                            self.encryption.load_public_key_pem(public_key_pem)
                            print("[CLIENT] Received RSA public key from server")
                            
                            # Generate AES session key
                            self.encryption.generate_session_key()
                            print("[CLIENT] Generated AES session key")
                            
                            # Encrypt session key with server's RSA public key
                            encrypted_session_key = self.encryption.encrypt_session_key()
                            print("[CLIENT] Encrypted session key")
                            
                            # Send encrypted session key to server
                            key_response = Message.create_message(
                                config.MSG_KEY_EXCHANGE,
                                username,
                                "SERVER",
                                None,
                                {"encrypted_session_key": encrypted_session_key, "step": "client_session_key"}
                            )
                            self.socket.send(key_response.encode())
                            print("[CLIENT] Sent encrypted session key to server")
                            
                            # Wait for acknowledgment
                            ack_data = self.socket.recv(config.BUFFER_SIZE)
                            ack_message = Message.parse_message(ack_data.decode('utf-8'))
                            
                            if ack_message and ack_message.get('type') == config.MSG_KEY_EXCHANGE:
                                print("[CLIENT] ✅ Encryption established successfully")
                            else:
                                print("[CLIENT ERROR] Key exchange acknowledgment failed")
                                self.socket.close()
                                self.socket = None
                                return
                        else:
                            print("[CLIENT ERROR] No public key received")
                            self.socket.close()
                            self.socket = None
                            return
                    else:
                        print("[CLIENT ERROR] Invalid key exchange message")
                        self.socket.close()
                        self.socket = None
                        return

                # Create I/O multiplexer for this socket
                self.io_multiplexer = IOMultiplexer(method=self.io_method)
                print(f"[CLIENT] I/O multiplexer initialized with {self.io_method}()")

                self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
                self.receive_thread.start()
                self.create_chat_screen()
            else:
                self.status_label.config(text=response.get('text', 'Connection failed'))
                self.socket.close()
                self.socket = None
        except Exception as e:
            self.status_label.config(text=f"Connection failed: {e}")
            print(f"[CLIENT ERROR] Connection error: {e}")
            import traceback
            traceback.print_exc()
            if self.socket:
                self.socket.close()
                self.socket = None

    def create_chat_screen(self):
        """Create main chat interface"""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title(f"ClassChat - {self.username}")

        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)

        self.create_sidebar(main_container)
        self.create_chat_area(main_container)

    def create_sidebar(self, parent):
        """Create sidebar with users and groups"""
        sidebar = tk.Frame(parent, bg='#34495e', width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg='#2c3e50')
        logo_frame.pack(fill=tk.X, pady=5)

        try:
            logo_path = os.path.join(os.path.dirname(__file__), 'ull_logo.png')
            if os.path.exists(logo_path):
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path).resize((60, 60))
                self.sidebar_logo = ImageTk.PhotoImage(logo_img)
                tk.Label(logo_frame, image=self.sidebar_logo, bg='#2c3e50').pack(side=tk.LEFT, padx=10)
        except:
            pass

        user_frame = tk.Frame(logo_frame, bg='#2c3e50')
        user_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tk.Label(user_frame, text=f"👤 {self.username}", font=('Arial', 12, 'bold'),
                 bg='#2c3e50', fg='white').pack(anchor='w', padx=5)
        tk.Label(user_frame, text="🟢 Online", font=('Arial', 9),
                 bg='#2c3e50', fg='#27ae60').pack(anchor='w', padx=5)

        tk.Button(sidebar, text="🚪 Go Offline / Quit", font=('Arial', 9),
                  bg='#e74c3c', fg='white', command=self.go_offline).pack(fill=tk.X, padx=10, pady=5)

        tab_control = ttk.Notebook(sidebar)
        tab_control.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        users_frame = tk.Frame(tab_control, bg='#34495e')
        tab_control.add(users_frame, text='Users')
        tk.Label(users_frame, text="Online Users:", font=('Arial', 11, 'bold'),
                 bg='#34495e', fg='white').pack(pady=5)
        self.users_listbox = tk.Listbox(users_frame, font=('Arial', 10),
                                        bg='#ecf0f1', selectmode=tk.SINGLE)
        self.users_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.users_listbox.bind('<Double-Button-1>', self.on_user_double_click)

        users_btn_frame = tk.Frame(users_frame, bg='#34495e')
        users_btn_frame.pack(pady=5)
        tk.Button(users_btn_frame, text="↻ Refresh", font=('Arial', 9),
                  command=self.refresh_users).pack(side=tk.LEFT, padx=2)
        tk.Button(users_btn_frame, text="📝 Type Username", font=('Arial', 9),
                  command=self.manual_recipient_dialog).pack(side=tk.LEFT, padx=2)

        groups_frame = tk.Frame(tab_control, bg='#34495e')
        tab_control.add(groups_frame, text='Groups')
        tk.Label(groups_frame, text="Groups:", font=('Arial', 11, 'bold'),
                 bg='#34495e', fg='white').pack(pady=5)
        self.groups_listbox = tk.Listbox(groups_frame, font=('Arial', 10),
                                         bg='#ecf0f1', selectmode=tk.SINGLE)
        self.groups_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.groups_listbox.bind('<Double-Button-1>', self.on_group_double_click)

        groups_btn_frame = tk.Frame(groups_frame, bg='#34495e')
        groups_btn_frame.pack(pady=5)
        tk.Button(groups_btn_frame, text="+ Create", font=('Arial', 9),
                  command=self.create_group_dialog).pack(side=tk.LEFT, padx=2)
        tk.Button(groups_btn_frame, text="↻ Refresh", font=('Arial', 9),
                  command=self.refresh_groups).pack(side=tk.LEFT, padx=2)

        self.refresh_users()
        self.refresh_groups()

    def create_chat_area(self, parent):
        """Creating chat display area"""
        chat_container = tk.Frame(parent, bg='white')
        chat_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_header = tk.Label(chat_container, text="Select a user or group to chat",
                                    font=('Arial', 14, 'bold'), bg='#3498db', fg='white',
                                    height=2)
        self.chat_header.pack(fill=tk.X)

        self.chat_display = scrolledtext.ScrolledText(chat_container, wrap=tk.WORD,
                                                      state=tk.DISABLED, font=('Arial', 11))
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(chat_container, bg='white')
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        input_frame.grid_rowconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_entry = tk.Text(input_frame, height=3, font=('Arial', 11), wrap=tk.WORD)
        self.message_entry.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message() if not e.state & 0x1 else None)
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())

        btn_frame = tk.Frame(input_frame, bg='white')
        btn_frame.grid(row=0, column=1, sticky='ns')
        tk.Button(btn_frame, text="Send", font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                  width=10, height=1, command=self.send_message).pack(pady=(0, 5))
        tk.Button(btn_frame, text="📎 Attach", font=('Arial', 9), width=10,
                  command=self.attach_file).pack(pady=(0, 5))
        self.send_file_btn = tk.Button(btn_frame, text="📤 File Send", font=('Arial', 9),
                                       width=10, state=tk.DISABLED, command=self.send_attached_file)
        self.send_file_btn.pack()

        self.current_recipient = None
        self.current_chat_type = None

    def receive_messages(self):
        """Receive messages thread using I/O multiplexing"""
        while self.connected:
            try:
                # Use I/O multiplexer (select/poll/epoll)
                if self.io_multiplexer.wait_for_read(self.socket, timeout=1):
                    data = self.socket.recv(config.BUFFER_SIZE)
                    if not data:
                        break
                    message_str = data.decode('utf-8')
                    
                    # DECRYPT MESSAGE if encryption is enabled and ready
                    if config.USE_ENCRYPTION and self.encryption.is_ready():
                        try:
                            message_str = self.encryption.decrypt_message(message_str)
                        except Exception as e:
                            print(f"[CLIENT ERROR] Decryption error: {e}")
                            continue
                    
                    message = Message.parse_message(message_str)
                    if message:
                        self.process_received_message(message)
            except Exception as e:
                if self.connected:
                    print(f"[CLIENT ERROR] Receive error: {e}")
                break
        self.disconnect()

    def process_received_message(self, message):
        """Process received message with CONVERSATION FILTERING"""
        msg_type = message.get('type')
        sender = message.get('sender')
        text = message.get('text')
        receiver = message.get('receiver')

        # CRITICAL: Filter messages by current chat
        if msg_type == config.MSG_PRIVATE:
            # ONLY display if this matches current private chat
            if self.current_chat_type == 'private' and self.current_recipient == sender:
                self.display_message(f"{sender} (private): {text}", 'received')
            elif not self.current_recipient:
                # No chat open - set context for offline message
                self.current_recipient = sender
                self.current_chat_type = 'private'
                self.chat_header.config(text=f"Private Chat with {sender}")
                self.display_message("", 'encrypted_header')
                self.display_message(f"{sender} (private): {text}", 'received')
            else:
                # Message from different conversation - ignore
                print(f"[CLIENT] Ignoring message from {sender} (current chat: {self.current_recipient})")

        elif msg_type == config.MSG_GROUP:
            group = message.get('receiver')
            # ONLY display if this matches current group chat
            if self.current_chat_type == 'group' and self.current_recipient == group:
                self.display_message(f"{sender} @{group}: {text}", 'group')
            else:
                # Message from different group - ignore
                print(f"[CLIENT] Ignoring group message from {group} (current chat: {self.current_recipient})")

        elif msg_type == config.MSG_FILE:
            # ✅ FIXED: Add proper filtering (same logic as private/group messages)
            sender = message.get('sender')
            is_group = message.get('is_group', False)

            if is_group:
                # This is a GROUP file transfer
                group_name = message.get('receiver')
                # Only process if we're currently viewing THIS group chat
                if self.current_chat_type == 'group' and self.current_recipient == group_name:
                    self.handle_received_file(message)
                else:
                    print(f"[CLIENT] Ignoring group file from {group_name} (current chat: {self.current_recipient})")
            else:
                # This is a PRIVATE file transfer
                # Only process if we're currently viewing a private chat with THIS sender
                if self.current_chat_type == 'private' and self.current_recipient == sender:
                    self.handle_received_file(message)
                elif not self.current_recipient:
                    # No chat open - open private chat with sender
                    self.current_recipient = sender
                    self.current_chat_type = 'private'
                    self.chat_header.config(text=f"Private Chat with {sender}")
                    self.display_message("", 'encrypted_header')
                    self.handle_received_file(message)
                else:
                    print(f"[CLIENT] Ignoring private file from {sender} (current chat: {self.current_recipient})")
        elif msg_type == config.MSG_SUCCESS:
            self.display_message(f"[✓] {text}", 'system')
        elif msg_type == config.MSG_ERROR:
            self.display_message(f"[✗] {text}", 'error')
        elif msg_type == config.MSG_OFFLINE:
            self.display_message(f"[📩] {text}", 'system')
        elif msg_type == config.MSG_LIST_USERS:
            self.update_users_list(message.get('data', {}).get('users', []))
        elif msg_type == config.MSG_LIST_GROUPS:
            self.update_groups_list(message.get('data', {}).get('groups', []))
        elif msg_type == config.MSG_HISTORY_RESPONSE:
            self.handle_history_response(message)

    def handle_history_response(self, message):
        """Display conversation history"""
        data = message.get('data', {})
        other_user = data.get('other_user')
        messages = data.get('messages', [])
        is_group = data.get('is_group', False)

        print(f"[CLIENT] Received {len(messages)} history messages")

        for msg in messages:
            sender = msg.get('sender')
            text = msg.get('text')
            timestamp = msg.get('timestamp', '')

            try:
                from datetime import datetime
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%H:%M:%S")
            except:
                time_str = "00:00:00"

            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.insert(tk.END, f"[{time_str}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"🔒 Encrypted | ", 'encrypt_label')

            if is_group:
                self.chat_display.insert(tk.END, f"{sender} @{other_user}: {text}\n", 'group')
            else:
                if sender == self.username:
                    self.chat_display.insert(tk.END, f"You to {other_user}: {text}\n", 'sent')
                else:
                    self.chat_display.insert(tk.END, f"{sender} (private): {text}\n", 'received')

            self.chat_display.config(state=tk.DISABLED)

        self.chat_display.see(tk.END)
        if messages:
            self.display_message("[Previous messages loaded]", 'system')

    def display_message(self, text, msg_type='normal'):
        """Display message in chat"""
        self.chat_display.config(state=tk.NORMAL)
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")

        if msg_type == 'encrypted_header':
            self.chat_display.insert(tk.END, f"\n{'=' * 60}\n", 'header')
            self.chat_display.insert(tk.END, f"          🔐 ENCRYPTED-CHAT          \n", 'encrypted_header')
            self.chat_display.insert(tk.END, f"{'=' * 60}\n\n", 'header')
        elif msg_type == 'sent':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"🔒 Encrypted | ", 'encrypt_label')
            self.chat_display.insert(tk.END, f"{text}\n", 'sent')
        elif msg_type == 'received':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"🔒 Encrypted | ", 'encrypt_label')
            self.chat_display.insert(tk.END, f"{text}\n", 'received')
        elif msg_type == 'group':
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.chat_display.insert(tk.END, f"🔒 Encrypted | ", 'encrypt_label')
            self.chat_display.insert(tk.END, f"{text}\n", 'group')
        elif msg_type == 'system':
            self.chat_display.insert(tk.END, f"[{timestamp}] {text}\n", 'system')
        elif msg_type == 'error':
            self.chat_display.insert(tk.END, f"[{timestamp}] {text}\n", 'error')
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] {text}\n")

        self.chat_display.tag_config('timestamp', foreground='gray', font=('Arial', 9))
        self.chat_display.tag_config('encrypt_label', foreground='#27ae60', font=('Arial', 10, 'bold italic'))
        self.chat_display.tag_config('sent', foreground='#2980b9', font=('Arial', 11))
        self.chat_display.tag_config('received', foreground='#27ae60', font=('Arial', 11))
        self.chat_display.tag_config('group', foreground='#8e44ad', font=('Arial', 11))
        self.chat_display.tag_config('system', foreground='#95a5a6', font=('Arial', 10, 'italic'))
        self.chat_display.tag_config('error', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        self.chat_display.tag_config('encrypted_header', foreground='#27ae60', font=('Arial', 16, 'bold'))
        self.chat_display.tag_config('header', foreground='#7f8c8d')

        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)
    
    def send_encrypted_data(self, message_str):
        """
        Send encrypted message to server
        Args:
            message_str: Message string to send (will be encrypted if encryption is enabled)
        """
        try:
            if config.USE_ENCRYPTION and self.encryption.is_ready():
                encrypted_msg = self.encryption.encrypt_message(message_str)
                self.socket.send(encrypted_msg.encode())
            else:
                self.socket.send(message_str.encode())
        except Exception as e:
            print(f"[CLIENT ERROR] Failed to send encrypted data: {e}")
            raise

    def send_message(self):
        """Send message"""
        if not self.current_recipient:
            messagebox.showwarning("No Recipient", "Please select a user or group to chat with")
            return

        text = self.message_entry.get('1.0', tk.END).strip()
        if not text:
            return

        try:
            if self.current_chat_type == 'private':
                msg = Message.create_private_message(self.username, self.current_recipient, text)
                self.send_encrypted_data(msg)
                self.display_message(f"You to {self.current_recipient}: {text}", 'sent')
            elif self.current_chat_type == 'group':
                msg = Message.create_group_message(self.username, self.current_recipient, text)
                self.send_encrypted_data(msg)
                self.display_message(f"You @{self.current_recipient}: {text}", 'sent')
            self.message_entry.delete('1.0', tk.END)
        except Exception as e:
            messagebox.showerror("Send Error", f"Failed to send message: {e}")

    def attach_file(self):
        """Attach file"""
        filename = filedialog.askopenfilename(title="Select file to attach")
        if filename:
            self.file_to_send = filename
            self.send_file_btn.config(state=tk.NORMAL, bg='#27ae60', fg='white')
            messagebox.showinfo("File Attached",
                                f"File attached: {os.path.basename(filename)}\nClick 'File Send' to send it.")

    def send_attached_file(self):
        """Send attached file"""
        if not self.file_to_send or not self.current_recipient:
            return
        try:
            file_size = os.path.getsize(self.file_to_send)
            if file_size > config.MAX_FILE_SIZE:
                messagebox.showerror("File Too Large", f"File size exceeds {config.MAX_FILE_SIZE / (1024 * 1024)}MB")
                return
            with open(self.file_to_send, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode()
            base_filename = os.path.basename(self.file_to_send)
            if self.current_chat_type == 'group':
                msg = Message.create_file_message(self.username, self.current_recipient, base_filename, file_data)
                msg_dict = json.loads(msg)
                msg_dict['is_group'] = True
                msg = json.dumps(msg_dict)
            else:
                msg = Message.create_file_message(self.username, self.current_recipient, base_filename, file_data)
            self.send_encrypted_data(msg)
            self.display_message(f"📎 Sent file '{base_filename}' to {self.current_recipient}", 'system')
            self.file_to_send = None
            self.send_file_btn.config(state=tk.DISABLED, bg='SystemButtonFace', fg='black')
        except Exception as e:
            messagebox.showerror("File Transfer Error", f"Failed to send file: {e}")

    def handle_received_file(self, message):
        """Handle received file"""
        sender = message.get('sender')
        data = message.get('data', {})
        filename = data.get('filename', 'unknown')
        file_data_b64 = data.get('filedata', '')
        save_path = filedialog.asksaveasfilename(title="Save received file", initialfile=filename)
        if save_path:
            try:
                file_data = base64.b64decode(file_data_b64)
                with open(save_path, 'wb') as f:
                    f.write(file_data)
                self.display_message(f"📎 File '{filename}' received from {sender} and saved", 'system')
            except Exception as e:
                messagebox.showerror("File Save Error", f"Failed to save file: {e}")

    def request_conversation_history(self, other_user, is_group=False):
        """Request conversation history from server"""
        try:
            history_request = Message.create_message(
                config.MSG_HISTORY_REQUEST,
                self.username,
                "SERVER",
                None,
                {
                    'other_user': other_user,
                    'is_group': is_group
                }
            )
            self.send_encrypted_data(history_request)
            print(f"[CLIENT] Requested history for {other_user}")
        except Exception as e:
            print(f"[CLIENT ERROR] Failed to request history: {e}")

    def on_user_double_click(self, event):
        """Handle user double-click - LOAD HISTORY"""
        selection = self.users_listbox.curselection()
        if selection:
            user_text = self.users_listbox.get(selection[0])
            user = user_text.split('(')[0].strip() if '(' in user_text else user_text.strip()
            user = user.replace('🟢', '').replace('🔴', '').strip()
            if user != self.username:
                # SWITCH CONVERSATION
                self.current_recipient = user
                self.current_chat_type = 'private'
                self.chat_header.config(text=f"Private Chat with {user}")

                # CLEAR DISPLAY
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete('1.0', tk.END)
                self.chat_display.config(state=tk.DISABLED)

                # SHOW HEADER
                self.display_message("", 'encrypted_header')

                # REQUEST HISTORY
                self.request_conversation_history(user, is_group=False)

    def on_group_double_click(self, event):
        """Handle group double-click"""
        selection = self.groups_listbox.curselection()
        if selection:
            group_text = self.groups_listbox.get(selection[0])
            group = group_text.replace('👥', '').strip()

            dialog = tk.Toplevel(self.root)
            dialog.title("Join Group")
            dialog.geometry("350x180")
            dialog.resizable(False, False)
            dialog.configure(bg='#2c3e50')
            dialog.transient(self.root)
            dialog.grab_set()

            tk.Label(dialog, text="👥", font=('Arial', 40), bg='#2c3e50', fg='white').pack(pady=(20, 10))
            tk.Label(dialog, text=f"Join group '{group}'?", font=('Arial', 12, 'bold'),
                     bg='#2c3e50', fg='white').pack(pady=10)

            def join_group():
                join_msg = Message.create_message(config.MSG_JOIN_GROUP, self.username, None, None,
                                                  {"group_name": group})
                self.send_encrypted_data(join_msg)

                # SWITCH TO GROUP
                self.current_recipient = group
                self.current_chat_type = 'group'
                self.chat_header.config(text=f"Group Chat: {group}")

                # CLEAR DISPLAY
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete('1.0', tk.END)
                self.chat_display.config(state=tk.DISABLED)

                # SHOW HEADER
                self.display_message("", 'encrypted_header')

                # REQUEST GROUP HISTORY
                self.request_conversation_history(group, is_group=True)

                self.display_message(f"[Joined group '{group}']", 'system')
                dialog.destroy()

            tk.Button(dialog, text="JOIN", font=('Arial', 12, 'bold'), bg='#27ae60', fg='white',
                      width=15, height=1, command=join_group, cursor='hand2').pack(pady=10)
            tk.Button(dialog, text="Cancel", font=('Arial', 10), bg='#95a5a6', fg='white',
                      width=15, command=dialog.destroy, cursor='hand2').pack(pady=(0, 10))

    def refresh_users(self):
        """Refresh users list"""
        if self.connected:
            msg = Message.create_message(config.MSG_LIST_USERS, self.username)
            self.send_encrypted_data(msg)

    def refresh_groups(self):
        """Refresh groups list"""
        if self.connected:
            msg = Message.create_message(config.MSG_LIST_GROUPS, self.username)
            self.send_encrypted_data(msg)

    def update_users_list(self, users):
        """Update users list"""
        self.users_listbox.delete(0, tk.END)
        for user in users:
            if user['username'] != self.username:
                status_icon = "🟢" if user['status'] == 'online' else "🔴"
                self.users_listbox.insert(tk.END, f"{status_icon} {user['username']} ({user['status']})")

    def update_groups_list(self, groups):
        """Update groups list"""
        self.groups_listbox.delete(0, tk.END)
        for group in groups:
            self.groups_listbox.insert(tk.END, f"👥 {group['name']}")

    def create_group_dialog(self):
        """Show create group dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Create Group")
        dialog.geometry("300x150")
        tk.Label(dialog, text="Group Name:", font=('Arial', 11)).pack(pady=20)
        group_name_entry = tk.Entry(dialog, font=('Arial', 11), width=25)
        group_name_entry.pack(pady=10)

        def create():
            group_name = group_name_entry.get().strip()
            if group_name:
                msg = Message.create_message(config.MSG_CREATE_GROUP, self.username, None, None,
                                             {"group_name": group_name})
                self.send_encrypted_data(msg)
                dialog.destroy()
                self.refresh_groups()

        tk.Button(dialog, text="Create", command=create).pack(pady=10)

    def manual_recipient_dialog(self):
        """ Dialog to manually enter recipient username """
        dialog = tk.Toplevel(self.root)
        dialog.title("Send to Username")
        dialog.geometry("400x200")
        dialog.configure(bg='#2c3e50')
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(dialog, text="📝 Type Username", font=('Arial', 14, 'bold'),
                 bg='#2c3e50', fg='white').pack(pady=20)
        tk.Label(dialog, text="Enter recipient username:", font=('Arial', 11),
                 bg='#2c3e50', fg='#ecf0f1').pack(pady=10)

        username_entry = tk.Entry(dialog, font=('Arial', 11), width=25)
        username_entry.pack(pady=10)
        username_entry.focus()

        def set_recipient():
            recipient = username_entry.get().strip()
            if recipient:
                if recipient == self.username:
                    messagebox.showwarning("Invalid", "You cannot send messages to yourself!")
                    return

                # SWITCH TO THIS USER
                self.current_recipient = recipient
                self.current_chat_type = 'private'
                self.chat_header.config(text=f"Private Chat with {recipient}")

                # CLEAR DISPLAY
                self.chat_display.config(state=tk.NORMAL)
                self.chat_display.delete('1.0', tk.END)
                self.chat_display.config(state=tk.DISABLED)

                # SHOW HEADER
                self.display_message("", 'encrypted_header')

                # REQUEST HISTORY
                self.request_conversation_history(recipient, is_group=False)

                self.display_message(f"[Chat with {recipient}. User may be offline.]", 'system')
                dialog.destroy()

        tk.Button(dialog, text="Start Chat", font=('Arial', 11, 'bold'), bg='#3498db', fg='white',
                  width=15, command=set_recipient, cursor='hand2').pack(pady=10)
        username_entry.bind('<Return>', lambda e: set_recipient())

    def go_offline(self):
        """Go offline and quit"""
        result = messagebox.askyesno("Go Offline", "Do you want to go offline and quit ClassChat?")
        if result:
            self.disconnect()
            self.root.destroy()

    def disconnect(self):
        """Disconnect from server"""
        if self.connected:
            try:
                disconnect_msg = Message.create_disconnect_message(self.username)
                self.send_encrypted_data(disconnect_msg)
            except:
                pass
            self.connected = False
            if self.socket:
                self.socket.close()

    def run(self):
        """Run the client"""
        self.root.mainloop()




def main():
    """Main function"""
    client = ClassChatClient()
    client.run()


if __name__ == "__main__":
    main()