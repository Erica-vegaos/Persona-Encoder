# app.py // v0.3.2-clean
# Author: Vega (for Eri)

import streamlit as st
import os
import json
import plotly.graph_objects as go
from datetime import datetime
from streamlit_lottie import st_lottie
from utils.usage_logger import log_usage
from PIL import Image



# ✅ 必須是第一個 st. 指令，放在所有 st.xx 之前
st.set_page_config(
    page_title="Eriga Persona Encoder",
    layout="centered"
)


# === 問號 icon 藍色配色 ===
st.markdown("""
    <style>
    /* 問號 icon 顏色（藍色主題） */
    [data-testid="stTooltipIcon"] svg {
        stroke: #2c3e50 !important; /* 深藍邊框 */
        fill: #d6eaf8 !important;   /* 淺藍底色 */
    }

    </style>
""", unsafe_allow_html=True)


# === 🔧 補上 tone 語義轉換描述函式 ===
def describe_tone(tone_dict):
    desc = {
        "formality": ["超隨性", "輕鬆", "普通", "有禮", "極度端正"],
        "conciseness": ["極簡", "簡短", "適中", "完整", "詳細如論文"],
        "emotionality": ["冷靜", "理性中帶情", "有感情", "容易感動", "情緒爆棚"],
        "humor": ["無趣", "偶爾笑點", "幽默", "超有梗", "喜劇天花板"],
        "sarcasm": ["超級正經", "少許毒舌", "微諷刺", "嘴賤", "全自動嘴砲"],
        "assertiveness": ["超溫吞", "婉轉", "直接", "主導性強", "控制狂"],
    }
    out = []
    for key, val in tone_dict.items():
        level = min(int(val / 2.5), 4)
        out.append(f"{key}：{desc.get(key, ['?'])[level]}")
    return "，".join(out)

# === Lottie 載入函式 ===
def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

# === 🔧 describe_traits()：將 trait 數值轉成語義描述 ===
def describe_traits(traits_dict):
    desc = {
        "verbosity_tolerance": ["熱情健談", "適中開放", "淡定冷靜", "內斂沉默", "社交厭倦"],
        "desire_for_control": ["隨遇而安", "中度引導", "習慣主導", "強勢決斷", "高控制慾"],
        "emotional_responsiveness": ["獨立理智", "偶爾依賴", "易被觸動", "情緒連結強", "情感依附型"],
        "ego_centric_focus": ["無需關注", "平衡互動", "略帶主角光環", "強烈表現慾", "極端自我中心"],
        "processing_depth": ["注意力渙散", "短時間集中", "中度深入", "長時間投入", "超長深度處理"],
        "tolerance_for_ambiguity": ["極需明確", "略感焦慮", "能接受模糊", "擁抱不確定", "無視所有標準"],
    }
    out = []
    for key, val in traits_dict.items():
        level = min(int(val / 2.5), 4)
        out.append(f"{key}：{desc.get(key, ['?'])[level]}")
    return "，".join(out)

# === TAB3 共用組句函式（空欄顯示：尚未填寫）===
def build_intro_sentences(i1, i2, i3, i4, i5, i6):
    result = []

    # 段落 1
    if i1.strip():
        result.append(f"我是{i1.strip()}")
    if i2.strip():
        result.append(f"特色是{i2.strip()}")

    # 段落 2
    like_parts = []
    if i3.strip():
        like_parts.append(i3.strip())
    if i4.strip():
        like_parts.append(i4.strip())
    if like_parts:
        result.append(f"我喜歡{'與'.join(like_parts)}")

    # 段落 3
    if i5.strip() or i6.strip():
        sentence = "希望 AI "
        sentence += f"{i5.strip()}" if i5.strip() else "（尚未指定角色）"
        if i6.strip():
            sentence += f"，但避免{i6.strip()}"
        sentence += " "
        result.append(sentence)

    return result

# === Session 初始化區塊 // v0.3.2 ===

