# Virtuoso install scripts

To install and run Virtuoso, use `./run-virtuoso.sh`. This script will probably
only work on Linux, and requires the following Virtuoso build dependencies:

* `autoconf`
* `automake`
* `libtool`
* `flex`
* `bison`
* `gperf`
* `gawk`
* `m4`
* `OpenSSL`

If you're using Ubuntu, then you'll probably have to install the `-dev` versions
of those packages, as well as `build-essential`. Heck, `build-essential` is
probably *all* you need.
