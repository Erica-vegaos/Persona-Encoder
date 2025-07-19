# app.py // v0.3.1（更新 Tab1 + 開頭）
# Author: Vega (for Eri)
# Update: 加入 Tab1 雷達圖配點器，改善寬度問題，移除 step 控制

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import json

# === 🔧 補上 tone 語義轉換描述函式 ===
def describe_tone(tone_dict):
    desc = {
        "formality": ["超隨性", "輕鬆", "普通", "有禮", "極度端正"],
        "conciseness": ["極簡", "簡短", "適中", "完整", "詳細如論文"],
        "emotionality": ["冷靜", "理性中帶情", "有感情", "容易感動", "情緒爆棚"],
        "humor": ["無趣", "偶爾笑點", "幽默", "超有梗", "喜劇天花板"],
        "sarcasm": ["超級正經", "少許毒舌", "微諷刺", "嘴賤", "全自動嘴砲"],
        "assertiveness": ["超溫吞", "婉轉", "直接", "主導性強", "控制狂"]
    }
    out = []
    for key, val in tone_dict.items():
        level = min(int(val / 2.5), 4)
        out.append(f"{key}：{desc.get(key, ['?'])[level]}")
    return "，".join(out)

# === 頁面配置 ===
st.set_page_config(page_title="Eriga Persona Encoder", layout="centered")

# === Session 初始化 ===
if "user_traits" not in st.session_state:
    st.session_state["user_traits"] = {}
if "user_traits_tone_pref" not in st.session_state:
    st.session_state["user_traits_tone_pref"] = {}
if "user_intro" not in st.session_state:
    st.session_state["user_intro"] = ""
if "user_style_pref" not in st.session_state:
    st.session_state["user_style_pref"] = ""
if "template_type" not in st.session_state:
    st.session_state["template_type"] = "默認人格模板"

# === Tabs 定義 ===
tabs = st.tabs([
    "🌀 Tab0 開場介紹",
    "🧬 Tab1 預設人格",
    "🎚️ Tab2 自我配點",
    "🧾 Tab3 自我敘述",
    "📥 Tab4 結果匯出"
])


# === Tab 0: 開場動畫 + 說明 ===
with tabs[0]:
    st.title("🌀 歡迎來到 Eriga Persona Encoder")
    st.markdown("""
    這是一個互動式人格建構器，您可以透過以下步驟設定、調整、導出個人風格資料。  
    所有輸入皆保存在本機，無需上網或串接 GPT API。
    """)
    # 🔧 TODO：插入 Lottie 動畫區塊
    st.info("👉 使用上方選單切換頁面開始操作。")

