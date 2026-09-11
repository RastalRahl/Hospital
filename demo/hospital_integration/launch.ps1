param([string]$Godot = 'godot', [switch]$Smoke, [switch]$DoorReview, [switch]$WallReview, [switch]$FamilyReview, [switch]$JunctionReview, [switch]$JunctionSmoke)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force (Join-Path $PSScriptRoot '.qa') | Out-Null
& $Godot --headless --editor --import --path $PSScriptRoot --log-file (Join-Path $PSScriptRoot '.qa/import.log')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$runtimeArgs = @()
if ($Smoke) { $runtimeArgs = @('--quit-after', '300', '--', '--smoke') }
if ($DoorReview) { $runtimeArgs = @('--quit-after', '300', '--', '--door-review') }
if ($WallReview) { $runtimeArgs = @('--quit-after', '300', '--', '--wall-review') }
if ($FamilyReview) { $runtimeArgs = @('--quit-after', '300', '--', '--family-review') }
if ($JunctionReview) { $runtimeArgs = @('--quit-after', '300', '--', '--junction-review') }
if ($JunctionSmoke) { $runtimeArgs = @('--quit-after', '300', '--', '--junction-smoke') }
& $Godot --path $PSScriptRoot --log-file (Join-Path $PSScriptRoot '.qa/runtime.log') @runtimeArgs
exit $LASTEXITCODE
