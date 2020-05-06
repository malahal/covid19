#!/bin/bash

python3 covid-india.py --savefig covid19-india-data.csv
git add covid19-india-data.csv covid19-india-total.png covid19-india-new.png
git diff-index --quiet HEAD || git commit -m 'script auto'
git push origin master
