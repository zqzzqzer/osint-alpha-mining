# 数据契约

小任务可直接填写证据卡；批量研究用 UTF-8 JSON/JSONL。未知用 null；空数组表示已经检查且没有记录，不代替未检查。时间使用 ISO 8601 并带时区；只有日期时保留精度，不补造时分秒。

## 研究账本

| 记录 | 必要字段 |
|---|---|
| run | run_id、as_of、市场/行业/窗口、来源范围、实际读取量、限制、规则版本 |
| evidence | evidence_id、kind(source/search_log/analysis)、url 或本地定位、最小必要摘录/摘要、published_at、first_seen_at、retrieved_at、root_source_id、independence_group_id、独立性依据 |
| source_profile | source_id、身份自述、核验身份及依据、领域、信息距离、分享目的、公开利益、历史样本与限制 |
| claim | claim_id、精确命题、类别、实体、事件日期、evidence_refs、来源位置、支持/反驳关系、核验状态 |
| event | case_id、critical_claim_ids、事件类型/窗口、聚合理由、重复与独立根源数、传导链、公司映射、影响方向、反证、催化、失效条件 |
| expectation | 变量/单位/周期、baseline_type、基线值/范围、基线来源及时间、新信息及时间、差异、适用限制 |
| revision | case_id、version、研究时间、旧状态、新状态、变更依据、原预测和到期结果 |

root_source_id 标识原始出处；independence_group_id 标识经核验可视为同一信息生产过程的材料组。未知独立性保留 null。检索日志与分析备忘不是独立事实来源，不能计入根源数。

历史材料记录至少区分事件发生、公开发表、系统首次看见与本次抓取时间。历史回放只允许使用当时可得版本；现在找到的旧帖可用于回顾性研究，但不能冒充当时系统已经获取的样本。

## 评分脚本输入（完整示例见 assets/example-case.json）

顶层为一个 case 对象或 case 对象数组。字段：

- case_id：非空字符串，同一批不能重复。
- as_of：带时区的研究截止时间。
- evidence：对象数组，每项含 id、kind、locator、summary、available_at。available_at 表示该证据在本轮评估中可用的时间；未来材料不准参与评分。原始证据还需在研究账本保存前述更细时间。
- assessments：包含 credibility、opportunity 两个对象，维度必须与 scoring.md 一致。每维度为 `{value: 0到4或null, reason: 非空说明, evidence_refs: [证据ID]}`。value=null 时说明缺什么，引用可为空。
- gates：fact_status、mapping_verified、counterevidence_checked、material_contradiction_unresolved、expectation_baseline_established。
- gate_evidence：与 gates 同名的证据 ID 数组。fact_status 除 unverified 外必须有依据；其余 gate 为 true 或 false 时都需要依据，null 表示未知。

fact_status 取 unverified/corroborated/conflicted/refuted；其余 gate 取 true/false/null。脚本只检查字段、范围、时间和引用存在，不验证原文真实性或 gate 的人工结论。

评分公式版本写入输出。自定义权重与阈值时，先在本项目另存并版本化规则和脚本，再用同一批输入复核，不悄悄修改已发布规则。默认版本 research-v1.0。

## 输出解释

每个分数输出 observed_score、coverage、priority_score、missing_dimensions。research_state 附 state_reasons，指出缺少的门槛。

候选表附关键命题、来源链接和时间、独立性、影响方向、两项分数及覆盖率、传导断点、预期基线、反证、下一个动作。不要只交股票名单和数字。
