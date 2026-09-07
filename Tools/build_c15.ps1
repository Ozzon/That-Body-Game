param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path -Parent $PSScriptRoot
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/Build.bat' ThatBodyGameEditor Win64 Development ('-Project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -WaitMutex -NoHotReloadFromIDE *> (Join-Path $taskRoot 'Docs/brain-c15-editor-build.log')
exit $LASTEXITCODE
