from rapid_cloud.configuration_handler import log_to_console
import curses
import time


class TerminalInterface:
    def __init__(self, ongoing_tasks=None):
        self.tasks = ongoing_tasks
        self.transfer_finished = False
        self.std_scr = None
        self.transfer_direction = None
        self.number_of_fragments = None

    def setup_terminal_interface(self):
        self.std_scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.std_scr.addstr(0, 0, "Starting {} of {} fragments -> \n".format(self.transfer_direction,
                                                                             str(self.number_of_fragments)))

    def teardown_terminal_interface(self):
        curses.echo()
        curses.nocbreak()
        curses.endwin()

    def refresh_ongoing_tasks(self, arrow):
        self.transfer_finished = True
        for task in self.tasks:
            task_id = self.tasks.index(task) + 1
            if not task.finish:
                self.transfer_finished = False
                self.std_scr.addstr(task_id, 0,
                                    "FRAGMENT_[{}] {} {}_{} ----------------------- [{} in progress]\n".format(
                                        task_id, arrow, task.provider, task.provider_id, self.transfer_direction),
                                    curses.color_pair(1))
            else:
                self.std_scr.addstr(task_id, 0,
                                    "FRAGMENT_[{}] {} {}_{} ----------------------- [{} finished]\n".format(
                                        task_id, arrow, task.provider, task.provider_id, self.transfer_direction),
                                    curses.color_pair(2))

    def show_ongoing_tasks(self, transfer_direction, frag_number):
        self.transfer_direction = transfer_direction
        self.number_of_fragments = frag_number
        try:
            self.setup_terminal_interface()
            if transfer_direction == "upload":
                arrow = "---->"
            else:
                arrow = "<----"
            while True:
                try:
                    self.refresh_ongoing_tasks(arrow)
                    if self.transfer_finished:
                        time.sleep(0.5)
                        break
                    self.std_scr.refresh()
                    time.sleep(0.2)
                except curses.error:
                    self.teardown_terminal_interface()
                    log_to_console("Maximize terminal to see ongoing tasks")
                    time.sleep(3)
                    self.setup_terminal_interface()
        finally:
            self.teardown_terminal_interface()
