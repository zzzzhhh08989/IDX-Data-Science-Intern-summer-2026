# California Property Close Price Prediction — Week 1 & 2 Checklist

> 项目目标：预测加州房产的 close price（最终成交价）。
> 来源：data-science-summer-2026 频道，Data Science v.4.pdf（12-Week Intern Game Plan）。

## Week 1 — Orientation & Setup（环境与上手）

- [x] 读 Task Prompt 文档，明确项目目标
- [x] 装好环境：Python 3.11.7、Git 2.50.1、VSCode
- [x] 下载 CRMLSSold 文件 → `data/sold/`，2022.01–2026.05 连续（远超 6 个月）
- [x] Trestle Property MetaData.pdf → `resources/`，关键字段已梳理
- [x] **Deliverable**：数据可访问已确认；关键列说明见 `week1_data_note.md`

## Week 2 — Data Exploration（数据探索）

- [ ] 把至少 6 个月的数据 load 进 pandas
- [ ] 探索关键变量的分布：ClosePrice（目标变量）、LivingArea、Bedrooms、Bathrooms、LotSize
- [ ] 按 task doc 限定范围：`PropertyType = Residential` 且 `PropertySubType = SingleFamilyResidence`
- [ ] **Deliverable**：Jupyter notebook `01_exploration.ipynb`，含基础 EDA 图表

## 提醒

- Week 1 下载量和 Week 2 的 load 量都是「至少 6 个月」，建议一次性下够，省得后面补。
- Week 2 的 EDA 重点是 ClosePrice 这个 target，先摸清分布和异常值，对 Week 3 预处理和 Week 4 baseline 都有帮助。
