from gensim import corpora, models
import jieba.posseg as jp, jieba
import json
import re

def getidbyinfo( info ):

    with open("public/static/service.json",'r',encoding='utf-8') as load_f:
        load_dict = json.load(load_f)
        print(load_dict)
    load_dict['smallberg'] = [8200,{1:[['Python',81],['shirt',300]]}]
    # print(load_dict)
    # print(type(load_dict['data'][0]))

    # 个人简介
    myinfo = info

    # 文本集
    texts = []
    for serv in load_dict['data']:
        text = re.sub(r"\?|？|。|、|，|（|）|/|；| |-|\+|\n|[0-9]|[a-z]|[A-Z]|\.|%", "", serv['info'], 0) 
        texts.append(text)
    texts.append(myinfo)
    '''
    for info in texts:
        print(info)
    '''

    # 分词过滤条件
    # jieba.add_word('四强', 9, 'n')
    flags = ('n', 'nr', 'ns', 'nt', 'eng', 'v', 'd')  # 词性
    stopwords = ('数据', '提供', '应用', '技术', '支持', '集成', '中国', '业务', '适用', '使用',
                '简称', '开发', '实现', '数据库', '需求', '平台')  # 停词
    # 分词
    words_ls = []
    for text in texts:
        words = [w.word for w in jp.cut(text) if w.flag in flags and w.word not in stopwords and len(w.word)>1]
        words_ls.append(words)
    # 构造词典
    dictionary = corpora.Dictionary(words_ls)
    # 基于词典，使词→稀疏向量，并将向量放入列表，形成稀疏向量集
    corpus = [dictionary.doc2bow(words) for words in words_ls]
    # lda模型，num_topics设置主题的个数
    lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=5)
    # 打印所有主题，每个主题显示5个词
    for topic in lda.print_topics(num_words=5):
        print(topic)
    # 主题推断
    print(lda.inference(corpus)[0])
    x = 0
    for value in lda.inference(corpus)[0][-1]:
        if value < 1 :
            x += 1
        else:
            break
    i = 0
    resultlist = []
    if x == 5:
        for i in range(len(texts)-1):
            resultlist.append(i)
    else:
        for line in lda.inference(corpus)[0]:
            if line[x]>1:
                print (i,':',line)
                resultlist.append(i)
            i += 1
        print(lda.inference(corpus)[0][-1])
        # print(type(lda.inference(corpus)))

    return resultlist

if __name__ == "__main__":
    print(getidbyinfo("大数据"))