from dh_libs import *


# 使用地理库计算平均距离，并清洗掉速度过大的，估计是坐标漂移
def speed_wash(max_speed,mode='train'):
    assert mode=='train' or mode=='test'

    if mode=='train':
        train_gps_path = './data/train0523.csv'
        save_path = './data/speed_wash_train.csv'
        NDATA = 100000
        # 训练集没有列名，读写header=None
        reader = pd.read_csv(train_gps_path, iterator = True,header=None)    
        

        len_df = NDATA
        sums = 0
        tt = 0
        while len_df==NDATA:
            time0 = time.time()
            df = reader.get_chunk(NDATA)
            len_df = df.shape[0]
            sums+=len_df
            
            df = set_data_columns(df)

            df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
            df['longitude'] = df['longitude'].astype(float)
            df['loadingOrder'] = df['loadingOrder'].astype(str)
            df['latitude'] = df['latitude'].astype(float)
            df['speed'] = df['speed'].astype(float)

            df.sort_values(['loadingOrder', 'timestamp'], inplace=True)

            df['lat_diff'] = df.groupby('loadingOrder')['latitude'].diff(1)
            df['lon_diff'] = df.groupby('loadingOrder')['longitude'].diff(1)
            df['diff_seconds'] = df.groupby('loadingOrder')['timestamp'].diff(1).dt.total_seconds()

            df = dd.from_pandas(df, npartitions=16)
            df['speed'] = df.apply(lambda x: cor2speed(x['latitude'],x['longitude'],x['lat_diff'],x['lon_diff'],x['diff_seconds']) if not pd.isna(x['lon_diff']) and x['diff_seconds']>0 else x['speed'], axis=1)
            df = df.compute()

            df.drop(['lat_diff','lon_diff','diff_seconds'],axis=1,inplace=True)

            mean = df['speed'].mean()
            maxx = df['speed'].max()

            overspeed = df[df['speed']>max_speed]['loadingOrder'].values
            df.drop(df[df['loadingOrder'].isin(overspeed)].index, inplace=True)
            df.to_csv(save_path,mode='a',index=False,header=False)

            drop_rate = (len_df - df.shape[0])/len_df *100
            
            time1 = time.time()
            minutes_delta = (time1-time0)/60
            tt+=minutes_delta
            print("minutes total/round: %.2f  %.2f"%(tt,minutes_delta))
            print("processed:",sums)
            print("speed mean/max: %.2f  %.2f"%(mean,maxx))
            print("drop rate: %.2f%%"%drop_rate)
            print()
    
    elif mode=='test':
        test_data_path = './data/A_testData0531.csv'
        save_path = './data/speed_wash_test.csv'
        df = pd.read_csv(test_data_path)
        
        df['temp_timestamp'] = df['timestamp']

        df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
        df['longitude'] = df['longitude'].astype(float)
        df['loadingOrder'] = df['loadingOrder'].astype(str)
        df['latitude'] = df['latitude'].astype(float)
        df['speed'] = df['speed'].astype(float)

        df['lat_diff'] = df.groupby('loadingOrder')['latitude'].diff(1)
        df['lon_diff'] = df.groupby('loadingOrder')['longitude'].diff(1)
        df['diff_seconds'] = df.groupby('loadingOrder')['timestamp'].diff(1).dt.total_seconds()

        df = dd.from_pandas(df, npartitions=16)
        df['speed'] = df.apply(lambda x: cor2speed(x['latitude'],x['longitude'],x['lat_diff'],x['lon_diff'],x['diff_seconds']) if not pd.isna(x['lon_diff']) and x['diff_seconds']>0 else x['speed'], axis=1)
        df = df.compute()
        
        df['timestamp'] = df['temp_timestamp']
        df.drop(['lat_diff','lon_diff','diff_seconds','temp_timestamp'],axis=1,inplace=True)
        
        df.to_csv(save_path,index=False)
# 给测试集根据最后一列Trace,添加起点与终点的坐标
def test_begin_end():
    test = pd.read_csv('./data/origin/A_testData0531.csv')
    port = pd.read_csv('./data/port_fixed.csv')
    
    def trace2cordinate(x):
        y = x.split('-')
        assert len(y)==2
        begin_cordinate = port[port['TRANS_NODE_NAME']==y[0]][['LATITUDE','LONGITUDE']].values
        begin_lat = begin_cordinate[0][0]
        begin_lon = begin_cordinate[0][1]
        end_cordinate = port[port['TRANS_NODE_NAME']==y[1]][['LATITUDE','LONGITUDE']].values
        end_lat = end_cordinate[0][0]
        end_lon = end_cordinate[0][1]
        return begin_lat,begin_lon,end_lat,end_lon
    
    test_group = test.groupby('loadingOrder')['TRANSPORT_TRACE'].last().reset_index()
    test_group.columns = ['loadingOrder','TRANSPORT_TRACE']
    test_group[['begin_lat','begin_lon','end_lat','end_lon']] = test_group.apply(lambda x:trace2cordinate(x['TRANSPORT_TRACE']),axis=1,result_type='expand')
    test_group.drop(['TRANSPORT_TRACE'],axis=1,inplace=True)

    test = test.merge(test_group,on='loadingOrder',how='left')
    # print(test)
    test.to_csv('./data/wash3_test.csv',index=False)
