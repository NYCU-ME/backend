FROM fluent/fluentd:v1.16.2-debian-1.1
USER root
RUN gem install elasticsearch -v 7.6
RUN gem install fluent-plugin-elasticsearch
RUN gem install fluent-plugin-rewrite-tag-filter
RUN gem install fluent-plugin-multi-format-parser
