param([int]$AfterProcess=0,[switch]$NestsOnly)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-mantle-author.log') -Pattern 'C14_DEEP_LIVING_ENVELOPE_READY' -Quiet)){throw 'Final tissue authoring failed'}
$filter=if($NestsOnly){' -C14NestsOnly'}else{''}
$p=Start-Process 'C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' -ArgumentList ('"'+$taskRoot+'/ThatBodyGame.uproject" -ExecutePythonScript="'+$taskRoot+'/Tools/import_c14_mantle.py"'+$filter+' -unattended -nosplash -NoSound -RenderOffscreen -abslog="'+$taskRoot+'/Docs/brain-c14-mantle-import.log"') -WindowStyle Hidden -PassThru
$p.Id | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-final-import-process.txt')
Wait-Process -Id $p.Id
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-mantle-import.log') -Pattern 'C14_FINAL_TISSUE_NATIVE_READY' -Quiet)){throw 'Final tissue import failed'}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C14-20260907'
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c14-package.log')
exit $LASTEXITCODE
