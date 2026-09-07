param([int]$AfterProcess=0,[string]$Revision='r01')
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot ('Docs/brain-c17-import-'+$Revision+'.log')) -Pattern 'C17_GARDEN_NATIVE_READY' -Quiet)){throw 'C17 native import did not finish.'}
$editor='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$common='"'+$taskRoot+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('Smoke','Controls','Roam','Capture')){
    $options=if($review -eq 'Capture'){'-CraftCapture -RenderOffscreen -windowed -ForceRes -ResX=1600 -ResY=1000'}else{'-Craft'+$review+' -nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $job=Start-Process $editor -ArgumentList ($common+$options+' -abslog="'+$taskRoot+'/Docs/brain-c17-'+$review.ToLower()+'-'+$Revision+'.log"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$job.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot ('Docs/brain-c17-review-'+$Revision+'-processes.json'))
Wait-Process -Id $jobs.Capture
$dest=Join-Path $taskRoot ('Art/BrainCraft/Reviews/C17/'+$Revision)
New-Item -ItemType Directory -Path $dest -Force | Out-Null
Copy-Item -Path (Join-Path $taskRoot 'Saved/Screenshots/Brain-C16-*.png') -Destination $dest
