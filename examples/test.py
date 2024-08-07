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

data_root="/data/workspace/quantify/qlib_data/cn_data/"
qlib.init(provider_uri=data_root, region=REG_CN)

def send_result(text):
    print("send_result:", text)
    data = {
        "msgtype": "text",
        "text": {
            "content": text
        }
    }
    json_data = json.dumps(data)
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c182e6ee-96b9-4b73-9144-1006a28dd48a"
    response = requests.post(url, data=json_data, headers={"Content-Type": "application/json"})
    print(f"send_result status_code:{response.status_code}")

if len(sys.argv) <= 2:
    print("usage python test.py $start_date $end_date")
    exit(0)
backtest_start_date = sys.argv[1]
backtest_end_date = sys.argv[2]

if len(sys.argv) > 3:
    if not is_workday(datetime.now()):
        print(f"{datetime.now()} is not workday")
        exit(0)
    file = "qlib_bin.tar.gz"
    file_url = f"https://github.com/chenditc/investment_data/releases/download/{backtest_end_date}/{file}"
    os.system(f"wget {file_url} .")
    if os.path.exists(file):
        os.system(f"rm -r {data_root}; mkdir -p {data_root}; mv {file} {data_root};")
        os.system(f"cd {data_root}; tar -xf {file}; mv qlib_bin/* .; rm -r qlib_bin")
    else:
        print(f"fatal error: {file_url} not found!!!")
        send_result(f"fatal error: {backtest_end_date} data not found!!!")
        exit(0)

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

def process_symbol(code):
    if code.startswith("SZ") or code.startswith("SH"):
        return code[2:]
    return code

global_stock_name = {}
def get_stock_name(code):
    global global_stock_name
    if code in global_stock_name:
        return global_stock_name[code]
    symbol = process_symbol(code)
    stock_info = ak.stock_individual_info_em(symbol)
    for row in stock_info.itertuples():
        # 你可以通过属性来访问行中的数据
        item = getattr(row, 'item')
        if item == "股票简称":
            global_stock_name[code] = getattr(row, 'value')
            return global_stock_name[code]
    return code

with R.start(experiment_name="test"):
    recorder = R.get_recorder()
    sr = SignalRecord(model, dataset, recorder)
    sr.generate()

    # Signal Analysis
    sar = SigAnaRecord(recorder)
    sar.generate()
    
    par = PortAnaRecord(recorder, port_analysis_config, "day")
    par.generate()

    path = f"logs/result/test_{backtest_end_date}.txt"
    fout = open(path, "w")
    positions = list(recorder.load_object("portfolio_analysis/positions_normal_1day.pkl").items())
    for timestamp, position in positions[-5:]:
        fout.write(f"\n----------------------  {timestamp} ----------------------\n")
        for key, value in position.position.items():
            if type(value) == dict:
                stock_name = get_stock_name(key)
                for k, v in value.items():
                    value[k] = "{:.4f}".format(float(v))
                fout.write(f"{key} {stock_name} {value}\n")
            else:
                value = "{:.4f}".format(value)
                fout.write(f"{key}:{value}\n")
    timestamp, position = positions[-1]
    date = timestamp.strftime("%Y-%m-%d")
    # url = "http://175.178.225.245:8080/save_predict_daily"
    # headers = {'Content-Type': 'application/json'}
    # data = {"date":date, "position":position.position}
    # response = requests.post(url, headers=headers, data=json.dumps(data)).json()
    print(f"send predict daily: {date} {position.position}")
    json.dump(position.position, open(f"logs/result/daily/{date}", "w"))
    
    fout.write("\n---------------------- tomorrow trade list  ----------------------\n")
    if len(positions) >= 2:
        new_position = positions[-1][1].position
        last_position = positions[-2][1].position
        for key, value in new_position.items():
            if type(value) != dict:
                continue
            stock_name = get_stock_name(key)
            if key not in last_position:
                 for k, v in value.items():
                    value[k] = "{:.4f}".format(float(v))
                 fout.write(f"buy {key} {stock_name} {value}\n")
                 continue
            last_value = last_position[key]
            if last_value['amount'] != value['amount']:
                for k, v in value.items():
                    value[k] = "{:.4f}".format(float(v))
                fout.write(f"ajust {key} {stock_name} {last_value}  --  {value}\n")
            
        for key, value  in last_position.items():
            if key not in new_position:
                stock_name = get_stock_name(key)
                for k, v in value.items():
                    print(k, v)
                    value[k] = "{:.4f}".format(float(v))
                fout.write(f"sell {key} {stock_name} {value}\n")
    fout.close()
    send_result(open(path).read())
    
