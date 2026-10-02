# OSINT Alpha Mining

一套用于 Codex 的公开信息研究 Skill：从评论、新闻和行业披露中提取产业线索，核验事实，分析预期差，输出可追溯的证据卡。

## 功能

- 将 15 项判断落实为信源、立场、信息距离、能力圈、可验证性、独立证据、反证和复盘流程。
- 拆分事实报告、观点和情绪，识别同源转载，聚合弱信号。
- 核验事件与公司的经济关系，逐步分析财务传导和同期预期差。
- 分别计算事实可信度与研究价值，保留未知项和信息覆盖率。
- 提供创新药虚构案例、证据卡模板和 Python 评分工具。

当前版本负责研究方法，不包含自动爬虫、行情服务、回测引擎或实盘交易。

## 安装与调用

将本仓库中的 `SKILL.md`、`agents/`、`assets/`、`references/` 和 `scripts/` 放入你的 Codex 技能目录下的 `osint-alpha-mining/`。默认技能目录为 `~/.codex/skills/`；若设置了 `CODEX_HOME`，则使用其下的 `skills/`。

调用示例：

> 使用 $osint-alpha-mining，核验下面这条产业线索，按 15 项判断建立证据卡，分析预期差并评分：……

## 文件入口

| 文件 | 用途 |
|---|---|
| [SKILL.md](SKILL.md) | 工作流程与调用入口 |
| [evidence.md](references/evidence.md) | 15 项判断、断言与独立证据 |
| [scoring.md](references/scoring.md) | 评分公式与研究候选门槛 |
| [industry.md](references/industry.md) | 产业传导、预期差与创新药示例 |
| [data-contract.md](references/data-contract.md) | 研究记录与评分输入格式 |
| [evidence-card.md](assets/evidence-card.md) | 可填写的证据卡 |

## 运行评分示例

安装 Python 3。评分脚本仅使用标准库，无额外依赖。

```bash
python scripts/score_cases.py assets/example-case.json
python scripts/score_cases.py assets/example-case.json --out scores.json
```

示例为虚构线索，正常结果是 `needs_verification`。输出文件已存在时脚本拒绝覆盖，以保留研究快照。

每个非空维度评分都需要理由和证据引用；脚本检查字段、分值、时间和引用，不能替代事实核验。研究候选状态不代表买卖建议或已验证的 Alpha。

## 评分解释

两个分数均报告：已知项得分、已知权重覆盖率、经覆盖率折扣的排序分。重大未决反证阻止候选晋级；缺少同期预期基线时不能确认预期差。

初始权重和门槛是研究排序规则，尚未经过收益验证。具体规则见 [评分说明](references/scoring.md)。
