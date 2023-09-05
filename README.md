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

## Howto

### Start the stack on a `monitored_node`

Retrieve source code (git clone, curl a zip release, ...).

Adjust the metricbeat image depending on your node architecture (and upgrade if you wish) in `monitored_node/docker-compose.yml`

Run the docker-compose stack:
```
cd monitored_node
docker compose -p bench up -d
```

Metricbeat recorded data will be placed in an `output` subfolder, and compressed by `compactor` in an `output/compressed` subfolder.

### How-to do that if `monitored_node` has no Internet access

It is not straightforward under all situations. In our case, we simply get the SD Card from the Pi Zero and plug
it to another Pi (3/4/...) with Internet access. Then we retrieve what is needed (source code + Docker image) and 
re-plug the SD Card back into the Pi Zero.