import logging
from typing import Any, Callable, List, Tuple

from btc_wallet.application_context import ApplicationContext
from btc_wallet.util import Modes, get_keypress, on_shutdown, print_with_theme


def generic_menu(
    menu_options: List[Tuple[str, Callable, Tuple[Any, ...]]],
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
            display_menu(
                t,
                menu_name,
                mode,
                menu_description,
                menu_options,
                selected_option_index,
            )

            key = get_keypress(t)

            selected_option_index = handle_keypress(
                t, key, selected_option_index, menu_options
            )

            if selected_option_index == -1:
                break
            if key.name == "KEY_ENTER":
                if execute_option(selected_option_index, menu_options):
                    break  # Exit the menu loop if the last option is selected
            elif not key:  # timeout
                logging.warn("Logging out due to inactivity")
                on_shutdown(t)
                break


def display_menu(
    t, menu_name, mode, menu_description, menu_options, selected_option_index
):
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


def execute_option(selected_option_index, menu_options):
    """Executes the selected menu option."""
    try:
        func = menu_options[selected_option_index][1]
        logging.info("Selected: " + menu_options[selected_option_index][0])
        func()
        return selected_option_index == len(menu_options) - 1
    except Exception as e:
        logging.error(
            f"Error executing option '{menu_options[selected_option_index][0]}': {e}"
        )
        return False


def handle_keypress(term, key, selected_option_index, menu_options):
    """Handles the keypress event."""
    if key.name == "KEY_UP":
        selected_option_index = (selected_option_index - 1) % len(menu_options)
    elif key.name == "KEY_DOWN":
        selected_option_index = (selected_option_index + 1) % len(menu_options)
    elif key.name == "KEY_ENTER":
        return selected_option_index
    elif key.lower() == "q":
        on_shutdown(term)
    return selected_option_index
