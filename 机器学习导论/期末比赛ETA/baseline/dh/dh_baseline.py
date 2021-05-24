from dh_libs import *

# 文件参数
train_gps_path = './data/train0523.csv'
test_data_path = './data/A_testData0531.csv'
order_data_path = './data/loadingOrderEvent.csv'
port_data_path = './data/port.csv'
# LGB参数
params = {
    'learning_rate': 0.01,
    'boosting_type': 'gbdt',
    'objective': 'regression',
    'num_leaves': 36,
    'feature_fraction': 0.6,
    'bagging_fraction': 0.7,
    'bagging_freq': 6,
    'seed': 8,
    'bagging_seed': 1,
    'feature_fraction_seed': 7,
    'min_data_in_leaf': 20,
    'nthread': 8,
    'verbose': 1,
}
clf = None
label = 'label'
seed=1080 
is_shuffle=True


# 其他参数
NDATA = 1000 # 一次读NDATA行
Thresold = 1*NDATA # 总共要读多少行
VALIDDATA = 1000 # 数据量过少会有问题，经过测试10w好像还可以,保险起见用100w
weight = float(NDATA)/Thresold


if __name__ == "__main__":
    # client = Client(n_workers=8)
    # print(client)


    # baseline只用到gps定位数据，即train_gps_path
    test_data = pd.read_csv(test_data_path)
    test_data = get_data(test_data, mode='test') # 预处理测试数据
    test = get_feature(test_data, mode='test')
    test_pred = np.zeros((test.shape[0], ))


    reader = pd.read_csv(train_gps_path, iterator = True)
    # 读取一部分训练集作为测试集
    valid_data = reader.get_chunk(VALIDDATA)
    valid_data = set_data_columns(valid_data)
    valid_data = get_data(valid_data,mode='valid')
    valid = get_feature(valid_data,mode='valid')
    valid_pred = np.zeros((valid.shape[0], ))


    summ = 0
    while summ <= Thresold:
        summ += NDATA

        batch_data = reader.get_chunk(NDATA)
        batch_data = set_data_columns(batch_data)
        batch_data = get_data(batch_data, mode = 'train')
        batch_train = get_feature(batch_data, mode='train')

        features = [c for c in batch_train.columns if c not in ['loadingOrder', 'label', 'mmin', 'mmax', 'count']]
        pred = features

        train_pred = np.zeros((batch_train.shape[0], ))
        n_splits = 5
        # Kfold
        fold = KFold(n_splits=n_splits, shuffle=is_shuffle, random_state=seed)
        kf_way = fold.split(batch_train[pred])
        
        # train
        for n_fold, (train_idx, valid_idx) in enumerate(kf_way, start=1):
            train_x, train_y = batch_train[pred].iloc[train_idx], batch_train[label].iloc[train_idx]
            valid_x, valid_y = batch_train[pred].iloc[valid_idx], batch_train[label].iloc[valid_idx]
            # 数据加载
            n_train = lgb.Dataset(train_x, label=train_y)
            n_valid = lgb.Dataset(valid_x, label=valid_y)

            clf = lgb.train(
                params=params,
                train_set=n_train,
                num_boost_round=3000,
                valid_sets=[n_valid],
                early_stopping_rounds=100,
                verbose_eval=100,
                feval=mse_score_eval,
                init_model=clf,
                keep_training_booster = True,
            )
            
            test_pred += clf.predict(test[pred], num_iteration=clf.best_iteration)*weight/fold.n_splits
            valid_pred += clf.predict(valid[pred], num_iteration=clf.best_iteration)*weight/fold.n_splits



    test['label'] = test_pred
    result = test[['loadingOrder', 'label']]


    test_data = test_data.merge(result, on='loadingOrder', how='left')
    test_data['ETA'] = (test_data['onboardDate'] + test_data['label'].apply(lambda x:pd.Timedelta(seconds=x))).apply(lambda x:x.strftime('%Y/%m/%d  %H:%M:%S'))
    test_data.drop(['direction','TRANSPORT_TRACE'],axis=1,inplace=True)
    test_data['onboardDate'] = test_data['onboardDate'].apply(lambda x:x.strftime('%Y/%m/%d  %H:%M:%S'))
    test_data['creatDate'] = pd.datetime.now().strftime('%Y/%m/%d  %H:%M:%S')
    test_data['timestamp'] = test_data['temp_timestamp']
    

    # 整理columns顺序
    result = test_data[['loadingOrder', 'timestamp', 'longitude', 'latitude', 'carrierName', 'vesselMMSI', 'onboardDate', 'ETA', 'creatDate']]
    result.to_csv('result.csv', index=False)
    # print(result)


    valid['pred_increase_ETA'] = valid_pred
    val = valid[['loadingOrder','pred_increase_ETA','label']]
    valid_data = valid_data.merge(val,on='loadingOrder', how='left')
    valid_data = valid_data[['loadingOrder','label','pred_increase_ETA']]
    valid_data.to_csv('valid.csv',index = False)
   
    mse = mean_squared_error(valid_data['label'],valid_data['pred_increase_ETA'])
   
    print(valid_data)
    print()
    print("valid_mse=",mse/3600**2,"h^2")

