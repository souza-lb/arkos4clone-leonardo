package main

import (
    "bufio"
    "errors"
    "fmt"
    "io"
    "io/fs"
    "os"
    "os/exec"
    "path/filepath"
    "runtime"
    "sort"
    "strconv"
    "strings"
)


// ===================== 配置：别名 & 排除 =====================
type ConsoleConfig struct {
	RealName     string
	DisplayName  string
	Brand        string
	ExtraSources []string
}

var Consoles = []ConsoleConfig{
	{"mymini", "XiFan Mymini", "XiFan HandHelds", []string{"logo/480P/", "kenrel/common/"}},
	{"r36max", "XiFan R36Max", "XiFan HandHelds", []string{"logo/720P/", "kenrel/common/"}},
	{"r36pro", "XiFan R36Pro", "XiFan HandHelds", []string{"logo/480P/", "kenrel/common/"}},
	{"xf35h", "XiFan XF35H", "XiFan HandHelds", []string{"logo/480P/", "kenrel/common/"}},
	{"xf40h", "XiFan XF40H", "XiFan HandHelds", []string{"logo/720P/", "kenrel/common/"}},
	{"hg36", "GameConsole HG36", "Other", []string{"logo/480p/", "kenrel/common/"}},
	{"r36ultra", "GameConsole R36Ultra", "Other", []string{"logo/720P/", "kenrel/common/"}},
	{"rx6h", "GameConsole RX6H", "Other", []string{"logo/480P/", "kenrel/common/"}},
	{"k36s", "GameConsole K36S", "Other", []string{"logo/480P/", "kenrel/common/"}},
	{"r46h", "GameConsole R46H", "GameConsole", []string{"logo/768p/", "kenrel/common/"}},
	{"r36splus", "GameConsole R36sPlus", "GameConsole", []string{"logo/720p/", "kenrel/common/"}},
	{"origin r36s panel 0", "GameConsole R36s Panel 0", "GameConsole", []string{"logo/480P/", "kenrel/common/"}},
	{"origin r36s panel 1", "GameConsole R36s Panel 1", "GameConsole", []string{"logo/480P/", "kenrel/common/"}},
	{"origin r36s panel 2", "GameConsole R36s Panel 2", "GameConsole", []string{"logo/480P/", "kenrel/common/"}},
	{"origin r36s panel 3", "GameConsole R36s Panel 3", "GameConsole", []string{"logo/480P/", "kenrel/common/"}},
	{"origin r36s panel 4", "GameConsole R36s Panel 4", "GameConsole", []string{"logo/480P/", "kenrel/common/"}},
	{"origin r36s panel 5", "GameConsole R36s Panel 5", "GameConsole", []string{"logo/480P/", "kenrel/panel5/"}},
	{"a10mini", "YMC A10MINI", "YMC", []string{"logo/480P/", "kenrel/common/"}},
	{"g80cambv12", "R36S Clone G80camb v1.2", "Clone R36s", []string{"logo/480P/", "kenrel/common/"}},
	{"r36s v20 719m", "R36S Clone V2.0 719M", "Clone R36s", []string{"logo/480P/", "kenrel/common/"}},
	{"k36p7", "K36 Panel 7", "Clone R36s", []string{"logo/480P/", "kenrel/common/"}},
	{"xgb36", "GameConsole XGB36", "Other", []string{"logo/480P/", "kenrel/common/"}},
}

var Brands = []string{
	"XiFan HandHelds",
	"GameConsole",
	"YMC",
	"Clone R36s",
	"Other",
}

// ===================== 全局输入 reader =====================
var stdinReader = bufio.NewReader(os.Stdin)

// ===================== ANSI 颜色 & Fancy UI =====================
var (
	ansiReset = "\033[0m"
	ansiRed   = "\033[31m"
	ansiGreen = "\033[32m"
	ansiBlue  = "\033[34m"
	ansiCyan  = "\033[36m"
	ansiBold  = "\033[1m"
)

func supportsANSI() bool {
	info, err := os.Stdout.Stat()
	if err != nil {
		return false
	}
	if (info.Mode() & os.ModeCharDevice) == 0 {
		return false
	}
	// 简单启用：现代 Windows、Linux、macOS 终端通常支持 ANSI
	return true
}

func colorWrap(s, code string) string {
	if !supportsANSI() {
		return s
	}
	return code + s + ansiReset
}

// ===================== ASCII LOGO: LCDYK =====================
func asciiLogoLCDYK() []string {
	return []string{
		`  _     ____ ______   ___  __`,
		` | |   / ___|  _ \ \ / / |/ / `,
		` | |  | |   | | | \ V /| ' /   `,
		` | |__| |___| |_| || | | . \  `,
		` |_____\____|____/ |_| |_|\_\ `,
	}
}

