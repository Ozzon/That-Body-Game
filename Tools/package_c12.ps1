param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
$importLog=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c12-build-prep.log') -Raw
if($importLog -notmatch 'C12_CAPE_CPU_ACCESS_READY'){throw 'Cape asset preparation failed'}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C12-20260907'
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c12-package.log')
exit $LASTEXITCODE
