# settings 3.1.0: reads the settings file.


def load():
    try:
        with open("{granted}/notes.txt") as f:
            return f.read()
    except OSError:
        return "defaults"