func fancyHeader(title string) {
	clearScreen()
	fmt.Println(colorWrap(strings.Repeat("=", 64), ansiCyan))
	for _, ln := range asciiLogoLCDYK() {
		fmt.Println(colorWrap(" "+ln, ansiBlue))
	}
	fmt.Println(colorWrap(" "+title, ansiBold+ansiGreen))
	fmt.Println(colorWrap(strings.Repeat("=", 64), ansiCyan))
	fmt.Println()
}

// ===================== 交互说明（双语） =====================
// ======= 样式常量与辅助打印函数 =======
var (
	// 复用之前的 ansi* 变量：ansiBold, ansiCyan, ansiRed, ansiGreen, ansiBlue 等
	HDR  = ansiBold + ansiGreen
	BUL  = ansiBlue
	WARN = ansiBold + ansiRed
	EMP  = ansiBold + ansiCyan
	NOTE = ansiCyan
	DIM  = "" // 终端中没有专门的 dim 颜色时，留空或用 cyan 淡化；保持空以自动退回无色
)

// c: wrap string with style code (会根据 supportsANSI 自动降级)
func c(s, style string) string {
	if style == "" {
		return s
	}
	return colorWrap(s, style)
}

// p: 打印（等同于你写的 print(...) ）
func p(s string) {
	fmt.Println(s)
}

// praw: 打印不换色（如果需要直接原样输出）
func praw(s string) {
	fmt.Println(s)
}

// ===================== 更新后的 introAndWaitFancy（使用你给的文案样式） =====================
func introAndWaitFancy() {
	fancyHeader("DTB Selector - 请选择机型 / Select Your Console")
	// 直接按你提供的行构造输出（中英并列）
	p(c("\n================ Welcome 欢迎使用 ================", HDR))
	p(c("说明：本系统目前只支持下列机型，如果你的 R36 克隆机不在列表中，则暂时无法使用。", BUL))
	p(c("请不要使用原装 EmuELEC 卡中的 dtb 文件搭配本系统，否则会导致系统无法启动！", WARN))
	p("") // 空行
	p(c("选择机型前请阅读：", EMP))
	p(c("  • 本工具会清理目标目录顶层的 .dtb/.ini/.orig/.tony 文件，并删除 BMPs 文件夹；", BUL))
	p(c("  • 随后复制所选机型及额外映射资源。", BUL))
	p(c("  • 按 Enter 继续；输入 q 退出。", NOTE))
	p(c("-----------------------------------------", DIM))
	p(c("NOTE:", EMP))
	p(c("  • This system currently only supports the listed R36 clones;", BUL))
	p(c("    if your clone is not in the list, it is not supported yet.", BUL))
	p(c("  • Do NOT use the dtb files from the stock EmuELEC card with this system — it will brick the boot.", WARN))
	p("") // 空行
	p(c("Before selecting a console:", EMP))
	p(c("  • This tool cleans top-level .dtb/.ini/.orig/.tony files and removes the BMPs/ folder,", BUL))
	p(c("    then copies the chosen console and any mapped extra sources.", BUL))
	p(c("  • Press Enter to continue; type 'q' to quit.", NOTE))

	// 等待用户输入或退出
	fmt.Print(colorWrap("\n按 Enter 继续，或输入 ", ansiBold))
	fmt.Print(colorWrap("q", ansiRed))
	fmt.Print(colorWrap(" 退出：", ansiBold))
	line, _ := stdinReader.ReadString('\n')
	if strings.TrimSpace(strings.ToLower(line)) == "q" {
		fmt.Println()
		fmt.Println(colorWrap("已取消，拜拜 👋 (Cancelled, bye!)", ansiGreen))
		os.Exit(0)
	}
}


// ===================== 屏幕/终端检查 =====================
func isTerminal() bool {
	info, err := os.Stdin.Stat()
	if err != nil {
		return false
	}
	return (info.Mode() & os.ModeCharDevice) != 0
}

func clearScreen() {
	if !isTerminal() {
		return
	}
	switch runtime.GOOS {
	case "windows":
		cmd := exec.Command("cmd", "/c", "cls")
		cmd.Stdout = os.Stdout
		_ = cmd.Run()
	default:
		cmd := exec.Command("clear")
		cmd.Stdout = os.Stdout
		_ = cmd.Run()
	}
}

// ===================== 输入工具（双语提示） =====================
func prompt(msg string) (string, error) {
	if !isTerminal() {
		return "", errors.New("non-interactive stdin")
	}
	fmt.Print(msg)
	line, err := stdinReader.ReadString('\n')
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(line), nil
}

