# 评分与候选状态

以下权重和门槛是本技能设计的初始排序规则，未经收益校准。用户设定优先；改变规则必须记录版本，不能在测试集结果出来后反向挑选。

## 两个分数

| 分数 | 维度及权重 |
|---|---|
| credibility 事实可信度 | source_reliability .15；firsthand .15；domain_fit .15；verifiability .20；corroboration .25；incentive_transparency .10 |
| opportunity 研究价值 | novelty .20；expectation_gap .25；materiality .25；timeliness .15；scarcity .15 |

每维度取 0—4 整数或 null。0 是已有证据支持的最低水平，null 是不知道，不能混用。每个非空评分必须有 evidence_refs 和 reason；仅引用并不证明评分正确，研究者仍要读证据。

共同锚点：0=有明确不利证据，1=弱，2=有限/混合，3=较强，4=强且有精确可复核依据。

特殊锚点：

- source_reliability：结合来源真实性、记录质量、历史校准；没有历史数据不能捏造历史命中率；官方来源也不能跨出记载范围。
- firsthand：直接公开原始记录或亲历高于多手转述；自称亲历未经核验最多作为弱支持，不直接给满分。
- domain_fit：相关领域公开可验证能力；身份不明保持 null。
- verifiability：0=关键描述与可查事实明显不符，2=部分定位，4=实体、时间、口径和原记录明确。
- corroboration：0=直接反证，1=只有原主张，2=独立性不明或部分支持，3=适当独立来源支持或权威原记录核验精确事实，4=独立路径一致核验且关键冲突已解释。
- incentive_transparency：评估利益披露和内容完整性；利益不一致不等于虚假，未知关系保持 null。
- novelty：相对于截止时点之前已发现材料的新信息；重复旧闻记低分。
- expectation_gap：有可引用的同期基线及可比较的新证据才评分；只知道股价和热度时保持 null。代理基线的上限与比较方法见 [产业传导](industry.md)。评分表示差异的研究价值，正负方向另列。
- materiality：0=有证据表明经济关联不成立，2=方向成立但规模有限，4=有可复核规模及敏感性分析。
- timeliness：结合信息可用时点、有效期、催化及用户研究周期；预计日期不当作已兑现。
- scarcity：可见传播覆盖与行业已有披露一并判断；无法观察总体传播时不装作精确测量。

计算方式：

```text
coverage = 已知维度权重之和
observed_score = 100 × Σ(权重 × 维度值 / 4) / coverage
priority_score = observed_score × coverage
```

coverage=0 时 observed_score=null，priority_score=0。priority_score 对信息缺口作排序折扣；不能把折扣后的低分表述为已证实不可靠。同时展示三项，避免只凭一项满分获得高排名。脚本中每项权重之和等于 1。

## 事实门槛先于评分

按优先级决定 research_state：

1. fact_status=refuted → rejected。
2. fact_status=conflicted 或 material_contradiction_unresolved=true → conflicted。
3. 反证检索未完成、重大冲突情况未知、事实仍未核验或公司映射未核验 → needs_verification。
4. 预期基线缺失或两个分数覆盖率有任一低于 .80 → watchlist。
5. 两个 priority_score 均至少 70 且以上门槛全部满足 → research_candidate。
6. 其余 → watchlist。

阈值只是工作队列分层。research_candidate 仍需独立的样本外验证和用户决策，不能译作买入。没有股票映射需求的产业观察可以直接报告事实，无需强行评级为股票候选。

脚本要求把事实状态、映射和预期基线的依据连到证据 ID；“反证已查”必须引用检索日志或发现的反证。“没有重大未决冲突”的人工判断要引用核验日志。脚本不能自动识别真假来源或验证这些语义。

若每项都评 3 分且覆盖率为 100%，对应排序分为 75；这仍必须通过上述事实门槛。若只有 verifiability=4 而可信度其他项未知，已知项分数为 100、覆盖率为 20%、排序分为 20，不能写成“可信度 100 分”。

## 复核评分

先完成证据卡再评分，不为满足晋级门槛倒推分数。边界项在理由中写明为什么不是相邻等级；对会改变候选状态的争议项，报告上下浮动一档时的状态变化，优先补证据。相同根源的数量不进入加分公式。

事实核验与评分单位必须一致：一个事件包含多个关键断言时分别核验；事件 fact_status 采用关键断言中最保守的状态，不按篇幅或点赞数平均。关键断言是否关键由研究假设决定，例如“参与试验”“达到终点”“某公司拥有商业权益”不能互相替代。
