import os
import json
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
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
        for i in range(0, len(df), 1):
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

# 读取词语数据（每个词只由 fast45.csv 中的字组成）
@st.cache_data
def load_words():
    try:
        with open('words.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except Exception as e:
        st.warning(f"读取词语数据时出错: {e}")
        return []

# 加载数据
text_list = load_data()
words_data = load_words()

if not text_list:
    st.stop()

# 按首次出现顺序去重的字符列表（用于词语参考表）
_seen = set()
ordered_unique_chars = []
for _ch in text_list:
    if _ch not in _seen:
        _seen.add(_ch)
        ordered_unique_chars.append(_ch)

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

if words_data:
    st.caption(f"📚 已加载 {len(words_data)} 个词语（全部仅由表中汉字组成）")

# 初始化状态
if 'current_text' not in st.session_state:
    st.session_state.current_text = ""
if 'start_time' not in st.session_state:
    st.session_state.start_time = None
if 'is_running' not in st.session_state:
    st.session_state.is_running = False
if 'interval' not in st.session_state:
    st.session_state.interval = 5.0
if 'trigger_speech' not in st.session_state:
    st.session_state.trigger_speech = False
if 'display_mode' not in st.session_state:
    st.session_state.display_mode = "字"

# 显示内容模式：单字 or 词语
mode_label = st.radio(
    "显示内容",
    ["🔤 单字", "📝 词语"],
    horizontal=True,
    disabled=not words_data,
    help=None if words_data else "未找到 words.json，暂时只能显示单字",
)
st.session_state.display_mode = "字" if mode_label == "🔤 单字" else "词"

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


def get_valid_pool(min_idx, max_idx, mode):
    """根据当前模式和范围，返回可供随机抽取的字符或词语列表"""
    if mode == "字":
        return text_list[min_idx - 1:max_idx]
    # 词语模式：词语中每个字的位置都必须落在所选范围内
    return [
        w["word"] for w in words_data
        if all(min_idx <= p <= max_idx for p in w["positions"])
    ]


valid_pool = get_valid_pool(min_index, max_index, st.session_state.display_mode)

# 显示当前范围的预览
unit = "字" if st.session_state.display_mode == "字" else "词"
if st.session_state.display_mode == "字":
    st.info(f"将从第 {min_index} 个字到第 {max_index} 个字中随机选择显示 (共 {max_index - min_index + 1} 个字)")
else:
    st.info(f"将从第 {min_index} 个字到第 {max_index} 个字的范围内，随机选择只由这些字组成的词语 (共找到 {len(valid_pool)} 个词)")
    if not valid_pool:
        st.warning("⚠️ 当前范围内的字还不能组成任何词语，请扩大范围（建议至少到第20个字以上）")

if valid_pool:
    preview_count = min(5, len(valid_pool))
    preview_text = "、".join(valid_pool[:preview_count])
    if len(valid_pool) > 5:
        preview_text += "..."
    st.write(f"预览: {preview_text}")

# 控制按钮
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("▶️ 开始显示", disabled=st.session_state.is_running or not valid_pool):
        st.session_state.start_time = time.time()
        st.session_state.is_running = True
        st.rerun()

with col2:
    if st.button("⏸️ 暂停", disabled=not st.session_state.is_running):
        st.session_state.is_running = False
        st.session_state.start_time = None

with col3:
    if st.button("🔄 手动刷新", disabled=not valid_pool):
        st.session_state.current_text = random.choice(valid_pool)

with col4:
    if st.button("🔊 朗读", disabled=not st.session_state.current_text):
        # 触发朗读并重新计时
        st.session_state.trigger_speech = True
        if st.session_state.is_running:
            st.session_state.start_time = time.time()  # 重新计时
        st.rerun()

# 显示区域
display_container = st.container()

# 更新显示内容
if st.session_state.is_running and st.session_state.start_time is not None:
    current_time = time.time()
    elapsed_time = current_time - st.session_state.start_time

    if elapsed_time >= st.session_state.interval:
        if valid_pool:
            st.session_state.current_text = random.choice(valid_pool)
        else:
            st.session_state.current_text = "范围无效"

        st.session_state.start_time = current_time

# 根据文字长度自适应字号（词语比单字长，字号相应缩小）
_text_len = len(st.session_state.current_text)
if _text_len <= 1:
    _font_size = 200
elif _text_len == 2:
    _font_size = 140
elif _text_len == 3:
    _font_size = 100
else:
    _font_size = 80

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
                    font-size: {_font_size}px;
                    font-weight: bold;
                    margin: 0;
                    color: #1f1f1f;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                ">{st.session_state.current_text}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # 添加语音合成功能
        if st.session_state.trigger_speech:
            # 使用组件方式触发语音
            speech_html = f"""
            <div id="speech-container">
                <script>
                function speakText() {{
                    if ('speechSynthesis' in window) {{
                        // 确保先停止当前语音
                        window.speechSynthesis.cancel();

                        setTimeout(() => {{
                            const utterance = new SpeechSynthesisUtterance('{st.session_state.current_text}');
                            utterance.lang = 'zh-CN';
                            utterance.rate = 0.5;
                            utterance.pitch = 1.0;
                            utterance.volume = 1.0;

                            // 添加事件监听
                            utterance.onstart = function() {{
                                console.log('开始朗读: {st.session_state.current_text}');
                            }};

                            utterance.onend = function() {{
                                console.log('朗读完成');
                            }};

                            utterance.onerror = function(event) {{
                                console.log('朗读错误:', event.error);
                            }};

                            window.speechSynthesis.speak(utterance);
                        }}, 100);
                    }} else {{
                        alert('您的浏览器不支持语音合成功能，请使用Chrome、Edge或Safari浏览器');
                    }}
                }}

                // 立即执行
                speakText();
                </script>
            </div>
            """
            components.html(speech_html, height=0)
            st.session_state.trigger_speech = False

        # 添加键盘事件监听 - 使用独立的HTML组件
        keyboard_html = f"""
        <script>
        document.addEventListener('keydown', function(event) {{
            if (event.code === 'Space') {{
                event.preventDefault();

                // 直接触发语音合成
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    setTimeout(() => {{
                        const utterance = new SpeechSynthesisUtterance('{st.session_state.current_text}');
                        utterance.lang = 'zh-CN';
                        utterance.rate = 0.5;
                        utterance.pitch = 1.0;
                        utterance.volume = 1.0;
                        window.speechSynthesis.speak(utterance);
                    }}, 100);
                }}
            }}
        }});
        </script>
        """
        components.html(keyboard_html, height=0)

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
    1. **显示内容**: 选择"🔤 单字"随机显示单个汉字，或"📝 词语"随机显示由已学汉字组成的词语
    2. **设置范围**: 输入你想要显示的字符范围（从第几个到第几个）；词语模式下，只会显示词语中每个字都落在该范围内的词
    3. **调整间隔**: 使用滑块设置每次显示的时间间隔
    4. **开始显示**: 点击"开始显示"按钮开始自动随机显示
    5. **暂停**: 点击"暂停"按钮停止自动显示
    6. **手动刷新**: 点击"手动刷新"立即显示一个新的随机字符/词语
    7. **🔊 朗读**: 点击"朗读"按钮或按下**空格键**朗读当前内容
       - 朗读速度已调慢，便于学习
       - 朗读后会重新开始计时（如果正在自动显示）

    **注意**:
    - 位置编号从1开始计算，程序会自动转换为正确的数组索引
    - 词语库中的所有词语都只使用本表中的汉字组成，不会出现表外的字
    - 语音功能需要浏览器支持，建议使用Chrome或Edge浏览器
    - 按空格键可以快速朗读当前字符/词语
    """)

# 显示完整的字符表格
st.markdown("---")
st.subheader("📋 完整字符表")
st.write("以下是所有字符及其对应的位置编号，每行显示20个字符：")

if text_list:
    # 创建表格数据
    table_data = []
    for i in range(0, len(text_list), 20):
        row_chars = []
        row_numbers = []

        # 获取这一行的字符和编号
        for j in range(20):
            if i + j < len(text_list):
                row_chars.append(text_list[i + j])
                row_numbers.append(str(i + j + 1))  # 位置编号从1开始
            else:
                row_chars.append("")
                row_numbers.append("")

        # 添加字符行和编号行
        table_data.append(row_chars)
        table_data.append(row_numbers)

    # 创建DataFrame并显示
    columns = [f"第{i+1}列" for i in range(20)]
    df_display = pd.DataFrame(table_data, columns=columns)

    # 使用HTML表格显示，交替行颜色
    html_table = "<table style='width:100%; border-collapse: collapse; font-size: 14px;'>"

    for idx, row in df_display.iterrows():
        if idx % 2 == 0:  # 字符行
            html_table += f"<tr style='background-color: #f8f9fa; border: 1px solid #dee2e6;'>"
            for col in row:
                if col:  # 如果不为空
                    html_table += f"<td style='text-align: center; padding: 8px; font-size: 18px; font-weight: bold; border: 1px solid #dee2e6;'>{col}</td>"
                else:
                    html_table += f"<td style='text-align: center; padding: 8px; border: 1px solid #dee2e6;'></td>"
        else:  # 编号行
            html_table += f"<tr style='background-color: #e9ecef; border: 1px solid #dee2e6;'>"
            for col in row:
                if col:  # 如果不为空
                    html_table += f"<td style='text-align: center; padding: 4px; font-size: 12px; color: #6c757d; border: 1px solid #dee2e6;'>#{col}</td>"
                else:
                    html_table += f"<td style='text-align: center; padding: 4px; border: 1px solid #dee2e6;'></td>"
        html_table += "</tr>"

    html_table += "</table>"

    st.markdown(html_table, unsafe_allow_html=True)

    # 添加搜索功能
    st.markdown("---")
    st.subheader("🔍 查找字符")
    search_char = st.text_input("输入要查找的字符：", placeholder="例如：的")

    if search_char:
        positions = []
        for i, char in enumerate(text_list):
            if char == search_char:
                positions.append(i + 1)  # 位置编号从1开始

        if positions:
            st.success(f"找到字符 '{search_char}' 在以下位置：{', '.join(map(str, positions))}")
        else:
            st.warning(f"未找到字符 '{search_char}'")

        if words_data and len(search_char) == 1:
            related_words = [w["word"] for w in words_data if search_char in w["word"]]
            if related_words:
                shown = related_words[:12]
                more = f" 等共 {len(related_words)} 个" if len(related_words) > 12 else ""
                st.write(f"📚 含有该字的词语举例：{'、'.join(shown)}{more}")
else:
    st.error("没有字符数据可显示")

# 词语参考表：每个字对应的常用词语
if words_data:
    st.markdown("---")
    st.subheader("📚 词语参考表")
    st.write(f"共收录 {len(words_data)} 个词语，全部仅由本表中的汉字组成。下表按字出现顺序列出每个字最常见的词语（最多8个）：")

    words_by_char = {}
    for w in words_data:
        for ch in dict.fromkeys(w["word"]):  # 去重但保持顺序
            words_by_char.setdefault(ch, []).append(w["word"])

    rows = []
    for ch in ordered_unique_chars:
        sample = words_by_char.get(ch, [])[:8]
        rows.append({"字": ch, "词语示例": "、".join(sample) if sample else "（暂无组词）"})

    df_words = pd.DataFrame(rows)
    st.dataframe(df_words, use_container_width=True, height=400)
