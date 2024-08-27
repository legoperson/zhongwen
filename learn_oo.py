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
from threading import Thread


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


def update_texts(placeholder, valid_numbers, texts):
    """在一个线程中定期更新文本"""
    while True:
        # 随机选择一个小于输入数字的值
        selected_number = np.random.choice(valid_numbers)
        st.markdown(f"<h1 style='color:red;'>{word_list[selected_number]}</h1>", unsafe_allow_html=True)        
        # 等待5秒
        time.sleep(5)
        
        
# Streamlit 应用 
st.title('Number Selection App')

# 用户输入
input_number = st.number_input('Enter a number', min_value=0)

if st.button('Submit'):
    valid_numbers = [num for num in numbers if num < input_number]    
    placeholder = st.empty()
    # 启动一个线程来更新文本
    update_thread = Thread(target=update_texts, args=(placeholder, valid_numbers, word_list))
    update_thread.start()

 