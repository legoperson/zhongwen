# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:07:27 2024

@author: 142397
"""

import os
import pandas as pd

# 
df = pd.read_csv('fast45.csv', header=None)
df = df.dropna()
# 创建一个空列表来存储结果
word_list = []

# 遍历CSV文件的行，步长为2（即奇数行是字，偶数行是对应的数字）
for i in range(0, len(df), 2):
    characters = df.iloc[i].tolist()     # 获取奇数行的字符
    numbers = df.iloc[i + 1].tolist()    # 获取偶数行的数字
    for j in characters:
        word_list.append(j)