#!/bin/bash
echo " " >> /etc/rsyslog.conf
echo "# Forward messages to localhost:{{ fluentd_demsg_port }} for fluentd" >> /etc/rsyslog.conf
echo "*.info;mail.none;authpriv.none;cron.none               @127.0.0.1:{{ fluentd_demsg_port }}" >> /etc/rsyslog.conf

systemctl restart rsyslog