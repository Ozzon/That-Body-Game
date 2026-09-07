param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$c15Root=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $c15Root 'Docs/brain-c15-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'C15 editor build failed'}
$p=Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList ('"'+$c15Root+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -CraftRoam -nullrhi -benchmark -fps=60 -UseFixedTimeStep -unattended -nosplash -NoSound -abslog="'+$c15Root+'/Docs/brain-c15-roam-r04.log"') -WindowStyle Hidden -PassThru
$p.Id | Set-Content -LiteralPath (Join-Path $c15Root 'Docs/brain-c15-roam-r04-process.txt')