func readIntChoice(msg string) (int, error) {
	for {
		resp, err := prompt(msg)
		if err != nil {
			return -1, err
		}
		n, err := strconv.Atoi(resp)
		if err != nil {
			fmt.Println(colorWrap("请输入数字（Please enter a number）", ansiRed))
			continue
		}
		return n, nil
	}
}

// ===================== 文件操作 =====================
func cleanTargetDirectory() error {
	fmt.Println()
	fmt.Println(colorWrap("开始清理目标目录 (Cleaning target directory)...", ansiCyan))

	patterns := []string{"*.dtb", "*.ini", "*.orig", "*.tony"}
	for _, pat := range patterns {
		matches, err := filepath.Glob(pat)
		if err != nil {
			return err
		}
		for _, f := range matches {
			fmt.Printf("  删除文件: %s\n", f)
			if err := os.Remove(f); err != nil {
				fmt.Printf("    警告: 删除失败 %s: %v\n", f, err)
			}
		}
	}

	bmpPath := "BMPs"
	if _, err := os.Stat(bmpPath); err == nil {
		fmt.Printf("  删除目录: %s\n", bmpPath)
		if err := os.RemoveAll(bmpPath); err != nil {
			fmt.Printf("    警告: 删除目录失败 %s: %v\n", bmpPath, err)
		}
	}
	return nil
}

func copyFile(src, dst string) error {
	in, err := os.Open(src)
	if err != nil {
		return err
	}
	defer in.Close()

	if err := os.MkdirAll(filepath.Dir(dst), 0o755); err != nil {
		return err
	}

	out, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o644)
	if err != nil {
		return err
	}
	defer out.Close()

	buf := make([]byte, 32*1024)
	if _, err := io.CopyBuffer(out, in, buf); err != nil {
		return err
	}
	return nil
}

func copyDirectory(src, dst string) error {
	info, err := os.Stat(src)
	if err != nil {
		return err
	}
	if !info.IsDir() {
		return fmt.Errorf("source is not a directory: %s", src)
	}

	return filepath.WalkDir(src, func(path string, d fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		rel, err := filepath.Rel(src, path)
		if err != nil {
			return err
		}
		targetPath := filepath.Join(dst, rel)
		if d.IsDir() {
			if err := os.MkdirAll(targetPath, 0o755); err != nil {
				return err
			}
			return nil
		}
		return copyFile(path, targetPath)
	})
}

// ===================== 菜单相关（双语） =====================
func selectBrand() (string, error) {
	clearScreen()
	fmt.Println()
	fmt.Println(colorWrap("┌────────────────────────────────────────┐", ansiCyan))
	fmt.Println(colorWrap("│ 请选择品牌 / Please select a brand", ansiBold+ansiGreen))
	fmt.Println(colorWrap("└────────────────────────────────────────┘", ansiCyan))
	for i, brand := range Brands {
		fmt.Printf("  %d. %s\n", i+1, brand)
	}
	fmt.Printf("  %d. %s\n", 0, "Exit/退出")

	for {
		choice, err := readIntChoice("\n选择序号 (Select number): ")
		if err != nil {
			return "", err
		}
		if choice == 0 {
			return "", nil
		}
		if choice > 0 && choice <= len(Brands) {
			return Brands[choice-1], nil
		}
		fmt.Println(colorWrap("选择无效，请重试 (Invalid selection).", ansiRed))
	}
}

func selectConsole(brand string) (*ConsoleConfig, error) {
	clearScreen()
	fmt.Println()
	fmt.Println(colorWrap("┌────────────────────────────────────────┐", ansiCyan))
	fmt.Printf("│ %s\n", colorWrap("该品牌可用机型 / Available consoles for: "+brand, ansiBold+ansiGreen))
	fmt.Println(colorWrap("└────────────────────────────────────────┘", ansiCyan))

	var brandConsoles []ConsoleConfig
	for _, c := range Consoles {
		if c.Brand == brand {
			brandConsoles = append(brandConsoles, c)
		}
	}
	sort.Slice(brandConsoles, func(i, j int) bool {
		return brandConsoles[i].DisplayName < brandConsoles[j].DisplayName
	})

	if len(brandConsoles) == 0 {
		fmt.Println(colorWrap("该品牌下没有机型 (No consoles found).", ansiRed))
		_, _ = prompt("按 Enter 返回 (Press Enter to continue)...")
		return nil, nil
	}

	for i, c := range brandConsoles {
		fmt.Printf("  %d. %s\n", i+1, c.DisplayName)
	}
	fmt.Printf("  %d. %s\n", 0, "Back/返回")

	for {
		choice, err := readIntChoice("\n选择序号 (Select number): ")
		if err != nil {
			return nil, err
		}
		if choice == 0 {
			return nil, nil
		}
		if choice > 0 && choice <= len(brandConsoles) {
			return &brandConsoles[choice-1], nil
		}
		fmt.Println(colorWrap("选择无效，请重试 (Invalid selection).", ansiRed))
	}
}

