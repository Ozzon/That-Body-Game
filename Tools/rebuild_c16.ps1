$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
$archive = Join-Path $taskRoot 'Builds/BrainAdventure-C16-R2-20260907'
if (Test-Path -LiteralPath $archive) { throw 'Preserve the existing build; choose a new archive.' }
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project=' + (Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory=' + $archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c16-r2-package.log')
$result = $LASTEXITCODE
$result | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-r2-package-exit.txt')
exit $result
