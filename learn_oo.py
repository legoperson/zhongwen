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
text_list = []

# 遍历CSV文件的行，步长为2（即奇数行是字，偶数行是对应的数字）
for i in range(0, len(df), 2):
    characters = df.iloc[i].tolist()     # 获取奇数行的字符
         # 获取偶数行的数字
    for j in characters:
        text_list.append(j)
        
numbers = range(len(text_list))

import streamlit as st
import random
import time

# 文字列表
 
# 初始化状态
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'max_index' not in st.session_state:
    st.session_state.max_index = len(text_list)  # 默认最大值为列表长度

# 按钮的回调函数
def start_display():
    st.session_state.start_time = time.time()

# 文本框输入
max_index = st.text_input("请输入最大显示字的索引位置", value=str(st.session_state.max_index))
if max_index.isdigit():
    st.session_state.max_index = int(max_index)
else:
    st.warning("请输入有效的数字")

# 创建按钮
if st.button("开始显示"):
    start_display()

# 更新显示内容
current_time = time.time()
if st.session_state.start_time is not None:
    elapsed_time = current_time - st.session_state.start_time
    if elapsed_time >= 5:
        # 限制从前max_index个位置中选择
        valid_text_list = text_list[:st.session_state.max_index]
        if valid_text_list:  # 确保valid_text_list非空
            st.session_state.current_text = random.choice(valid_text_list)
        else:
            st.session_state.current_text = "列表为空或索引超出范围"
        st.session_state.start_time = current_time  # 重置时间

    st.write(st.session_state.current_text)

    # 自动刷新以便于5秒钟更新一次
    time.sleep(0.1)
    st.experimental_rerun()
