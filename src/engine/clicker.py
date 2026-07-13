import random
import threading
import time

from engine.win32 import get_cursor_pos, send_click, set_cursor_pos


class WiltClicker:
	def __init__(self) -> None:
		self.is_running = False
		self.cps = 10.0
		self.button = "left"

		self.humanize = False
		self.jitter = False
		self.move_drop = False
		self.lock_coords = False

		self.use_count_limit = False
		self.use_time_limit = False
		self.count_limit = 0
		self.time_limit = 0.0
		self.start_time = 0.0

		self.target_x = 0
		self.target_y = 0
		self.hum_min = 0.8
		self.hum_max = 1.2
		self.drop_pct = 0.4

		self.master_switch = True

		self._thread: threading.Thread | None = None

	def update_settings(
		self,
		cps: float,
		button: str,
		humanize: bool,
		jitter: bool,
		move_drop: bool,
		lock_coords: bool,
		tx: int,
		ty: int,
		hum_min: float,
		hum_max: float,
		drop_pct: float,
		use_count_limit: bool,
		count_limit: int,
		use_time_limit: bool,
		time_limit: float,
		master_switch: bool,
	) -> None:
		self.cps = cps
		self.button = button
		self.humanize = humanize
		self.jitter = jitter
		self.move_drop = move_drop
		self.lock_coords = lock_coords
		self.target_x = tx
		self.target_y = ty
		self.hum_min = hum_min
		self.hum_max = hum_max
		self.drop_pct = drop_pct
		self.use_count_limit = use_count_limit
		self.count_limit = count_limit
		self.use_time_limit = use_time_limit
		self.time_limit = time_limit
		self.master_switch = master_switch

	def start(self) -> None:
		if self.is_running:
			return
		self.is_running = True
		new_thread = threading.Thread(target=self._click_loop, daemon=True)
		self._thread = new_thread
		new_thread.start()

	def stop(self) -> None:
		self.is_running = False
		if self._thread and self._thread.is_alive():
			self._thread.join(timeout=0.1)

	def _click_loop(self) -> None:
		delay = 1.0 / self.cps
		next_click = time.perf_counter() + delay
		last_pos = get_cursor_pos()
		clicks_done = 0

		while self.is_running:
			current_time = time.perf_counter()
			if current_time >= next_click:
				if self.use_time_limit and (current_time - self.start_time) >= self.time_limit:
					self.stop()
					break

				if self.use_count_limit and clicks_done >= self.count_limit:
					self.stop()
					break

				if self.lock_coords:
					set_cursor_pos(self.target_x, self.target_y)
				if self.jitter:
					cx, cy = get_cursor_pos()
					set_cursor_pos(cx + random.randint(-2, 2), cy + random.randint(-2, 2))

				send_click(self.button)
				clicks_done += 1

				current_pos = get_cursor_pos()
				active_cps = self.cps
				if self.move_drop and current_pos != last_pos:
					active_cps = max(1.0, self.cps * (1.0 - self.drop_pct))
				last_pos = current_pos

				base_delay = 1.0 / active_cps
				if self.humanize:
					delay = base_delay * random.uniform(self.hum_min, self.hum_max)
				else:
					delay = base_delay

				next_click = current_time + delay
