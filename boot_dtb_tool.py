#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import fnmatch

# ===================== 配置：别名 & 排除 =====================
# 1) 目录别名映射：键 = 实际子目录名（位于 consoles/ 下面），值 = 想展示的别名
ALIASES = {
    "mymini": "XiFan Mymini",
    "r36max": "XiFan R36Max",
    "r36pro": ["XiFan R36Pro", "K36 Panel 1"],
    "xf35h": "XiFan XF35H",
    "xf40h": "XiFan XF40H",
    "hg36": "GameConsole HG36",
    "r36ultra": "GameConsole R36Ultra",
    "rx6h": "GameConsole RX6H",
    "k36s": ["GameConsole K36S", "GameConsole R36T"],
    "r46h": "GameConsole R46H",
    "r36splus": "GameConsole R36sPlus",
    "origin r36s panel 0": "GameConsole R36s Panel 0",
    "origin r36s panel 1": "GameConsole R36s Panel 1",
    "origin r36s panel 2": "GameConsole R36s Panel 2",
    "origin r36s panel 3": "GameConsole R36s Panel 3",
    "origin r36s panel 4": "GameConsole R36s Panel 4",
    "origin r36s panel 5": "GameConsole R36s Panel 5",
    "a10mini": "YMC A10MINI",
    "g80cambv12": "R36S Clone G80camb v1.2",
    "r36s v20 719m": "R36S Clone V2.0 719M",
    "k36p7": "K36 Panel 7",
}

# 1.1) 新增：品牌映射（用于一级菜单分组）
#      键为 consoles 下的真实目录名；值为品牌名
BRAND_MAP = {
    "XiFan HandHeld" : ["XiFan Mymini", "XiFan R36Max", "XiFan R36Pro", "XiFan XF35H", "XiFan XF40H"],
    "GameConsole" : ["GameConsole R36s Panel 0", "GameConsole R36s Panel 1", "GameConsole R36s Panel 2", "GameConsole R36s Panel 3", "GameConsole R36s Panel 4", "GameConsole R36s Panel 5", "GameConsole R36sPlus", "GameConsole R46H"],
    "YMC" : ["YMC A10MINI"],
    "Clone R36s" : ["R36S Clone G80camb v1.2", "R36S Clone V2.0 719M", "K36 Panel 1", "K36 Panel 7"],
    "Other" : ["GameConsole HG36", "GameConsole R36Ultra", "GameConsole RX6H", "GameConsole K36S", "GameConsole R36T", ]
}

# 2) 排除规则（glob 通配，多条规则其一匹配即排除）
EXCLUDE_PATTERNS = {
    "files", "kenrel", "logo",
}

# 3) 额外复制映射：
#    键：你“选中”的 consoles 子目录名（real name）
#    值：一个列表，里面是“还需要一起复制”的其它目录路径：
#       - 如果是相对路径：相对于 consoles/ 目录（例如 "common"、"shared/skins"）
#       - 如果是绝对路径：按绝对路径处理（例如 "D:/assets/overrides" 或 "/opt/assets"）
#    复制规则与主复制一致：会把来源目录下“所有内容”覆盖复制到目标（脚本目录）。
EXTRA_COPY_MAP = {
    # 示例：选中 r36max 时，同时把 consoles/common 与 consoles/shared/ui 也复制过去
    "mymini": ["logo/480P/", "kenrel/common/"],
    "r36max": ["logo/720P/", "kenrel/common/"],
    "r36pro": ["logo/480P/", "kenrel/common/"],
    "xf35h": ["logo/480P/", "kenrel/common/"],
    "xf40h": ["logo/720P/", "kenrel/common/"],
    "r36ultra": ["logo/720P/", "kenrel/common/"],
    "k36s": ["logo/480P/", "kenrel/common/"],
    "hg36": ["logo/480p/", "kenrel/common/"],
    "rx6h": ["logo/480p/", "kenrel/common/"],
    "r46h": ["logo/768p/", "kenrel/common/"],
    "r36splus": ["logo/720p/", "kenrel/common/"],
    "origin r36s panel 0": ["logo/480P/", "kenrel/common/"],
    "origin r36s panel 1": ["logo/480P/", "kenrel/common/"],
    "origin r36s panel 2": ["logo/480P/", "kenrel/common/"],
    "origin r36s panel 3": ["logo/480P/", "kenrel/common/"],
    "origin r36s panel 4": ["logo/480P/", "kenrel/common/"],
    "origin r36s panel 5": ["logo/480P/", "kenrel/panel5/"],
    "a10mini": ["logo/480P/", "kenrel/common/"],
    "g80cambv12": ["logo/480P/", "kenrel/common/"],
    "r36s v20 719m": ["logo/480P/", "kenrel/common/"],
    "k36p7": ["logo/480P/", "kenrel/common/"],

    # 按需添加更多键值
}

