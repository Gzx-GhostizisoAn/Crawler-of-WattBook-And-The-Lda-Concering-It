import pandas as pd
import re
import nltk
import gensim
import pyLDAvis
import pyLDAvis.gensim_models
from gensim import corpora
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# 第一次运行需要
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("omw-1.4")


# 1. 读取数据

df = pd.read_csv("scraped_descriptions.csv")
df = df[df["merged"] != "抓取失败/无摘要"].dropna()

texts = df["merged"].astype(str).tolist()
print(f"有效文本数量: {len(texts)}")

# 2. NLP 预处理

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)   
    tokens = text.split()
    tokens = [w for w in tokens if w not in stop_words and len(w) > 2]
    tokens = [lemmatizer.lemmatize(w) for w in tokens]
    return tokens

processed_texts = [preprocess(t) for t in texts]

print("示例清洗结果：")
print(processed_texts[0][:20])

# =======================
# 3. 构建词典与语料
# =======================
dictionary = corpora.Dictionary(processed_texts)
dictionary.filter_extremes(no_below=5, no_above=0.5)

corpus = [dictionary.doc2bow(text) for text in processed_texts]

print(f"词典大小: {len(dictionary)}")


# 4. LDA 

NUM_TOPICS = 10   

lda_model = gensim.models.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=NUM_TOPICS,
    random_state=42,
    passes=10,
    alpha="auto",
    per_word_topics=True
)


# 5. 输出主题关键词

print("\n====== 主题关键词 ======")
for idx, topic in lda_model.print_topics(num_words=10):
    print(f"\nTopic {idx}:")
    print(topic)


# 6. 每本书的主题分布

doc_topics = []
for i, bow in enumerate(corpus):
    topic_dist = lda_model.get_document_topics(bow)
    doc_topics.append(topic_dist)

df["topic_distribution"] = doc_topics
df.to_csv("lda_results_with_topics.csv", index=False, encoding="utf-8-sig")
print("\n已保存每本书的主题分布到: lda_results_with_topics.csv")


# 7. 可视化

vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary)
pyLDAvis.save_html(vis, "lda_visualization.html")
print("已生成交互式可视化文件: lda_visualization.html")
