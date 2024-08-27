# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 18:07:27 2024

@author: 142397
"""

import os
import pandas as pd
import streamlit as st
import numpy as np
import time
# 
df = pd.read_csv('fast45.csv', header=None)
df = df.dropna()
# 创建一个空列表来存储结果
word_list = []

# 遍历CSV文件的行，步长为2（即奇数行是字，偶数行是对应的数字）
for i in range(0, len(df), 2):
    characters = df.iloc[i].tolist()     # 获取奇数行的字符
         # 获取偶数行的数字
    for j in characters:
        word_list.append(j)
        
numbers = range(len(word_list))


 
# Streamlit 应用
 
st.title('Number Selection App')

# 用户输入
input_number = st.number_input('Enter a number', min_value=0)

if st.button('Submit'):
    # 延迟5秒
    time.sleep(5)

    # 筛选小于用户输入的数字
    valid_numbers = [num for num in numbers if num < input_number]
    
 

    # 随机选择一个小于输入数字的值
    selected_number = np.random.choice(valid_numbers)

    # # 获取选中的数字在原列表中的索引
    # index = numbers.index(selected_number)

    # 显示对应的文本
    st.markdown(f"<h1 style='color:black;'>{word_list[selected_number]}</h1>", unsafe_allow_html=True)

 