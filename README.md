# ECP0 Persona Encoder CN 

由 [Eriga Enrich Inc.](https://ecp0.com/) 開發的語氣人格建構工具。  
此為「預設人格編碼器」MVP 版本，支援自我風格偏好設定、語氣雷達圖視覺化與 JSON 導出。

---

## 🧠 產品定位

ECP0 Persona Encoder 是一套設計給一般AI用戶的工具，協助用戶：

- 建立自己的語氣偏好設定檔（Tone Preference Profile）
- 結構化呈現語氣強度與傾向
- 匯出 JSON 作為語氣治理模組的基礎輸入（對接 LLM 或語氣治理 API）

此版本為中文介面原型，日後將推出英文版與進階角色訓練模組。

---

## 🌟 功能特色（Demo 亮點）

- 🧭 語氣六維滑桿（冷靜 vs. 熱情等）自由調整
- 📊 即時雷達圖視覺化呈現人格輪廓
- 🧩 自動產生語義描述文字
- 💾 一鍵下載 JSON 設定檔
- 📈 Log 使用者操作（僅用於後續部署觀測下載次數）

---

## 🔧 運行方式

本專案使用 [Streamlit](https://streamlit.io) 建構，部署於 Render / Fly.io 或本地皆可。  
如需本地運行：

```bash
pip install -r requirements.txt
streamlit run app.py

## 📦 專案狀態

中文版 MVP：功能測試完成
英文版製作中：將支援語氣風格自動轉換

📍 計畫中：語氣風格對照模組、人格轉譯器、Preset Library

## 📜 授權聲明
本專案為開源演示版本，禁止用於任何形式的微調商業模型或語氣分析競品。
如需 API 授權或 OEM 合作，請聯絡：ericaxvega@hotmail.com

© 2025 Eriga Enrich Inc. All rights reserved.
