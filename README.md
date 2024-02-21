# Consistency and Isolation for Python Programmers

Files related to A. Jesse Jiryu Davis's PyCon 2023 talk. [Blog post with links to video and a podcast interview](https://emptysqua.re/blog/pycon-2023-consistency-isolation/).

Requires Python 3.10+.

Run the server like: `python no_isolation/db.py`. (Substitute whichever variant of the server you
want to run.)

Interact with the server using Telnet:
```
> brew install telnet
> telnet localhost
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Welcome to no_isolation/db.py!
Type 'bye' to quit.
db> get foo
not found
db> set foo 1
db> get foo
1
db> bye
Connection closed by foreign host.
```