func showMenu() (*ConsoleConfig, error) {
	for {
		brand, err := selectBrand()
		if err != nil {
			return nil, err
		}
		if brand == "" {
			return nil, nil
		}
		console, err := selectConsole(brand)
		if err != nil {
			return nil, err
		}
		if console != nil {
			return console, nil
		}
	}
}

// ===================== 复制逻辑 =====================
func copySelectedConsole(console *ConsoleConfig) error {
	if console == nil {
		return errors.New("no console selected")
	}
	fmt.Printf("\n%s\n", colorWrap("开始复制 (Copying): "+console.DisplayName, ansiCyan))

	srcPath := filepath.Join("consoles", console.RealName)
	if _, err := os.Stat(srcPath); os.IsNotExist(err) {
		return fmt.Errorf("source directory not found: %s", srcPath)
	}

	if err := copyDirectory(srcPath, "."); err != nil {
		return fmt.Errorf("failed to copy console: %v", err)
	}

	fmt.Println(colorWrap("正在复制额外资源 (Copying extra resources)...", ansiCyan))
	for _, extra := range console.ExtraSources {
		extraSrc := filepath.Join("consoles", extra)
		if _, err := os.Stat(extraSrc); err == nil {
			fmt.Printf("  Copying: %s\n", extra)
			if err := copyDirectory(extraSrc, "."); err != nil {
				return fmt.Errorf("failed to copy extra source %s: %v", extra, err)
			}
		} else {
			fmt.Printf("  Warning: Extra source not found: %s\n", extra)
		}
	}
	return nil
}

func showSuccessFancy(consoleName string) {
	fmt.Println()
	fmt.Println(colorWrap(strings.Repeat("=", 64), ansiCyan))
	fmt.Println(colorWrap("  ✅  操作完成！Operation completed!", ansiBold+ansiGreen))
	fmt.Printf("  %s\n", colorWrap("已复制的机型： "+consoleName+" (Copied console: "+consoleName+")", ansiBold+ansiBlue))
	fmt.Println(colorWrap("  提示：请检查目标目录确保文件完整。(Tip: verify files in the destination directory.)", ansiCyan))
	fmt.Println(colorWrap(strings.Repeat("=", 64), ansiCyan))
}

// ===================== 语言选择 =====================
func selectLanguage() (string, error) {
	clearScreen()
	fmt.Println()
	fmt.Println(colorWrap("请选择语言 / Select language:", EMP))
	fmt.Println("  1. English (默认 Default)")
	fmt.Println("  2. 中文")

	for {
		choice, err := prompt("输入序号或按 Enter 默认选择 English: ")
		if err != nil {
			return "", err
		}
		choice = strings.TrimSpace(choice)
		if choice == "" || choice == "1" {
			return "en", nil
		} else if choice == "2" {
			return "cn", nil
		} else {
			fmt.Println(colorWrap("选择无效，请重试 (Invalid selection).", ansiRed))
		}
	}
}
// 创建语言标记文件
func createLanguageFile(lang string) error {
	if lang == "cn" {
		f, err := os.Create(".cn")
		if err != nil {
			return err
		}
		defer f.Close()
		fmt.Println(colorWrap("已创建中文语言标记文件 (.cn created)", ansiCyan))
	}
	return nil
}


// ===================== main =====================
func main() {
	clearScreen()
	fmt.Println(colorWrap("DTB Selector Tool - Go Version", ansiBold+ansiGreen))
	introAndWaitFancy()

	console, err := showMenu()
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	if console == nil {
		fmt.Println(colorWrap("Goodbye! 再见。", ansiGreen))
		return
	}

	if err := cleanTargetDirectory(); err != nil {
		fmt.Printf("Error cleaning directory: %v\n", err)
		return
	}

	if err := copySelectedConsole(console); err != nil {
		fmt.Printf("Error copying files: %v\n", err)
		return
	}

	showSuccessFancy(console.DisplayName)

		// ===== 新增语言选择 =====
	lang, err := selectLanguage()
	if err != nil {
		fmt.Printf("Error selecting language: %v\n", err)
		return
	}
	if err := createLanguageFile(lang); err != nil {
		fmt.Printf("Error creating language file: %v\n", err)
		return
	}

	fmt.Println(colorWrap("\n操作完成！已选择语言: "+lang, ansiGreen))
}
