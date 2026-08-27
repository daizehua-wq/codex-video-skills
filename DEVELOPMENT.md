# 开发档案

本文记录 `codex-video-skills` 的设计边界、关键演进、已发生问题、修复依据和发布流程。它解释“为什么这样改”；各 Skill 的运行规则仍以对应目录中的 `SKILL.md`、schema 和校验脚本为准。

## 1. 项目基线

- 版本仓库：`git@github.com:daizehua-wq/codex-video-skills.git`
- 发布分支：`main`
- 运行时安装目录：`~/.codex/skills/<skill-name>`
- 版本化目录：本仓库根目录下的 `<skill-name>/`
- 当前流水线：`video-fact-checker` → `video-script-writer` → `video-director` → `broll-asset-executor`

四个 Skill 必须保持职责隔离：事实核验不写稿，写稿不补造事实，导演不负责素材获取，素材执行器不新增镜头需求。

运行时目录用于 Codex 实际加载，Git 仓库用于版本留档和发布。一次 Skill 更新只有在以下条件全部满足后才算完成：

1. 运行时文件与拟发布文件已同步；
2. Skill、schema 和脚本通过相应验证；
3. 只暂存本次范围内的文件；
4. 提交并推送到 `origin/main`；
5. 本地 `main` 与 `origin/main` 的提交哈希一致。

## 2. 开发时间线

| 日期 | 提交 | 变化 | 形成的能力 |
| --- | --- | --- | --- |
| 2026-08-19 | `72e32e4` | Add video director and B-roll asset executor skills | 建立导演规划与素材执行两段式工作流，并用 schema、manifest 和脚本约束交接。 |
| 2026-08-20 | `479a947` | Add fact-checking and script-writing skills | 加入事实核验和视频写稿，四段流水线成形。 |
| 2026-08-20 | `4f53764` | Refine director and script workflows | 强化 A-roll 就绪检查、导演计划、交接 schema 和脚本校验。 |
| 2026-08-20 | `173e5a1` | Restore script package and HKRR review | 恢复完整稿件交付包，加入 HKRR 自审与对应结构化校验。 |
| 2026-08-20 | `0aa604a` | Refine script relevance and neutrality gates | 增加相关性、中立性和避免宣传腔的写作门槛。 |
| 2026-08-21 | `05bd3a8` | Integrate high-retention hook framework | 加入高留存开头框架，同时要求钩子受事实卡证据约束。 |
| 2026-08-22 | `3283958` | Harden fact checker source audits | 将事实卡升级到 schema 1.1，补齐时间覆盖、负向结论、二手来源回溯和修订全量复核。 |
| 2026-08-22 | `65a0040` | Document skill development history | 删除 7 个未跟踪旧副本，建立本开发档案和维护约定。 |
| 2026-08-26 | `15a0d40` | Add transferable lesson gates to video skills | 将“案例事实”与“可复用经验”分层，加入适用条件、失败条件、实施难度和评估信号。 |
| 2026-08-27 | `111676f` | Require staged implementation paths in fact cards | 将实施路径升级为事实卡的一等交接对象，schema 更新至 1.3。 |
| 2026-08-27 | `b17eead` | Make fact checker plug-and-play | 增加自动模式判断和无第三方依赖的完整 schema 校验。 |

完整事实以 Git 为准：

```bash
git log --oneline --decorate --stat
git show <commit>
```

## 3. 问题档案

### 3.1 写稿 Skill：为什么经历多轮加固

触发案例是 BBVA The Eight 稿件在事实卡之后仍经历多次重写。问题并不是单个句子写错，而是“事实正确”没有自动转化成“第一次就可发布”：稿件还需要稳定处理主线、段落推进、信息取舍、中立表达、开头承诺和证据边界。

对应修复不是把某一篇稿子的答案写死，而是分层补齐通用约束：

1. `4f53764`：把脚本交接从自由文本推进为可校验的结构化工作流；
2. `173e5a1`：加入 HKRR 自审，检查 Hook、Knowledge、Relevance、Rhythm；
3. `0aa604a`：补相关性与中立性门槛，防止信息堆积和品牌宣传腔；
4. `05bd3a8`：加入高留存开头框架，但仍要求每个事实性承诺可回溯到事实卡。

维护原则：从真实失败中抽取“可复用的决策规则”，不要把单篇稿件的措辞、结构或偏好固化成所有选题的模板。

### 3.2 事实核验 Skill：Adecco 来源漏检

现象：修订 Adecco Agentforce 事实卡时，仅复查到 2025 年页面，因此一度把“节省 15% 时间”判断为无法追溯；Adecco 官方 2026 年 3 月材料实际上包含该信息。

根因：旧流程要求来源分级和 claim/source 关联，但没有强制记录以下审计证据：

- 是否围绕数字、引语、时间、因果和预测做过时间范围检索；
- 二手来源是否沿引用链回溯到上游原始材料；
- “不存在、未披露、无法验证”这类负向结论是否完成反证搜索；
- 修订事实卡时是否以原文件为基线并全量重查，而不是只检查新增或争议项。

修复：`3283958` 引入事实卡 schema 1.1 和 `verification_audit`，并在校验器中强制执行：

- claim 与 source 双向关联；
- `secondary_only` 不得伪装成直接来源；
- 只有 D/E 级来源时，不得标为独立确认或一手确认；
- 数字、引语、时间、因果和预测必须有时间检索记录；
- 修订必须记录基线文件并完成全量复核；
- `secondary_only`、`unverified`、`false` 必须有负向结论审计；
- D 级来源必须记录上游回溯，且共享同一独立性分组。

