# CMOS 音频对比工具 · 俄语

用于对比 **Google 离线 TTS** 与 **我们模型合成音频** 的网页工具，设计为 **GitHub Pages 静态部署**。

- **俄语**：按性别分组对比 — 男声 Google vs 我们男声，女声 Google vs 我们女声
- 额外展示 **TN 归一化前原文** 与 **归一化后文本**

当前使用 **100** 条样本。

## GitHub Pages 部署（推荐）

本仓库即为 Pages 站点根目录，无需 `serve.py`。

### 首次启用

1. 在本机更新音频并生成 JSON：
   ```bash
   bash update_audio.sh
   git add -A && git commit -m "update audio" && git push
   ```
2. 打开 GitHub 仓库 **Settings → Pages**
3. **Source** 选 `Deploy from a branch`
4. **Branch** 选 `main`，文件夹选 `/ (root)`，保存
5. 等待部署完成，访问：
   ```
   https://<username>.github.io/LITs_cmos_evaluation/
   ```

仓库已包含 `.nojekyll`，确保 `sources/` 等目录可被正常访问。

### 测试人员使用方式

1. 打开上述 GitHub Pages 链接
2. 进行听感对比
3. 在右侧笔记本记录问题（**自动保存到浏览器 localStorage**）
4. 评测结束后点击 **「导出笔记」**，将 `cmos_ru_notebook_YYYYMMDD.txt` 提交给负责人
5. 如需恢复之前的笔记，可使用 **「导入笔记」** 加载本地 txt

> 笔记保存在各测试人员浏览器中，**不会写入 git**。负责人通过收集导出的 txt 文件汇总结果。

### 更新音频后重新发布

```bash
bash update_audio.sh
git add sources/ ru_data.json
git commit -m "update CMOS audio for eval"
git push
```

GitHub Pages 会在 push 后自动更新（通常 1–3 分钟）。

## 维护者本地预览（可选）

若需在 push 前本地检查页面，可用任意静态服务器：

```bash
python3 -m http.server 8765
# 打开 http://localhost:8765
```

`serve.py` 仍可用于本地预览（含 HTTP Range 音频 seek），但 **GitHub Pages 部署不依赖它**。

## 目录结构

```
ru_eval/
├── .nojekyll            # GitHub Pages 静态资源
├── config.json          # 音频路径配置（repo 内相对路径）
├── sync_sources.py      # 从外部目录复制到 sources/
├── make_jsons.py        # 从 sources/ 生成 JSON
├── update_audio.sh      # 一键同步 + 生成 JSON
├── index.html           # 对比页面（纯静态）
├── ru_data.json         # 俄语数据
└── sources/             # 音频与文本（需提交到 git）
    ├── google/
    └── our/
```

## 配置说明

| 字段 | 说明 |
|------|------|
| `google.ru_male_dir` / `google.ru_female_dir` | Google 俄语男/女声 |
| `our.ru_male_dir` / `our.ru_female_dir` | 我们俄语男/女声 |
| `our.ru_text_dir` | 俄语原文与归一化文本 |
| `num_items` | 对比条数，默认 100 |

## 更新音频

修改 `update_audio.sh` 顶部的本机绝对路径，然后：

```bash
bash update_audio.sh
```

首次同步 Google 参考音频时，将 `NEED_TO_COPY_GOOGLE=1`。

| 变量 | 说明 |
|------|------|
| `GOOGLE_RU_MALE` / `GOOGLE_RU_FEMALE` | `CMOS-google-offline-ref/ru_cmos-man` / `ru_cmos` |
| `OUR_RU_MALE` / `OUR_RU_FEMALE` | 俄语推理 wav 目录 |
| `RU_ORIGINAL` | CMOS 未经处理的俄语原文（`ru_cmos.txt`） |
| `OUR_RU_NORMALIZED` | 含 `normalized.txt` 的推理 run 目录 |

## 页面功能

- **俄语**：男声、女声分组对比
- 展示 CMOS 原文（`ru_cmos.txt`）与我们的归一化结果
- **笔记本**：浏览器 localStorage 自动保存；支持导入 / 导出 txt
- **快捷键**：`←` / `→` 切换样本

## 注意事项

- 音频文件较大（约 1GB+），首次 clone / Pages 加载可能较慢；若超出 GitHub 限制，可考虑 Git LFS 或将音频托管到 CDN 后修改 JSON 路径
- `.gitignore` 已忽略 `*notebook*.txt`，测试笔记不入库
