#!/usr/bin/env bash
set -euo pipefail

# =============== DTB -> LABEL 映射（按你的表）===============
# 从 /boot/boot.ini 中匹配：load mmc 1:1 ${dtb_loadaddr} <DTB>
BOOTINI="/boot/boot.ini"
DTB=""
if [[ -r "$BOOTINI" ]]; then
  # 容忍失败：整条管道最后加 || true
  DTB="$(grep -oE 'load[[:space:]]+mmc[[:space:]]+1:1[[:space:]]+\$\{dtb_loadaddr\}[[:space:]]+[[:graph:]]+' "$BOOTINI" \
        | awk '{print $NF}' | tail -n1 | xargs -r basename || true)"
else
  warn "boot.ini not readable: $BOOTINI"
fi
declare -A dtb2label=(
  [rk3326-mymini-linux.dtb]=mymini
  [rk3326-xf35h-linux.dtb]=xf35h
  [rk3326-r36pro-linux.dtb]=r36pro
  [rk3326-r36max-linux.dtb]=r36max
  [rk3326-xf40h-linux.dtb]=xf40h
  [rk3326-dc40v-linux.dtb]=dc40v
  [rk3326-dc35v-linux.dtb]=dc35v
  [rk3326-r36plus-linux.dtb]=r36splus
  [rk3326-r46h-linux.dtb]=r46h
  [rk3326-hg36-linux.dtb]=hg36
  [rk3326-rx6h-linux.dtb]=rx6h
  [rk3326-k36s-linux.dtb]=k36s
  [rk3326-r36ultra-linux.dtb]=r36ultra
  [rk3326-xgb36-linux.dtb]=xgb36
  [rk3326-a10mini-linux.dtb]=a10mini
)
declare -A console_profile=(
  [mymini]=480p
  [xf35h]=480p
  [r36pro]=480p
  [r36max]=720p
  [xf40h]=720p
  [dc40v]=720p
  [dc35v]=720p
  [r36splus]=720p
  [r46h]=768p
  [hg36]=480p
  [rx6h]=480p
  [k36s]=480p
  [r36ultra]=720p
  [xgb36]=480p
  [a10mini]=480p
  [r36s]=480p
)
declare -A joy_conf_map=(
  [mymini]=single
  [xf35h]=dual
  [r36pro]=dual
  [r36max]=dual
  [xf40h]=dual
  [dc40v]=dual
  [dc35v]=dual
  [r36splus]=dual
  [r46h]=dual
  [hg36]=dual
  [rx6h]=dual
  [k36s]=single
  [r36ultra]=dual
  [xgb36]=single
  [a10mini]=none
  [r36s]=dual
)
declare -A ogage_conf_map=(
  [mymini]=select
  [xf35h]=select
  [r36pro]=happy5
  [r36max]=happy5
  [xf40h]=select
  [dc40v]=happy5
  [dc35v]=happy5
  [r36splus]=happy5
  [r46h]=select
  [hg36]=happy5
  [rx6h]=select
  [k36s]=happy5
  [r36ultra]=happy5
  [xgb36]=happy5
  [a10mini]=happy5
  [r36s]=happy5
)
rk915_set=("xf40h" "dc40v" "xf35h" "dc35v" "r36ultra" "k36s")   # 按需增删
spi_set=("dc35v" "dc40v")   # 按需增删
LABEL="${dtb2label[$DTB]:-r36s}"   # 默认 r36s
# =============== 路径配置（可按需调整）===============
QUIRKS_DIR="/home/ark/.quirks"                  # 目标机型库
CONSOLE_FILE="/boot/.console"                   # 当前生效机型标记
# =============== 小工具函数（英文输出 / 中文注释）===============
msg()  { echo "[clone.sh] $*"; }
warn() { echo "[clone.sh][WARN] $*" >&2; }
err()  { echo "[clone.sh][ERR ] $*" >&2; }