回归结果：真实 Adecco schema 1.1 事实卡通过；旧 schema 1.0 仍可通过但产生升级警告；故意缺少时间搜索、修订基线、全量复核或负向审计的 1.1 样本会被拒绝。

维护原则：网页“没看到”不是证据。任何负向判断都必须说明搜索边界、时间覆盖和反证路径。

### 3.3 案例核验完成，但没有沉淀可复用经验

现象：旧事实卡能够回答“案例中发生了什么”，却没有稳定回答“其他企业能学什么、在什么条件下可复用、实现起来是否简单”。写稿阶段只能临时从原始事实推导方法论，导致事实核验与写作之间的职责断层。

修复：`15a0d40` 加入 `transferability` 层，要求案例型事实卡记录：

- 案例中的实际运行机制；
- 可复用经验及其证据层级；
- 适用条件、失败条件和不可复用部分；
- 实施难度、难度驱动因素、最小试点和评估信号。

`video-script-writer` 只能使用事实卡中已标记为可交接的经验，不能从原始 claim 自行升级出企业方法论。

### 3.4 有方法论，但没有明确实施路径

现象：事实卡虽然能够给出“值得学习的原则”，但没有形成从低自动化试点到扩大范围的可执行顺序。实施步骤容易在写稿时被临时补造，或被误写成案例公司已经采用的事实。

修复：`111676f` 将事实卡升级到 schema 1.3，要求适用的案例分析包含 `implementation_path`。每个阶段必须说明目标、动作、前置条件、人工控制、难度和退出条件，并引用支持它的 lesson 或 claim。实施路径统一标记为 `editorial_guidance`；证据不足时必须输出 `insufficient_evidence` 和 blockers，不能静默省略。

### 3.5 服务器运行时缺少实施路径校验

现象：原校验器把 `jsonschema` 当作可选依赖。服务器未安装该库时，只执行 claim/source 关联检查，事实卡结构和必填实施路径可能未经完整校验。

根因：Skill 的说明文件已经要求实施路径，但运行脚本仍依赖服务器环境，部署后不能保证同一行为。

修复：`b17eead` 完成三项改造：

- 自动识别“案例分析”和“单项事实核查”，不要求用户额外配置模式；
- 在校验器中内置当前 fact-card schema 所需的标准库实现；
- 增加 `--stdlib-schema`，可强制验证无第三方依赖路径。

回归结果：在 `python3 -S` 隔离环境中，真实 schema 1.3 案例事实卡通过；错误的实施路径标记和缺失的 `implementation_path` 均被拒绝。

### 3.6 未跟踪的“2”副本

2026-08-22 清理以下文件：

- `video-director/SKILL 2.md`
- `video-director/references/handoff-schema 2.md`
- `video-director/scripts/validate_broll_requests 2.py`
- `video-script-writer/SKILL 2.md`
- `video-script-writer/references/script-claims.schema 2.json`
- `video-script-writer/references/style-profile 2.md`
- `video-script-writer/scripts/validate_script_handoff 2.py`

这些文件从未被 Git 跟踪，内容早于同目录正式文件，也不属于 Skill 的正式入口。旧脚本还可能被批量脚本扫描误执行。它们已按精确路径删除；正式文件未受影响。

文件约定：正式文件名不得带 Finder 式数字后缀。若确需并行版本，必须使用 Git 分支或带明确语义的文件名，并写明调用方；不要以 `SKILL 2.md`、`schema 2.json`、`script 2.py` 保存版本。

## 4. 验证与发布

### 4.1 修改前

```bash
git status --short
git log -5 --oneline
```

先确认工作区中哪些文件属于本次修改。未跟踪文件和用户已有改动默认不纳入提交。

### 4.2 Skill 结构验证

对每个改动过的 Skill 执行：

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>
```

### 4.3 脚本与交接物验证

至少完成：

```bash
python3 -m py_compile <changed-python-files>
python3 <validator.py> <representative-artifact.json>
```

凡是修复校验漏洞，必须同时验证：

- 一个真实有效样本应通过；
- 一个旧版兼容样本按设计通过或明确拒绝；
- 一个针对本次漏洞构造的无效样本必须失败。

不能只验证“脚本能运行”，还要验证它能阻止原来的错误。

### 4.4 提交与推送

```bash
git status --short
git add <本次修改的明确文件列表>
git diff --cached --check
git diff --cached --stat
git commit -m "本次更新说明"
git push origin main
git rev-parse main
git rev-parse origin/main
```

禁止用 `git add .` 顺手带入副本、测试产物、下载文件或用户的无关修改。

## 5. 每次问题修复必须留下什么

开发档案中的问题记录至少包含：

1. 触发案例与可观察现象；
2. 根因，而不只是错误结果；
3. 修改过的规则、schema 或脚本；
4. 正向、兼容和反向回归结果；
5. 对应 Git 提交；
6. 仍然存在的限制。

如果只有提交标题而没有这些信息，同类问题很容易在下一次迭代中重复出现。

## 6. 当前已知限制

- 仓库目前没有 CI 配置，验证仍依赖本地执行；
- 仓库目前没有语义化版本标签，发布定位主要依赖提交哈希；
- schema 校验能保证结构和部分证据规则，但不能替代人工判断来源内容是否真的支持 claim；
- 实时事实核验仍需要运行环境具备可用的网页检索能力；这与 Python 包依赖无关；
- 写作自审能提高首次成稿率，但事实卡质量、选题判断和用户明确的风格目标仍会影响结果。

后续若引入 CI 或版本标签，应在本档案中补充发布规则，并以新的提交记录为准。
