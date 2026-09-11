param([string]$Godot = 'godot', [switch]$Smoke, [switch]$DoorReview)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot '.qa') | Out-Null
& $Godot --headless --editor --import --path $PSScriptRoot --log-file (Join-Path $PSScriptRoot '.qa/import.log')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$runtimeArgs = @()
if ($Smoke) { $runtimeArgs = @('--quit-after', '300', '--', '--smoke') }
if ($DoorReview) { $runtimeArgs = @('--quit-after', '300', '--', '--door-review') }
& $Godot --path $PSScriptRoot --log-file (Join-Path $PSScriptRoot '.qa/runtime.log') @runtimeArgs
exit $LASTEXITCODE
