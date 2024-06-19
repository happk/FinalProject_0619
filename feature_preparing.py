# fasta to feature
import os
from work20230906 import ExtractFeatures
# 由於是調用遠在天邊的pse-in-one，所以要用絕對路徑
maindir = os.getcwd().replace('\\','/') + '/'
train_fasta_path = maindir + 'data/train.mfasta'
test_fasta_path = maindir + 'data/test.mfasta'
train_feature_path = maindir + 'data/train_feature.csv'
test_feature_path = maindir + 'data/test_feature.csv'


encode = ['pse.py','SC-PseAAC',['-lamada','5','-w','0.2']]

train_feature = ExtractFeatures(train_fasta_path, encode[0], encode[1], encode[2], train_feature_path)
test_feature = ExtractFeatures(test_fasta_path, encode[0], encode[1], encode[2], test_feature_path)