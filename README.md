# Experiments with linked data

This repository contains some data munging scripts and Elda/Virtuoso
configurations for playing with linked data. The dataset in `data/` was taken
from a COMP1040 assignment in S2 2015, which was in turn derived from ACT police
traffic account on Twitter (possibly amongst other sources).

## `make_rdf.py`

To convert the accident data into RDF, use `make_rdf.py`. This script has some
dependencies (see `requirements.txt`). If you have `virtualenv`, you can easily
run the script using:

```bash
$ virtualenv -p "$(which python3)" env
$ . env/bin/activate
$ pip install -r requirements.txt
$ ./make_rdf.py
$ # with Fuseki running already
$ fuseki/soh put 'http://localhost:3030/accidents' default data/accidents.ttl
```
