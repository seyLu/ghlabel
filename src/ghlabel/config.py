g_GHLABEL_DEBUG_MODE = False


def set_ghlabel_debug_mode(is_debug: bool) -> None:
    global g_GHLABEL_DEBUG_MODE  # noqa: PLW0603
    g_GHLABEL_DEBUG_MODE = is_debug


def is_ghlabel_debug_mode() -> bool:
    global g_GHLABEL_DEBUG_MODE  # noqa: PLW0602
    return g_GHLABEL_DEBUG_MODE
