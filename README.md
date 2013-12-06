personal_scripts
================

A repository for my personal scripts. Those scripts aren't documented, but feel free to ask me anything about them.

hide.py
-------

The script I created for publishing these scripts stripped from my personal informations.

It reads a list of passwords from an hidden file, and replaces them with their hashes.

Inspired by [halitalptekin/doorman](https://github.com/halitalptekin/doorman/).


tpb_fetcher.py
--------------

It searchs The Pirate Bay(using apify.ifc0nfig.com/) for the latest episodes of TV series I follow
and lists them with their magnet links. I periodically run
```bash
for i in $(python tpb_fetcher.py | grep magnet | xargs); do deluge-console add $i; done
```
to download them with Deluge.


