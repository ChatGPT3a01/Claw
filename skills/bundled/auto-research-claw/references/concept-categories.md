# 概念分類規則（20 個子目錄）

自動提取論文中的技術術語（`[[概念]]` wikilink），歸類到以下 20 個子目錄。

## 分類規則

| # | 子目錄 | 歸類標準 | 範例關鍵字 |
|---|--------|----------|-----------|
| 1 | `1-自然語言處理` | NLP、文本分析、語言模型、對話 | LLM, BERT, GPT, ChatGPT, RAG, Prompt Engineering |
| 2 | `2-教育科技` | 教學科技、數位學習、自適應學習、學習平台 | Adaptive Learning, LMS, MOOC, 教學策略, 數位教材 |
| 3 | `3-學習分析` | 學習歷程、評量、學生行為預測 | Learning Analytics, 學習成效, 形成性評量, 預測模型 |
| 4 | `4-生成模型` | 擴散模型、GAN、VAE、Flow、圖像生成 | Diffusion, DDPM, Stable Diffusion, DiT, Flow Matching |
| 5 | `5-電腦視覺` | 影像辨識、物件偵測、分割、3D視覺 | CNN, YOLO, ViT, NeRF, 3D Gaussian Splatting |
| 6 | `6-強化學習` | RL 算法、策略優化、值函數、獎勵模型 | PPO, DPO, RLHF, Q-Learning, SAC |
| 7 | `7-深度學習基礎` | 通用 DL 架構、Attention、MoE、最佳化 | Transformer, Mamba, MoE, Dropout, BatchNorm |
| 8 | `8-多模態AI` | 視覺-語言模型、跨模態學習 | CLIP, GPT-4V, LLaVA, Multimodal, VLM |
| 9 | `9-AI智能體` | Agent、工具使用、自主推理、程式碼生成 | WebAgent, Code Generation, Tool Use, ReAct |
| 10 | `10-資訊檢索` | 搜尋、推薦系統、知識圖譜 | RAG, Embedding, Vector DB, Knowledge Graph |
| 11 | `11-社會科學方法` | 問卷、量表、質性研究、混合研究法 | Likert Scale, SEM, 紮根理論, 行動研究, 設計本位研究 |
| 12 | `12-統計與資料分析` | 統計檢定、效果量、迴歸、機器學習 | t-test, ANOVA, Cohen's d, Random Forest, SVM |
| 13 | `13-機器人與自動化` | 機器人策略、導航、控制、硬體 | Diffusion Policy, SLAM, MPC, ROS |
| 14 | `14-資料集與基準` | Dataset、Benchmark、評估基準 | ImageNet, COCO, GLUE, SQuAD |
| 15 | `15-安全與倫理` | AI 安全、對抗攻擊、偏見、公平性 | Adversarial Attack, Fairness, Alignment, AI Ethics |
| 16 | `16-語音與音訊` | 語音辨識、語音合成、音訊處理 | ASR, TTS, Whisper, WaveNet |
| 17 | `17-偏鄉與特殊教育` | 偏鄉教育、特教、融合教育、文化回應教學 | 偏鄉, 遠距教學, 差異化教學, UDL |
| 18 | `18-課程與教學設計` | 教案設計、課綱、素養導向、評量設計 | 108課綱, 素養, PBL, 翻轉教學, 差異化教學 |
| 19 | `19-人機互動` | UI/UX、互動設計、可用性、XR | HCI, UX, AR, VR, 使用者體驗, 人機介面 |
| 20 | `20-系統與工程` | 軟體架構、分散式系統、MLOps | Docker, Kubernetes, CI/CD, MLflow |
| 0 | `0-待分類` | 完全無法判斷時才歸入此類 | — |

## 分類原則

1. **優先精確匹配**：先看論文的 `method_name` 和 `tags`，再看標題和摘要
2. **一詞一類**：每個概念只歸入一個最相關的類別
3. **層級優先**：如果同時符合多個類別，選擇最具體的那個
4. **0-待分類 是最後手段**：除非真的完全無法判斷，否則不用
5. **台灣論文概念**：台灣博碩士論文中出現的中文術語，優先用中文建立概念筆記，再附上英文對照
6. **跨領域歸類**：教育科技論文中的技術概念歸入技術類（如 NLP、深度學習），教育面歸入教育類（如教育科技、學習分析）

## 概念筆記格式

```markdown
---
aliases: ["{english_name}", "{其他中文別名}"]
category: "{分類名}"
---

# {概念名稱}

**英文**：{english_name}
**分類**：[[{分類名}]]

## 定義
{一段話定義}

## 相關論文
- [[論文筆記1]]
- [[論文筆記2]]

## 相關概念
- [[相關概念1]]
- [[相關概念2]]
```