# 如果源存在则复制；isfile=yes 时以文件目标安装（保持权限 0755）
cp_if_exists() {
  local src="$1" dst="$2" isfile="${3:-no}"
  if [[ -e "$src" ]]; then
    if [[ "$isfile" == "yes" ]]; then
      mkdir -p "$(dirname "$dst")"
      # 保留属主/属组/时间戳等
      if cp -a "$src" "$dst" 2>/dev/null; then
        :
      else
        # 极端情况下的兜底：还用 install，但把所有权按源文件纠正回去
        install -m 0755 -D "$src" "$dst"
        sudo chown --reference="$src" "$dst" 2>/dev/null || true
        sudo touch -r "$src" "$dst" 2>/dev/null || true
      fi
      # 统一权限为 0755（不影响属主/属组）
      sudo chmod 0755 "$dst" || true
    else
      mkdir -p "$dst"
      cp -a "$src" "$dst/"
    fi
    msg "Copied: $src -> $dst"
  else
    warn "Source not found, skip: $src"
  fi
}

apply_hotkey_conf() {
  local dtbval="$1" kind ogage_conf ra_conf ra32_conf
  # 键不存在时，kind 为空串（避免 set -u 爆炸）
  kind="${ogage_conf_map[$dtbval]-}"

  case "$kind" in
    select) 
      ogage_conf="$QUIRKS_DIR/ogage.select.conf" 
      ra_conf="$QUIRKS_DIR/retroarch.select"
      ra32_conf="$QUIRKS_DIR/retroarch32.select"
      ;;
    happy5)   
      ogage_conf="$QUIRKS_DIR/ogage.happy5.conf" 
      ra_conf="$QUIRKS_DIR/retroarch.happy5"
      ra32_conf="$QUIRKS_DIR/retroarch32.happy5"
      ;;
    *)
      ogage_conf="" 
      ra_conf=""
      ra32_conf=""
      ;;
  esac

  if [[ -n "$ogage_conf" ]]; then
    msg "change hotkey: $dtbval -> $(basename "$ogage_conf")"
    cp_if_exists "$ogage_conf" "/home/ark/ogage.conf" "yes"
  else
    msg "hotkey unchanged for: $dtbval (no mapping)"
  fi
  if [[ -n "$ra_conf" ]]; then
    msg "change hotkey: $dtbval -> $(basename "$ra_conf")"
    cp_if_exists "$ra_conf" "/home/ark/.config/retroarch/retroarch.cfg" "yes"
  else
    msg "hotkey unchanged for: $dtbval (no mapping)"
  fi
  if [[ -n "$ra32_conf" ]]; then
    msg "change hotkey: $dtbval -> $(basename "$ra32_conf")"
    cp_if_exists "$ra32_conf" "/home/ark/.config/retroarch32/retroarch.cfg" "yes"
  else
    msg "hotkey unchanged for: $dtbval (no mapping)"
  fi
}

adjust_per_joy_conf() {
  local dtbval="$1" kind conf
  # 键不存在时，kind 为空串（避免 set -u 爆炸）
  prof="${joy_conf_map[$dtbval]-}"
  case "$prof" in
    none|single)
      cp_if_exists "$QUIRKS_DIR/noneJoy/controls.ini" "/roms/psp/ppsspp/PSP/SYSTEM/controls.ini" "yes"
      cp_if_exists "$QUIRKS_DIR/noneJoy/ppsspp.ini" "/roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini" "yes"
      cp_if_exists "$QUIRKS_DIR/noneJoy/ppsspp.ini.sdl" "/roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl" "yes"
      cp_if_exists "$QUIRKS_DIR/noneJoy/drastic.cfg" "/opt/drastic/config/drastic.cfg" "yes"
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/noneJoy/controls.ini" "/roms2/psp/ppsspp/PSP/SYSTEM/controls.ini" "yes" || true
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/noneJoy/ppsspp.ini" "/roms2/psp/ppsspp/PSP/SYSTEM/ppsspp.ini" "yes" || true
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/noneJoy/ppsspp.ini.sdl" "/roms2/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl" "yes" || true
      ;;
    dual)
      cp_if_exists "$QUIRKS_DIR/dualJoy/controls.ini" "/roms/psp/ppsspp/PSP/SYSTEM/controls.ini" "yes"
      cp_if_exists "$QUIRKS_DIR/dualJoy/ppsspp.ini" "/roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini" "yes"
      cp_if_exists "$QUIRKS_DIR/dualJoy/ppsspp.ini.sdl" "/roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl" "yes"
      cp_if_exists "$QUIRKS_DIR/dualJoy/drastic.cfg" "/opt/drastic/config/drastic.cfg" "yes"
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/dualJoy/controls.ini" "/roms2/psp/ppsspp/PSP/SYSTEM/controls.ini" "yes" || true
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/dualJoy/ppsspp.ini" "/roms2/psp/ppsspp/PSP/SYSTEM/ppsspp.ini" "yes" || true
      [[ -d "/roms2/psp" ]] && cp_if_exists "$QUIRKS_DIR/dualJoy/ppsspp.ini.sdl" "/roms2/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl" "yes" || true
      ;;
    *) msg "No profile assets for: $prof" ;;
  esac
}


