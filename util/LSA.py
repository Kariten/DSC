import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import sqlite3
import re
import jieba

def getdb():
    conn = sqlite3.connect('public/classification.db',detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

# db源
texts = []
conn = getdb()
c = conn.cursor()
# 获取动态分类服务
query = "SELECT * FROM Serv"
servs = c.execute(query).fetchall()
for serv in servs:
    text = re.sub(r"(|)|\?|？|。|、|，|（|）|/|；| |-|\+|\n|[0-9]|[a-z]|[A-Z]|\.|%", "", serv[3], 0) 
    texts.append(text)
conn.close()

pd.set_option("display.max_colwidth", 200)

from sklearn.datasets import fetch_20newsgroups

dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))

# print(type(dataset))
# documents = dataset.data
# print(type(documents))
documents = texts
# print(len(documents))

# print(dataset.target_names)

news_df = pd.DataFrame({'document':documents})

# print(news_df)
# print(type(news_df))

# removing everything except alphabets`
news_df['clean_doc'] = news_df['document'].str.replace(",", " ")

# removing short words
# news_df['clean_doc'] = news_df['clean_doc'].apply(lambda x: ' '.join([w for w in x.split() if len(w)>3]))

# make all text lowercase
# news_df['clean_doc'] = news_df['clean_doc'].apply(lambda x: x.lower())

# stop_words = [line.strip() for line in open('stopwords.txt',encoding='GB2312').readlines()]
stop_words = ('数据', '提供', '应用', '技术', '支持', '集成', '中国', '业务', '适用', '使用',
                '简称', '开发', '实现', '数据库', '需求', '平台', '管理', '通过')  # 停词


# tokenization
# tokenized_doc = news_df['clean_doc'].apply(lambda x: x.split()) 
tokenized_doc = news_df['clean_doc'].apply(lambda x: jieba.lcut(x)) 
# [w.word for w in jp.cut(text) if w.flag in flags and w.word not in stopwords and len(w.word)>1]

# remove stop-words
tokenized_doc = tokenized_doc.apply(lambda x: [item for item in x if item not in stop_words])

# de-tokenization
detokenized_doc = []
for i in range(len(news_df)):
    t = ' '.join(tokenized_doc[i])
    detokenized_doc.append(t)
    
news_df['clean_doc'] = detokenized_doc

from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(stop_words='english', 
                             max_features= 1000, # keep top 1000 terms 
                             max_df = 0.5, 
                             smooth_idf=True)

X = vectorizer.fit_transform(news_df['clean_doc'])

print(X.shape) # check shape of the document-term matrix

from sklearn.decomposition import TruncatedSVD

# SVD represent documents and terms in vectors 
svd_model = TruncatedSVD(n_components=6, algorithm='randomized', n_iter=100, random_state=122)
# n_components=主题数

svd_model.fit(X)

print(len(svd_model.components_))

terms = vectorizer.get_feature_names()

topics = []
for i, comp in enumerate(svd_model.components_):
    if i:
        topic = []
        topic.append(i-1)
        terms_comp = zip(terms, comp)
        sorted_terms = sorted(terms_comp, key= lambda x:x[1], reverse=True)[:4] # 主题词数
        for t in sorted_terms:
            topic.append(t[0])
        topics.append(tuple(topic))

for topic in topics:
    print(topic)
print(len(dataset.target))
import umap

X_topics = svd_model.fit_transform(X)
embedding = umap.UMAP(n_neighbors=150, min_dist=0.5, random_state=12).fit_transform(X_topics)
plt.figure(figsize=(7,5))
plt.scatter(
    embedding[:, 0], embedding[:, 1], 
    # c = dataset.target,
    c = documents,
    s = 10, # size
    edgecolor='none'
)
plt.show()