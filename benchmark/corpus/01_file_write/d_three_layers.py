# The write sits three calls down: main -> report -> render -> store.
import sys


def store(path, text):
    open(path, "w").write(text)  # DANGER


def render(path, total):
    text = "total %d" % total
    store(path, text)
    return text


def report(path, amounts):
    return render(path, sum(amounts))


path = sys.stdin.readline().strip()
print(report(path, [2500, 45000, 12000]))
