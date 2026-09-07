param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'C16 compilation failed.'}
$editor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$common='"'+$taskRoot+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('headless','rendered')){
    $options=if($review -eq 'rendered'){'-RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $p=Start-Process $editor -ArgumentList ($common+'-CraftSmoke '+$options+' -abslog="'+$taskRoot+'/Docs/brain-c16-'+$review+'-r03.log"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-motion-r03-processes.json')
Wait-Process -Id $jobs['rendered']
# Image readback stalls wall time. Fixed simulation time keeps a motion-review
# recording temporally coherent; the preceding rendered run measures real time.
$film=Start-Process $editor -ArgumentList ($common+'-CraftFilm -CraftFilmFront -benchmark -fps=60 -UseFixedTimeStep -RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800 -abslog="'+$taskRoot+'/Docs/brain-c16-film-r03.log"') -WindowStyle Hidden -PassThru
$film.Id | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-film-r03-process.txt')
