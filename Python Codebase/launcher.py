"""
ClassChat Launcher - All-in-One Control Panel
"""
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import threading
import time


class ClassChatLauncher:
    """Main launcher for ClassChat system"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ClassChat Control Panel")
        self.root.geometry("700x800")  # Increased height
        self.root.configure(bg='#2c3e50')
        self.root.resizable(True, True)

        self.server_process = None
        self.client_processes = []
        self.client_count = 0
        self.server_running = False

        self.create_gui()

    def create_gui(self):
        """Create the launcher GUI"""
        # Header with logo
        header_frame = tk.Frame(self.root, bg='#2c3e50')
        header_frame.pack(pady=20)

        # Try to load ULL logo with robust path handling
        logo_loaded = False
        try:
            # Try multiple possible locations for the logo
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ull_logo.png'),
                os.path.join(os.getcwd(), 'ull_logo.png'),
                'ull_logo.png',
                os.path.join(os.path.dirname(__file__), 'ull_logo.png')
            ]

            logo_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    logo_path = path
                    print(f"[LAUNCHER] ✅ Found logo at: {logo_path}")
                    break

            if logo_path:
                from PIL import Image, ImageTk
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((100, 100))
                self.logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header_frame, image=self.logo_photo, bg='#2c3e50')
                logo_label.pack()
                logo_loaded = True
            else:
                print("[LAUNCHER] ⚠️ Logo file 'ull_logo.png' not found in any location")

        except ImportError:
            print("[LAUNCHER] ⚠️ PIL/Pillow not installed - cannot load logo")
        except Exception as e:
            print(f"[LAUNCHER] ⚠️ Could not load logo: {e}")

        # If logo didn't load, show a placeholder emoji
        if not logo_loaded:
            placeholder = tk.Label(
                header_frame,
                text="🎓",
                font=('Arial', 64),
                bg='#2c3e50',
                fg='white'
            )
            placeholder.pack()

        # Title
        title_label = tk.Label(
            header_frame,
            text="ClassChat Control Panel",
            font=('Arial', 24, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="University of Louisiana at Lafayette",
            font=('Arial', 12),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        subtitle_label.pack()

        # Control buttons frame
        control_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        control_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        # Server section
        server_label = tk.Label(
            control_frame,
            text="Server Control",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white'
        )
        server_label.pack(pady=(0, 10))

        self.server_btn = tk.Button(
            control_frame,
            text="🖥️  START SERVER",
            font=('Arial', 12, 'bold'),
            bg='#27ae60',
            fg='white',
            width=30,
            height=2,
            command=self.start_server,
            cursor='hand2'
        )
        self.server_btn.pack(pady=5)

        self.server_status_label = tk.Label(
            control_frame,
            text="Status: Not Running",
            font=('Arial', 10),
            bg='#34495e',
            fg='#e74c3c'
        )
        self.server_status_label.pack(pady=5)

        # Separator
        separator = tk.Frame(control_frame, height=2, bg='#7f8c8d')
        separator.pack(fill=tk.X, pady=20)

        # Clients section
        clients_label = tk.Label(
            control_frame,
            text="Client Control",
            font=('Arial', 14, 'bold'),
            bg='#34495e',
            fg='white'
        )
        clients_label.pack(pady=(0, 10))

        self.client_btn = tk.Button(
            control_frame,
            text="👤  START CLIENT",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            width=30,
            height=2,
            command=self.start_client,
            cursor='hand2',
            state=tk.DISABLED
        )
        self.client_btn.pack(pady=5)

        self.clients_status_label = tk.Label(
            control_frame,
            text="Active Clients: 0",
            font=('Arial', 10),
            bg='#34495e',
            fg='#95a5a6'
        )
        self.clients_status_label.pack(pady=5)

        # Client buttons frame (dynamic)
        self.client_buttons_frame = tk.Frame(control_frame, bg='#34495e')
        self.client_buttons_frame.pack(pady=10, fill=tk.X)

        # Stop all button
        separator2 = tk.Frame(control_frame, height=2, bg='#7f8c8d')
        separator2.pack(fill=tk.X, pady=20)

        stop_all_btn = tk.Button(
            control_frame,
            text="⛔  STOP ALL",
            font=('Arial', 11, 'bold'),
            bg='#e74c3c',
            fg='white',
            width=20,
            command=self.stop_all,
            cursor='hand2'
        )
        stop_all_btn.pack(pady=5)

        # Info label
        info_label = tk.Label(
            self.root,
            text="Tip: Start SERVER first, then start CLIENTS",
            font=('Arial', 9, 'italic'),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        info_label.pack(pady=10)

    def start_server(self):
        """Start the ClassChat server"""
        if self.server_running:
            messagebox.showinfo("Server", "Server is already running!")
            return

        try:
            # Start server WITH visible console window
            server_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server.py')

            print(f"[LAUNCHER] Starting server: {server_script}")

            if sys.platform == 'win32':
                # Windows - SHOW console window for server (so you can see debug output)
                self.server_process = subprocess.Popen(
                    [sys.executable, server_script],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                # Linux/Mac - run in terminal
                self.server_process = subprocess.Popen(
                    [sys.executable, server_script]
                )

            # Give server time to start
            time.sleep(1)

            self.server_running = True

            # Update UI
            self.server_btn.config(
                text="✅  SERVER RUNNING",
                bg='#27ae60',
                state=tk.DISABLED
            )
            self.server_status_label.config(
                text="Status: Running on 127.0.0.1:5555",
                fg='#27ae60'
            )

            # Enable client button
            self.client_btn.config(state=tk.NORMAL, bg='#3498db')

            # Show success message
            messagebox.showinfo(
                "Server Started",
                "✅ Server started successfully!\n\n"
                "Server console window opened.\n"
                "You can now start clients."
            )

            print("[LAUNCHER] ✅ Server started successfully")

        except Exception as e:
            print(f"[LAUNCHER] ❌ Failed to start server: {e}")
            messagebox.showerror("Error", f"Failed to start server:\n{e}")

    def start_client(self):
        """Start a new client"""
        if not self.server_running:
            messagebox.showwarning(
                "No Server",
                "Please start the SERVER first!"
            )
            return

        try:
            self.client_count += 1

            # Start client in its own window
            client_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client.py')

            print(f"[LAUNCHER] Starting client #{self.client_count}: {client_script}")

            if sys.platform == 'win32':
                # Windows - just run normally (GUI will show)
                process = subprocess.Popen([sys.executable, client_script])
            else:
                # Linux/Mac
                process = subprocess.Popen([sys.executable, client_script])

            self.client_processes.append(process)

            # Update UI
            self.clients_status_label.config(
                text=f"Active Clients: {self.client_count}",
                fg='#3498db'
            )

            # Add individual client button
            self.add_client_button(self.client_count)

            # Show info
            messagebox.showinfo(
                f"Client {self.client_count}",
                f"✅ Client {self.client_count} window opened!\n\n"
                f"Login with any username."
            )

            print(f"[LAUNCHER] ✅ Client #{self.client_count} started")

        except Exception as e:
            print(f"[LAUNCHER] ❌ Failed to start client: {e}")
            messagebox.showerror("Error", f"Failed to start client:\n{e}")

    def add_client_button(self, client_num):
        """Add a button for each client"""
        btn_frame = tk.Frame(self.client_buttons_frame, bg='#34495e')
        btn_frame.pack(fill=tk.X, pady=2)

        client_label = tk.Label(
            btn_frame,
            text=f"Client {client_num}:",
            font=('Arial', 10),
            bg='#34495e',
            fg='white',
            width=10
        )
        client_label.pack(side=tk.LEFT, padx=5)

        status = tk.Label(
            btn_frame,
            text="● Running",
            font=('Arial', 9),
            bg='#34495e',
            fg='#27ae60'
        )
        status.pack(side=tk.LEFT)

    def stop_all(self):
        """Stop all processes"""
        confirm = messagebox.askyesno(
            "Stop All",
            "Are you sure you want to stop all processes?\n\n"
            "This will close the server and all clients."
        )

        if not confirm:
            return

        print("[LAUNCHER] Stopping all processes...")

        # Stop all clients
        for i, process in enumerate(self.client_processes, 1):
            try:
                process.terminate()
                print(f"[LAUNCHER] Stopped client #{i}")
            except Exception as e:
                print(f"[LAUNCHER] Error stopping client #{i}: {e}")

        # Stop server
        if self.server_process:
            try:
                self.server_process.terminate()
                print("[LAUNCHER] Stopped server")
            except Exception as e:
                print(f"[LAUNCHER] Error stopping server: {e}")

        # Reset UI
        self.server_running = False
        self.client_count = 0
        self.client_processes = []

        self.server_btn.config(
            text="🖥️  START SERVER",
            bg='#27ae60',
            state=tk.NORMAL
        )
        self.server_status_label.config(
            text="Status: Not Running",
            fg='#e74c3c'
        )
        self.client_btn.config(state=tk.DISABLED, bg='#7f8c8d')
        self.clients_status_label.config(
            text="Active Clients: 0",
            fg='#95a5a6'
        )

        # Clear client buttons
        for widget in self.client_buttons_frame.winfo_children():
            widget.destroy()

        messagebox.showinfo("Stopped", "All processes stopped successfully!")
        print("[LAUNCHER] ✅ All processes stopped")

    def on_closing(self):
        """Handle window closing"""
        if self.server_running or self.client_processes:
            confirm = messagebox.askyesno(
                "Exit",
                "Server/Clients are still running.\n\n"
                "Stop all processes and exit?"
            )
            if confirm:
                self.stop_all()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Run the launcher"""
        print("[LAUNCHER] ClassChat Launcher starting...")
        print(f"[LAUNCHER] Working directory: {os.getcwd()}")
        print(f"[LAUNCHER] Script location: {os.path.dirname(os.path.abspath(__file__))}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()



def main():
    """Main function"""
    launcher = ClassChatLauncher()
    launcher.run()



if __name__ == "__main__":
    main()