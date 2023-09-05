# Benchmarking

## Purpose

This project is a benchmarking solution to:
- record system and docker metrics on a small node without Internet connectivity
  - this node is named `monitored_node` for simplicity is the rest of the documentation
- exploit those metrics on another node with nice dashboard
  - this node is named `analysis_node` for simplicity is the rest of the documentation

Our use-case is to record monitoring data on a Pi Zero (`monitored_node`) running our offpost,
while performing various activities on the web interface (browse Zims, ...). Since the Pi Zero 
is used as a Hotspot (i.e. no Internet and very limited network connectivity) and has limited 
computing power, we need a stack which is lightweight and capable to record data for further analysis
on any other machine with bigger CPU / RAM (`analysis_node`). We also need this architecture to limit
the impact of the monitoring stack on the monitored device.

## Overview

Elastic `metricbeat` has been selected to record system and docker activity. It has the advantage
to be able to output recorded data in `ndjson` files, 

We had to compliment the `monitored_node` with a `compactor` which is responsible to compact rotated
`ndjson` files. Elastic `metricbeat` is capable to rotate files but does not compact rotated ones automatically.
These files are however very good candidates for compaction, achieving up to x10 compaction rate with default
GZip compaction.