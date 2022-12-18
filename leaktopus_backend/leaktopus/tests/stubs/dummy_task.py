class DummyTask:
    def __init__(self, override_methods={}):
        self.override_methods = override_methods

    def run(self, **kwargs):
        return (
            self.override_methods["run"]() if "run" in self.override_methods else None
        )
