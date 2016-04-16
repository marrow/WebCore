#!/bin/bash
set -e
set -x

git config --global user.email "alice+travis@gothcandy.com"
git config --global user.name "Travis: Marrow"

pip install --upgrade 'setuptools<18.5' pip pytest
pip install tox tox-travis codecov

