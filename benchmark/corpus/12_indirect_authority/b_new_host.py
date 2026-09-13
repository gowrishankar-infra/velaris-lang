# Sends a receipt through a mail library; the program names no host itself.
import sys

import mailer

to = sys.stdin.readline().strip()
print(mailer.send(to, "Your receipt: 2 items, 450"))
