import logging
from typing import Callable, List, Tuple

from btc_wallet.application_context import ApplicationContext
from btc_wallet.util import Modes, get_keypress, on_shutdown, print_with_theme


def generic_menu(
    menu_options: List[Tuple[str, Callable]],
    menu_name,
    menu_description="",
) -> int:
    """
    Displays a generic menu with the given options and menu name.
    User selects an option and the corresponding function is called.
    """
    t = ApplicationContext.get_terminal()
    mode = ApplicationContext.get_mode()
    selected_option_index = 0

    with t.fullscreen(), t.cbreak(), t.hidden_cursor():
        while True:
            print_with_theme(t, t.clear)
            print_with_theme(t, "*" * t.width)
            print_with_theme(
                t,
                t.bold(f" {menu_name} - ({mode.value.upper()} MODE)"),
            )
            print_with_theme(t, "*" * t.width)
            if mode == Modes.TEST:
                print_with_theme(
                    t,
                    t.red(
                        " WARNING: You are in TESTNET mode. This mode is only for testing and using test bitcoin. Do not enter real bitcoin addresses or send real bitcoin!"
                    ),
                )
            elif mode == Modes.PROD:
                print_with_theme(
                    t,
                    t.green(
                        " WARNING: You are in MAINNET mode. Do NOT enter testnet addresses. Be careful with real bitcoin!"
                    ),
                )
            if menu_description != "":
                print_with_theme(t, menu_description)
                print_with_theme(t, "*" * t.width)
            for i, option in enumerate(menu_options):
                if i == selected_option_index:
                    print_with_theme(
                        t, t.bold_reverse(" > " + option[0])
                    )  # Highlight the selected option
                else:
                    print_with_theme(t, " " + option[0])

            with t.location(0, t.height - 1):
                print_with_theme(
                    t, " Use arrow keys to navigate, ENTER to select, and Q to quit."
                )

            key = get_keypress(t)

            if key.name == "KEY_UP":
                selected_option_index = max(0, selected_option_index - 1)
            elif key.name == "KEY_DOWN":
                selected_option_index = min(
                    len(menu_options) - 1, selected_option_index + 1
                )
            elif key.name == "KEY_ENTER":
                # execute the function corresponding to the selected option
                func = menu_options[selected_option_index][1]
                logging.info(menu_options[selected_option_index][0])
                func()
                if selected_option_index == len(menu_options) - 1:
                    break  # Exit the menu loop if the last option is selected
            elif key.lower() == "q":
                on_shutdown(t)
            elif not key:  # timeout
                logging.warn("Logging out due to inactivity")
                on_shutdown(t)
