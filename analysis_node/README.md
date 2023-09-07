pip install -U pip requests

curl -k --user elastic:${ELASTIC_PASSWORD} https://localhost:9200/_data_stream

=> metricbeat-<STACK_VERSION> e.g. metricbeat-8.9.1