import qlib
from qlib.constant import REG_CN
from qlib.utils import init_instance_by_config
qlib.init(provider_uri="/data/workspace/quantify/qlib_data/cn_data", region=REG_CN)

ds_config = {
    'class': 'TSDatasetH',
    'module_path': 'qlib.data.dataset',
    'kwargs': {
        'handler': {
            'class': 'Alpha158',
            'module_path': 'qlib.contrib.data.handler',
            'kwargs': {'start_time': "2015-01-01",
                'end_time': "2022-03-01",
                'fit_start_time': "2015-01-01",
                'fit_end_time': "2019-12-31",
                'instruments': 'sh000300',
                # 与之前的示例相比，这里新增了infer_processors和learn_processors
                'infer_processors': [
                    {
                        'class': 'RobustZScoreNorm',
                        'kwargs': {'fields_group': 'feature', 'clip_outlier': True}
                    },
                    {
                        'class': 'Fillna', 
                        'kwargs': {'fields_group': 'feature'}
                    }
                ],
                'learn_processors': [
                    {'class': 'DropnaLabel'},
                    # 对预测的目标进行截面排序处理
                    {'class': 'CSRankNorm', 'kwargs': {'fields_group': 'label'}}
                ],
                # 预测的目标
                'label': ['Ref($close, -1) / $close - 1']}},
        'segments': {
            'train': ["2015-01-01", "2019-12-31"],
            'valid': ["2020-01-01", "2020-12-31"],
            'test': ["2021-01-01", "2022-03-01"]
        },
        'step_len': 40
    }
}

model_config = {
    'class': 'ALSTM',
    'module_path': 'qlib.contrib.model.pytorch_alstm_ts',
    'kwargs': {
        'd_feat': 158,
        'hidden_size': 64,
        'num_layers': 2,
        'dropout': 0.0,
        'n_epochs': 200,
        'lr': '1e-3',
        'early_stop': 10,
        'batch_size': 800,
        'metric': 'loss',
        'loss': 'mse',
        'n_jobs': 20,
        'GPU': 0,
        'rnn_type': 'GRU'
    }
}

# 实例化数据集及模型
ds = init_instance_by_config(ds_config)
model = init_instance_by_config(model_config)

# 当然，也可以将配置写在外部文件里（如yaml）
# import yaml
# config = yaml.load(open('./workflow_config_alstm_Alpha158.yaml', 'rb'), Loader=yaml.FullLoader)

# 模型训练
model.fit(dataset=ds)