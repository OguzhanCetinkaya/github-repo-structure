from git import RemoteProgress

class CloneProgress(RemoteProgress):
    """
    A custom progress handler that integrates GitPython's clone progress
    with the alive-progress library.
    """
    def __init__(self):
        super().__init__()
        self._bar = None

    def set_bar(self, bar):
        """
        Store a reference to an alive_bar so we can update it in `update()`.
        """
        self._bar = bar

    def update(self, op_code, cur_count, max_count=None, message=''):
        """
        Called by GitPython for each progress update.
        :param op_code: A numeric code describing the type of operation.
        :param cur_count: The current item count or bytes.
        :param max_count: The maximum item count or bytes (may be None).
        :param message: A progress message from git (may be empty).
        """
        # If the bar exists, simply increment or set a position.
        # Because max_count can be None, we typically do an "indefinite" bar.
        if self._bar:
            # Indefinite approach: just call bar() to increment by 1 each time
            self._bar()
        
        # Optional: print Git messages if you want more detail
        if message:
            print(message)
