param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c12-package.log') -Pattern 'BUILD SUCCESSFUL' -Quiet)){throw 'Packaging did not succeed'}
$exe=Join-Path $taskRoot 'Builds/BrainAdventure-C12-20260907/Windows/ThatBodyGame.exe'
$jobs=@{}
foreach($review in @('Capture','Smoke','Controls')) {
    $options=if($review -eq 'Capture'){'-RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800'}else{'-nullrhi -benchmark -fps=60 -UseFixedTimeStep'}
    $log=Join-Path $taskRoot ('Docs/brain-c12-packaged-'+$review.ToLower()+'.log')
    $p=Start-Process -FilePath $exe -ArgumentList ('-Craft'+$review+' '+$options+' -unattended -NoSound -abslog="'+$log+'"') -WindowStyle Hidden -PassThru
    $jobs[$review]=$p.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c12-packaged-processes.json')
