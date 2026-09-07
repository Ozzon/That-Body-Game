param([int]$AfterProcess=0,[string]$Revision='r01')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c11-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'Editor build failed'}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-import-repair.log') -Pattern 'C14_CONNECTED_GARDEN_NATIVE_READY' -Quiet)){throw 'Native garden import failed'}
$editor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$common='"'+$taskRoot+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('Capture','Smoke','Roam','GripBaseline')) {
    $options=if($review -eq 'Capture'){'-RenderOffscreen -windowed -ForceRes -ResX=1600 -ResY=1000'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $flag=if($review -eq 'GripBaseline'){'-CraftSmoke -CraftGripBaseline'}else{'-Craft'+$review}
    $p=Start-Process $editor -ArgumentList ($common+$flag+' '+$options+' -abslog="'+$taskRoot+'/Docs/brain-c14-'+$review.ToLower()+'-'+$Revision+'.log"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot ('Docs/brain-c14-review-'+$Revision+'-processes.json'))
