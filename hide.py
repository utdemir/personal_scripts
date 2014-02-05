#!/usr/bin/env python3

import os
import re
import sys
import hashlib
import itertools
import functools

def invalid_arguments():
    print("Invalid arguments.", file=sys.stderr) # TODO: Usage
    sys.exit(1)

try:
    _, secrets_file, mode, *args = sys.argv
except ValueError:
    invalid_arguments()

if mode not in ("hide", "reveal", "ensure"):
    invalid_arguments()

args = set(map(os.path.abspath, args))

secrets_file = os.path.abspath(secrets_file)
args = args - {secrets_file} # To allow `./hide.py secrets lock *`

files = set(filter(os.path.isfile, args))
dirs = set(filter(os.path.isdir, args))

if len(files) + len(dirs) != len(args):
    invalid_arguments()

def list_files(dir):
    contents = [os.path.join(dir, i) for i in os.listdir(dir)]
    files = set(filter(os.path.isfile, contents))
    dirs = {i for i in contents if os.path.isdir(i) and not i.startswith(".")}

    yield from files
    yield from itertools.chain(*map(list_files, dirs))

all_files = files | set(itertools.chain(*map(list_files, dirs)))
from pprint import pprint

salt, *secrets = [i.strip() for i in open(secrets_file) if i.strip()]
secrets.sort(key=len, reverse=True)

def hash(secret, fname):
    key = "%s:%s:%s" % (salt, fname, secret)
    return "hidepy" + hashlib.sha256(key.encode()).hexdigest()

def replace_all(s, d):
    pat = re.compile("|".join(map(re.escape, d)))
    found = re.findall(pat, s)
    return (len(found), re.sub(pat, lambda i: d[i.group(0)], s))

for filepath in all_files:
    filename = os.path.basename(filepath)
    hashes = {i: hash(i, filename) for i in secrets}
    
    with open(filepath, "r") as f:
        content = f.read()
        c = 0
        if mode == "hide":
            c, content = replace_all(contents, hashes)
            if c: print("%s secrets hidden in %s." % (c, filename))
        elif mode == "reveal":
            c, content = replace_all(contents, {j: i for i, j in hashes.items()})
            if c: print("%s secrets revealed in %s." % (c, filename))
        elif mode == "ensure" and any(s in content for s in hashes):
            print("Error: '%s' contains a secret." % filename)
            sys.exit(1)
    if c:
        with open(filepath, "w") as f:
            f.write(content)