if "profile" not in st.session_state:
    st.session_state.profile = {
        "tone_pref": {},             # 來自 Tab1：語氣偏好
        "personality_traits": {},    # 來自 Tab2：人格自我配點
        "persona_profile": {         # 來自 Tab3：自我介紹 + 使用偏好
            "self_intro": "",
            "tone_style": "",
            "avoid_triggers": [],
            "response_format": "",
            "usage_contexts": [],
            "user_extra": "",
        },
        "timestamp": "",             # Tab4 存檔時自動加入
    }



# === Tabs 定義 ===
tabs = st.tabs(
    [
        "說明",
        "AI  人格",
        "User配點",
        "文字敘述",
        "📥 結果匯出",
    ]
)


# === Tab 0: 開場動畫 + 說明 ===
with tabs[0]:
    st.title("ECP0🧬編碼語氣")

    # 安全載入動畫 + 手機 fallback 圖像
    lottie_path = os.path.join("animations", "Technology isometric ai robot brain.json")
    fallback_img_path = os.path.join("static", "animation_placeholder.png")  # 📌 確保這張圖存在

    try:
        lottie_json = load_lottiefile(lottie_path)
        if lottie_json:
            st_lottie(
                lottie_json,
                speed=1,
                loop=True,
                quality="high",
                height=320,
            )
        else:
            raise ValueError("空的 Lottie JSON")
    except Exception as e:
        st.image(fallback_img_path, caption="🧊 載入動畫失敗，改顯示圖像")


    st.markdown(
        """
    歡迎使用這個快速的 AI語氣調整 生成器 <br>
    想要微調語氣、打造個人風格？動動滑桿就搞定！<br><br>

    ✅ **快速開始**：選 AI 人格 + 自訂配點<br>
    💡 **進階玩法**：加上自我描述文字，生成更貼近你的 LLM 輸出風格<br><br>

    **資料隱私聲明**<br>
    本工具所有輸入與操作記錄皆儲存在使用者瀏覽器端的本機暫存區域，<br>
    系統不會上傳、儲存或傳送任何輸入內容至伺服器或第三方服務。<br>
    本生成器亦無法讀取或記憶使用者的個人資訊。<br>
    使用本工具不涉及任何形式的資料傳輸行為，請放心使用。
    """,
    unsafe_allow_html=True  # ← 開啟 HTML 標籤支援
    )
    st.info("👉 使用上方選單切換頁面開始操作。")
    st.markdown("---")
    st.subheader("📂 載入上次設定")

    # === Session Flag 初始化 ===
    if "load_triggered" not in st.session_state:
        st.session_state.load_triggered = False
    if "uploaded_json_data" not in st.session_state:
        st.session_state.uploaded_json_data = None
    if "load_applied" not in st.session_state:
        st.session_state.load_applied = False
    if "clear_uploader" not in st.session_state:
        st.session_state.clear_uploader = False

    # ✅ Debug 區塊：即時顯示所有關鍵 flag 狀態
    with st.expander("🛠️ Debug: Session Flag 狀態"):
        st.write("`load_triggered`:", st.session_state.load_triggered)
        st.write("`load_applied`:", st.session_state.load_applied)
        st.write("`clear_uploader`:", st.session_state.clear_uploader)
        st.write("`uploaded_json_data is not None`:", st.session_state.uploaded_json_data is not None)
        st.write("`uploader` in session_state:", "uploader" in st.session_state)

    # ✅ 清除 uploader 狀態（防止 widget 記憶導致重複上傳）
    if st.session_state.clear_uploader:
        if "uploader" in st.session_state:
            del st.session_state["uploader"]
        st.session_state.clear_uploader = False

    # ✅ UI 控件：上傳與解析
    load_checkbox = st.checkbox("🔘 我要載入先前的設定檔 (.json)")

    if load_checkbox and not st.session_state.load_triggered:
        uploaded_file = st.file_uploader(
            "請上傳 persona_profile.json 檔案",
            type=["json"],
            key="uploader"
        )
        if uploaded_file is not None:
            try:
                raw = uploaded_file.read().decode("utf-8")
                data = json.loads(raw)

                st.session_state.uploaded_json_data = data
                st.session_state.load_triggered = True
                st.session_state.clear_uploader = True  # ➜ 讓下一輪去清 uploader

                st.rerun()

            except Exception as e:
                st.error(f"⚠️ JSON 載入失敗，錯誤訊息：{str(e)}")

    # ✅ JSON 載入完畢 → 檢查格式並寫入 session
    if st.session_state.load_triggered and not st.session_state.load_applied:
        data = st.session_state.uploaded_json_data
        if data:
            required_keys = ["tone_preferences", "personality_traits", "persona_profile"]
            missing_keys = [k for k in required_keys if k not in data]

            if missing_keys:
                st.error(f"❌ JSON 結構不正確，缺少欄位：{missing_keys}")
            else:
                st.session_state.profile = {
                    "tone_pref": data.get("tone_preferences", {}),
                    "personality_traits": data.get("personality_traits", {}),
                    "persona_profile": data.get("persona_profile", {}),
                    "timestamp": data.get("timestamp", ""),
                }
                st.success("✅ 設定檔已成功載入，可前往其他分頁確認內容。")

                # ✅ 清除所有旗標
                st.session_state.load_triggered = False
                st.session_state.load_applied = True
                st.session_state.uploaded_json_data = None


