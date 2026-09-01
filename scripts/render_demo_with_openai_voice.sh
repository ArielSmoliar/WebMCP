#!/bin/zsh
set -euo pipefail

project_root="${0:A:h:h}"
visual="$project_root/output/demo/captains-table-demo-visual.mp4"
narration_text="$project_root/docs/demo-video-narration.txt"
narration_audio="$project_root/output/demo/captains-table-narration.wav"
final_video="$project_root/output/demo/captains-table-demo-final.mp4"
payload="$(mktemp -t captains-table-tts.XXXXXX.json)"
trap 'rm -f "$payload"' EXIT

if [[ -f "$project_root/.env" ]]; then
  set -a
  source "$project_root/.env"
  set +a
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "OPENAI_API_KEY is not set." >&2
  exit 2
fi

if [[ ! -f "$visual" ]]; then
  echo "Missing visual master: $visual" >&2
  exit 3
fi

jq -n --rawfile input "$narration_text" '{
  model: "gpt-4o-mini-tts",
  voice: "cedar",
  input: $input,
  instructions: "Speak in a composed, intelligent, quietly confident documentary product-narration voice. Be warm but restrained, never salesy. Maintain an even, brisk-but-unhurried pace around 125 words per minute. Use brief natural pauses between paragraphs. Give subtle emphasis to conflict, human authorization, exactly once, and durable proof. Pronounce WebMCP as Web M C P and ChatGPT as Chat G P T.",
  response_format: "wav"
}' > "$payload"

curl --fail-with-body --silent --show-error \
  https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary "@$payload" \
  --output "$narration_audio"

/opt/homebrew/bin/ffmpeg -y \
  -i "$visual" \
  -i "$narration_audio" \
  -filter_complex "[0:v]tpad=stop_mode=clone:stop_duration=12[v];[1:a]adelay=500:all=1[a]" \
  -map "[v]" -map "[a]" \
  -shortest \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  "$final_video"

/opt/homebrew/bin/ffprobe -v error \
  -show_entries format=duration,size \
  -of default=noprint_wrappers=1 \
  "$final_video"

echo "$final_video"
