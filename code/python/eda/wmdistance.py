import os
import sys
sys.path.append("../")

from gensim import models

import pandas as pd
import numpy as np

import preprocessing as pp


filename = "../../../data/sample.csv"
data = pd.read_csv(filename, sep=',')


data['header_features'] = data.Headline.apply(lambda x : pp.process(x))
data['content_features'] = data.articleBody.apply(lambda x : pp.process(x))


model = models.Word2Vec.load_word2vec_format('/media/sree/venus/code/word2vec/GoogleNews-vectors-negative300.bin', binary=True)

def sent2vec(words):
    M = []
    for w in words:
        try:
            M.append(model[w])
        except:
            continue
    M = np.array(M)
    v = M.sum(axis=0)
    return v / np.sqrt((v ** 2).sum())



## create the header vector    
header_vectors = np.zeros((data.shape[0], 300))
for i, q in enumerate(data.header_features.values):
    header_vectors[i, :] = sent2vec(q)

# header_series = pd.Series(header_vectors)
# data['header_vector'] = header_series.values


## create the content vector    
content_vectors  = np.zeros((data.shape[0], 300))
for i, q in enumerate(data.content_features.values):
    content_vectors[i, :] = sent2vec(q)

# content_series = pd.Series(content_vectors)
# data['content_vector'] = content_series.values

# model = KeyedVectors.load_word2vec_format('data/GoogleNews-vectors-negative300.bin.gz', binary=True)
data['wmd'] = data.apply(lambda x: model.wmdistance(x['header_features'], x['content_features']), axis=1)


# data['header_vectors'] = data.header_features.apply(lambda x : sent2vec(x))
# data['content_vectors'] = data.header_features.apply(lambda x : sent2vec(x))


## Word2Vec WMD Distance

def toCSV(stance, values):
    metric = "word_mover_"
    f = open(metric + stance + "_values.csv", "w")

    try:
        os.remove(f.name)
    except OSError:
        pass

    f = open(metric + stance + "_values.csv", "w")        
    for i in values:
        f.write(str(i) + "\n")
    
range_of_values = {}

for stance_level in np.unique(data.Stance):

    filtered_rows = data[(data.Stance == stance_level)]
    print("Statistics for group : " + stance_level)

    ## range of wmds
    group_max_wmd = np.max(filtered_rows.wmd)  
    group_min_wmd = np.min(filtered_rows.wmd)

    range_of_values[stance_level] = filtered_rows.wmd.tolist()

    value_list = filtered_rows.wmd.tolist()
    value_list.sort()
    toCSV(stance_level, value_list)
