import numpy as np
import pandas as pd
import gc
from sklearn.decomposition import PCA, KernelPCA
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def read_csv_data(file_name, debug, server=True, num_rows=200):
    if server:
        path = '/home/science/data/'
        df = pd.read_hdf(path + file_name + '.h5', 'data')
    else:
        path = '/home/gublu/Desktop/THINKSTATS/Competition/data/'
        if debug:
            df = pd.read_csv(path + file_name + '.csv', nrows=num_rows)
        else:
            df = pd.read_csv(path + file_name + '.csv')
    for col in list(df):
        if str(df[col].dtype) == 'category':
            df[col] = df[col].astype('object')
    return df
def label_encode_it(df):
    encode_these_columns = []
    for col in list(df):
        if col == 'TARGET':
            continue
        if str(df[col].dtype) in ['object', 'category']:
            encode_these_columns.append(col)
            df[col] = df[col].astype('category').cat.codes
    print(encode_these_columns, '**********')
    return df
def min_max_scale_it(df):
    cols = [col for col in df.columns if col not in ['TARGET', 'SK_ID_CURR']]
    for col in cols:
        try:
            df[col]  = df[col].fillna(df[col].mean())
            df[col]=(df[col]-df[col].min())/(df[col].max()-df[col].min())
        except:
            pass
    return df

# fix random seed for reproducibility
seed = 7
np.random.seed(seed)


# In[2]:


df = read_csv_data('shiv', debug=False)


# In[ ]:


# impute and scale
df = df.replace(-np.inf, np.nan)
df = df.replace(np.inf, np.nan)

cols = [col for col in df.columns if col not in ['TARGET', 'SK_ID_CURR']]
df  = min_max_scale_it(df)
df[cols] = label_encode_it(df[cols])

train = df[df['TARGET'].notnull()]
test = df[df['TARGET'].isnull()]

train  = train.fillna(df.mean())
test  = test.fillna(df.mean())

cols_to_drop = []
for col in list(df):
    if col == 'TARGET':
        continue
    train[col].replace(np.inf, np.nan, inplace=True)
    test[col].replace(np.inf, np.nan, inplace=True)
    train[col].replace(-np.inf, np.nan, inplace=True)
    test[col].replace(-np.inf, np.nan, inplace=True)
    if train[col].isnull().any():
        cols_to_drop.append(col)
    if test[col].isnull().any():
        cols_to_drop.append(col)
    cols_to_drop = list(set(cols_to_drop))

train.drop(cols_to_drop, axis=1, inplace=True)
test.drop(cols_to_drop, axis=1, inplace=True)
test = test.reset_index(drop=True)
print(test.head())
print(test.shape)
#print(cols_to_drop, 'cols_to_drop')
print(train.shape, test.shape)
train_dataset = train.values
X = train_dataset[:,2:]
y = train_dataset[:,1]
y=y.astype('int')
#print(X)


# In[4]:
out_df = pd.DataFrame({"SK_ID_CURR": df['SK_ID_CURR']})
del df
gc.collect()

train_dataset = train.values
X = train_dataset[:,2:]
y = train_dataset[:,1]
y=y.astype('int')
test_dataset = test.values
X_test = test_dataset[:,2:]
print(type(X_test))
print('X.shape, y.shape, X_test.shape', X.shape, y.shape, X_test.shape)


# In[5]:



n_components = 2
kernels = [ 'linear' ,'poly' ,'rbf' ,'sigmoid' ,'cosine' , 'precomputed']
for kernel in kernels:
    col_names  = ["kernel_pca_" + kernel + str(col+1) for col in range(n_components)]
    kpca = KernelPCA(n_components=n_components, kernel=kernel, gamma=10, degree=3)
    principalComponents = kpca.fit_transform(X)
    principalDf  = pd.DataFrame(data = principalComponents, columns = col_names)
    tr = pd.concat([principalDf, train[['SK_ID_CURR']]], axis = 1)
    del principalDf
    gc.collect()
    print('tr shape', tr.shape)
    print(tr.head())
    X_test_transformed = kpca.transform(X_test)
    print('X_test_transformed', X_test_transformed.shape)
    test_principalDf  = pd.DataFrame(data = X_test_transformed, columns = col_names)
    te = test_principalDf.join(test[['SK_ID_CURR']])
    del test_principalDf
    gc.collect()
    print('te shape', te.shape)
    print(te.head())
    tr_te = tr.append(te).reset_index()
    del (tr, te)
    gc.collect()
    print('tr_te shape', tr_te.shape)
    out_df = out_df.merge(tr_te, on=['SK_ID_CURR'], how='left')
    del tr_te
    gc.collect()

out_df.to_csv('kernel_pca_tr_te.csv', index= False)

print(out_df.shape)
print(out_df.head())


