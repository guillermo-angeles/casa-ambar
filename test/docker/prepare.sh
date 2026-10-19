#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
REPO=../../config
rm -rf config
mkdir -p config/packages
cp "$REPO"/packages/*.yaml config/packages/
cp -R "$REPO"/themes config/themes
cp -R "$REPO"/dashboards config/dashboards
cp -R "$REPO"/www config/www
cp stubs.yaml config/packages/stubs.yaml
cp -R custom_components config/custom_components
cp -R ../../custom_components/casa_groq_stt config/custom_components/
[ "$(head -1 "$REPO/configuration.snippet.yaml")" = "homeassistant:" ]
{
  cat <<'YAML'
default_config:

stub_esphome:

frontend:
  themes: !include_dir_merge_named themes

homeassistant:
  name: Casa test
  latitude: 40.4168
  longitude: -3.7038
  elevation: 650
  unit_system: metric
  time_zone: Europe/Madrid
  currency: EUR
  country: ES
YAML
  tail -n +2 "$REPO/configuration.snippet.yaml"
} > config/configuration.yaml
cat > config/secrets.yaml <<'YAML'
echo_camera_rtsp: "-rtsp_transport tcp -i rtsp://camera:stub-camera-pass@127.0.0.1:8554/camera"
YAML
touch config/automations.yaml config/scripts.yaml config/scenes.yaml