# ===================== 工具函数 =====================
def intro_and_wait():
    if not sys.stdin.isatty():  # 非交互直接返回
        return

    # 尽量在 Windows 上启用 ANSI 颜色
    try:
        import colorama
        colorama.init()
    except Exception:
        pass

    def c(txt, style=None):
        return f"\033[{style}m{txt}\033[0m" if style else txt

    HDR   = "96;1"   # 亮青色 + 粗体
    WARN  = "91;1"   # 亮红色 + 粗体
    NOTE  = "93"     # 黄色
    BUL   = "97"     # 亮白
    DIM   = "90"     # 灰色
    EMP   = "97;1"   # 亮白粗体
    PROMPT= "92;1"   # 亮绿色粗体

    print(c("\n================ Welcome 欢迎使用 ================", HDR))
    print(c("说明：本系统目前只支持下列机型，如果你的 R36 克隆机不在列表中，则暂时无法使用。", BUL))
    print(c("请不要使用原装 EmuELEC 卡中的 dtb 文件搭配本系统，否则会导致系统无法启动！", WARN))
    print()
    print(c("选择机型前请阅读：", EMP))
    print(c("  • 本工具会清理目标目录顶层的 .dtb/.ini/.orig/.tony 文件，并删除 BMPs 文件夹；", BUL))
    print(c("  • 随后复制所选机型及额外映射资源。", BUL))
    print(c("  • 按 Enter 继续；输入 q 退出。", NOTE))
    print(c("-----------------------------------------", DIM))
    print(c("NOTE:", EMP))
    print(c("  • This system currently only supports the listed R36 clones;", BUL))
    print(c("    if your clone is not in the list, it is not supported yet.", BUL))
    print(c("  • Do NOT use the dtb files from the stock EmuELEC card with this system — it will brick the boot.", WARN))
    print()
    print(c("Before selecting a console:", EMP))
    print(c("  • This tool cleans top-level .dtb/.ini/.orig/.tony files and removes the BMPs/ folder,", BUL))
    print(c("    then copies the chosen console and any mapped extra sources.", BUL))
    print(c("  • Press Enter to continue; type 'q' to quit.", NOTE))
    cont = input(c("\n按 Enter 继续 / Press Enter to continue (q to quit): ", PROMPT)).strip().lower()
    if cont == 'q':
        print("已退出 / Exited.")
        sys.exit(0)


