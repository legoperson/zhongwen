import os
import pandas as pd
import streamlit as st
import numpy as np
import time
import random

# 设置页面配置
st.set_page_config(page_title="汉字随机显示器", layout="centered")

# 读取CSV文件
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('fast45.csv', header=None)
        df = df.dropna()
        
        # 创建一个空列表来存储结果
        text_list = []
        # 遍历CSV文件的行，步长为2（即奇数行是字，偶数行是对应的数字）
        for i in range(0, len(df), 2):
            characters = df.iloc[i].tolist()     # 获取奇数行的字符
            for j in characters:
                if pd.notna(j):  # 确保不是NaN值
                    text_list.append(str(j))
        return text_list
    except FileNotFoundError:
        st.error("找不到 'fast45.csv' 文件，请确保文件在当前目录中")
        return []
    except Exception as e:
        st.error(f"读取文件时出错: {e}")
        return []

# 加载数据
text_list = load_data()

if not text_list:
    st.stop()

# 页面标题
st.title("🔤 汉字随机显示器")

# 显示数据加载信息
if text_list:
    st.success(f"✅ 成功读取 {len(text_list)} 个字符")
    
    # 显示前10个字符作为示例
    if len(text_list) >= 10:
        sample_chars = "、".join(text_list[:10])
        st.write(f"📋 前10个字符示例: {sample_chars}...")
    else:
        sample_chars = "、".join(text_list)
        st.write(f"📋 所有字符: {sample_chars}")
else:
    st.error("❌ 未能读取到任何字符")

# 初始化状态
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'interval' not in st.session_state:
    st.session_state.interval = 5.0

# 创建两列布局
col1, col2 = st.columns(2)

with col1:
    min_index = st.number_input(
        "起始位置 (从第几个字开始)", 
        min_value=1, 
        max_value=len(text_list), 
        value=1,
        step=1
    )

with col2:
    max_index = st.number_input(
        "结束位置 (到第几个字结束)", 
        min_value=1, 
        max_value=len(text_list), 
        value=min(100, len(text_list)),
        step=1
    )

# 显示间隔设置
interval = st.slider("显示间隔 (秒)", min_value=1.0, max_value=10.0, value=5.0, step=0.5)
st.session_state.interval = interval

# 验证输入范围
if min_index > max_index:
    st.error("⚠️ 起始位置不能大于结束位置！")
    st.stop()

if max_index > len(text_list):
    st.error(f"⚠️ 结束位置不能大于总字符数 ({len(text_list)})！")
    st.stop()

# 显示当前范围的预览
st.info(f"将从第 {min_index} 个字到第 {max_index} 个字中随机选择显示 (共 {max_index - min_index + 1} 个字)")

if max_index >= min_index and len(text_list) >= max_index:
    preview_count = min(5, max_index - min_index + 1)
    preview_text = "、".join(text_list[min_index-1:min_index-1+preview_count])
    if max_index - min_index + 1 > 5:
        preview_text += "..."
    st.write(f"预览: {preview_text}")

# 控制按钮
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("▶️ 开始显示", disabled=st.session_state.is_running):
        st.session_state.start_time = time.time()
        st.session_state.is_running = True
        st.rerun()

with col2:
    if st.button("⏸️ 暂停", disabled=not st.session_state.is_running):
        st.session_state.is_running = False
        st.session_state.start_time = None

with col3:
    if st.button("🔄 手动刷新"):
        if min_index <= max_index <= len(text_list):
            valid_text_list = text_list[min_index-1:max_index]
            if valid_text_list:
                st.session_state.current_text = random.choice(valid_text_list)

# 显示区域
display_container = st.container()

# 更新显示内容
if st.session_state.is_running and st.session_state.start_time is not None:
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time
    
    if elapsed_time >= st.session_state.interval:
        # 确保索引范围有效
        if min_index <= max_index <= len(text_list):
            valid_text_list = text_list[min_index-1:max_index]  # 转换为0索引
            if valid_text_list:
                st.session_state.current_text = random.choice(valid_text_list)
            else:
                st.session_state.current_text = "范围无效"
        else:
            st.session_state.current_text = "索引超出范围"
        
        st.session_state.start_time = current_time

# 显示当前文字
with display_container:
    if st.session_state.current_text:
        # 创建居中的大字显示
        st.markdown(
            f"""
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 300px;
                background-color: #f0f2f6;
                border-radius: 10px;
                margin: 20px 0;
            ">
                <p style="
                    font-size: 200px;
                    font-weight: bold;
                    margin: 0;
                    color: #1f1f1f;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                ">{st.session_state.current_text}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="
                display: flex;
                justify-content: center;
                align-items: center;
                height: 300px;
                background-color: #f0f2f6;
                border-radius: 10px;
                margin: 20px 0;
                border: 2px dashed #ccc;
            ">
                <p style="font-size: 24px; color: #666; margin: 0;">点击"开始显示"按钮开始</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

# 状态指示器
if st.session_state.is_running:
    st.success("🟢 正在运行中...")
    # 自动刷新
    time.sleep(0.1)
    st.rerun()
else:
    st.info("⏸️ 已暂停")

# 添加说明
with st.expander("使用说明"):
    st.write("""
    1. **设置范围**: 输入你想要显示的字符范围（从第几个到第几个）
    2. **调整间隔**: 使用滑块设置每次显示的时间间隔
    3. **开始显示**: 点击"开始显示"按钮开始自动随机显示
    4. **暂停**: 点击"暂停"按钮停止自动显示
    5. **手动刷新**: 点击"手动刷新"立即显示一个新的随机字符
    
    **注意**: 位置编号从1开始计算，程序会自动转换为正确的数组索引。
    """)
