#!/usr/bin/env python3

import os
import sys
import hashlib
import itertools
import functools

def invalid_arguments():
    print("Invalid arguments.", file=sys.stderr) # TODO: Usage
    sys.exit(1)

try:
    _, secrets_file, mode, *files = sys.argv
except ValueError:
    invalid_arguments()

if mode not in ("hide", "reveal"):
    invalid_arguments()

secrets_file = os.path.abspath(secrets_file)

files = list(map(os.path.abspath, files))
if not all(map(os.path.isfile, files)):
    invalid_arguments()

files = set(files) - {secrets_file} # To allow `./hide.py secrets lock *`

salt, *secrets = [i.strip() for i in open(secrets_file) if i.strip()]

def hash(secret, fname):
    key = "%s:%s:%s" % (salt, fname, secret)
    return "hidepy" + hashlib.sha256(key.encode()).hexdigest()

for filepath in files:
    filename = os.path.basename(filepath) 
    hashes = [(i, hash(i, filename)) for i in secrets] 
    with open(filename, "r") as f:
       contents = f.read()
       for s, h in hashes:
           if mode == "hide":
               contents = contents.replace(s, h)
           elif mode == "reveal":
               contents = contents.replace(h, s)
    with open(filename, "w") as f:
       f.write(contents)
