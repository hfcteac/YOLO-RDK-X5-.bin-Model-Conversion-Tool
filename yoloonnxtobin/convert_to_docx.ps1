# ============================================================
# convert_to_docx.ps1  — 将 README.md 转为漂亮 Word 文档
# 使用方式：右键 → "使用 PowerShell 运行" 或在终端执行：
#   powershell -ExecutionPolicy Bypass -File convert_to_docx.ps1
# ============================================================

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$MD  = "README.md"
$DOC = "YOLO转RDK_X5_bin完整指南.docx"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  README.md → 漂亮 Word 文档转换器" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ------- Step 1: 检查 pandoc -------
$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    Write-Host "[!] 未安装 pandoc，正在自动安装..." -ForegroundColor Yellow
    $choice = Read-Host "  是否允许通过 winget 安装? (Y/n)"
    if ($choice -ne 'n' -and $choice -ne 'N') {
        winget install --id JohnMacFarlane.Pandoc -e --silent 2>$null
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  winget 失败，尝试 chocolatey..." -ForegroundColor Yellow
            choco install pandoc -y 2>$null
        }
    }
    # 刷新 PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

$pandoc = Get-Command pandoc -ErrorAction SilentlyContinue
if (-not $pandoc) {
    Write-Host ""
    Write-Host "❌ 自动安装失败，请手动下载 pandoc：" -ForegroundColor Red
    Write-Host "   https://github.com/jgm/pandoc/releases/latest" -ForegroundColor Yellow
    Write-Host "   下载 pandoc-*-windows-x86_64.msi，双击安装后重新运行本脚本。" -ForegroundColor Yellow
    Read-Host "按回车退出..."
    exit 1
}

Write-Host "[1/3] pandoc 就绪：$($pandoc.Source)" -ForegroundColor Green

# ------- Step 2: 检查源文件 -------
if (-not (Test-Path $MD)) {
    Write-Host "❌ 找不到 $MD" -ForegroundColor Red
    Read-Host "按回车退出..."
    exit 1
}
Write-Host "[2/3] 源文件：$MD" -ForegroundColor Green

# ------- Step 3: 生成自定义参考文档（optional）-------
# 如果有 reference.docx 就用它控制样式，否则用 pandoc 默认
$refDoc = Join-Path $ScriptDir "reference.docx"

# ------- Step 4: 转换 -------
Write-Host "[3/3] 正在生成 Word 文档..." -ForegroundColor Green

$args = @(
    "-s",
    "-f", "markdown+emoji+yaml_metadata_block+smart",
    "-t", "docx",
    "-o", $DOC,
    "--toc",           # 自动生成目录
    "--toc-depth=3",   # 目录到三级标题
    "--number-sections", # 章节自动编号
    "--highlight-style=tango",
    "-M", "title=`"YOLO 模型转 RDK X5 .bin 完整指南`"",
    "-M", "author=`"RDK X5 开发手册`"",
    "-M", "date=`"$(Get-Date -Format 'yyyy-MM-dd')`"",
    "-M", "lang=zh-CN",
    "--metadata", "papersize:a4",
    "-V", "mainfont=微软雅黑",
    "-V", "CJKmainfont=微软雅黑",
    "-V", "monofont=Consolas",
    "-V", "fontsize=11pt",
    "-V", "linestretch=1.25",
    "-V", "margin-top=2.5cm",
    "-V", "margin-bottom=2.5cm",
    "-V", "margin-left=2.5cm",
    "-V", "margin-right=2.5cm"
)

if (Test-Path $refDoc) {
    $args += "--reference-doc=$refDoc"
}
$args += $MD

& pandoc $args

if ($LASTEXITCODE -eq 0 -and (Test-Path $DOC)) {
    $size = [math]::Round((Get-Item $DOC).Length / 1KB, 1)
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ 转换成功！" -ForegroundColor Green
    Write-Host "  文件：$DOC" -ForegroundColor Green
    Write-Host "  大小：${size} KB" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  文档包含：" -ForegroundColor White
    Write-Host "  • 自动目录（带章节编号）" -ForegroundColor White
    Write-Host "  • 中文字体（微软雅黑）" -ForegroundColor White
    Write-Host "  • 代码高亮" -ForegroundColor White
    Write-Host "  • Mermaid 流程图" -ForegroundColor White
    Write-Host ""
    
    # 问要不要打开
    $open = Read-Host "  是否立即打开 Word 文档? (Y/n)"
    if ($open -ne 'n' -and $open -ne 'N') {
        Start-Process $DOC
    }
} else {
    Write-Host ""
    Write-Host "❌ 转换失败！请检查 pandoc 是否正确安装。" -ForegroundColor Red
    Write-Host "  手动测试：pandoc README.md -o test.docx" -ForegroundColor Yellow
}

Read-Host "`n按回车退出..."