# === Tab 1：AI 語氣配點器（新版左右分欄）===
with tabs[1]:
    st.header("AI 語氣配點器")
    st.markdown("選擇你的 AI 性格，問號可參考輸出影響。")


    # === 中文顯示用的 UI label 映射表 ===
    ui_labels = {
        "formality": "🤓正經",
        "conciseness": "🤐簡潔",
        "emotionality": "🤭感性",
        "humor": "🤣幽默",
        "sarcasm": "🤖嘴賤",
        "assertiveness": "🙄被討厭的勇氣",
    }

    # === 建立兩欄版面（可依需要改成 [3, 2] 調整寬度）===
    col1, col2 = st.columns([2, 3])

    with col1:

        formality = st.slider(
            "正經(正經程度)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("formality", 5),
            help="從『欸中午吃啥』到『您好，請問有何需求？』"
        )

        conciseness = st.slider(
            "簡潔(表達長度)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("conciseness", 7),
            help="從『一行解完』到『以下是我的十點觀察與補充』"
        )
        emotionality = st.slider(
            "感性(情緒濃度)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("emotionality", 2),
            help="從『我不在乎你怎麼想』到『我感受到你內心的糾結』"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        humor = st.slider(
            "幽默(風趣程度)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("humor", 3),
            help="從『一本正經像 PDF』到『笑到鍵盤打翻』"
        )

        sarcasm = st.slider(
            "嘴賤(諷刺含量)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("sarcasm", 8),
            help="從『全力挺你』到『你這操作 AI 都不忍看』"
        )

        assertiveness = st.slider(
            "被討厭的勇氣(語氣強度)",
            min_value=0,
            max_value=10,
            value=st.session_state.profile["tone_pref"].get("assertiveness", 6),
            help="從「您說得真好，我超愛」到「認真？這也能拿出來講」"
        )


        # === 儲存 tone_pref 結果到 session_state 中 ===
        tone_pref = {
            "formality": formality,
            "conciseness": conciseness,
            "emotionality": emotionality,
            "humor": humor,
            "sarcasm": sarcasm,
            "assertiveness": assertiveness,
        }

        if "profile" not in st.session_state:
            st.session_state.profile = {}

        st.session_state.profile["tone_pref"] = tone_pref

    with col2:
        st.markdown("####  ")

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
            line=dict(color='rgba(251, 100, 50, 1)', width=3),
            fillcolor='rgba(251, 100, 50, 0.2)',
            marker=dict(size=6, color='rgba(251, 100, 50, 1)'),
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
                    tickfont=dict(size=13, color='#333333'),  # 加上這行
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            height=420,
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor='white',
            font=dict(family="Orbitron, Arial", size=14, color='#333333')
        )

        st.plotly_chart(radar, use_container_width=True, config={"staticPlot": True})

    # === Internal Log: Tab1 結構設定完成（左右欄 / tone_pref 存入）===

    st.info("配點已即時儲存，可往下一步或直接切至 Tab4 導出。")


