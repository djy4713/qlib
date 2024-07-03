# -*- coding: utf-8 -*-
import json, os
import akshare as ak
from datetime import datetime
import qlib, yaml, sys, requests
from qlib.workflow import R
from qlib.constant import REG_CN
from chinese_calendar import is_workday
from qlib.utils import init_instance_by_config
from qlib.workflow.record_temp import SignalRecord, PortAnaRecord, SigAnaRecord
qlib.init(provider_uri="/data/workspace/quantify/qlib_data/cn_data", region=REG_CN)

backtest_start_date = sys.argv[1]
backtest_end_date = sys.argv[2]

config = yaml.load(open('test.yaml', 'rb'), Loader=yaml.FullLoader)
config['filter']['filter_end_time'] = backtest_end_date
config['data_handler_config']['end_time'] = backtest_end_date
print(config['data_handler_config'])

port_analysis_config = config['port_analysis_config']
port_analysis_config['backtest']['start_time'] = backtest_start_date
port_analysis_config['backtest']['end_time'] = backtest_end_date
port_analysis_config['backtest']['account'] = 100000
port_analysis_config['strategy']['kwargs']['topk'] = 5
port_analysis_config['strategy']['kwargs']['n_drop'] = 1

dataset_config = config['task']['dataset']
dataset_config['kwargs']['segments']['valid'][1] = backtest_end_date
dataset_config['kwargs']['segments']['test'][1] = backtest_end_date

ba_rid = "3c8fc03ac4554bf6980c3bd8a5f53cba"
recorder = R.get_recorder(recorder_id=ba_rid, experiment_name="workflow")
model = recorder.load_object("params.pkl")
dataset = init_instance_by_config(dataset_config)

with R.start(experiment_name="test"):
    recorder = R.get_recorder()
    sr = SignalRecord(model, dataset, recorder)
    sr.generate()

    # Signal Analysis
    sar = SigAnaRecord(recorder)
    sar.generate()
    
    par = PortAnaRecord(recorder, port_analysis_config, "day")
    par.generate()
    
