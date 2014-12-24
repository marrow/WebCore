#!/bin/bash
set -e
set -x

export LC_CTYPE=en_US.UTF-8
export TZ=UTC

tox
