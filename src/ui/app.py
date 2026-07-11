import json
import os
import sys
import threading
from pathlib import Path

import customtkinter as ctk
import keyboard

from engine.clicker import WiltClicker
from engine.hotkeys import HotkeyManager

ctk.set_window_scaling(1.1)
ctk.set_widget_scaling(1.1)


def resource_path(relative_path: str) -> str:
	"""Get absolute path to resource, works for dev and for PyInstaller"""
	base_path = getattr(sys, "_MEIPASS", None)

	if isinstance(base_path, str):
		return str(Path(base_path) / relative_path)

	dev_path = Path(__file__).resolve().parent.parent.parent
	return str(dev_path / relative_path)


class AutoclickerApp(ctk.CTk):
	humanize_var: ctk.BooleanVar
	jitter_var: ctk.BooleanVar
	move_drop_var: ctk.BooleanVar
	lock_coords_var: ctk.BooleanVar
	strict_hotkey_var: ctk.BooleanVar
	button_var: ctk.StringVar
	mode_var: ctk.StringVar

	def __init__(self):
		super().__init__()
		self.title("Wilt Clicker")
		self.geometry("750x450")
		self.minsize(700, 400)
		ctk.set_appearance_mode("dark")

		self.engine = WiltClicker()
		self.hotkeys = HotkeyManager(self.engine)

		self.bound_keys = {
			"main": "f6",
			"escape": "ctrl+shift+comma",
			"humanize": "",
			"jitter": "",
			"move_drop": "",
			"lock": "",
			"limit_count": "",
			"limit_time": "",
		}
		self.status_error = ""

		self.config_file = "wilt-clicker-config.json"

		ctk.FontManager.load_font(resource_path("Inter-Regular.ttf"))
		ctk.FontManager.load_font(resource_path("Inter-Bold.ttf"))

		self._build_ui()
		self.load_config()
		self._update_settings()

		self.protocol("WM_DELETE_WINDOW", self._on_closing)

	def _build_ui(self):
		self.title_label = ctk.CTkLabel(self, text="Wilt Clicker", font=("Inter", 24, "bold"))
		self.title_label.pack(pady=(15, 5))

		self.tabs = ctk.CTkTabview(self)
		self.tabs.pack(fill="both", expand=True, padx=20, pady=(5, 10))

		self.tab_main = self.tabs.add("Main")
		self.tab_adv = self.tabs.add("Advanced")
		self.tab_hotkeys = self.tabs.add("Hotkeys")

		self._build_main_tab()
		self._build_advanced_tab()
		self._build_hotkeys_tab()

		self.status_label = ctk.CTkLabel(self, text="Status: Idle", text_color="gray", font=("Inter", 12))
		self.status_label.pack(side="bottom", pady=5)

		self._update_ui_loop()

	def _build_main_tab(self):
		ctrl_frame = ctk.CTkFrame(self.tab_main, fg_color="transparent")
		ctrl_frame.pack(fill="x", pady=(10, 5), padx=20)
		inner_ctrl = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
		inner_ctrl.pack(expand=True)

		ctk.CTkLabel(inner_ctrl, text="CPS:", font=("Inter", 14, "bold")).pack(side="left", padx=(0, 5))
		self.cps_entry = ctk.CTkEntry(inner_ctrl, width=60, justify="center", font=("Inter", 14))
		self.cps_entry.insert(0, "10")
		self.cps_entry.pack(side="left", padx=(0, 15))
		self.cps_entry.bind("<KeyRelease>", self._on_cps_change)

		ctk.CTkLabel(inner_ctrl, text="Delay (ms):", font=("Inter", 14, "bold")).pack(side="left", padx=(0, 5))
		self.delay_entry = ctk.CTkEntry(inner_ctrl, width=65, justify="center", font=("Inter", 14))
		self.delay_entry.insert(0, "100")
		self.delay_entry.pack(side="left", padx=(0, 20))
		self.delay_entry.bind("<KeyRelease>", self._on_delay_change)

		self.button_var = ctk.StringVar(value="Left")
		ctk.CTkOptionMenu(
			inner_ctrl,
			values=["Left", "Right", "Middle"],
			variable=self.button_var,
			command=lambda val: self._update_settings(),
			width=90,
			font=("Inter", 13),
		).pack(side="left", padx=10)

		self.mode_var = ctk.StringVar(value="Toggle")
		ctk.CTkOptionMenu(
			inner_ctrl,
			values=["Toggle", "Hold"],
			variable=self.mode_var,
			command=lambda val: self._update_settings(),
			width=90,
			font=("Inter", 13),
		).pack(side="left", padx=10)

		target_frame = ctk.CTkFrame(self.tab_main, fg_color="#2b2b2b", corner_radius=8)
		target_frame.pack(fill="x", pady=10, padx=20)
		inner_target = ctk.CTkFrame(target_frame, fg_color="transparent")
		inner_target.pack(pady=10, expand=True)

		self.lock_coords_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			inner_target,
			text="Lock Coords",
			variable=self.lock_coords_var,
			command=self._update_settings,
			font=("Inter", 14, "bold"),
		).pack(side="left", padx=(0, 15))

		ctk.CTkLabel(inner_target, text="X:", font=("Inter", 14)).pack(side="left")
		self.x_entry = ctk.CTkEntry(inner_target, width=60, justify="center", font=("Inter", 14))
		self.x_entry.insert(0, "0")
		self.x_entry.pack(side="left", padx=(5, 10))
		self.x_entry.bind("<KeyRelease>", lambda event: self._update_settings())

		ctk.CTkLabel(inner_target, text="Y:", font=("Inter", 14)).pack(side="left")
		self.y_entry = ctk.CTkEntry(inner_target, width=60, justify="center", font=("Inter", 14))
		self.y_entry.insert(0, "0")
		self.y_entry.pack(side="left", padx=(5, 20))
		self.y_entry.bind("<KeyRelease>", lambda event: self._update_settings())

		self.capture_btn = ctk.CTkButton(
			inner_target, text="Capture Overlay", width=120, font=("Inter", 13, "bold"), command=self._capture_mode
		)
		self.capture_btn.pack(side="left")

		toggles_wrapper = ctk.CTkFrame(self.tab_main, fg_color="transparent")
		toggles_wrapper.pack(fill="x", pady=5)
		toggles_frame = ctk.CTkFrame(toggles_wrapper, fg_color="transparent")
		toggles_frame.pack(expand=True)

		self.humanize_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			toggles_frame,
			text="Humanize (Randomize CPS)",
			variable=self.humanize_var,
			command=self._update_settings,
			font=("Inter", 14),
		).grid(row=0, column=0, sticky="w", pady=8, padx=20)

		self.jitter_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			toggles_frame,
			text="Cursor Jitter (Shake)",
			variable=self.jitter_var,
			command=self._update_settings,
			font=("Inter", 14),
		).grid(row=0, column=1, sticky="w", pady=8, padx=20)

		self.move_drop_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			toggles_frame,
			text="Drop CPS on Mouse Move",
			variable=self.move_drop_var,
			command=self._update_settings,
			font=("Inter", 14),
		).grid(row=1, column=0, sticky="w", pady=8, padx=20)

		self.strict_hotkey_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			toggles_frame,
			text="Loose Hotkey Matching",
			variable=self.strict_hotkey_var,
			command=self._update_settings,
			font=("Inter", 14),
		).grid(row=1, column=1, sticky="w", pady=8, padx=20)

		count_frame = ctk.CTkFrame(toggles_frame, fg_color="transparent")
		count_frame.grid(row=2, column=0, sticky="w", pady=8, padx=20)

		self.use_count_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			count_frame,
			text="Click To:",
			variable=self.use_count_var,
			command=self._on_limit_toggle,
			font=("Inter", 14),
		).pack(side="left")
		self.limit_count_entry = ctk.CTkEntry(count_frame, width=60, justify="center", font=("Inter", 14))
		self.limit_count_entry.insert(0, "100")
		self.limit_count_entry.pack(side="left", padx=10)
		self.limit_count_entry.bind("<KeyRelease>", lambda event: self._update_settings())

		time_frame = ctk.CTkFrame(toggles_frame, fg_color="transparent")
		time_frame.grid(row=2, column=1, sticky="w", pady=8, padx=20)

		self.use_time_var = ctk.BooleanVar(value=False)
		ctk.CTkCheckBox(
			time_frame,
			text="Click For (Secs):",
			variable=self.use_time_var,
			command=self._on_limit_toggle,
			font=("Inter", 14),
		).pack(side="left")
		self.limit_time_entry = ctk.CTkEntry(time_frame, width=60, justify="center", font=("Inter", 14))
		self.limit_time_entry.insert(0, "10")
		self.limit_time_entry.pack(side="left", padx=10)
		self.limit_time_entry.bind("<KeyRelease>", lambda event: self._update_settings())

	def _on_cps_change(self, _event: object):
		"""Fires when the user types in the CPS box, updates the Delay box."""
		try:
			cps = float(self.cps_entry.get())
			if cps > 0:
				delay = 1000.0 / cps
				self.delay_entry.delete(0, "end")
				self.delay_entry.insert(0, f"{delay:.4f}".rstrip("0").rstrip("."))
		except ValueError:
			pass
		self._update_settings()

	def _on_delay_change(self, _event: object):
		"""Fires when the user types in the Delay box, updates the CPS box."""
		try:
			delay = float(self.delay_entry.get())
			if delay > 0:
				cps = 1000.0 / delay
				self.cps_entry.delete(0, "end")
				self.cps_entry.insert(0, f"{cps:.4f}".rstrip("0").rstrip("."))
		except ValueError:
			pass
		self._update_settings()

	def _on_limit_toggle(self):
		if self.use_count_var.get():
			self.use_time_var.set(False)
		elif self.use_time_var.get():
			self.use_count_var.set(False)
		self._update_settings()

	def _build_advanced_tab(self):
		adv_wrapper = ctk.CTkFrame(self.tab_adv, fg_color="transparent")
		adv_wrapper.pack(fill="both", expand=True)

		adv_frame = ctk.CTkFrame(adv_wrapper, fg_color="transparent")
		adv_frame.pack(expand=True)

		hum_frame = ctk.CTkFrame(adv_frame, fg_color="transparent")
		hum_frame.grid(row=0, column=0, padx=40, sticky="n")
		ctk.CTkLabel(hum_frame, text="Humanize Range (%)", font=("Inter", 15, "bold")).pack(pady=(0, 5))
		ctk.CTkLabel(hum_frame, text="Varies delay randomly", font=("Inter", 12, "italic"), text_color="gray").pack(
			pady=(0, 10)
		)

		row_min = ctk.CTkFrame(hum_frame, fg_color="transparent")
		row_min.pack(pady=5)
		ctk.CTkLabel(row_min, text="Min:", width=40, anchor="e").pack(side="left", padx=5)
		self.hum_min_entry = ctk.CTkEntry(row_min, placeholder_text="80", width=80, font=("Inter", 13))
		self.hum_min_entry.insert(0, "80")
		self.hum_min_entry.pack(side="left")
		self.hum_min_entry.bind("<KeyRelease>", lambda event: self._update_settings())

		row_max = ctk.CTkFrame(hum_frame, fg_color="transparent")
		row_max.pack(pady=5)
		ctk.CTkLabel(row_max, text="Max:", width=40, anchor="e").pack(side="left", padx=5)
		self.hum_max_entry = ctk.CTkEntry(row_max, placeholder_text="120", width=80, font=("Inter", 13))
		self.hum_max_entry.insert(0, "120")
		self.hum_max_entry.pack(side="left")
		self.hum_max_entry.bind("<KeyRelease>", lambda event: self._update_settings())

		drop_frame = ctk.CTkFrame(adv_frame, fg_color="transparent")
		drop_frame.grid(row=0, column=1, padx=40, sticky="n")
		ctk.CTkLabel(drop_frame, text="Movement Drop (%)", font=("Inter", 15, "bold")).pack(pady=(0, 5))
		ctk.CTkLabel(drop_frame, text="CPS lost when moving", font=("Inter", 12, "italic"), text_color="gray").pack(
			pady=(0, 10)
		)

		row_drop = ctk.CTkFrame(drop_frame, fg_color="transparent")
		row_drop.pack(pady=5)
		ctk.CTkLabel(row_drop, text="Drop:", width=40, anchor="e").pack(side="left", padx=5)
		self.drop_entry = ctk.CTkEntry(row_drop, placeholder_text="60", width=80, font=("Inter", 13))
		self.drop_entry.insert(0, "60")
		self.drop_entry.pack(side="left")
		self.drop_entry.bind("<KeyRelease>", lambda event: self._update_settings())

	def _build_hotkeys_tab(self):
		ctk.CTkLabel(
			self.tab_hotkeys,
			text="Click a button, then press a key. (ESC to Unbind)",
			font=("Inter", 13, "italic"),
			text_color="gray",
		).pack(pady=(5, 10))

		self.hotkey_btns: dict[str, ctk.CTkButton] = {}

		main_wrapper = ctk.CTkFrame(self.tab_hotkeys, fg_color="transparent")
		main_wrapper.pack(fill="x", pady=5)
		main_row = ctk.CTkFrame(main_wrapper, fg_color="transparent")
		main_row.pack(expand=True)

		ctk.CTkLabel(main_row, text="Main Clicker", width=140, anchor="w", font=("Inter", 14, "bold")).pack(
			side="left", padx=10
		)
		main_current = self.bound_keys["main"]
		main_btn = ctk.CTkButton(
			main_row,
			text=f"[{main_current.upper()}]" if main_current else "Unbound",
			width=150,
			fg_color="#600080" if main_current else "#4a4a4a",
			font=("Inter", 13, "bold"),
			command=lambda n="main": self._listen_for_hotkey(n),
		)
		main_btn.pack(side="right", padx=10)
		self.hotkey_btns["main"] = main_btn

		grid_wrapper = ctk.CTkFrame(self.tab_hotkeys, fg_color="transparent")
		grid_wrapper.pack(fill="both", expand=True)
		grid_frame = ctk.CTkFrame(grid_wrapper, fg_color="transparent")
		grid_frame.pack(expand=True)

		def create_bind_cell(name: str, label_text: str, row_idx: int, col_idx: int):
			cell = ctk.CTkFrame(grid_frame, fg_color="transparent")
			cell.grid(row=row_idx, column=col_idx, sticky="ew", padx=30, pady=5)
			ctk.CTkLabel(cell, text=label_text, width=150, anchor="w", font=("Inter", 14)).pack(side="left")
			current = self.bound_keys[name]
			btn = ctk.CTkButton(
				cell,
				text=f"[{current.upper()}]" if current else "Unbound",
				width=150,
				fg_color="#600080" if current else "#4a4a4a",
				font=("Inter", 13, "bold"),
				command=lambda n=name: self._listen_for_hotkey(n),
			)
			btn.pack(side="right")
			self.hotkey_btns[name] = btn

		create_bind_cell("humanize", "Toggle Humanize", 0, 0)
		create_bind_cell("jitter", "Toggle Jitter", 0, 1)
		create_bind_cell("move_drop", "Toggle Move Drop", 1, 0)
		create_bind_cell("lock", "Toggle Coords Lock", 1, 1)
		create_bind_cell("limit_count", "Toggle Click Limit", 2, 0)
		create_bind_cell("limit_time", "Toggle Time Limit", 2, 1)

		exit_row = ctk.CTkFrame(self.tab_hotkeys, fg_color="#3a2525", corner_radius=8)
		exit_row.pack(fill="x", padx=35, pady=(10, 20))
		inner_exit = ctk.CTkFrame(exit_row, fg_color="transparent")
		inner_exit.pack(expand=True, pady=10)

		ctk.CTkLabel(
			inner_exit,
			text="Emergency Exit",
			width=140,
			anchor="w",
			font=("Inter", 14, "bold"),
			text_color="#ff6b6b",
		).pack(side="left", padx=10)
		exit_current = self.bound_keys["escape"]
		exit_btn = ctk.CTkButton(
			inner_exit,
			text=f"[{exit_current.upper()}]",
			width=150,
			fg_color="#a83232",
			hover_color="#8b2828",
			font=("Inter", 13, "bold"),
			command=lambda n="escape": self._listen_for_hotkey(n),
		)
		exit_btn.pack(side="right", padx=10)
		self.hotkey_btns["escape"] = exit_btn

	@staticmethod
	def _safe_float(entry: ctk.CTkEntry, default: float) -> float:
		try:
			return float(entry.get())
		except ValueError:
			return default

	def _update_settings(self):
		main_k = self.bound_keys["main"]
		esc_k = self.bound_keys["escape"]
		toggle_keys = [
			self.bound_keys[k]
			for k in ["humanize", "jitter", "move_drop", "lock", "limit_count", "limit_time"]
			if self.bound_keys[k]
		]

		has_conflict = False
		if main_k and esc_k and main_k == esc_k:
			has_conflict = True
		if main_k and main_k in toggle_keys:
			has_conflict = True
		if esc_k and esc_k in toggle_keys:
			has_conflict = True

		if has_conflict:
			self.status_error = "Error: Main Clicker and Emergency Exit keys must be unique!"
			self.hotkeys.set_error_state(True)
			return

		self.status_error = ""
		self.hotkeys.set_error_state(False)

		cps = self._safe_float(self.cps_entry, 10.0)
		tx = int(self._safe_float(self.x_entry, 0.0))
		ty = int(self._safe_float(self.y_entry, 0.0))
		hum_min = self._safe_float(self.hum_min_entry, 80.0) / 100.0
		hum_max = self._safe_float(self.hum_max_entry, 120.0) / 100.0
		drop_pct = self._safe_float(self.drop_entry, 60.0) / 100.0
		click_limit = int(self._safe_float(self.limit_count_entry, 0.0))
		time_limit = self._safe_float(self.limit_time_entry, 0.0)

		self.engine.update_settings(
			cps,
			self.button_var.get().lower(),
			self.humanize_var.get(),
			self.jitter_var.get(),
			self.move_drop_var.get(),
			self.lock_coords_var.get(),
			tx,
			ty,
			hum_min,
			hum_max,
			drop_pct,
			self.use_count_var.get(),
			click_limit,
			self.use_time_var.get(),
			time_limit,
		)

		self.hotkeys.update_main_settings(main_k, self.mode_var.get().lower(), self.strict_hotkey_var.get())
		self.hotkeys.update_exit_hotkey(esc_k)

		mapping = {
			"humanize": lambda: self._toggle_var(self.humanize_var),
			"jitter": lambda: self._toggle_var(self.jitter_var),
			"move_drop": lambda: self._toggle_var(self.move_drop_var),
			"lock": lambda: self._toggle_var(self.lock_coords_var),
			"limit_count": lambda: self._toggle_exclusive("count"),
			"limit_time": lambda: self._toggle_exclusive("time"),
		}
		for t_name in ["humanize", "jitter", "move_drop", "lock", "limit_count", "limit_time"]:
			self.hotkeys.bind_toggle(t_name, self.bound_keys[t_name], mapping[t_name])

	def _toggle_var(self, var: ctk.BooleanVar):
		var.set(not var.get())
		self._update_settings()

	def _toggle_exclusive(self, mode: str):
		if mode == "count":
			self.use_count_var.set(not self.use_count_var.get())
			if self.use_count_var.get():
				self.use_time_var.set(False)
		else:
			self.use_time_var.set(not self.use_time_var.get())
			if self.use_time_var.get():
				self.use_count_var.set(False)
		self._update_settings()

	def _listen_for_hotkey(self, bind_name: str):
		btn = self.hotkey_btns[bind_name]
		btn.configure(text="Listening...", fg_color="#a83232")

		def listener():
			key = keyboard.read_hotkey(suppress=False)

			if key == "esc":
				if bind_name == "escape":
					key = "ctrl+shift+comma"
				else:
					key = ""

			self.bound_keys[bind_name] = key
			display_text = f"[{key.upper()}]" if key else "Unbound"
			if bind_name == "escape":
				btn.configure(text=display_text, fg_color="#a83232")
			else:
				btn.configure(text=display_text, fg_color="#600080" if key else "#4a4a4a")

			self._update_settings()

		threading.Thread(target=listener, daemon=True).start()

	def _capture_mode(self):
		self.capture_btn.configure(text="Click Screen (ESC Cancel)", fg_color="#a83232")

		overlay = ctk.CTkToplevel(self)
		overlay.attributes("-fullscreen", True)
		overlay.attributes("-alpha", 0.4)
		overlay.attributes("-topmost", True)
		overlay.configure(cursor="crosshair")
		overlay.focus_force()

		def on_click(event: object):
			x, y = getattr(event, "x_root", 0), getattr(event, "y_root", 0)

			self.x_entry.delete(0, "end")
			self.x_entry.insert(0, str(x))
			self.y_entry.delete(0, "end")
			self.y_entry.insert(0, str(y))

			self.capture_btn.configure(text="Capture Overlay", fg_color="#600080")
			self._update_settings()
			overlay.destroy()

		def on_cancel(_event: object):
			self.capture_btn.configure(text="Capture Overlay", fg_color="#600080")
			overlay.destroy()

		overlay.bind("<Button-1>", on_click)
		overlay.bind("<Escape>", on_cancel)

	def save_config(self):
		"""Gathers all current UI states and saves them to a JSON file."""
		config_data = {
			"cps": self.cps_entry.get(),
			"button": self.button_var.get(),
			"mode": self.mode_var.get(),
			"lock_coords": self.lock_coords_var.get(),
			"target_x": self.x_entry.get(),
			"target_y": self.y_entry.get(),
			"humanize": self.humanize_var.get(),
			"jitter": self.jitter_var.get(),
			"move_drop": self.move_drop_var.get(),
			"strict_hotkey": self.strict_hotkey_var.get(),
			"use_count": self.use_count_var.get(),
			"click_limit": self.limit_count_entry.get(),
			"use_time": self.use_time_var.get(),
			"time_limit": self.limit_time_entry.get(),
			"hum_min": self.hum_min_entry.get(),
			"hum_max": self.hum_max_entry.get(),
			"drop_pct": self.drop_entry.get(),
			"hotkeys": self.bound_keys,
		}
		try:
			with open(self.config_file, "w") as f:
				json.dump(config_data, f, indent=4)
		except OSError:
			pass

	def load_config(self):
		"""Reads the JSON file and populates the UI."""
		if not os.path.exists(self.config_file):
			return

		try:
			with open(self.config_file, "r") as f:
				config = json.load(f)

			def set_entry(entry: ctk.CTkEntry, val: str | float | int):
				entry.delete(0, "end")
				entry.insert(0, str(val))

			set_entry(self.cps_entry, config.get("cps", "10"))
			self.button_var.set(config.get("button", "left"))
			self.mode_var.set(config.get("mode", "toggle"))
			self.lock_coords_var.set(config.get("lock_coords", False))
			set_entry(self.x_entry, config.get("target_x", "0"))
			set_entry(self.y_entry, config.get("target_y", "0"))

			self.humanize_var.set(config.get("humanize", False))
			self.jitter_var.set(config.get("jitter", False))
			self.move_drop_var.set(config.get("move_drop", False))
			self.strict_hotkey_var.set(config.get("strict_hotkey", False))

			self.use_count_var.set(config.get("use_count", False))
			set_entry(self.limit_count_entry, config.get("click_limit", "100"))
			self.use_time_var.set(config.get("use_time", False))
			set_entry(self.limit_time_entry, config.get("time_limit", "10"))

			set_entry(self.hum_min_entry, config.get("hum_min", "80"))
			set_entry(self.hum_max_entry, config.get("hum_max", "120"))
			set_entry(self.drop_entry, config.get("drop_pct", "60"))

			saved_keys = config.get("hotkeys", {})
			for k, v in saved_keys.items():
				if k in self.bound_keys:
					self.bound_keys[k] = v
					btn = self.hotkey_btns.get(k)
					if btn:
						if k == "escape":
							btn.configure(text=f"[{v.upper()}]", fg_color="#a83232")
						else:
							btn.configure(
								text=f"[{v.upper()}]" if v else "Unbound", fg_color="#600080" if v else "#4a4a4a"
							)

			self._on_cps_change(None)

		except (OSError, json.JSONDecodeError):
			pass

	def _on_closing(self):
		"""Fires when the user clicks the 'X' to close the app."""
		self.save_config()
		self.engine.stop()
		self.destroy()
		os._exit(0)

	def _update_ui_loop(self):
		if self.status_error:
			self.status_label.configure(text=self.status_error, text_color="#ff4444")
		elif self.engine.is_running:
			self.status_label.configure(text="Status: CLICKING", text_color="green")
		else:
			self.status_label.configure(text="Status: Idle", text_color="gray")

		# noinspection PyTypeChecker
		self.after(100, self._update_ui_loop)
