param([int]$AfterProcess=0,[int]$AuthorProcess=0,[string]$Revision='r01',[switch]$SurfacesOnly)
$ErrorActionPreference='Stop'
$c15Root=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if($AuthorProcess -gt 0 -and (Get-Process -Id $AuthorProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AuthorProcess}
$authorLog=if($SurfacesOnly){'Docs/brain-c15-surfaces-'+$Revision+'.log'}else{'Docs/brain-c15-author-r02.log'}
if(-not (Select-String -LiteralPath (Join-Path $c15Root $authorLog) -Pattern 'C15_EDITABLE_GARDEN_READY' -Quiet)){throw 'C15 authoring failed'}
if(-not (Select-String -LiteralPath (Join-Path $c15Root 'Docs/brain-c15-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'C15 editor build failed'}
$editor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$filter=if($SurfacesOnly){' -C15SurfacesOnly'}else{''}
$import=Start-Process $editor -ArgumentList ('"'+$c15Root+'/ThatBodyGame.uproject" -ExecutePythonScript="'+$c15Root+'/Tools/import_c15_garden.py"'+$filter+' -unattended -nosplash -NoSound -RenderOffscreen -abslog="'+$c15Root+'/Docs/brain-c15-import-'+$Revision+'.log"') -WindowStyle Hidden -PassThru
$import.Id | Set-Content -LiteralPath (Join-Path $c15Root 'Docs/brain-c15-import-process.txt')
Wait-Process -Id $import.Id
if(-not (Select-String -LiteralPath (Join-Path $c15Root ('Docs/brain-c15-import-'+$Revision+'.log')) -Pattern 'C15_GARDEN_NATIVE_READY' -Quiet)){throw 'C15 native import failed'}
$common='"'+$c15Root+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('Capture','Smoke','Roam','Controls')){
    $options=if($review -eq 'Capture'){'-RenderOffscreen -windowed -ForceRes -ResX=1600 -ResY=1000'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $p=Start-Process $editor -ArgumentList ($common+'-Craft'+$review+' '+$options+' -abslog="'+$c15Root+'/Docs/brain-c15-'+$review.ToLower()+'-'+$Revision+'.log"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $c15Root ('Docs/brain-c15-review-'+$Revision+'-processes.json'))