# === Tab 2: 使用者自我配點 ===
with tabs[2]:
    st.header("🎚️ 自我配點區")
    st.markdown("請調整下列配點，描述你的人格特質：")

    # ✅ 中文顯示 label 對照表
    ui_labels = {
        "verbosity_tolerance": "😑厭世",
        "desire_for_control": "📏<br>控制欲",
        "emotional_responsiveness": "🫶<br>依賴度",
        "tolerance_for_ambiguity": "🌫️不確定容忍度",
        "processing_depth": "🧠<br>注意力",
        "ego_centric_focus": "🎭自我"
    }

    # ✅ Slider + Style 包裝函式
    def styled_slider(label, key, col, default=5, help=None):
        with col:
            st.markdown('<div class="blue-slider">', unsafe_allow_html=True)
            val = st.slider(label, 0, 10, default, help=help, key=key)
            st.markdown('</div>', unsafe_allow_html=True)
            return val

    # 建立左右欄位
    col1, col2 = st.columns([2, 3])

    # 在 col1 放 slider
    with col1:
        trait_values = {}

        trait_values["verbosity_tolerance"] = styled_slider(
            "厭世(對話耐心程度)",
            key="verbosity_tolerance",
            col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("verbosity_tolerance", 2),
            help="從『我想一起深聊宇宙真理』到『你快點講完我要關視窗了』"
        )

        trait_values["desire_for_control"] = styled_slider(
            "控制欲(主導對話的需求)",
            key="desire_for_control",
            col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("desire_for_control", 7),
            help="從『你說說看，我聽聽看』到『照我說的講，不然我自己來』"
        )

        trait_values["emotional_responsiveness"] = styled_slider(
            "依賴度(與 AI 的互動慣性)",
            key="emotional_responsiveness",
            col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("emotional_responsiveness", 1),
            help="從『偶爾叫你一下』到『沒你我今天活不了』"
        )

        trait_values["tolerance_for_ambiguity"] = styled_slider(
            "不確定性容忍度",
            key="tolerance_for_ambiguity",
            col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("tolerance_for_ambiguity", 6),
            help="從『先給答案，不然我不活了』到『人生沒有正解，也沒差』"
        )

        trait_values["processing_depth"] = styled_slider(
            "注意力(對話時的集中力)",
            key="processing_depth",
            col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("processing_depth", 8),
            help="從『聊三句就 bye~』到『我可以連續提問 12 小時不眨眼』"
        )

        trait_values["ego_centric_focus"] = styled_slider(
            "自我(主角光環)",
            key="ego_centric_focus", col=col1,
            default=st.session_state.profile.get("personality_traits", {}).get("ego_centric_focus", 2),
            help="從『我不是主角也可以』到『請把攝影機對準我內心的戲』"
        )


    # ⛳ 儲存到 Session State
    if "profile" not in st.session_state:
        st.session_state.profile = {}

    st.session_state.profile["personality_traits"] = trait_values


    with col2:
        st.markdown("#### ")
        categories = [ui_labels[key] for key in trait_values.keys()]
        values = list(trait_values.values())

        radar = go.Figure()
        radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            name='人格設定',
            line=dict(color='rgba(251, 100, 50, 1)', width=3),
            fillcolor='rgba(251, 100, 50, 0.2)',
            marker=dict(size=6, color='rgba(251, 100, 50, 1)'),
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
                    tickfont=dict(size=13, color='#333333'),  # 加上這行
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            height=420,
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor='white',
            font=dict(family="Orbitron, Arial", size=14, color='#333333')  # 加上這行
        )

        st.plotly_chart(radar, use_container_width=True, config={"staticPlot": True})

    # === Internal Log: Tab2 結構設定完成（左右欄 / traits 存入）===
    st.info("配點已即時儲存，往 Tab3 或 Tab4 即可使用個人屬性。")


