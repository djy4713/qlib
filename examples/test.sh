#!/usr/bin/env bash
cd $(dirname $0)
pwd=`pwd`
start_date="2024-05-10"
end_date=`date +%F`
root="/data/workspace/quantify/qlib_data/cn_data/"
file="qlib_bin.tar.gz"
rm -r $root; mkdir -p $root; cd $root; 
wget https://github.com/chenditc/investment_data/releases/download/$end_date/$file .
tar -xvf $file; mv qlib_bin/* .; rm -r qlib_bin
cd $pwd; /root/anaconda3/envs/qlib/bin/python test.py $start_date $end_date 1>logs/test_${end_date}.txt 2>&1;

