Collectd rrd graphs examples
============================

This is not a library. This is just a module which contains set of example rrd graphs generators for some standard collectd plugins.

Additionally it contains my pyrrd backend which handles localization (legend on graphs are translated).

# Installation
As it is not an real python library `setup.py` is missing. If you want to try my generators you should clone this repo and install dependencies (probably in virtualenv):

$ pip install -r REQUIREMENTS

# Usage
You can generate graphs with provided module:

$ python graphs.py --help

# Examples

Lets assume that my rrd bases are in `./rrd/host1` directory:

    $ python graphs.py cpu --rrd-dir=./rrd/host1/cpu-0 --locale='pl_PL' --end='2013-03-28' -o cpu.png

![CPU graph](paluh.github.com/collectd-rrd-graphs-in-python/examples/cpu.jpg)


    $ python graphs.py load --rrd-dir=./rrd/host1/load --locale='pl_PL' --end='2013-03-28' -o load.png

![CPU graph](paluh.github.com/collectd-rrd-graphs-in-python/examples/load.jpg)


    $ python graphs.py memory --rrd-dir=./rrd/host1/memory --locale='pl_PL' --end='2013-03-28' -o memory.png

![CPU graph](paluh.github.com/collectd-rrd-graphs-in-python/examples/memory.jpg)


    $ python graphs.py disk --rrd-dir=./rrd/host1/disk-xvda2 --locale='pl_PL' --end='2013-03-28' --logarithmic -o disk.png && gqview disk.png

![CPU graph](paluh.github.com/collectd-rrd-graphs-in-python/examples/disk.jpg)
