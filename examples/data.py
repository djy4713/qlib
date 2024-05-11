import qlib
from qlib.data import D
from qlib.constant import REG_CN
provider_uri = "/data/workspace/quantify/qlib_data/cn_data"
qlib.init(provider_uri=provider_uri, region=REG_CN)
from qlib.data.dataset.loader import QlibDataLoader

if __name__ == "__main__":
    instruments = ["SH603195", "SZ002493", "SH603501", "SZ000895", "SH600233"]
    # instruments = {'market': 'all', 'filter_pipe': []} 
    # fields = "$open,$close,$high,$low,$volume,$factor,$change".split(",") + ['$Ref($open, -1)']
    fields = ['$change', '$volume', '$close', '$open', '$factor']
    df = D.features(instruments, fields, start_time='2024-04-02', end_time='2024-04-03')
    print(df)

    # data_loader:
    #     class: QlibDataLoader
    #     kwargs:
    #         config:
    #             feature:
    #                 - ["Resi($close, 15)/$close", "Std(Abs($close/Ref($close, 1)-1)*$volume, 5)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 5)+1e-12)", "Rsquare($close, 5)", "($high-$low)/$open", "Rsquare($close, 10)", "Corr($close, Log($volume+1), 5)", "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 5)", "Corr($close, Log($volume+1), 10)", "Rsquare($close, 20)", "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 60)", "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 10)", "Corr($close, Log($volume+1), 20)", "(Less($open, $close)-$low)/$open"]
    #                 - ["RESI5", "WVMA5", "RSQR5", "KLEN", "RSQR10", "CORR5", "CORD5", "CORR10", "RSQR20", "CORD60", "CORD10", "CORR20", "KLOW"]
    #             label:
    #                 - ["Ref($close, -2)/Ref($close, -1) - 1"]
    #                 - ["LABEL0"]
    #         freq: day
    fields = ['Ref($open, -1)', '$change', '$volume', '$close', '$open', '$factor']
    data_loader_config = {
        "feature": fields,
    }
    data_loader = QlibDataLoader(config=data_loader_config)
    df = data_loader.load(instruments, start_time='2024-04-02', end_time='2024-04-03')
    df = df.swaplevel("instrument", "datetime").sort_index(level='instrument')
    print(df)
