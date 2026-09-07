param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c17-repair-r02.log') -Pattern 'C17_TREE_REPAIR_READY' -Quiet)){throw 'Geometry repair did not finish.'}
$job=Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList ('"'+$taskRoot+'/ThatBodyGame.uproject" -ExecutePythonScript="'+$taskRoot+'/Tools/import_c17_garden.py" -C17ResumeImport -unattended -nosplash -NoSound -RenderOffscreen -abslog="'+$taskRoot+'/Docs/brain-c17-import-r02.log"') -WindowStyle Hidden -PassThru
$job.Id | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c17-import-r02-process.txt')
& (Join-Path $taskRoot 'Tools/review_c17.ps1') -AfterProcess $job.Id -Revision r02
