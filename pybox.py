import os
import json
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import textwrap
import signal
import sys

# === VM METADATA MANAGER ===
class PyBoxManager:
    def __init__(self, storage_file="vms.json"):
        self.storage_file = storage_file
        self.vms = self.load_vm_list()

    def load_vm_list(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, "r") as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    print("Warning: Could not parse VM list file.")
        return {}

    def save_vm_list(self):
        with open(self.storage_file, "w") as f:
            json.dump(self.vms, f, indent=4)

    def add_vm(self, vm_name, path, description="No description", ram=64, cpu=1):
        self.vms[vm_name] = {
            "path": path,
            "description": description,
            "ram": ram,
            "cpu": cpu
        }
        self.save_vm_list()

    def remove_vm(self, vm_name):
        if vm_name in self.vms:
            del self.vms[vm_name]
            self.save_vm_list()

    def list_vms(self):
        return self.vms


# === CONSOLE OUTPUT WINDOW ===
class VMConsole(tk.Toplevel):
    def __init__(self, master, vm_name, proc=None, thread=None):
        super().__init__(master)
        self.title(f"Console - {vm_name}")
        self.geometry("600x450")

        self.proc = proc
        self.thread = thread

        self.text = scrolledtext.ScrolledText(self, state='disabled', bg='black', fg='white')
        self.text.pack(fill=tk.BOTH, expand=True)

        ctrl_frame = tk.Frame(self)
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.pause_btn = tk.Button(ctrl_frame, text="Pause", command=self.pause)
        self.pause_btn.pack(side=tk.LEFT, padx=5)

        self.resume_btn = tk.Button(ctrl_frame, text="Resume", command=self.resume, state=tk.DISABLED)
        self.resume_btn.pack(side=tk.LEFT, padx=5)

        self.kill_btn = tk.Button(ctrl_frame, text="Kill", command=self.kill)
        self.kill_btn.pack(side=tk.LEFT, padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def set_proc(self, proc):
        self.proc = proc

    def set_thread(self, thread):
        self.thread = thread

    def write(self, data):
        self.text.config(state='normal')
        self.text.insert(tk.END, data)
        self.text.see(tk.END)
        self.text.config(state='disabled')

    def pause(self):
        if self.proc and self.proc.poll() is None:
            if sys.platform != "win32":
                self.proc.send_signal(signal.SIGSTOP)
                self.pause_btn.config(state=tk.DISABLED)
                self.resume_btn.config(state=tk.NORMAL)
            else:
                messagebox.showinfo("Pause Not Supported", "Pause is not supported on Windows.")

    def resume(self):
        if self.proc and self.proc.poll() is None:
            if sys.platform != "win32":
                self.proc.send_signal(signal.SIGCONT)
                self.pause_btn.config(state=tk.NORMAL)
                self.resume_btn.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Resume Not Supported", "Resume is not supported on Windows.")

    def kill(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.pause_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.DISABLED)
            self.kill_btn.config(state=tk.DISABLED)
            self.write("\n[Process terminated by user]\n")

    def on_close(self):
        # Optionally kill the process when closing console
        if self.proc and self.proc.poll() is None:
            if messagebox.askyesno("Exit", "VM is running. Kill and close?"):
                self.kill()
                self.destroy()
        else:
            self.destroy()


# === MAIN GUI ===
class PyBoxGUI(tk.Tk):
    def __init__(self, manager):
        super().__init__()
        self.title("PyBox - Python VM Manager")
        self.geometry("500x400")
        self.manager = manager

        self.vm_listbox = tk.Listbox(self)
        self.vm_listbox.pack(fill=tk.BOTH, expand=True)

        self.desc_label = tk.Label(self, text="Select a VM", anchor="w", justify="left", wraplength=480)
        self.desc_label.pack(fill=tk.X, padx=5)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X)

        buttons = [
            ("Add VM", self.add_vm),
            ("Remove VM", self.remove_vm),
            ("Launch VM", self.launch_vm),
            ("New Advanced OS", self.create_advanced_os),
            ("Refresh", self.refresh_vm_list),
        ]

        for text, cmd in buttons:
            btn = tk.Button(btn_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        self.vm_listbox.bind("<<ListboxSelect>>", self.update_description)
        self.vm_listbox.bind("<Double-1>", lambda e: self.launch_vm())

        self.refresh_vm_list()

    def refresh_vm_list(self):
        self.vm_listbox.delete(0, tk.END)
        for name in sorted(self.manager.vms.keys()):
            self.vm_listbox.insert(tk.END, name)

    def update_description(self, event):
        selection = self.vm_listbox.curselection()
        if selection:
            vm_name = self.vm_listbox.get(selection[0])
            desc = self.manager.vms[vm_name].get("description", "No description")
            self.desc_label.config(text=f"{vm_name}: {desc}")
        else:
            self.desc_label.config(text="Select a VM")

    def add_vm(self):
        vm_name = simpledialog.askstring("VM Name", "Enter VM name:")
        if not vm_name:
            return

        path = filedialog.askopenfilename(
            title="Select entry script (e.g. main.py)",
            initialdir="isos",
            filetypes=[("Python files", "*.py")]
        )
        if not path:
            return

        description = simpledialog.askstring("Description", "Enter description:", initialvalue="A Python VM ISO")
        ram = simpledialog.askinteger("RAM (MB)", "Enter RAM amount:", initialvalue=64)
        cpu = simpledialog.askinteger("CPU Cores", "Enter number of cores:", initialvalue=1)

        self.manager.add_vm(vm_name, path, description, ram, cpu)
        self.refresh_vm_list()

    def remove_vm(self):
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showinfo("Remove VM", "Please select a VM to remove.")
            return

        vm_name = self.vm_listbox.get(selection[0])
        self.manager.remove_vm(vm_name)
        self.refresh_vm_list()
        self.desc_label.config(text="Select a VM")

    def launch_vm(self):
        selection = self.vm_listbox.curselection()
        if not selection:
            messagebox.showinfo("Launch VM", "Please select a VM to launch.")
            return

        vm_name = self.vm_listbox.get(selection[0])
        vm_data = self.manager.vms[vm_name]
        path = vm_data["path"]

        if not os.path.exists(path):
            messagebox.showerror("Missing File", f"ISO entry script not found: {path}")
            return

        console = VMConsole(self, vm_name)

        def run_vm():
            proc = subprocess.Popen(
                ["python3", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            console.set_proc(proc)

            for line in proc.stdout:
                console.write(line)
            proc.wait()

            # Optionally disable buttons after process ends
            console.pause_btn.config(state=tk.DISABLED)
            console.resume_btn.config(state=tk.DISABLED)
            console.kill_btn.config(state=tk.DISABLED)
            console.write("\n[Process finished]\n")

        thread = threading.Thread(target=run_vm, daemon=True)
        thread.start()
        console.set_thread(thread)

    def create_advanced_os(self):
        name = simpledialog.askstring("New OS", "Enter OS name (e.g., myos):")
        if not name:
            return

        name = name.strip().lower()
        if name in self.manager.vms:
            messagebox.showerror("Error", f"OS '{name}' already exists.")
            return

        description = simpledialog.askstring("Description", "Enter OS description:", initialvalue="My custom Python OS")
        ram = simpledialog.askinteger("RAM (MB)", "Enter RAM amount:", initialvalue=64)
        cpu = simpledialog.askinteger("CPU Cores", "Enter number of CPU cores:", initialvalue=1)

        iso_dir = os.path.join("isos", name)
        apps_dir = os.path.join(iso_dir, "apps")
        try:
            os.makedirs(apps_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create OS directories:\n{e}")
            return

        with open(os.path.join(iso_dir, "main.py"), "w") as f:
            f.write(textwrap.dedent(f"""\
                # Entry point for {name}
                from kernel import boot

                if __name__ == "__main__":
                    boot()
            """))

        with open(os.path.join(iso_dir, "kernel.py"), "w") as f:
            f.write(textwrap.dedent(f"""\
                def boot():
                    print("Booting {name} OS...")
                    import desktop
                    desktop.start()
            """))

        with open(os.path.join(iso_dir, "desktop.py"), "w") as f:
            f.write(textwrap.dedent("""\
                def start():
                    print("Welcome to the desktop environment!")
                    print("Apps: calculator, text_editor")
            """))

        with open(os.path.join(iso_dir, "vfs.py"), "w") as f:
            f.write(textwrap.dedent("""\
                # Virtual file system for the OS
                filesystem = {}

                def read_file(path):
                    return filesystem.get(path, "[file not found]")

                def write_file(path, content):
                    filesystem[path] = content
            """))

        with open(os.path.join(iso_dir, "wm_api.py"), "w") as f:
            f.write(textwrap.dedent("""\
                # Simulated window manager API
                def open_window(title):
                    print(f"[Window: {title}]")
            """))

        with open(os.path.join(apps_dir, "__init__.py"), "w") as f:
            f.write("# apps package")

        with open(os.path.join(apps_dir, "calculator.py"), "w") as f:
            f.write(textwrap.dedent("""\
                def run():
                    print("Calculator app launched!")
            """))

        with open(os.path.join(apps_dir, "text_editor.py"), "w") as f:
            f.write(textwrap.dedent("""\
                def run():
                    print("Text editor app launched!")
            """))

        self.manager.add_vm(name, os.path.join(iso_dir, "main.py"), description, ram, cpu)
        self.refresh_vm_list()
        messagebox.showinfo("Success", f"New OS '{name}' created successfully!")


if __name__ == "__main__":
    manager = PyBoxManager()
    app = PyBoxGUI(manager)
    app.mainloop()
