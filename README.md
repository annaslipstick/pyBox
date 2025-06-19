# PyBox — The Anarchist's Python VM Manager

Forget your bloated, corporate-grade hypervisors. PyBox is the raw, unfiltered gateway to unleashing Python-powered virtual realms. No flashy GUIs, no internet dependency, just pure, unapologetic control over your custom-made Python OS “PISOs” — sandboxed, isolated, and ready to bend reality on your command.

PyBox doesn’t ask for your permission. It executes. It manages. It launches your wildest Python dystopias. From stripped-down kernels to bespoke desktop environments, your imagination is the only limit. Build your own kingdom of code, your virtual empire where you reign supreme.

No bloatware. No bullshit. Just Python, power, and anarchy.

## How It Works

PyBox is a minimalist Python VM manager designed to launch and manage your own custom Python-powered operating systems — called “PISOs.”

1. **Create Your OS**  
   Develop your OS inside the `isos/` folder. Each OS is a directory with a `main.py` entry script plus supporting files and apps.  
   Alternatively, use PyBox’s **Create Advanced OS** feature to automatically generate a barebones OS skeleton with essential files and example apps — a perfect starting point for your custom OS.

2. **Manage VMs**  
   Use the PyBox GUI to add, remove, and launch your Python OS PISOs. You provide a name, path to the entry script, and optionally description, RAM, and CPU metadata.

3. **Launch & Run**  
   PyBox launches your OS in an isolated Python subprocess with its own console window, sandboxed from other VMs and the host system.

4. **Interact & Build**  
   Your OS controls its own interface, lifecycle, and applications. PyBox handles only the VM management: launching, pausing, resuming, and killing.

PyBox gives you raw, unrestricted control to build anything from simple kernels to full desktop environments — all in pure Python.

No dependencies. No bloat. Just your code, your rules.

## License

PyBox is available under the MIT License for personal, educational, and non-commercial use. Feel free to share, modify, and enjoy it freely — just don’t make money off it.

If you intend to use PyBox for commercial purposes (for example, as part of a product you sell or a paid service), please contact me to obtain a commercial license:

Email: pybox.boil971@passmail.net

## Thanks

I want to give my thanks to my useless friend who inspired me, and for completely ignoring me when I actually started it.  
I also want to thank deepseek and ChatGPT for actually creating this piece of shit — hence it’s free for all, don’t make money off it.
