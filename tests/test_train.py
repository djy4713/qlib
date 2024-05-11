import qlib
from qlib.constant import REG_CN
qlib.init(provider_uri="/data/workspace/quantify/qlib_data/cn_data", region=REG_CN)
from qlib.contrib.data.handler import Alpha158
from qlib.data.dataset import TSDatasetH
from qlib.contrib.model.pytorch_alstm_ts import ALSTM

# 配置数据
train_period = ("2015-01-01", "2019-12-31")
valid_period = ("2020-01-01", "2020-12-31")
test_period = ("2021-01-01", "2022-03-01")

dh = Alpha158(instruments='sh000300', 
              start_time=train_period[0], 
              end_time=test_period[1],
              infer_processors={}
              
             )
ds = TSDatasetH(handler=dh,
                step_len=40, # 时间步数
                segments={"train": train_period, 
                          "valid": valid_period, 
                          "test": test_period})

# 配置模型
model = ALSTM(d_feat=158, 
              metric='mse', 
              rnn_type='GRU', 
              batch_size=800, 
              early_stop=10) # 其他参数使用默认设置


# 模型训练, 使用fit方法
model.fit(dataset=ds,
          save_path=None) # 保存模型的路径，默认存在当前路径

model.predict(dataset=ds, segment='test')