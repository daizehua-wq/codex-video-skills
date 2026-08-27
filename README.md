# Codex 视频生产 Skills

这个仓库包含四个职责独立、按顺序交接的 Codex Skill。每个一级目录都是一个可独立复制和加载的 Skill；仓库根目录只保存项目说明和开发记录。

## Skill 一览

| Skill | 输入 | 输出 | 明确不负责 |
| --- | --- | --- | --- |
| `video-fact-checker` | 选题、案例、来源材料或待核查说法 | `fact_card.json`、`fact_card.md`、`sources.md` | 写视频稿、设计镜头 |
| `video-script-writer` | 已批准的 `fact_card.json` | `narration.md`、`script_claims.json` 等稿件交付物 | 补查事实、规划画面 |
| `video-director` | 人工定稿的 A-roll、对应时间码字幕和制作约束 | `director_plan.json`、`broll_requests.json` | 搜索或下载素材、改写口播 |
| `broll-asset-executor` | 已校验的 `broll_requests.json` | 素材、manifest 和来源记录 | 决定哪里需要 B-roll |

## 流水线

```text
选题 / 来源材料
        ↓
video-fact-checker
        ↓
fact_card.json + fact_card.md + sources.md
        ↓
video-script-writer
        ↓
narration.md + script_claims.json
        ↓
人工完成并锁定 A-roll
        ↓
video-director
        ↓
director_plan.json + broll_requests.json
        ↓
broll-asset-executor
        ↓
assets/ + manifest.csv + manifest.json + sources.md
```

这四段边界是有意设计的：事实核验不写故事，写稿不补造证据，导演不获取素材，素材执行器不新增镜头需求。

## 部署

服务器更新仓库后，只需把需要使用的一级 Skill 目录完整复制到 Codex 的 Skills 目录，例如：

```text
~/.codex/skills/video-fact-checker/
~/.codex/skills/video-script-writer/
~/.codex/skills/video-director/
~/.codex/skills/broll-asset-executor/
```

`README.md` 和 `DEVELOPMENT.md` 是仓库文档，不需要复制到运行时 Skills 目录。不要只复制 `SKILL.md`；对应的 `agents/`、`references/` 和 `scripts/` 也是 Skill 的组成部分。

`video-fact-checker` 支持 Python 3.7+，无需额外安装 `jsonschema`。如果运行环境没有该库，它会自动使用随 Skill 提供的标准库校验器。

## 发布前检查

每次提交只应包含明确修改过的 Skill 文件或仓库文档。至少确认：

1. 工作区没有临时文件、缓存和无关改动；
2. 改动过的 Skill 通过 `quick_validate.py`；
3. 改动过的校验脚本通过有效样本和无效样本回归；
4. 本地 `main` 与 `origin/main` 指向同一提交。

设计依据、问题复盘和发布流程见 [DEVELOPMENT.md](DEVELOPMENT.md)。
