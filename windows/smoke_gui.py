"""Create and render the real Tk interface, then close without starting Docker."""
from pathlib import Path
import tempfile
import tkinter as tk

from ewb_windows.gui import App
from ewb_windows.state import Store


with tempfile.TemporaryDirectory() as directory:
    root = tk.Tk()
    app = App(root, Store(Path(directory)))
    root.update()
    assert len(app.buttons) >= 12
    assert app.phase.get()
    assert app.settings_match()
    app.timezone.set("Etc/UTC")
    assert not app.settings_match()
    app.poll()
    assert app.confirm_button.instate(["disabled"])
    root.after(500, root.destroy)
    root.mainloop()
    print("GUI smoke check passed")
