from datetime import datetime


def info(text, main="undefined"):

    message = text
    main = main
    start = "\033[94m"
    end = "\033[0m"
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    name = "INFO"
    dt = datetime.now().strftime(dt_fmt)
    esc = f"\x1b[30;1m{dt}\x1b[0m"
    colors = {
        "grey": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
    }
    send_color = lambda n, m: f"[{colors[n]}m{m}[0m"

    print()
    print(f"{esc} {start}{name:<8}{end} {send_color('magenta', main)} {message}")
    print()
