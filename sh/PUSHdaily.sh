#!/bin/bash
# Delete the LOG files
rm /tmp/push2ogn.log.old
rm /tmp/push2ogn.err.old
mv /tmp/push2ogn*.log /tmp/push2ogn.log.old
mv /tmp/push2ogn*.err /tmp/push2ogn.err.old
rm /tmp/push2*log
rm /tmp/push2*err
