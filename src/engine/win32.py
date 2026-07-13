import ctypes
from ctypes import wintypes

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

user32 = ctypes.windll.user32

mouse_event = getattr(user32, "mouse_event")
mouse_event.argtypes = [
	wintypes.DWORD,
	wintypes.DWORD,
	wintypes.DWORD,
	wintypes.DWORD,
	ctypes.c_void_p,
]
mouse_event.restype = None

GetCursorPos = getattr(user32, "GetCursorPos")
GetCursorPos.argtypes = [wintypes.LPPOINT]
GetCursorPos.restype = wintypes.BOOL

SetCursorPos = getattr(user32, "SetCursorPos")
SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
SetCursorPos.restype = wintypes.BOOL

GetAsyncKeyState = getattr(user32, "GetAsyncKeyState")
GetAsyncKeyState.argtypes = [ctypes.c_int]
GetAsyncKeyState.restype = wintypes.SHORT


def get_cursor_pos() -> tuple[int, int]:
	pt = wintypes.POINT()
	GetCursorPos(ctypes.byref(pt))
	return pt.x, pt.y


def set_cursor_pos(x: int, y: int) -> None:
	SetCursorPos(x, y)


def send_click(button: str = "left") -> None:
	if button == "left":
		mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, None)
		mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, None)
	elif button == "right":
		mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, None)
		mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, None)
