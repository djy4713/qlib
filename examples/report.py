import qlib, json
import akshare as ak
from datetime import datetime
from qlib.constant import REG_CN
from qlib.workflow import R
from qlib.contrib.report import analysis_model, analysis_position
provider_uri = "/data/workspace/quantify/qlib_data/cn_data"  # target_dir
qlib.init(provider_uri=provider_uri, region=REG_CN)

ba_rid = "832677ee2bf34cdaa37a81d8177fe005"
recorder = R.get_recorder(recorder_id=ba_rid, experiment_name="test")
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

path = f"logs/result/test_2024-05-01.txt"
fout = open(path, "w")
positions = list(recorder.load_object("portfolio_analysis/positions_normal_1day.pkl").items())
for timestamp, position in positions:
    date = timestamp.strftime("%Y-%m-%d")
    print(f"send predict daily: {date} {position.position}")
    json.dump(position.position, open(f"logs/result/daily/{date}", "w"))

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

    