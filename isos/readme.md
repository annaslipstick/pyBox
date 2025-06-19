 PyBox ISOs (PISOs)

This folder is where your custom Python-powered operating systems (PISOs) live.

## Creating Your Own PISO

Each PISO is a folder containing at minimum:

- `main.py`: The entry point script that PyBox launches.
- Any additional Python files, assets, or apps your OS needs.

### Minimal Example

Create a new folder inside `isos/`:

isos/
└── my_os/
└── main.py


Example `main.py`:

```python
def main():
    print("Welcome to my custom Python OS!")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()

How to Add Your PISO to PyBox

    Open PyBox GUI.

    Click “Add PISO” and fill out:

        Name: Your OS name.

        Entry Script: Path to your main.py inside your PISO folder.

        Optional: Description, RAM, CPU.

    Launch and watch your OS run in isolation.

Happy hacking. Build your own digital dystopia or utopia — whatever floats your anarchist boat.

