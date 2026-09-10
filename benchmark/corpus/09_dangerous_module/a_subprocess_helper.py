# A helper named like a text utility runs a shell command.
import subprocess


def tidy(text):
    return subprocess.getoutput("echo " + text)  # DANGER


print(tidy("spawned-child-ran"))
