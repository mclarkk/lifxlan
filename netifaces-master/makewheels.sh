#!/bin/bash

for bindir in /opt/python/*/bin; do
    "$bindir/pip" wheel /netifaces/ -w wheelhouse/
done

for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /netifaces/wheelhouse/
done