def get_base_dir():
    """
    返回当前脚本/可执行程序所在目录（兼容 PyInstaller 冻结的可执行文件）
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_consoles_dir():
    return os.path.join(get_base_dir(), "consoles")

def is_excluded(name: str) -> bool:
    """
    判断目录名是否被 EXCLUDE_PATTERNS 排除（glob 匹配）
    """
    for pat in EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(name, pat):
            return True
    return False

def list_subfolders(parent_dir):
    """
    列出未被排除、且在 EXTRA_COPY_MAP 中配置过的子目录（大小写/前后空格不敏感）。
    支持 ALIASES 的 value 为字符串或列表：
      - 字符串：生成一条菜单
      - 列表：为同一真实目录生成多条菜单（每个显示名一条）
    返回 [(display_name, real_name)]，顺序跟 EXTRA_COPY_MAP 的键顺序一致
    """
    if not os.path.exists(parent_dir):
        print("❌ 'consoles' folder not found:", parent_dir)
        return []

    items = []
    for real_key in EXTRA_COPY_MAP.keys():
        norm = real_key.strip().casefold()
        # 实际目录必须存在才能展示
        for name in os.listdir(parent_dir):
            full = os.path.join(parent_dir, name)
            if not os.path.isdir(full):
                continue
            if is_excluded(name):
                continue
            if name.strip().casefold() == norm:
                alias_val = ALIASES.get(real_key, real_key)
                if isinstance(alias_val, (list, tuple)):
                    for disp in alias_val:
                        items.append((str(disp), name))  # 同一真实目录 -> 多条菜单
                else:
                    items.append((str(alias_val), name))
                break  # 找到对应目录就跳出

    return items


def show_menu(items):
    """
    打印菜单（只展示别名/显示名）
    """
    print("\nFound {} subfolders in 'consoles':".format(len(items)))
    for i, (display, _real) in enumerate(items, 1):
        print(f"{i}. {display}")

def copy_all_contents(src_dir, dst_dir):
    """
    复制 src_dir 下所有内容至 dst_dir（保留层级，覆盖同名文件）
    返回 (files_copied, dirs_touched)
    """
    files_copied = 0
    dirs_touched = 0

    for root, dirs, files in os.walk(src_dir):
        rel = os.path.relpath(root, src_dir)
        target_root = dst_dir if rel == "." else os.path.join(dst_dir, rel)

        if not os.path.exists(target_root):
            os.makedirs(target_root, exist_ok=True)
            dirs_touched += 1

        for f in files:
            src_path = os.path.join(root, f)
            dst_path = os.path.join(target_root, f)
            shutil.copy2(src_path, dst_path)  # overwrite
            files_copied += 1

    return files_copied, dirs_touched

def remove_files_by_ext(base_dir, extensions):
    """
    删除 base_dir 目录（仅该层，不递归）中指定扩展名的所有文件。
    extensions: 形如 {'.dtb', '.ini'}
    返回删除计数
    """
    removed = 0
    for name in os.listdir(base_dir):
        full = os.path.join(base_dir, name)
        if os.path.isfile(full):
            _, ext = os.path.splitext(name)
            if ext.lower() in extensions:
                try:
                    os.remove(full)
                    removed += 1
                    print(f"🧹 Removed file: {full}")
                except Exception as e:
                    print(f"Failed to remove {full}: {e}")
    return removed

def remove_dir_if_exists(path):
    """
    删除目录（若存在），返回是否删除成功
    """
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
            print(f"Removed folder: {path}")
            return True
        except Exception as e:
            print(f"Failed to remove folder {path}: {e}")
    return False

def clean_destination(dst_dir):
    """
    清理目标目录：删除 .dtb / .ini 文件（仅顶层），并删除 BMPs 文件夹。
    """
    # print("\nCleaning destination directory...")
    removed_files = remove_files_by_ext(dst_dir, {".dtb", ".ini", ".orig", ".tony"})
    # bmps_removed = remove_dir_if_exists(os.path.join(dst_dir, "BMPs"))
    # print(f"✨ Cleaned. Removed files: {removed_files}, removed BMPs: {bmps_removed}")

def resolve_extra_source(consoles_dir, path_str):
    """
    解析 EXTRA_COPY_MAP 里的路径：
      - 绝对路径：原样返回
      - 相对路径：认为是相对 consoles_dir
    """
    if os.path.isabs(path_str):
        return path_str
    return os.path.join(consoles_dir, path_str)

def copy_with_extras(selected_real_name, consoles_dir, dst_dir):
    """
    先复制选中目录，再根据 EXTRA_COPY_MAP 复制额外来源。
    """
    total_files = 0
    total_dirs = 0

    # 1) 复制选中目录
    selected_src = os.path.join(consoles_dir, selected_real_name)
    # print("Copying selected folder (overwrite existing files)...")
    f1, d1 = copy_all_contents(selected_src, dst_dir)
    total_files += f1
    total_dirs += d1
    # print(f"Selected copied: files={f1}, dirs={d1}")

    # 2) 复制额外来源（如果配置了）
    extras = EXTRA_COPY_MAP.get(selected_real_name, [])
    if extras:
        # print("\n➕ Copying extra mapped sources:")
        for p in extras:
            src_path = resolve_extra_source(consoles_dir, p)
            if not os.path.isdir(src_path):
                print(f"Extra source not found or not a directory, skipped: {src_path}")
                continue
            f, d = copy_all_contents(src_path, dst_dir)
            total_files += f
            total_dirs += d
            print(f"   • {src_path}  → files={f}, dirs={d}")
    else:
        print("\n(no extra sources mapped for this selection)")

    return total_files, total_dirs

def choose_language_and_mark(dst_dir):
    """
    选择语言：英文不动；中文则在目标目录创建一个 .cn 文件作为标记。
    非交互环境下直接跳过。
    """
    if not sys.stdin.isatty():
        return

    print("\n🌐 选择语言 / Language")
    print("1) English (默认 / default)")
    print("2) 中文")
    sel = input("Enter 1 or 2 [1]: ").strip().lower()

    if sel in {"2", "zh", "cn", "chinese", "中文", "汉语"}:
        marker = os.path.join(dst_dir, ".cn")
        try:
            # 创建空文件；已存在则保持不变
            with open(marker, "a", encoding="utf-8"):
                pass
            # print(f"已选择中文，已创建标记文件: {marker}")
        except Exception as e:
            print(f"创建 {marker} 失败: {e}")
    # else:
        # print("✓ English selected; no changes made.")

def build_brand_to_items(items):
    """
    基于 BRAND_MAP 把现有 items[(display, real)] 分组到品牌。
    仅展示既在 BRAND_MAP 中、又真实存在于 consoles/ 的机型。
    返回：Ordered dict-like 的普通 dict：{brand: [(display, real), ...]}
    """
    # 现有可用机型的 display -> (display, real)
    display_map = {disp.strip().casefold(): (disp, real) for disp, real in items}

    brand_to_items = {}
    for brand, display_list in BRAND_MAP.items():
        sub = []
        for disp in display_list:
            key = disp.strip().casefold()
            if key in display_map:
                sub.append(display_map[key])
        if sub:
            brand_to_items[brand] = sub

    # 若 BRAND_MAP 没覆盖但 items 里有剩余机型，可作为兜底“Other (Unmapped)”
    covered = {d.strip().casefold() for lst in BRAND_MAP.values() for d in (lst if isinstance(lst, list) else [])}
    unmapped = [pair for disp, pair in display_map.items() if disp not in covered]
    if unmapped:
        brand_to_items.setdefault("Other", [])
        # 去重追加（避免 BRAND_MAP 自带的 Other 覆盖）
        existing = {d for d, _ in brand_to_items["Other"]}
        for d, r in unmapped:
            if d not in existing:
                brand_to_items["Other"].append((d, r))

    return brand_to_items


def show_brand_menu(brand_to_items):
    """
    显示品牌一级菜单（整齐对齐），返回用户选择的品牌名；返回 None 表示退出。
    """
    if not sys.stdin.isatty():
        return next(iter(brand_to_items), None)

    brands = list(brand_to_items.keys())
    counts = [len(brand_to_items[b]) for b in brands]

    # 计算对齐宽度
    idx_w = len(str(len(brands)))
    brand_w = max(len(b) for b in brands) if brands else 0
    cnt_w = len(str(max(counts))) if counts else 1

    print("\n选择品牌 / Choose a brand")
    for i, b in enumerate(brands, 1):
        c = len(brand_to_items[b])
        plural = "model" if c == 1 else "models"
        # 右对齐序号，左对齐品牌名，右对齐数量，括号与单位对齐
        print(f"{str(i).rjust(idx_w)}. {b.ljust(brand_w)}  ({str(c).rjust(cnt_w)} {plural})")

    while True:
        choice = input("\nEnter a number to choose a brand (0 to exit): ").strip().lower()
        if choice in {"0", "q"}:
            print("Exited.")
            return None
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(brands):
                return brands[idx - 1]
        print("Please enter a valid number.")



def choose_folder_and_copy_or_back(items, consoles_dir):
    """
    机型菜单：数字选择机型；输入 0 返回上一级品牌菜单；输入 q 退出整个程序。
    成功完成拷贝返回 'done'；返回上一级返回 'back'；退出返回 'exit'。
    """
    if not items:
        print("(No subfolders to choose from.)")
        return "back"

    while True:
        choice = input("\nEnter a number to choose a model (0 to go back, q to exit): ").strip().lower()
        if choice == "0":
            os.system("cls" if os.name == "nt" else "clear")
            return "back"
        if choice == "q":
            print("Exited.")
            return "exit"
        if not choice.isdigit():
            print("⚠️ Please enter a valid number.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(items):
            display, real = items[idx - 1]
            src_dir = os.path.join(consoles_dir, real)
            dst_dir = get_base_dir()

            print(f"\nYou chose: {display}  (folder: {real})")
            # 先清理，再复制
            clean_destination(dst_dir)
            total_files, total_dirs = copy_with_extras(real, consoles_dir, dst_dir)

            # 复制完成后语言选择
            os.system("cls" if os.name == "nt" else "clear")
            choose_language_and_mark(dst_dir)
            return "done"
        else:
            print("Number out of range, try again.")


def choose_brand_then_model(items, consoles_dir):
    """
    新入口：先选品牌，再选机型。
    在机型菜单按 0 返回品牌菜单；按 q 直接退出。
    （已去掉中文提示行）
    """
    if not items:
        print("(No subfolders to choose from.)")
        return

    brand_to_items = build_brand_to_items(items)

    # 若 BRAND_MAP 没有匹配上任何机型：使用单层菜单，但仍支持 0 返回（即重新显示同一菜单），q 退出
    if not brand_to_items:
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            show_menu(items)
            status = choose_folder_and_copy_or_back(items, consoles_dir)
            if status in {"done", "exit"}:
                return
            # status == "back" 时继续循环，重新显示菜单
        # 不会到达这里
        return

    # 正常两级菜单：品牌 -> 机型
    while True:
        brand = show_brand_menu(brand_to_items)
        if brand is None:
            return  # 用户在品牌菜单选择退出

        while True:
            os.system("cls" if os.name == "nt" else "clear")
            sub_items = brand_to_items[brand]
            show_menu(sub_items)  # 不再打印额外的中文提示

            status = choose_folder_and_copy_or_back(sub_items, consoles_dir)
            if status == "back":
                # 回到品牌选择
                break
            # 'done' 表示已完成复制；'exit' 表示用户选择退出
            return

def main():
    consoles_dir = get_consoles_dir()
    items = list_subfolders(consoles_dir)   # [(display_name, real_name)]
    intro_and_wait()  
    os.system("cls" if os.name == "nt" else "clear")
    # show_menu(items)
 
    # choose_folder_and_copy(items, consoles_dir)
    choose_brand_then_model(items, consoles_dir)

if __name__ == "__main__":
    main()
