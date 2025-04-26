class NFA:
    def __init__(self):
        self.patterns = []
        self.max_len = 0

    def add_pattern(self, pattern, label):
        self.patterns.append((pattern, label))
        self.max_len = max(self.max_len, len(pattern))

    def check(self, event_series):
        matches = []
        for pattern, label in self.patterns:
            pattern_len = len(pattern)
            if len(event_series) >= pattern_len:
                window = event_series[-pattern_len:]
                if self._matches(window, pattern):
                    matches.append(label)
        return matches

    def _matches(self, window, pattern):
        if len(window) != len(pattern):
            return False
        for w, p in zip(window, pattern):
            if w != p:
                return False
        return True