# === Tab 1：AI 語氣配點器（新版左右分欄）===
with tabs[1]:
    st.header("🧬 AI 語氣配點器")

    # === 中文顯示用的 UI label 映射表 ===
    ui_labels = {
        "formality": "🤓正經",
        "conciseness": "🤐簡潔",
        "emotionality": "🤭感性",
        "humor": "🤣幽默",
        "sarcasm": "🤖嘴賤",
        "assertiveness": "🙄被討厭的勇氣"
    }

    # === 建立兩欄版面（可依需要改成 [3, 2] 調整寬度）===
    col1, col2 = st.columns([2, 3])

    with col1:
        st.markdown("#### 🎛️ 選擇你的 AI 性格：")
        formality = st.slider("正經(正經程度)", 0, 10, 5, help="從『欸中午吃啥』到『您好，請問有何需求？』")
        conciseness = st.slider("簡潔(表達長度)", 0, 10, 7, help="從『一行解完』到『以下是我的十點觀察與補充』")
        emotionality = st.slider("感性(情緒濃度)", 0, 10, 2, help="從『我不在乎你怎麼想』到『我感受到你內心的糾結』")

        st.markdown("<br>", unsafe_allow_html=True)

        humor = st.slider("幽默(風趣程度)", 0, 10, 3, help="從『一本正經像 PDF』到『笑到鍵盤打翻』")
        sarcasm = st.slider("嘴賤(諷刺含量)", 0, 10, 8, help="從『全力挺你』到『你這操作 AI 都不忍看』")
        assertiveness = st.slider("被討厭的勇氣(語氣強度)", 0, 10, 6, help="從「您說得真好，我超愛」到「認真？這也能拿出來講」")

        # === 儲存 tone_pref 結果到 session_state 中 ===
        tone_pref = {
            "formality": formality,
            "conciseness": conciseness,
            "emotionality": emotionality,
            "humor": humor,
            "sarcasm": sarcasm,
            "assertiveness": assertiveness
        }

        if "profile" not in st.session_state:
            st.session_state.profile = {}

        st.session_state.profile["tone_pref"] = tone_pref

    with col2:
        st.markdown("#### 📊 語氣雷達圖：")

        # 自訂雷達圖順序，避免文字重疊
        custom_order = ["conciseness", "formality", "emotionality", "assertiveness", "humor", "sarcasm"]
        categories = [ui_labels[k] for k in custom_order]
        values = [tone_pref[k] for k in custom_order]

        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='語氣設定',
            line=dict(color='rgba(192, 57, 43, 1)', width=3),
            fillcolor='rgba(192, 57, 43, 0.2)',
            marker=dict(size=6, color='rgba(231, 76, 60, 1)'),
            hoverinfo='skip'
        ))

        radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    showline=False,
                    showticklabels=True,
                    gridcolor='lightgray',
                    gridwidth=0.5
                ),
                angularaxis=dict(
                    rotation=90,
                    direction="clockwise",
                    tickfont=dict(size=13),
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            height=420,
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor='white',
            font=dict(family="Orbitron, Arial", size=14)
        )

        st.plotly_chart(radar, use_container_width=True, config={"staticPlot": True})

    # === Internal Log: Tab1 結構設定完成（左右欄 / tone_pref 存入）===


# === Tab 2: 使用者自我配點 ===
with tabs[2]:
    st.header("🎚️ 自我配點區")
    st.markdown("請調整下列配點，描述你的人格特質：")

    # 🔧 TODO：自行設定軸項，例如理性、外向、想像力等
    traits = {
        "理性 Rationality": "rationality",
        "外向 Extroversion": "extroversion",
        "想像力 Imagination": "imagination",
    }
    for label, key in traits.items():
        val = st.slider(label, 0, 100, 50, step=5)
        st.session_state["user_traits"][key] = val

    st.info("配點已即時儲存，可切至 Tab4 導出。")

# === Tab 3: 使用者自我描述填空 ===
with tabs[3]:
    st.header("🧾 自我介紹與偏好設定")
    st.markdown("填寫以下欄位，用於建立你的個人風格設定。")

    st.session_state["user_intro"] = st.text_area("🗣️ 自我介紹", st.session_state.get("user_intro", ""))
    st.session_state["user_style_pref"] = st.selectbox(
        "🎨 偏好語氣風格",
        ["嚴謹", "輕鬆幽默", "感性溫柔", "邏輯清晰", "開放中性"],
        index=0
    )

    st.success("填寫完成後可切至 Tab4 導出結果。")

# === Tab 4: 結果整合 + 匯出 JSON ===
with tabs[4]:
    st.header("📥 結果匯出")
    st.markdown("以下為您目前設定的所有資料：")

    result = {
        "template_type": st.session_state["template_type"],
        "user_traits": st.session_state["user_traits"],
        "user_intro": st.session_state["user_intro"],
        "style_preference": st.session_state["user_style_pref"],
        "timestamp": str(datetime.now())
    }

    st.json(result)

    st.download_button(
        label="📁 下載設定檔 (JSON)",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="persona_profile.json",
        mime="application/json"
    )

    # 🔧 TODO：可依風格變數播放不同 Lottie 動畫
    st.info("🎉 您可以根據填寫程度自由導出，所有資料將保存在下載檔案中。")
