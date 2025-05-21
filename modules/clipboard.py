import io
import platform
import subprocess
from PIL import Image

def copy_to_clipboard(image_path):
    """Copy an image to the clipboard based on the OS."""
    try:
        if platform.system() == 'Windows':
            import win32clipboard
            image = Image.open(image_path)
            output = io.BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]  # Skip BMP header
            output.close()
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
        elif platform.system() == 'Darwin':  # macOS
            script = f'set the clipboard to (read (POSIX file "{image_path}") as picture)'
            subprocess.run(['osascript', '-e', script], check=True)
        elif platform.system() == 'Linux':
            subprocess.run(['xclip', '-selection', 'clipboard', '-t', 'image/png', '-i', image_path], check=True)
        return True
    except Exception as e:
        raise Exception(f"Clipboard error: {str(e)}") 