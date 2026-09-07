param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-package.log') -Pattern 'BUILD SUCCESSFUL' -Quiet)){throw 'C14 package did not complete'}
$exe=Join-Path $taskRoot 'Builds/BrainAdventure-C14-20260907/Windows/ThatBodyGame.exe';$jobs=@{}
foreach($review in @('Smoke','Controls','Roam','Capture')) {
    $options=if($review -eq 'Capture'){'-RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $p=Start-Process $exe -ArgumentList ('-unattended -nosplash -NoSound -Craft'+$review+' '+$options+' -abslog="'+$taskRoot+'/Docs/brain-c14-packaged-'+$review.ToLower()+'.log"') -WorkingDirectory (Split-Path $exe -Parent) -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c14-packaged-check-processes.json')
