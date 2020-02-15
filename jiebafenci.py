import jieba

string = '废话了！你个受！'
result = jieba.cut(string)
# result = jieba.cut(string,cut_all=True)

print('/'.join(result))