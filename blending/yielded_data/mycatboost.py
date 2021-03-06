### FINALIZED
import numpy as np
import pandas as pd
import gc
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler



from catboost import CatBoostClassifier



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


seed = 7
np.random.seed(seed)


df = read_csv_data('shiv', debug=False)
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
print(cols_to_drop, 'cols_to_drop')
print(train.shape, test.shape)
train_dataset = train.values
X = train_dataset[:,2:]
y = train_dataset[:,1]
y=y.astype('int')
print(X)

test_dataset = test.values
X_test = test_dataset[:,2:]
print(type(X_test))


print(X.shape, y.shape, X_test.shape)
output_df = pd.DataFrame({"SK_ID_CURR": df['SK_ID_CURR']})

del df
gc.collect()


# In[34]:
# https://www.kaggle.com/aharless/simple-ffnn-from-dromosys-features

index_of_categorical_columns = []
for i, col in enumerate(X.T):
    uniques = np.unique(col, return_index=False, return_inverse=False, return_counts=False, axis=None)
    nuniques = len(uniques)
    if nuniques <=20 and col.dtype.kind in np.typecodes['AllInteger']:
      index_of_categorical_columns.append(i)


print( 'Setting up CatBoostClassifier...' )
cb = CatBoostClassifier(iterations=2800, learning_rate=0.01, depth=7, loss_function='Logloss')


print( 'Fitting ...' )
cb.fit(X, y, index_of_categorical_columns)
cb_X_prediction  = cb.predict_proba(X)[:, 1]
cb_X_test_prediction  = cb.predict_proba(X_test)[:, 1]
tr_te_concatenated = np.concatenate([cb_X_prediction, cb_X_test_prediction])
output_df['catboost_classifier'] = tr_te_concatenated

print('final tr_te shape', output_df.shape)
print(output_df.head())

output_df.to_csv('catboost_tr_te.csv', index= False)

print( output_df.head() )
