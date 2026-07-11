import os
import threading
import time
from typing import Callable

import keyboard

from engine.clicker import WiltClicker


class HotkeyManager:
	def __init__(self, clicker_engine: WiltClicker):
		self.engine = clicker_engine

		self.main_hotkey = ""
		self.mode = "toggle"
		self.ignore_extra = False
		self._is_toggled = False
		self._was_pressed = False

		self.has_error = False

		self.exit_hotkey = ""
		self.exit_callback: Callable[[], None] = lambda: os._exit(0)

		self.toggle_callbacks: dict[str, Callable[[], None]] = {}
		self.toggle_hotkeys: dict[str, str] = {}

		threading.Thread(target=self._monitor_loop, daemon=True).start()

	def set_error_state(self, state: bool):
		"""Locks the hotkey listener and stops the clicker if bindings are invalid."""
		self.has_error = state
		if state:
			self.engine.stop()

	def update_main_settings(self, hotkey: str, mode: str, ignore_extra: bool):
		self.main_hotkey = hotkey
		self.mode = mode
		self.ignore_extra = ignore_extra
		self._is_toggled = False
		self.engine.stop()

	def update_exit_hotkey(self, hotkey: str):
		"""Safely unbinds the old exit key and binds the new one."""
		if self.exit_hotkey == hotkey:
			return

		if self.exit_hotkey:
			try:
				keyboard.remove_hotkey(self.exit_hotkey)
			except KeyError:
				pass

		self.exit_hotkey = hotkey
		if hotkey:
			keyboard.add_hotkey(hotkey, self.exit_callback, suppress=False)

	def bind_toggle(self, name: str, hotkey: str, callback: Callable[[], None]):
		if self.toggle_hotkeys.get(name) == hotkey:
			return

		if name in self.toggle_hotkeys and self.toggle_hotkeys[name]:
			try:
				keyboard.remove_hotkey(self.toggle_hotkeys[name])
			except KeyError:
				pass

		self.toggle_hotkeys[name] = hotkey
		self.toggle_callbacks[name] = callback

		if hotkey:
			keyboard.add_hotkey(hotkey, callback, suppress=False)

	def _is_hotkey_active(self) -> bool:
		if not self.main_hotkey:
			return False
		try:
			if not keyboard.is_pressed(self.main_hotkey):
				return False
			if self.ignore_extra:
				return True
			modifiers = ["ctrl", "shift", "alt"]
			hotkey_parts = self.main_hotkey.lower().split("+")
			for mod in modifiers:
				if mod not in hotkey_parts and keyboard.is_pressed(mod):
					return False
			return True
		except ValueError:
			return False

	def _monitor_loop(self):
		while True:
			time.sleep(0.01)

			if self.has_error:
				continue

			currently_pressed = self._is_hotkey_active()

			if self.mode == "hold":
				if currently_pressed and not self.engine.is_running:
					self.engine.start()
				elif not currently_pressed and self.engine.is_running:
					self.engine.stop()
			elif self.mode == "toggle":
				if currently_pressed and not self._was_pressed:
					self._is_toggled = not self._is_toggled
					if self._is_toggled:
						self.engine.start()
					else:
						self.engine.stop()
			self._was_pressed = currently_pressed
