import curses
import dataclasses

from . import tmux


@dataclasses.dataclass(frozen=False)
class Box:
    value = None


class Selection:
    def __init__(
        self,
        options: tuple[str, ...],
    ) -> None:
        self._options = options
        self._curr_index = 0
        self._filter_text = ""

    @property
    def options(self) -> tuple[str, ...]:
        if not self._filter_text:
            return self._options

        return tuple(
            option
            for option in self._options
            if self._filter_text in option.lower()
        )

    @property
    def selected_index(self) -> int:
        return self._curr_index

    @property
    def selected_option(self) -> str:
        return self.options[self._curr_index]

    def move_up(self) -> None:
        if self._curr_index > 0:
            self._curr_index -= 1

    def move_down(self) -> None:
        if self._curr_index < len(self.options) - 1:
            self._curr_index += 1

    def add_filter_char(self, char: str) -> None:
        selected_index = self._curr_index
        self._update_filter(self._filter_text + char.lower())

    def remove_filter_char(self) -> None:
        if self._filter_text:
            self._update_filter(self._filter_text[:-1])

    @property
    def filter_text(self) -> str:
        return self._filter_text

    def _update_filter(self, new_filter: str) -> None:
        originally_selected = self.selected_option
        original_filter = self._filter_text

        self._filter_text = new_filter

        new_options = self.options
        if not new_options:
            self._filter_text = original_filter
        elif new_filter in originally_selected.lower():
            self._curr_index = new_options.index(originally_selected)
        else:
            self._curr_index = 0


def choose(
    choices: list[tmux.Session],
) -> tmux.Session | None:
    box = Box()

    def low_level_main(stdscr: curses.window) -> None:
        box.value = _main_loop(
            stdscr=stdscr,
            choices=choices,
        )

    curses.wrapper(low_level_main)

    return box.value


def _main_loop(
    *,
    stdscr: curses.window,
    choices: list[tmux.Session],
) -> tmux.Session | None:
    name_to_session = {session.name: session for session in choices}

    selection = Selection(
        options=tuple(name_to_session),
    )

    curses.curs_set(0)  # Hide cursor

    while True:
        stdscr.clear()

        filter_text = "Filter: " + (selection.filter_text or "(no filter)")
        stdscr.addstr(0, 0, filter_text)
        offset = 2

        for i, session_name in enumerate(selection.options):
            extra_args = [curses.A_REVERSE] if i == selection.selected_index else []
            stdscr.addstr(i + offset, 0, session_name, *extra_args)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            selection.move_up()
        elif key == curses.KEY_DOWN:
            selection.move_down()
        elif key in [curses.KEY_ENTER, 10, 13]:
            return name_to_session[selection.selected_option]
        elif key == 27:  # ESC key
            return None
        elif key in (curses.KEY_BACKSPACE, 127):
            selection.remove_filter_char()
        elif 32 <= key <= 126:
            selection.add_filter_char(chr(key))
        else:
            pass  # Ignore other keys
