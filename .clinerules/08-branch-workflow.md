# 08 分支工作流（dev 开发 / v17 只合并）

## 铁律（违反即停手）

1. **开发修改一律在 `dev` 分支进行**：功能新增、缺陷修复、重构、测试补充、版本 bump，
   全部提交到 `dev`。
2. **不动 `v17`**：不得在 `v17` 上做任何直接提交（不 `commit`、不 `bump`、不往 v17 里
   merge 其它分支），也不得切到 `v17` 后修改文件。`v17` 只接受来自 `dev` 的**快进合并**。
3. **`dev` 分支永远保留**：合并进 `v17` 后不删除 `dev`；此时 `dev` 与 `v17` 指向同一提交，
   后续开发继续提交在 `dev`，`dev` 再次领先 `v17`。
4. **远端推送由用户手动执行**（VS Code 任务或手动 `git push`）；Cline 一律不得执行
   `git push` / `git push --tags`。

## 标准流程

| 步骤 | 操作 | 入口 |
| :--- | :--- | :--- |
| 1 | 在 `dev` 开发并提交（Conventional Commits） | `git checkout dev` |
| 2 | 推送远端 dev | VS Code 任务「推送 dev 到 origin」 |
| 3 | 非开发环境的 XUAN 在更新窗口「更新分支」选 `dev` 拉取测试；普通环境一律 `v17` | 更新弹窗 |
| 4 | 测试无异常后合并进 v17（本地 + 远端，保留 dev） | VS Code 任务「dev 合并进 v17（本地+远端，保留 dev）」 |
| 5 | 版本 tag / 安装包 | 既有任务「更新小版本号 (patch)」「推送 Tags 到 origin」「打包新版本」 |

## 提交前自检

- `git branch --show-current` → 必须是 `dev`（合并任务内部自动切换除外）
- `git status --porcelain` → 无输出（工作区干净）
- `git log --oneline v17..dev` → 能看到本次开发提交（确认提交确实落在 dev 上）
- 若发现误提交到 `v17`：**停止并报告用户**，由用户决定如何迁移（不要自行
  `reset` / `rebase` / 强推远端分支）。

## 合并任务的行为（`scripts/git_merge_dev_into_v17.py`）

- 前置：工作区干净；本地 `dev` 与 `origin/dev` 一致（未推送则中止并提示先推 dev）
- 执行：`git checkout v17` → `git merge --ff-only origin/v17` → `git merge --ff-only dev`
  → `git push origin v17`
- 收尾：无论成功失败都切回原分支（通常是 `dev`）；`dev` 分支保留
- 非快进关系（v17 有 dev 之外的新提交）时中止并提示人工处理，不做强推

## 相关脚本 / 任务

- `scripts/git_push_dev.py` ←→ 任务「推送 dev 到 origin」
- `scripts/git_merge_dev_into_v17.py` ←→ 任务「dev 合并进 v17（本地+远端，保留 dev）」
