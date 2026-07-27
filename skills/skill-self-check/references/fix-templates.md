# Fix templates — 效率护栏与文件包问题的可粘贴改法

配合 Pass 4 使用。`EFF.*` 和 `PKG.*` 是脚本判定的机械问题：答案不取决于业务，
所以**不要问用户**，直接给出改法。需要用户拍板的空缺走
[`gap-questions.md`](gap-questions.md)。

改完必须复检，别凭感觉宣布修好了：

```bash
python scripts/hard_gates.py <skill> > baseline.json   # 改之前先存
python scripts/verify_fix.py <skill> --baseline baseline.json --pretty
```

## 分工

| 谁来改 | 范围 | 落盘闸门 |
| --- | --- | --- |
| 模型改文字 | `EFF.1` `EFF.2` `EFF.3` `PKG.2` `PKG.4` `PKG.5` | 用户说「按意见改」之后 |
| 用户改磁盘 | `PKG.1` `PKG.3` `PKG.6` `PKG.7`（移动/删除文件） | 给命令，由用户执行 |

脚本不会替用户删文件。涉及删除或移动的，写清楚删哪个、为什么、影响什么。

## EFF.1 — 循环没有停止条件

脚本发现了「重试 / 再跑一次 / retry」这类指令，附近找不到次数上限、超时或人工出口。
不加护栏的循环会让 Agent 在失败输入上反复烧 token。

改法是给每个循环补齐三件事：**试几次、每次之间改什么、到头了找谁。**

```markdown
3. 运行 <命令>
   完成标准: 退出码为 0
   失败时: 最多重试 2 次；每次重试前必须修掉上一次报错的那一条，
   不要原样重跑。2 次之后仍失败就停下，把最后一次的完整报错贴给 <角色>。
```

只有条件分支没有次数时同样算不合格：

| 改之前 | 改之后 |
| --- | --- |
| 「如果失败就重新运行」 | 「如果失败，最多重新运行 2 次；仍失败则记为失败并升级」 |
| 「retry until it passes」 | 「retry at most 3 times, then stop and report the last error」 |
| 「不通过就再检查一遍」 | 「不通过就再检查一遍（只做一轮）；第二轮仍不通过交人工判断」 |

写「不要重复运行」这类**禁止**性说法不会被算成循环指令，不用改。

## EFF.2 — 开放式打磨

「直到满意 / 直到完美 / 不断优化 / until perfect」没有可判定的终点，模型无法知道
什么时候算完。把主观标准换成一次性可验证的清单。

```markdown
## 验收

- [ ] <可观察的凭据 1>
- [ ] <可观察的凭据 2>

全部勾上就交付，不再继续打磨。清单之外的改进写进「后续建议」，本次不做。
```

| 改之前 | 改之后 |
| --- | --- |
| 「反复优化文案直到满意」 | 「按验收清单逐条过一遍；全部满足即停」 |
| 「keep refining until it's good enough」 | 「run one revision pass against the checklist below, then stop」 |

需要多轮时给轮数，不要给形容词：「最多 2 轮，每轮只解决清单里的一类问题」。

## EFF.3 — 静态 token 超预算

`SKILL.md` 每次触发都会整篇进上下文。超过约 8000 token 说明正文里堆了
只在特定分支才需要的材料。**搬走，不是删掉。**

判断标准：**每次都要读的留在正文，偶尔查的搬去 `references/`。**

| 内容 | 去处 |
| --- | --- |
| 触发条件、步骤主干、验收、危险信号 | 留在 `SKILL.md` |
| 长表格、字段字典、术语表、平台差异 | `references/<主题>.md` |
| 完整示例、正反对照 | `examples/<场景>.md` |
| 能被脚本判定的规则 | `scripts/`，正文只留一行调用 |

正文里用一行指路替换搬走的段落：

```markdown
字段口径见 [`references/field-dictionary.md`](references/field-dictionary.md)，
需要核对字段时再读。
```

