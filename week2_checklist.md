# Week 2 — Data Exploration 清单

> 目标：把多月数据 load 进 pandas，探索关键变量分布，限定到住宅单户。
> Deliverable：`01_exploration.ipynb`（含基础 EDA 图表）。
> 数据在 [data/sold/](data/sold/)；字段说明见 [week1_data_note.md](week1_data_note.md)。

## A. 加载数据
- [ ] 选定加载月份（≥6 个月；建议先用近 12 个月跑通，再视情况扩到全量）
- [ ] **对齐两版 schema**：`_filled` 月份与原始月份列不同，合并前取「共有列」（~76 列）再 `concat`
- [ ] 加 `source_file` / `year_month` 列，方便后面按月分析
- [ ] 确认行数、列数符合预期，无整列变 NaN（schema 没对齐的典型症状）

## B. 限定建模范围（任务硬性约束）
- [ ] 只保留 `PropertyType == "Residential"`
- [ ] **且** `PropertySubType == "SingleFamilyResidence"`
- [ ] 记录筛选前后行数（保留比例心里有数）

## C. 探索 5 个关键变量分布
- [ ] **ClosePrice（目标）**：直方图 + 描述统计；检查右偏 / 长尾，试 `log(ClosePrice)` 分布
- [ ] **LivingArea**：分布 + 与 ClosePrice 散点（看正相关）
- [ ] **BedroomsTotal**：分布；留意异常值（如 0 或极大）
- [ ] **BathroomsTotalInteger**：分布
- [ ] **LotSize**：`LotSizeSquareFeet` 和 `LotSizeAcres` 二选一（别重复用）；分布通常极右偏
- [ ] 关键变量空值率统计（参考 note：Living/Bed/Bath ~5–7%，LotSize ~9–10%）

## D. 异常值 / 数据质量速查
- [ ] ClosePrice 异常：极低（如 < 1万，可能是非市场交易）/ 极高离群
- [ ] LivingArea / LotSize = 0 或异常大
- [ ] 相关性热图（关键数值列 vs ClosePrice），初步看哪些特征有用

## E. （加分，为 Week 3 铺垫）时间维度
- [ ] 按 `year_month` 看 ClosePrice 中位数随时间变化（是否有价格漂移/趋势）
- [ ] 这直接影响 Week 3 选「训练窗口 X 个月」——提前观察有帮助

## F. Deliverable
- [ ] **`01_exploration.ipynb`**：含上述图表，每段配简短结论（不只贴图）
- [ ] notebook 顶部写清：用了哪几个月、筛选条件、最终样本量
- [ ] 把 EDA 主要发现（分布特点、异常值、缺失、相关性）总结成几条，供 Week 3 用

## 提醒
- 价格泄漏：`ListPrice` / `OriginalListPrice` 与 ClosePrice 几乎共线，EDA 可看，但建模特征要谨慎（见 note）。
- 几乎全空的列（`TaxAnnualAmount`、`FireplacesTotal`）EDA 阶段可直接跳过。