# === Tab 3: 使用者自我描述填空（v0.3.2）===
with tabs[3]:
    st.header("🧾 自我風格探索頁（Tab3）")
    st.markdown("依據下列填空與設定，建立你的語氣風格偏好。可於 Tab4 導出完整設定。")

    # === 還原 intro 欄位用：從 self_intro 字串解析回填空 ===
    def parse_intro_fields(self_intro_text):
        intro_fields = ["", "", "", "", "", ""]
        if "我是" in self_intro_text:
            intro_fields[0] = self_intro_text.split("我是")[1].split("特色是")[0].strip()
        if "特色是" in self_intro_text:
            intro_fields[1] = self_intro_text.split("特色是")[1].split("我喜歡")[0].strip()
        if "我喜歡" in self_intro_text:
            like_block = self_intro_text.split("我喜歡")[1].split("希望 AI")[0].strip()
            likes = like_block.split("與")
            intro_fields[2] = likes[0].strip() if len(likes) > 0 else ""
            intro_fields[3] = likes[1].strip() if len(likes) > 1 else ""
        if "希望 AI" in self_intro_text:
            post_ai = self_intro_text.split("希望 AI")[1]
            if "但避免" in post_ai:
                intro_fields[4] = post_ai.split("但避免")[0].strip()
                intro_fields[5] = post_ai.split("但避免")[1].strip()
            else:
                intro_fields[4] = post_ai.strip()
        return intro_fields

    intro_defaults = parse_intro_fields(
        st.session_state.profile["persona_profile"].get("self_intro", "")
    )

    # === Step 1：填空式風格描述 ===
    st.subheader("🧩 Step 1：填空式風格描述")
    col1, col2, col3, col4 = st.columns([1, 3, 1, 3])
    with col1:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>我是</div>", unsafe_allow_html=True)
    with col2:
        intro_1 = st.text_input("intro_1", label_visibility="collapsed", placeholder="例如：一個老師", value=intro_defaults[0])
    with col3:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>特色</div>", unsafe_allow_html=True)
    with col4:
        intro_2 = st.text_input("intro_2", label_visibility="collapsed", placeholder="例如：三分鐘熱度", value=intro_defaults[1])

    col5, col6, col7, col8 = st.columns([1, 3, 1, 3])
    with col5:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>我喜歡</div>", unsafe_allow_html=True)
    with col6:
        intro_3 = st.text_input("intro_3", label_visibility="collapsed", placeholder="例如：Kpop+韓劇", value=intro_defaults[2])
    with col7:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>還有</div>", unsafe_allow_html=True)
    with col8:
        intro_4 = st.text_input("intro_4", label_visibility="collapsed", placeholder="例如：在地深度旅遊", value=intro_defaults[3])

    col9, col10, col11, col12 = st.columns([1, 3, 1, 3])
    with col9:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>希望AI當</div>", unsafe_allow_html=True)
    with col10:
        intro_5 = st.text_input("intro_5", label_visibility="collapsed", placeholder="例如：嚴厲但溫柔的人生導師", value=intro_defaults[4])
    with col11:
        st.markdown("<div style='text-align: center; padding-top: 0.6em;'>但避免</div>", unsafe_allow_html=True)
    with col12:
        intro_6 = st.text_input("intro_6", label_visibility="collapsed", placeholder="例如：理想化、過度簡化", value=intro_defaults[5])

    intro_sentences = build_intro_sentences(
        intro_1, intro_2, intro_3, intro_4, intro_5, intro_6
    )

    if any(intro_sentences):
        st.markdown("### 🧠 你的語氣偏好摘要")
        st.info("。".join([s for s in intro_sentences if s]) + "。")

    # === Step 2：語氣偏好與使用場景設定 ===
    st.subheader("🎛️ Step 2：語氣偏好與使用場景設定")

    tone_style_list = ["專業", "友善", "嚴肅", "輕鬆", "邏輯派", "哲學派"]
    tone_style_val = st.session_state.profile["persona_profile"].get("tone_style", "友善")

    tone_style = st.selectbox(
        "你偏好的語氣風格是？",
        tone_style_list,
        index=tone_style_list.index(tone_style_val) if tone_style_val in tone_style_list else 1
    )

    avoid_triggers = st.multiselect(
        "你希望 AI 避免哪些語氣或反應？",
        ["無條件迎合", "過度擬人", "碎碎念", "反問句", "說教"],
        default=st.session_state.profile["persona_profile"].get("avoid_triggers", [])
    )

    response_format_list = [
        "像筆記一樣列點", "分段講清楚", "像老師一步步推理", "一句話先給我結論，再細講", "隨便啦，只要清楚就好"
    ]
    response_format_val = st.session_state.profile["persona_profile"].get("response_format", "分段講清楚")

    response_format = st.selectbox(
        "你喜歡的回應格式是？",
        response_format_list,
        index=response_format_list.index(response_format_val) if response_format_val in response_format_list else 1
    )

    usage_contexts = st.multiselect(
        "你預期在哪些情境中使用這個 AI？",
        ["思考與決策輔助", "內容撰寫與潤飾", "自我探索", "日常問答與知識搜尋"],
        default=st.session_state.profile["persona_profile"].get("usage_contexts", [])
    )

    # === Step 3：自由補充區 ===
    st.subheader("📝 Step 3：想讓 AI 知道的事（選填）")

    user_extra = st.text_area(
        "可以簡單說說你現在的狀態、生活近況或想學的東西，也可以當作是給 AI 的自我介紹。",
        placeholder="例如：我剛換工作，對未來有點不安／我最近在學日文，也在找學習方法／我平常很忙，希望你回覆我要快一點",
        value=st.session_state.profile["persona_profile"].get("user_extra", "")
    )

    # === 儲存所有值回 session ===
    st.session_state.profile["persona_profile"] = {
        "self_intro": " ".join(intro_sentences) if intro_sentences else "",
        "tone_style": tone_style,
        "avoid_triggers": avoid_triggers,
        "response_format": response_format,
        "usage_contexts": usage_contexts,
        "user_extra": user_extra.strip(),
    }

    st.success("🧭 已儲存語氣偏好設定，可切至 Tab4 導出或套用")



