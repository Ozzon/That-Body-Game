param([string]$Revision='r07')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$jobsPath=Join-Path $taskRoot ('Docs/brain-c11-review-'+$Revision+'-processes.json')
if(-not (Test-Path -LiteralPath $jobsPath)){throw 'Native review has not started'}
$jobs=Get-Content -LiteralPath $jobsPath -Raw|ConvertFrom-Json
if(Get-Process -Id $jobs.Smoke -ErrorAction SilentlyContinue){Wait-Process -Id $jobs.Smoke}
$reportPath=Join-Path $taskRoot 'Saved/brain-c11-input-report.json'
if((Get-Item -LiteralPath $reportPath).LastWriteTime -lt (Get-Item -LiteralPath $jobsPath).LastWriteTime){throw 'Input report is stale'}
$report=Get-Content -LiteralPath $reportPath -Raw|ConvertFrom-Json
if(-not $report.passed){throw 'Native gameplay route has not passed'}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C11-20260907'
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c11-package.log')
exit $LASTEXITCODE
