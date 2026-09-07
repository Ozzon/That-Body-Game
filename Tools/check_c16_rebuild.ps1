$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
if ((Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-r2-package-exit.txt') -Raw).Trim() -ne '0') { throw 'Packaging failed.' }
if (-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-r2-package.log') -Pattern 'BUILD SUCCESSFUL' -Quiet)) { throw 'Packaging completion not found.' }
$exe = Join-Path $taskRoot 'Builds/BrainAdventure-C16-R2-20260907/Windows/ThatBodyGame.exe'
$jobs = @{}
foreach ($review in @('Smoke', 'Controls', 'Roam', 'Capture')) {
    $options = if ($review -eq 'Capture') { '-RenderOffscreen -windowed -ForceRes -ResX=1280 -ResY=800' } else { '-nullrhi -benchmark -fps=60 -UseFixedTimeStep' }
    $arguments = '-unattended -nosplash -NoSound -Craft' + $review + ' ' + $options + ' -abslog="' + $taskRoot + '/Docs/brain-c16-r2-packaged-' + $review.ToLower() + '.log"'
    $job = Start-Process $exe -ArgumentList $arguments -WorkingDirectory (Split-Path $exe -Parent) -WindowStyle Hidden -PassThru
    $jobs[$review] = $job.Id
}
$jobs | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-r2-packaged-processes.json')
$jobs | ConvertTo-Json
