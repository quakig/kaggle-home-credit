from tr_te import TrainTest
from b import Bureau
from cc import CreditCard
from ip import InstallmentPayments
from pa import PreviousApplication
from pos import POSCASHBalance
from litegbm import LiteGBM
from woe_scores import WOEScores
import gc
import warnings
from utils import *
warnings.simplefilter(action='ignore')
#warnings.simplefilter(action='ignore', category=SettingWithCopyWarning)

# woe
# auto_encode
# target encoding
# categorical embedding vith neural network
# libfm, vowpal vabbit
# multilayer stacking
# unsupervised methods that reduce dimensionality (like SVD, PCA, ISOMAP, KDTREE clustering)
# similarlity features
# interaction features - like popular product AND good rating
# factorization machines
# https://github.com/fred-navruzov/featuretools-workshop/blob/master/featuretools-workshop.ipynb
# https://www.kaggle.com/kailex/tidy-xgb-all-tables-0-796/code
# genetic programming https://www.kaggle.com/scirpus/hybrid-jeepy-and-lgb-ii
# https://www.kaggle.com/ogrellier/feature-selection-with-null-importances
# https://www.kaggle.com/davidsalazarv95/fast-ai-pytorch-starter-version-two
# https://www.kaggle.com/shep312/deep-learning-in-tf-with-upsampling-lb-758
# https://github.com/turi-code/python-libffm/blob/master/examples/basic.py

debug = True

def post_process_data(df):
  return df

def change_data():
  df = TrainTest(debug=debug).execute()
  b = Bureau(debug=debug).execute()
  df = df.merge(b, on=['SK_ID_CURR'], how='left')
  cc = CreditCard(debug=debug).execute()
  df = df.merge(cc, on=['SK_ID_CURR'], how='left')
  ip = InstallmentPayments(debug=debug).execute()
  df = df.merge(ip, on=['SK_ID_CURR'], how='left')
  pa = PreviousApplication(debug=debug).execute()
  df = df.merge(pa, on=['SK_ID_CURR'], how='left')
  pos = POSCASHBalance(debug=debug).execute()
  df = df.merge(pos, on=['SK_ID_CURR'], how='left')
  del (b,cc,ip,pa, pos)
  gc.collect()
  df = post_process_data(df)
  df = reduce_mem_usage(df)
  print(df.shape)
  #df.to_csv('shiv_300.csv', index=False)
  #df.to_hdf('../hdf/shiv.h5', key='data', mode='w', format="table")
  df.to_hdf('/home/science/data/shiv.h5', key='data', mode='w', format="table")
  return df


def main():
    df = change_data()
    #df = WOEScores(df, debug=debug).append_woe_scores()
    #df[:300].to_csv('shiv_300.csv', index=False)
    #pe(df.shape)
    #df = pd.read_hdf('hdf/shiv.h5', 'data')
    #df = add_as_type_category(df)
    #df =reduce_mem_usage(df)
    #full_train(df, params)
    #train_test_split_run(df, params)
    #LiteGBM(df, debug= debug)
    #play_on_done()

if __name__ == "__main__":
    main()


