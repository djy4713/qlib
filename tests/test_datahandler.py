# 实现一个自定义的特征集，MACD、RSI

from qlib.data.dataset.handler import DataHandlerLP

class MyFeatureSet(DataHandlerLP):
    def __init__(self,
                 instruments="sh000300", 
                 start_time=None,
                 end_time=None,
                 freq="day",
                 infer_processors=[],
                 learn_processors=[],
                 fit_start_time=None,
                 fit_end_time=None,
                 process_type=DataHandlerLP.PTYPE_A,
                 filter_pipe=None,
                 inst_processor=None,
                 **kwargs,
                ):
        data_loader = {
            "class": "QlibDataLoader",
            "kwargs": {
                "config": {
                    "feature": self.get_feature_config(),
                    "label": kwargs.get("label", self.get_label_config()), # label可以自定义，也可以使用初始化时候的设置
                },
                "filter_pipe": filter_pipe,
                "freq": freq,
                "inst_processor": inst_processor,
                },
            }
        super().__init__(
            instruments=instruments,
            start_time=start_time,
            end_time=end_time,
            data_loader=data_loader,
            infer_processors=infer_processors,
            learn_processors=learn_processors,
            process_type=process_type,
        )
        
    def get_feature_config(self):
        
        MACD = '(EMA($close, 12) - EMA($close, 26))/$close - EMA((EMA($close, 12) - EMA($close, 26))/$close, 9)/$close'
        RSI = '100 - 100/(1+(Sum(Greater($close-Ref($close, 1),0), 14)/Count(($close-Ref($close, 1))>0, 14))/ (Sum(Abs(Greater(Ref($close, 1)-$close,0)), 14)/Count(($close-Ref($close, 1))<0, 14)))'
        
        return [MACD, RSI ], ['MACD', 'RSI']

    def get_label_config(self):
        return (["Ref($close, -1)/$close - 1"], ["LABEL"])

# 初始化的过程中已经完成的数据的load
my_feature = MyFeatureSet(instruments='sh000300', start_time='2021-01-01', end_time='2021-06-30')

# my_feature.get_feature_config()
my_feature.fetch() # my_feature.fetch(col_set='feature') / my_feature.fetch(col_set='label')