搬完复跑 `hard_gates.py` 确认 `token_consumption.budget.status` 回到 `within`；
同时确认没有搬出 `PKG.5`（引用了不存在的文件）。

## PKG.1 — 目标不是 Skill 包根目录

缺 `SKILL.md`。多半是路径指到了上一层（`skills/` 而不是 `skills/<name>/`），
或者说明书叫了别的名字。先确认路径，再确认文件名大小写必须是 `SKILL.md`。

## PKG.2 — 声明名与目录名不一致

frontmatter 的 `name` 和文件夹名必须逐字符相同。两边取哪个由**已经在用哪个**决定：

- 已经有人按目录名安装过 → 改 frontmatter，保住安装路径。
- 还没发布 → 两边统一成小写连字符（`invoice-check`），跨平台最稳。

```markdown
---
name: <与所在文件夹完全一致的名字>
description: <保持原样>
---
```

## PKG.3 — 运行产物混进了安装包

`out/` `reports/` `logs/` `tmp/` 这类目录不该跟着 Skill 一起分发：会把客户数据
带进版本库，也会让每次安装体积变大。

```bash
# 移到仓库外，不要留在 Skill 里
mv <skill>/reports "$HOME/Documents/skill-audits/<skill>"
```

产物路径改成运行时参数（`--out-dir`），并在 `SKILL.md` 里写明默认落在仓库之外。
目录已进版本控制的，一并从索引里移除并补 `.gitignore`。

## PKG.4 — 写死了本机绝对路径

`D:\path\to\your-repo\...` 或 `/Users/your-name/...` 换台机器必然失效。改成相对
包根的路径，或者显式的参数占位。

| 位置 | 改之前 | 改之后 |
| --- | --- | --- |
| 调用自带脚本 | `D:\path\to\your-repo\scripts\run.py` | `scripts/run.py`（相对包根） |
| 读取用户数据 | `C:\Users\your-name\data\list.csv` | `<你的数据目录>/list.csv`（由用户传入） |

（上表左列刻意用了 `your-name` 这类占位写法。真实违规里那一段是你本机的真实
用户名或项目名——脚本认的就是这个差别，占位符不算违规。）

需要用户自己的目录时，写成占位符加一句说明，不要塞自己的路径当例子。

## PKG.5 — 引用了不存在的文件

正文链接的 `references/x.md` 或 `scripts/y.py` 在包里找不到。三选一，不要放着不管：

1. 文件本该存在 → 补上。
2. 名字写错了 → 改成实际文件名（注意大小写，Linux 区分）。
3. 内容已经不需要 → 删掉这句引用，同时删掉依赖它的步骤。

## PKG.6 — 归档、临时与系统残留

`.zip` `.bak` `~$*` `.DS_Store` `Thumbs.db` 之类不属于可安装内容。

```bash
# 先看清单再删
git clean -nXd <skill>
```

`.DS_Store` / `Thumbs.db` 顺手加进 `.gitignore`，否则下次还会回来。

## PKG.7 — 大文件重复

同一份资源在包里存了多份，安装者不知道该信哪个。留一份权威副本，其余改成引用。
确实需要多种格式（比如模板的 `.md` 和 `.html`）时，在 `SKILL.md` 里写明各自用途，
让"重复"变成有理由的分工。

## 复检怎么读

`verify_fix.py` 的结论对应不同动作：

| verdict | 含义 | 下一步 |
| --- | --- | --- |
| `improved` | 有改善，没有硬回退 | 看 `introduced` 里新冒出来的项，决定这轮改不改 |
| `unchanged` | 分数和 finding 都没动 | 改的地方没被检查覆盖，或者根本没落盘 |
| `mixed` | 有改善也有新问题 | 先处理 `new_critical`，再看其余 |
| `regressed` | 出现新的 critical 或分数下降 | 回滚这次改动，重新来 |

`not_comparable` 不是错误：该维度的满分变了（比如补上步骤之后配套材料才开始适用），
前后分数不能直接比，看 finding 列表即可。