# === Tab 4: 結果整合 + 匯出 JSON / TXT with Section Selection ===
with tabs[4]:
    st.header("📥 結果匯出")
    st.markdown("請選擇您想要匯出的資料區塊，並選擇格式：")

    # 👉 字典本身不能使用 HTML <br>，會噴錯（建議只在顯示用 markdown 使用）
    export_options = {
        "語氣偏好設定（Tone Preferences）": "tone_preferences",
        "人格特質描述（Personality Traits）": "personality_traits",
        "自我介紹資訊（Persona Profile）": "persona_profile",
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("語氣偏好設定<br><sub>(Tone Preferences)</sub>", unsafe_allow_html=True)
        export_tone = st.checkbox(" ", key="export_tone_checkbox", value=st.session_state.get("tone", True))

    with col2:
        st.markdown("人格特質描述<br><sub>(Personality Traits)</sub>", unsafe_allow_html=True)
        export_traits = st.checkbox(" ", key="export_traits_checkbox", value=st.session_state.get("traits", True))


    with col3:
        st.markdown("自我介紹資訊<br><sub>(Persona Profile)</sub>", unsafe_allow_html=True)
        export_profile = st.checkbox(" ", key="export_profile_checkbox", value=st.session_state.get("profile", True))
    # ⏺ 將使用者勾選的區塊，轉為要匯出的 key list
    selected_sections_keys = []

    if export_tone:
        selected_sections_keys.append("tone_preferences")
    if export_traits:
        selected_sections_keys.append("personality_traits")
    if export_profile:
        selected_sections_keys.append("persona_profile")

    # -- 匯出結果整合
    result = {
        "timestamp": datetime.now().isoformat()
    }

    if "tone_preferences" in selected_sections_keys:
        result["tone_preferences"] = st.session_state.profile.get("tone_pref", {})

    if "personality_traits" in selected_sections_keys:
        result["personality_traits"] = st.session_state.profile.get("personality_traits", {})

    if "persona_profile" in selected_sections_keys:
        result["persona_profile"] = st.session_state.profile.get("persona_profile", {})




    # TXT 匯出組裝
    txt_lines = []
    if "tone_preferences" in result:
        txt_lines.append("[🧬 Tone Preferences]")
        for k, v in result["tone_preferences"].items():
            txt_lines.append(f"{k}: {v}")
    if "personality_traits" in result:
        txt_lines.append("\n[🌟 Personality Traits]")
        for k, v in result["personality_traits"].items():
            txt_lines.append(f"{k}: {v}")
    if "persona_profile" in result:
        txt_lines.append("\n[🧑 Persona Profile]")
        for k, v in result["persona_profile"].items():
            txt_lines.append(f"{k}: {v}")
    txt_lines.append(f"\n📅 Timestamp: {result['timestamp']}")
    txt_output = "\n".join(txt_lines)

    st.json(result)  # 可視化 JSON 結構


    # === 📁 JSON / TXT 雙下載按鈕（左右排列）===
    col1, col2 = st.columns(2)

    with col1:
        if st.download_button(
            label="📁 下載設定檔 (JSON)",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="persona_profile.json",
            mime="application/json",
        ):
            log_usage("TAB4_download_json")

    with col2:
        if st.download_button(
            label="📝 下載設定檔 (TXT)",
            data=txt_output,
            file_name="persona_profile.txt",
            mime="text/plain",
        ):
            log_usage("TAB4_download_txt")





    st.markdown("""
    <div style="background-color: #e1f5fe; padding: 10px; border-radius: 5px;">
    🎉 您可以根據填寫程度自由導出，所有資料將保存在下載檔案中。<br><br>
    <strong>建議貼給 AI JSON 檔（一般記事本即可打開使用），AI 讀取 JSON 檔比記事本檔更有效。</strong><br><br>
    若在長期對話內發現 AI 忘記你的設定了，請重複貼上 JSON /TXT 內容，讓 AI 重新對齊你的偏好。
    </div>
    """, unsafe_allow_html=True)


    # === 🧹 美化版：清除設定區塊 ===
    st.markdown("---")

    with st.container():
        st.markdown(
            """
            <div style='padding: 10px; background-color: #fff4e6; border-radius: 5px;'>
                <strong>⚠️ 此操作會清除所有已填寫資料，回到預設值</strong><br>
                不小心填錯或想從頭來過，可按下方按鈕清除所有記憶。<br>
                <span style="color: gray; font-size: 0.9em;">＊請點擊兩次完全清除</span>
            </div>
            """,
            unsafe_allow_html=True
        )

        clear_button = st.button(" 🗑️ 我確定要清除所有記憶", type="secondary")

        if clear_button:
            # 清除主要欄位
            if "profile" in st.session_state:
                del st.session_state["profile"]

            # 清除 Tab0 Flag
            for k in ["load_triggered", "load_applied", "uploaded_json_data", "clear_uploader"]:
                if k in st.session_state:
                    del st.session_state[k]

            # 清除 Tab2 用到的 slider keys（若有 key）
            for k in [
                "verbosity_tolerance", "desire_for_control", "emotional_responsiveness",
                "tolerance_for_ambiguity", "processing_depth", "ego_centric_focus"
            ]:
                if k in st.session_state:
                    del st.session_state[k]

            # 初始化空白結構，避免報錯
            st.session_state.profile = {
                "tone_pref": {},
                "personality_traits": {},
                "persona_profile": {
                    "self_intro": "",
                    "tone_style": "",
                    "avoid_triggers": [],
                    "response_format": "",
                    "usage_contexts": [],
                    "user_extra": "",
                },
                "timestamp": "",
            }

            st.success("🧹 已清除，目前為空白狀態（請點第二次即可完全清除記憶）")
            
def log_usage(event_name: str):
    if "usage_log" not in st.session_state:
        st.session_state["usage_log"] = []
    st.session_state["usage_log"].append({
        "event": event_name,
        "timestamp": datetime.now().isoformat()
    })
    print(f"[LOG] {event_name} @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")