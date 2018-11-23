from pymonad.Maybe import Nothing


def nothing_with_message(message: str) -> Nothing:
    print(message)
    return Nothing

