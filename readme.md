# Stack Bruteforce Tool

Small script for bruteforcing stack canary, saved rbp and return addr byte-by-byte.
It connect many time to target program and guess next byte until program not crash.

## How to use

1. run your vulnerable server on localhost:1337
2. edit HOST/PORT/OFFSET if not same
3. run:

    python3 brute.py

Script will print canary, ebp and ret when finish.

## Note

This work only if program give different response when byte is good. 
If not, you need other leak or side channel.
