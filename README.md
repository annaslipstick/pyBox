PyBox VM (QEMU-like Host) – Goals Recap
Component	Required?	Description
🧠 CPU Emulator	✅	Simulates instruction loop or Python execution
🧮 Memory Manager	✅	Allocate RAM space, model memory constraints
🗃️ Filesystem Layer	✅	Simulate disk, folders, virtual drives
🧾 Syscalls / APIs	✅	Controlled interface exposed to ISOs
📜 ISO Loader	✅	Loads and parses .iso Python files
🔒 Sandbox	✅	Safely executes ISO code without escaping VM
⏱️ Resource Limits	✅	Cap CPU time, RAM usage, prevent infinite loops
📺 (Optional GUI)	🔜	Screen/desktop emulation (Tkinter/PyGame)
