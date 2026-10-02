# 需求来源与设计取舍

本技能根据公开信息研究中的 15 项判断框架编写，当前版本聚焦研究标准、证据卡与可解释评分。

对话的 15 项判断已逐项映射到 evidence.md。用户的创新药个案用于说明如何发现线索，不视为疗效或投资成功的已验证事实。

保留：信源与立场判断、事实/观点分离、独立核验、弱信号聚合、产业传导、预期差、反证和长期复盘。

本轮新增设计：两项分数、缺失值覆盖率、初始权重、70 分/.80 覆盖率门槛、JSON 数据契约。它们是工程化研究规则，不来自原对话的实证结果，也没有被回测验证。

原对话的多维相乘再除以传播度公式是概念表达。本版改成两个可解释的加权分数与事实门槛，避免量纲混用、重复维度放大、未知值被错误填入、低传播度导致分数失控。仍需在真实使用和后续独立验证中校准。

方法核验参考（2026-10-01 查阅；执行具体研究时仍应核验当前原始记录）：

- [NLM：ClinicalTrials.gov 功能与日期说明](https://www.nlm.nih.gov/pubs/techbull/nd17/nd17_clinicaltrials_enhanced.html)：登记提交和公开发布不是同一时点；据此保留版本与公开时间。
- [Investor.gov：社交情绪投资工具](https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-18)：社交来源分析有局限，聚合结果需要进一步研究。
- [Bailey 等：The Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)：支持后续检验时记录试验选择及样本外验证；本技能未实现该论文算法，也不声称提供已验证策略。
