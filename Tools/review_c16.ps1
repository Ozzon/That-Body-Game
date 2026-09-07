param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'C16 editor compilation failed.'}
$editor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$import=Start-Process $editor -ArgumentList ('"'+$taskRoot+'/ThatBodyGame.uproject" -ExecutePythonScript="'+$taskRoot+'/Tools/import_c16_cast.py" -unattended -nosplash -NoSound -RenderOffscreen -abslog="'+$taskRoot+'/Docs/brain-c16-import-r01.log"') -WindowStyle Hidden -PassThru
$import.Id | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-import-process.txt')
Wait-Process -Id $import.Id
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-import-r01.log') -Pattern 'C16_NATIVE_CAST_READY' -Quiet)){throw 'C16 cast import failed.'}
$common='"'+$taskRoot+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('Smoke','Controls','Roam','Portraits')){
    $options=if($review -eq 'Portraits'){'-CraftCapture -CraftCastPortraits -RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800'}else{'-Craft'+$review+' -nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $p=Start-Process $editor -ArgumentList ($common+$options+' -abslog="'+$taskRoot+'/Docs/brain-c16-'+$review.ToLower()+'-r01.log"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-review-r01-processes.json')
Wait-Process -Id $jobs['Portraits']
$film=Start-Process $editor -ArgumentList ($common+'-CraftFilm -RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800 -abslog="'+$taskRoot+'/Docs/brain-c16-film-r01.log"') -WindowStyle Hidden -PassThru
$film.Id | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-film-r01-process.txt')
