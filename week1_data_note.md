# Week 1 Deliverable — 数据访问确认 & 关键列说明

> 项目：California Property Close Price Prediction（预测加州住宅成交价 ClosePrice）
> 数据源：CRMLS（California Regional MLS），经 Trestle/CoreLogic API 下载
> 字段定义参考：[resources/Trestle Property MetaData.pdf](resources/Trestle Property MetaData.pdf)（RESO Property 资源，完整 36 页）

## 1. 数据访问确认 ✅

- **位置**：[data/sold/](data/sold/) — 30 个 CRMLSSold 文件
- **时间覆盖**：2022.01 → 2026.05，连续无断档（远超任务要求的「≥6 个月」）
  - `CRMLSSold20220101_20231231_filled.csv` = 2022–2023 两年合并（585,834 行）
  - 其余为逐月文件（2024.01 起）
- **每文件约 80 列、1–2.5 万行**（合并文件 58 万行）

### ⚠️ 两种 schema（列结构不完全一致）
| | 带后缀 `_filled` 的月份 | 普通月份（原始） |
|---|---|---|
| 覆盖 | 2022–2023、2024.01–07、2025.01 | 2024.08 起、2025.02 起、2026 全部 |
| 独有列 | `latfilled`、`lonfilled`、`BuyerAgencyCompensation(Type)` | `BuyerAgentAOR`、`ListAgentAOR` |
| 共有列 | ~76 列（含 `Latitude`/`Longitude`） | 同左 |

- **`_filled` 填的是经纬度**（对原始 `Latitude`/`Longitude` 缺失的行做地理编码补全），**不是**填补 LivingArea/Bedrooms 等特征的缺失值——这些特征的缺失两版完全一样，仍需自己处理。
- 直接 `pd.concat` 多个月会因这 4 列对不齐而产生 NaN 列；合并前需先取「共有列」或显式对齐。

## 2. 关键列字典（聚焦建模相关）

> 空值率以 `CRMLSSold202502.csv`（18,702 行）为样本，仅供量级参考，各月略有差异。

### 目标变量
| 列名 | 类型 | 含义 | 数据情况 |
|---|---|---|---|
| **ClosePrice** | Decimal | **成交价（最终售价）= 预测目标** | 0% 空，单位美元 |

### 价格类（⚠️ 注意泄漏）
| 列名 | 类型 | 含义 | 数据情况 / 备注 |
|---|---|---|---|
| ListPrice | Decimal | 当前挂牌价 | 0.2% 空。与 ClosePrice 高度相关 |
| OriginalListPrice | Decimal | 最初挂牌价 | 0.3% 空 |

> **泄漏提醒**：任务要预测「任意住宅（在售或不在售）」的成交价。`ListPrice`/`OriginalListPrice` 只有挂牌后才存在，对「不在售」房产不可得，且与目标几乎共线。是否纳入特征要谨慎——建议先做不含价格列的基线，再单独评估加入的影响。

### 房屋结构特征（核心 feature）
| 列名 | 类型 | 含义 | 数据情况 |
|---|---|---|---|
| LivingArea | Decimal | 居住面积（平方英尺） | ~7% 空 |
| BedroomsTotal | Int | 卧室总数 | ~7% 空 |
| BathroomsTotalInteger | Int | 卫生间总数（整数） | ~5% 空 |
| YearBuilt | Int | 建成年份 | ~4% 空 |
| Stories | Int | 楼层数 | ~22% 空 |
| GarageSpaces | Decimal | 车库车位数 | ~14% 空 |
| FireplacesTotal | Int | 壁炉数 | **该月 100% 空 → 基本不可用** |
| PoolPrivateYN | Bool | 是否有私人泳池 | ~14% 空 |
| AboveGradeFinishedArea / BuildingAreaTotal | Decimal | 地上完工面积 / 建筑总面积 | 与 LivingArea 部分冗余 |

### 地块 / 面积
| 列名 | 类型 | 含义 | 数据情况 |
|---|---|---|---|
| LotSizeSquareFeet | Decimal | 地块面积（平方英尺） | ~9% 空 |
| LotSizeAcres | Decimal | 地块面积（英亩） | ~10% 空，与上者冗余（择一/互补即可） |

### 位置
| 列名 | 类型 | 含义 | 数据情况 |
|---|---|---|---|
| City | String | 城市 | ~0.1% 空 |
| PostalCode | String | 邮编 | 0% 空，强位置信号 |
| CountyOrParish | String | 县 | 0% 空 |
| Latitude / Longitude | Decimal | 纬/经度 | 该月 0% 空（旧月份可能缺，靠 `latfilled`/`lonfilled` 补） |

### 类型 / 时间 / 状态
| 列名 | 类型 | 含义 | 数据情况 / 备注 |
|---|---|---|---|
| **PropertyType** | Enum | 物业大类 | 0% 空。**建模只保留 `Residential`** |
| **PropertySubType** | Enum | 物业子类 | ~8% 空。**建模只保留 `SingleFamilyResidence`** |
| CloseDate | DateTime | 成交日期 | 0% 空，可做时间特征/切分 |
| MlsStatus | Enum | MLS 状态 | Sold 文件里基本全为 `Closed` |
| DaysOnMarket | Int | 在市天数 | 0% 空 |
| AssociationFee | Decimal | HOA 月费 | ~32% 空，且大量为 0 |
| TaxAnnualAmount | Decimal | 年度房产税 | **该月 99.5% 空 → 基本不可用** |

## 3. 建模范围（任务硬性约束）
仅使用：`PropertyType == "Residential"` **且** `PropertySubType == "SingleFamilyResidence"` 的记录。

## 4. 数据质量红旗（Week 2/3 重点处理）
1. **几乎全空、暂不可用**：`TaxAnnualAmount`（~99.5% 空）、`FireplacesTotal`（100% 空）。
2. **价格列泄漏风险**：`ListPrice` / `OriginalListPrice`，见上。
3. **冗余列**：`LotSizeSquareFeet` vs `LotSizeAcres`；`LivingArea` vs `BuildingAreaTotal`/`AboveGradeFinishedArea`——预处理时去重/单位统一。
4. **两版 schema 差异**：合并前对齐共有列。
5. **核心特征中等缺失**（5–22%）：LivingArea/Bedrooms/Bathrooms/Stories/GarageSpaces 需缺失值策略。

---
*完整字段定义见 [Trestle Property MetaData.pdf](resources/Trestle Property MetaData.pdf)；本 note 只覆盖建模相关关键列。*
