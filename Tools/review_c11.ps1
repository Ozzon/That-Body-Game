param([int]$AfterProcess=0,[string]$Revision='r05')
$ErrorActionPreference='Stop'
if($AfterProcess -gt 0){Wait-Process -Id $AfterProcess -ErrorAction SilentlyContinue}
$taskRoot=Split-Path $PSScriptRoot -Parent
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c11-editor-build.log') -Pattern 'Result: Succeeded' -Quiet)){throw 'Editor build did not succeed'}
$reviewDir=Join-Path $taskRoot 'Docs/Reviews/C11-r03'
New-Item -ItemType Directory -Path $reviewDir -Force | Out-Null
Get-ChildItem -LiteralPath (Join-Path $taskRoot 'Saved/Screenshots') -Filter 'Brain-C11-*.png' | Copy-Item -Destination $reviewDir
$engineExe='C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe'
$common='"'+$taskRoot+'/ThatBodyGame.uproject" /Game/Maps/BrainCraft -game -unattended -nosplash -NoSound '
$jobs=@{}
foreach($review in @('Capture','Smoke','Controls','Explore')){
    $options=if($review -eq 'Capture'){'-RenderOffscreen -windowed -ForceRes -ResX=1600 -ResY=1000'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $log=Join-Path $taskRoot ('Docs/brain-c11-'+$review.ToLower()+'-'+$Revision+'.log')
    $p=Start-Process -FilePath $engineExe -ArgumentList ($common+'-Craft'+$review+' '+$options+' -abslog="'+$log+'"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $taskRoot ('Docs/brain-c11-review-'+$Revision+'-processes.json'))
