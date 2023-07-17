
## Stack

### Overview

### Components

- collectd: collect metrics from the host/node
- collectd_exporter: receive collectd data and expose them in a Prometheus format
- prom_node_exporter: collect metrics from the host/node and expose them in a Prometheus format
- fluent_bit: collect metrics from host and from Docker and expose them in a Prometheus format
- prometheus: scrape targets exposing metrics and store them in a local database
- grafana: expose nice dashboards of data residing in prometheus DB


### Overlap
There is functional overlap between collectd, prom_node_exporter and the node_exporter input of fluent_bit. All of them are exporting host metrics. Unfortunately, there is no silver bullet. 

The node_exporter of fluent_bit is for now more limited than prom_node_exporter.

Prom_node_exporter is for now more limited than collectd plus there is no official Docker image for ARM plus it is not clear wether it is a good idea to run it within a container.

Collectd is for instance the single system which can collect metrics about an individual process. But on another hand, collectd does not have an official Docker image and its exporter has no ARM Docker image. 

## Deployment

Confirm that you can live without collectd and Prometheus node exporter. If so, you can deploy the stack with docker-compose simply, and without the collectd_exporter and prom_node_exporter containers.

If you need prom_node_exporter, it is simply a matter of keeping it in docker-compose.

If you need collectd, you have to keep collectd_exporter in docker-compose + install collectd on the host + place collectd.conf manually at the right place (/etc/collectd/collectd.conf).
