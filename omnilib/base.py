_omnilib_initialized = False


def init():
    """Initialize the Omnilib Library!

    Calls initialization methods on various Omnilib components. `Init` should
    be called only once and with keyword arguments preferably.

    All arguments have safe defaults. Ordering of arguments subject to change
    without notice.
    """
    global _omnilib_initialized
    if _omnilib_initialized:
        return
    _omnilib_initialized = True

    # Initialization Code here
