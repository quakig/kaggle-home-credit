from lightgbm import LGBMClassifier
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import time
import numpy as np
import datetime
import gc

def one_hot_encode_it(df, nan_as_category = False, exclude_columns=[]):
    encode_these_coumns = []
    for col in df:
        if col == 'TARGET':
            continue
        x = df[col].nunique()
        if (2 <= x <= 4):
            encode_these_coumns.append(col)
    encode_these_coumns = list(set(encode_these_coumns) - set(exclude_columns))
    df = pd.get_dummies(df, columns= encode_these_coumns, dummy_na= nan_as_category)
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



class OurLightGBM:

  def __init__(self):
    self.debug = False #debug
    df = read_csv_data('shiv', debug=False)
    df = df.drop('NEW_LIVE_IND_SUM', 1) # giving dtypes invalid errors in lightgbm
    df = label_encode_it(df)
    df = one_hot_encode_it(df)
    self.train_df = df[df['TARGET'].notnull()]
    self.y = self.train_df['TARGET']
    self.test_df = df[df['TARGET'].isnull()]
    self.test_df = self.test_df.drop('TARGET', 1)
    self.num_folds = 5
    #self.training_params = ['number_boosting_rounds', 'early_stopping_rounds']
    self.params = {  'objective': 'binary', 'metric': 'auc','nthread': 4, #'boost_from_average':False,
            'n_estimators':10000, 'learning_rate':0.01,
            'max_depth': -1, 'num_leaves':32, 'max_bin': 25,
            'feature_fraction': 0.80, 'bagging_fraction':0.7, 'bagging_freq': 1,
            'reg_alpha':3, 'reg_lambda':3,
            'min_split_gain':0.0000215, #'min_child_weight':40,
            #'class_weight': 'balanced',
            'verbose':-1}
    self.output_df = pd.DataFrame({"SK_ID_CURR": df['SK_ID_CURR']})
    del df
    gc.collect()
    self.kfold_lightgbm()




  def kfold_lightgbm(self):
    print("Starting LightGBM. Train shape: {}, test shape: {}".format(self.train_df.shape, self.test_df.shape))
    folds = StratifiedKFold(n_splits= self.num_folds, shuffle=True, random_state=1)
    # Create arrays and dataframes to store results
    oof_preds = np.zeros(self.train_df.shape[0])

    train_predictions = np.zeros(self.train_df.shape[0])
    submission_test_predictions = np.zeros(self.test_df.shape[0])

    feature_importance_df = pd.DataFrame()
    feats = [f for f in self.train_df.columns if f not in ['TARGET','SK_ID_CURR','SK_ID_BUREAU','SK_ID_PREV']]
    #categorical_features = ['NAME_CONTRACT_TYPE','CODE_GENDER','FLAG_OWN_CAR','FLAG_OWN_REALTY','CNT_CHILDREN','NAME_TYPE_SUITE','NAME_INCOME_TYPE','NAME_EDUCATION_TYPE','NAME_FAMILY_STATUS','NAME_HOUSING_TYPE','FLAG_MOBIL','FLAG_EMP_PHONE','FLAG_WORK_PHONE','FLAG_CONT_MOBILE','FLAG_PHONE','FLAG_EMAIL','CNT_FAM_MEMBERS','REGION_RATING_CLIENT','REGION_RATING_CLIENT_W_CITY','WEEKDAY_APPR_PROCESS_START','REG_REGION_NOT_LIVE_REGION','REG_REGION_NOT_WORK_REGION','LIVE_REGION_NOT_WORK_REGION','REG_CITY_NOT_LIVE_CITY','REG_CITY_NOT_WORK_CITY','LIVE_CITY_NOT_WORK_CITY','FONDKAPREMONT_MODE','HOUSETYPE_MODE','WALLSMATERIAL_MODE','EMERGENCYSTATE_MODE','DEF_30_CNT_SOCIAL_CIRCLE','DEF_60_CNT_SOCIAL_CIRCLE','FLAG_DOCUMENT_3','FLAG_DOCUMENT_5','FLAG_DOCUMENT_6','FLAG_DOCUMENT_8','FLAG_DOCUMENT_9','FLAG_DOCUMENT_11','FLAG_DOCUMENT_13','FLAG_DOCUMENT_14','FLAG_DOCUMENT_15','FLAG_DOCUMENT_16','FLAG_DOCUMENT_18','FLAG_DOCUMENT_19','FLAG_DOCUMENT_20','AMT_REQ_CREDIT_BUREAU_HOUR','AMT_REQ_CREDIT_BUREAU_DAY','AMT_REQ_CREDIT_BUREAU_WEEK','AMT_REQ_CREDIT_BUREAU_QRT','be_credit_status_sold_count','be_CREDIT_CURRENCY','be_last_CREDIT_TYPE','bb_b_latest_month_STATUS_DPD_count','be_sum_CNT_CREDIT_PROLONG','be_is_AMT_CREDIT_MAX_OVERDUE','be_is_AMT_CREDIT_SUM_OVERDUE','pae_NAME_CONTRACT_TYPE','pae_num_of_previous_applications_unused_offers','pae_name_client_type_new_count','pae_name_client_type_xna_count','pae_NAME_PAYMENT_TYPE','pae_NAME_YIELD_GROUP','pae_CODE_REJECT_REASON','pae_NAME_CLIENT_TYPE','pae_NAME_TYPE_SUITE','pae_NAME_PORTFOLIO','pae_NAME_PRODUCT_TYPE','pae_CHANNEL_TYPE','pae_NAME_SELLER_INDUSTRY','pae_PRODUCT_COMBINATION','pos_pa_latest_NAME_CONTRACT_STATUS_y','does_client_have_a_credit_card_with_us','does_client_have_pos_cas_balance_record_with_us','total_number_of_documents_submitted','is_nan_EXT_SOURCE_1','is_nan_OCCUPATION_TYPE','is_nan_AMT_REQ_CREDIT_BUREAU_DAY','is_nan_DAYS_EMPLOYED']
    #indexes_of_categories = [X_train.columns.get_loc(col) for col in categorical_features]
    #sample_weight = np.array([11 if i == 1 else 1 for i in y_train])
    #sample_weight.shape
    for n_fold, (train_idx, valid_idx) in enumerate(folds.split(self.train_df[feats], self.train_df['TARGET'])):
      train_x, train_y = self.train_df[feats].iloc[train_idx], self.train_df['TARGET'].iloc[train_idx]
      valid_x, valid_y = self.train_df[feats].iloc[valid_idx], self.train_df['TARGET'].iloc[valid_idx]
      clf = LGBMClassifier(**self.params)
      clf.fit(train_x, train_y, eval_set=[(train_x, train_y), (valid_x, valid_y)], eval_metric= 'auc', verbose= 100, early_stopping_rounds= 200 )
      oof_preds[valid_idx] = clf.predict_proba(valid_x, num_iteration=clf.best_iteration_)[:, 1]

      train_predictions += clf.predict_proba(self.train_df[feats])[:, 1] / folds.n_splits
      submission_test_predictions += clf.predict_proba(self.test_df[feats], num_iteration=clf.best_iteration_)[:, 1] / folds.n_splits

      del clf, train_x, train_y, valid_x, valid_y
      gc.collect()
    self.test_df['TARGET'] = submission_test_predictions
    submission = self.test_df[['SK_ID_CURR', 'TARGET']]

    tr_te_concatenated = np.concatenate([train_predictions, submission_test_predictions])
    self.output_df['lightgbm'] = tr_te_concatenated
    self.output_df.to_csv('lightgbm_tr_te.csv', index= False)



if __name__ == "__main__":
    OurLightGBM()
