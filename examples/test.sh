#!/usr/bin/env bash
cd $(dirname $0)
start_date="2024-05-10"
end_date=`date -d "yesterday" +%F`
/root/anaconda3/envs/qlib/bin/python test.py $start_date $end_date 1 1>logs/test_${end_date}.txt 2>&1;

cd /data/workspace/quantify/online
git add . --all
git commit -m'update qlib predict daily'
git push

