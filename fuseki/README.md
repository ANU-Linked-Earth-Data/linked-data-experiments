# Fuseki install and run scripts

To install and run Fuseki, use `./run-fuseki`. This script will probably only
work on Linux, and requires Java 8 to run (Ubuntu users: `sudo apt-get install
openjdk-8-{jdk,jre}`).

You can query Fuseki by going to [localhost:3030](http://localhost:3030/) and
using the web console, or by using the `soh` binary (if you've run
`./run-fuseki`, you'll have a symlink to it in this directory). For example:

```sh
SERVICE=http://localhost:3030/accidents
QUERY='SELECT ?a ?b ?c WHERE { ?a ?b ?c } LIMIT 10'
./soh put "$SERVICE" default ../data/accidents.rdf
./soh query --output=tsv --service="$SERVICE" "$QUERY"
```
