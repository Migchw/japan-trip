"""
copy_to_clipboard.py
Fast Windows clipboard utility to copy `japan_trip_places_with_images.tsv`
directly to the OS clipboard using UTF-16LE encoding so it pastes into Google Sheets perfectly.
"""

import ctypes
from ctypes import wintypes
import os
import sys

def set_clipboard(text: str) -> bool:
    CF_UNICODETEXT = 13
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
    
    kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    
    kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
    kernel32.GlobalUnlock.restype = wintypes.BOOL
    
    user32.OpenClipboard.argtypes = [wintypes.HWND]
    user32.OpenClipboard.restype = wintypes.BOOL
    
    user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
    user32.SetClipboardData.restype = wintypes.HANDLE
    
    if not user32.OpenClipboard(None):
        return False
    try:
        user32.EmptyClipboard()
        data = text.encode('utf-16-le') + b'\x00\x00'
        h_mem = kernel32.GlobalAlloc(0x0002, len(data)) # GMEM_MOVEABLE
        p_mem = kernel32.GlobalLock(h_mem)
        ctypes.memmove(p_mem, data, len(data))
        kernel32.GlobalUnlock(h_mem)
        user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        return True
    finally:
        user32.CloseClipboard()

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_file = os.path.join(base_dir, "japan_trip_places_with_images.tsv")
    
    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        sys.exit(1)
        
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    if set_clipboard(content):
        print(f"[SUCCESS] Copied {len(content.splitlines())} lines from {os.path.basename(target_file)} to clipboard!")
        print("Tip: Go to Google Sheets, click cell A1, and press Ctrl + V.")
    else:
        print("[ERROR] Could not access Windows clipboard.")
        sys.exit(1)
