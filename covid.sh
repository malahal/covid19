#!/bin/bash

python3 covid-india.py --savefig covid19-india-data.csv
git add covid19-india-data.csv
git diff-index --quiet HEAD || git add covid19-india-total.png covid19-india-new.png covid19-states-total.png covid19-states-new.png && git commit -m 'script auto'
git push origin master