# 依据 LABEL 执行
apply_quirks_for() {
  local dtbval="$1"
  local base="$QUIRKS_DIR/$dtbval"
  adjust_per_joy_conf "$dtbval"
  apply_hotkey_conf "$dtbval"
  copy_file
}

install_profile_assets() {
  local prof="$1"
  case "$prof" in
    480p|720p|768p)
      cp_if_exists "$QUIRKS_DIR/$prof/351Files" "/opt/351Files" "no"
      cp_if_exists "$QUIRKS_DIR/$prof/drastic/TF1/libSDL2-2.0.so.0.3000.2" "/opt/drastic/TF1/" "yes"
      cp_if_exists "$QUIRKS_DIR/$prof/drastic/TF2/libSDL2-2.0.so.0.3000.2" "/opt/drastic/TF2/" "yes"
      cp_if_exists "$QUIRKS_DIR/$prof/drastic/bg" "/roms/nds" "no"
      [[ -d "/roms2/nds/bg" ]] && cp_if_exists "$QUIRKS_DIR/$prof/drastic/bg" "/roms2/nds" "no" || true
      ;;
    *) msg "No profile assets for: $prof" ;;
  esac
}

copy_file() {
  [[ -f "$CONSOLE_FILE" ]] && cur_console="$(tr -d '\r\n' < "$CONSOLE_FILE")" || cur_console=""
  [[ -n "$cur_console" ]] && install_profile_assets "${console_profile[$cur_console]}"
}


# =============== 执行开始 ===============
msg "DTB filename: ${DTB:-<empty>}, LABEL: $LABEL"

# 按规则处理 /boot/.console
if [[ ! -f "$CONSOLE_FILE" ]]; then
  clear
  echo "==============================="
  echo "   arkos for clone lcdyk  ..."
  echo "==============================="
  sleep 2
  echo "$LABEL" > "$CONSOLE_FILE"
  msg "Wrote new console file: $CONSOLE_FILE -> $LABEL"
  apply_quirks_for "$LABEL"
  sleep 5
else
  CUR_VAL="$(tr -d '\r\n' < "$CONSOLE_FILE" || true)"
  if [[ "$CUR_VAL" == "$LABEL" ]]; then
    msg "Console unchanged ($CUR_VAL); nothing to do."
  else
    (
      # ==== 所有输出都到 tty1 ====
      # 复位/清屏并回到左上角
      printf '\033c'
      echo "==============================="
      echo "   arkos for clone lcdyk  ..."
      echo "==============================="
      echo
      echo "[firstboot.sh] old config: ${CUR_VAL}"
      echo "[firstboot.sh] new config: ${LABEL}"
      echo
      # 顺序保持不变：先写 .console，再应用 quirks（避免重入时再次触发）
      echo "$LABEL" | sudo tee "$CONSOLE_FILE" > /dev/null
      apply_quirks_for "$LABEL"
      sleep 5
    )  > /dev/tty1 2>&1
  fi
fi