# 训练集极大匹配，起点终点阈值筛选与添加
def distance_wash(max_dis):
    port = pd.read_csv('./data/port_fixed.csv')
    port = port[['LATITUDE','LONGITUDE']].values


    def NN(lat,lon):
        dis_list = [geodesic((lat,lon),port[i]).km for i in range(len(port))]
        dis_list = np.array(dis_list)
        nn = np.argmin(dis_list)
        # print(port[nn][0],port[nn][1],dis_list[nn])
        return port[nn][0],port[nn][1],dis_list[nn]


    reader = pd.read_csv('./data/wash1_train.csv', iterator = True,header=None)
    NDATA = 1000000
    len_df = NDATA
    sums = 0
    tt = 0
    while len_df==NDATA:
        time0 = time.time()
        df = reader.get_chunk(NDATA)
        len_df = df.shape[0]
        sums+=len_df
        df = set_data_columns(df)

        df['timestamp'] = pd.to_datetime(df['timestamp'], infer_datetime_format=True)
        df['longitude'] = df['longitude'].astype(float)
        df['loadingOrder'] = df['loadingOrder'].astype(str)
        df['latitude'] = df['latitude'].astype(float)
        df.sort_values(['loadingOrder', 'timestamp'], inplace=True)

        begin_df = df.groupby('loadingOrder')['latitude','longitude'].first().reset_index()
        begin_df.columns=['loadingOrder','begin_lat','begin_lon']

        begin_df = dd.from_pandas(begin_df, npartitions=16)
        begin_df[['begin_lat','begin_lon','distance']] = begin_df.apply(lambda x: NN(x['begin_lat'],x['begin_lon']),axis=1,result_type='expand')
        begin_df = begin_df.compute()
        
        wash_list = begin_df[begin_df['distance']>max_dis]['loadingOrder'].values
        begin_df.drop(['distance'],axis=1,inplace=True)
        begin_df.drop(begin_df[begin_df['loadingOrder'].isin(wash_list)].index,inplace=True)
        df.drop(df[df['loadingOrder'].isin(wash_list)].index,inplace=True)
        df = df.merge(begin_df,on='loadingOrder',how='left')

        end_df = df.groupby('loadingOrder')['latitude','longitude'].last().reset_index()
        end_df.columns=['loadingOrder','end_lat','end_lon']

        end_df = dd.from_pandas(end_df, npartitions=16)
        end_df[['end_lat','end_lon','distance']] = end_df.apply(lambda x: NN(x['end_lat'],x['end_lon']),axis=1,result_type='expand')
        end_df = end_df.compute()
        
        wash_list = end_df[end_df['distance']>max_dis]['loadingOrder'].values
        end_df.drop(['distance'],axis=1,inplace=True)
        end_df.drop(end_df[end_df['loadingOrder'].isin(wash_list)].index,inplace=True)
        df.drop(df[df['loadingOrder'].isin(wash_list)].index,inplace=True)
        df = df.merge(end_df,on='loadingOrder',how='left')
        
        df.drop(df[df['begin_lat']==df['end_lat']].index,inplace=True)
        
        df.to_csv('./data/wash2_train.csv',mode='a',index=False,header=False)

        drop_rate = (len_df - df.shape[0])/len_df *100
        time1 = time.time()
        minutes_delta = (time1-time0)/60
        tt+=minutes_delta
        print("minutes total/round: %.2f  %.2f"%(tt,minutes_delta))
        print("processed:",sums)
        print("drop rate: %.2f%%"%drop_rate)
        print()
# event清洗与规范化
def event_feature():
    def port2cordinate(x):
        end_cordinate = port[port['TRANS_NODE_NAME']==x][['LATITUDE','LONGITUDE']].values
        if len(end_cordinate)==1:
            lat=end_cordinate[0][0]
            lon=end_cordinate[0][1]
            return lat,lon
        else:
            return 200,200
    
    port_data_path = 'data/port_fixed.csv'
    order_data_path = 'data/origin/loadingOrderEvent.csv'
    event_data = pd.read_csv(order_data_path)
    port = pd.read_csv(port_data_path)

    event_data.dropna(axis=0,how='any',inplace=True)
    event_data['timestamp'] = pd.to_datetime(event_data['EVENT_CONVOLUTION_DATE'], infer_datetime_format=True,utc=True)
    event_data.drop('EVENT_CONVOLUTION_DATE',axis=1,inplace=True)
    event_data.sort_values(['loadingOrder','timestamp'], inplace=True)
    event_data[['latitude','longitude']] = event_data.apply(lambda x: port2cordinate(x['EVENT_LOCATION_ID']),axis=1,result_type='expand')
    event_data.to_csv('data/wash1_event.csv')




if __name__=='__main__':
    # client = Client(n_workers=8)
    # print(client)

    # 第一次速度清洗，将瞬时速度替换为平均速度，并洗掉速度过大的
    # speed_wash(60,'train')
    # speed_wash(10000,'test')


    # 给测试集增添起点终点坐标
    test_begin_end()
    
    # 清洗掉训练集中起点、终点离港口过远的点
    # distance_wash(50)

    # 给event数据集进行特征工程，加上经度纬度，并重命名timestamp
    # event_feature()