import time
import numpy as np
import scipy as sp
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

file = open("processed.txt.semifinal", "r", encoding='utf8')
file.readline()
lines = []
line_limit = 100000
for i in range(line_limit):
    lines.append(file.readline())
vectorizer = CountVectorizer(lowercase=False)
X = vectorizer.fit_transform(lines)
print(X.shape)
U, S, V = np.linalg.svd(X.toarray())
print(U.shape)
print(S)
print(V.shape)

print(len(vectorizer.get_feature_names_out()))
