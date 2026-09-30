# 🖱️ 遊戲連點器 Game Clicker

簡單好用的繁體中文滑鼠連點器，免註冊、免安裝，Windows / macOS / Linux 都能跑。

## 功能
- 自訂點擊間隔（最低 1 毫秒）＋**隨機抖動**，避免間隔死板
- 左鍵 / 右鍵 / 中鍵、雙擊、**按住不放**模式（蓄力、採集）
- 指定點擊次數（0 = 無限）
- 開始前倒數，讓你有時間切回遊戲
- **全域熱鍵**（預設 F6）開始／停止，遊戲在前景也有效
- 停止時保證放開按鍵，不會讓滑鼠卡住

## 使用
```bash
pip install -r requirements.txt
python autoclicker.py
```
需要 Python 3.9+（含 tkinter；Linux 需 `sudo apt install python3-tk`）。
連點會點在**游標目前位置**，開始後把游標放到遊戲目標處即可。

## 注意事項
- 部分遊戲以系統管理員權限執行，連點器也要「以系統管理員身分執行」才會有效。
- macOS 需在「系統設定 → 隱私權與安全性」授權「輔助使用」與「輸入監控」。
- 請遵守遊戲服務條款；線上遊戲使用自動化工具可能導致帳號受罰，風險自負。

## 測試
```bash
python -m unittest discover -s tests
```
