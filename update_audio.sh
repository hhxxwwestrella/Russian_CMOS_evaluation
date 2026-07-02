#!/usr/bin/env bash
# 从本机固定路径同步俄语音频到 repo 内 sources/，并重新生成 JSON。
# 修改下方绝对路径即可；config.json 保持相对路径，便于 git 部署。
#
# Usage:
#   ./update_audio.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

NEED_TO_COPY_GOOGLE=0

# --- 本机音频来源（按需修改）---
GOOGLE_RU_MALE="/chenmingjie/xingwen/CMOS/CMOS-google-offline-ref/ru_cmos-man"
GOOGLE_RU_FEMALE="/chenmingjie/xingwen/CMOS/CMOS-google-offline-ref/ru_cmos"

OUR_RU_MALE="/chenmingjie/xingwen/multiling_up-to-date/e2e_test/output/runs/ru_0702_ckpt1083_cmos_male/wav"
OUR_RU_FEMALE="/chenmingjie/xingwen/multiling_up-to-date/e2e_test/output/runs/ru_0702_ckpt1083_cmos_female/wav"
RU_ORIGINAL="/chenmingjie/xingwen/chuanyin_testset/CMOS/CMOS_original_txt_files/ru_cmos.txt"
OUR_RU_NORMALIZED="/chenmingjie/xingwen/multiling_up-to-date/e2e_test/output/runs/ru_0702_ckpt1083_cmos_female"

if [ "$NEED_TO_COPY_GOOGLE" -eq 1 ]; then
  python3 sync_sources.py \
    --google_ru_male "$GOOGLE_RU_MALE" \
    --google_ru_female "$GOOGLE_RU_FEMALE" \
    --our_ru_male "$OUR_RU_MALE" \
    --our_ru_female "$OUR_RU_FEMALE" \
    --ru_original "$RU_ORIGINAL" \
    --our_ru_normalized "$OUR_RU_NORMALIZED"
else
  python3 sync_sources.py \
    --our_ru_male "$OUR_RU_MALE" \
    --our_ru_female "$OUR_RU_FEMALE" \
    --ru_original "$RU_ORIGINAL" \
    --our_ru_normalized "$OUR_RU_NORMALIZED"
fi

python3 make_jsons.py
echo "Audio updated. Run: python3 serve.py"