# 加载驱动
sudo depmod -a || true
# 安装915wifi驱动
if [[ -f "$CONSOLE_FILE" ]]; then
  cur_console="$(tr -d '\r\n' < "$CONSOLE_FILE")"
  for x in "${rk915_set[@]}"; do
    if [[ "$cur_console" == "$x" ]]; then
      msg "insmod rk915.ko: $cur_console"
      sudo modprobe -v rk915 || true
      break
    fi
  done
fi

# ws2812摇杆灯控制加载spi模块
if [[ -f "$CONSOLE_FILE" ]]; then
  cur_console="$(tr -d '\r\n' < "$CONSOLE_FILE")"
  for x in "${spi_set[@]}"; do
    if [[ "$cur_console" == "$x" ]]; then
      msg "sudo modprobe spidev : $cur_console"
      sudo modprobe spidev || true
      break
    fi
  done
fi

sudo modprobe -v mt7610u_sta || true
# 开机将音频设置为SPK如果是OFF的话
STATE=$(amixer get 'Playback Path' | grep -oP "Item0: '\K\w+")
if [ "$STATE" = "OFF" ]; then
    echo "Playback Path is OFF, switching to SPK..."
    amixer set 'Playback Path' 'SPK' || true
    sudo alsactl store || true
else
    echo "Playback Path is already set to $STATE, no change."
fi

if [[ -f "/boot/.cn" ]]; then
  if grep -q "Language" /home/ark/.emulationstation/es_settings.cfg; then
      sed -i -e '/<string name\=\"Language/c\<string name\=\"Language\" value\=\"zh-CN\" \/>' /home/ark/.emulationstation/es_settings.cfg || true
  else
      sed -i '$a <string name\=\"Language\" value\=\"zh-CN\" \/>' /home/ark/.emulationstation/es_settings.cfg || true
  fi
  cp_if_exists "$QUIRKS_DIR/option-gamelist.xml" "/opt/system/gamelist.xml" "yes"
  sudo rm -f /etc/localtime || true
  sudo ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime || true
  sudo sed -i -e '/Language \= en_US/c\Language \= zh_CN' /opt/ppsspp/backupforromsfolder/ppsspp/PSP/SYSTEM/ppsspp.ini || true
  sudo sed -i -e '/Language \= en_US/c\Language \= zh_CN' /opt/ppsspp/backupforromsfolder/ppsspp/PSP/SYSTEM/ppsspp.ini.go || true
  sudo sed -i -e '/Language \= en_US/c\Language \= zh_CN' /opt/ppsspp/backupforromsfolder/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl || true
  sed -i -e '/Language \= en_US/c\Language \= zh_CN' /roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini || true
  sed -i -e '/Language \= en_US/c\Language \= zh_CN' /roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.go || true
  sed -i -e '/Language \= en_US/c\Language \= zh_CN' /roms/psp/ppsspp/PSP/SYSTEM/ppsspp.ini.sdl || true
  sed -i -e '/user_language \= \"/c\user_language \= \"12\"' /home/ark/.config/retroarch32/retroarch.cfg || true
  sed -i -e '/user_language \= \"/c\user_language \= \"12\"' /home/ark/.config/retroarch/retroarch.cfg || true
  sed -i -e '/user_language \= \"/c\user_language \= \"12\"' /home/ark/.config/retroarch32/retroarch.cfg.bak || true
  sed -i -e '/user_language \= \"/c\user_language \= \"12\"' /home/ark/.config/retroarch/retroarch.cfg.bak || true
  sed -i -e '/menu_driver \= \"/c\menu_driver \= \"ozone\"' /home/ark/.config/retroarch32/retroarch.cfg || true
  sed -i -e '/menu_driver \= \"/c\menu_driver \= \"ozone\"' /home/ark/.config/retroarch/retroarch.cfg || true
  sed -i -e '/menu_driver \= \"/c\menu_driver \= \"ozone\"' /home/ark/.config/retroarch32/retroarch.cfg.bak || true
  sed -i -e '/menu_driver \= \"/c\menu_driver \= \"ozone\"' /home/ark/.config/retroarch/retroarch.cfg.bak || true
  sudo rm /boot/.cn
fi

msg "Done."
exit 0
