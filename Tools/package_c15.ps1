param([int]$AfterProcess=0)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
if($AfterProcess -gt 0 -and (Get-Process -Id $AfterProcess -ErrorAction SilentlyContinue)){Wait-Process -Id $AfterProcess}
$importLog=Get-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c15-import-r03.log') -Raw
if($importLog -notmatch 'C15_GARDEN_NATIVE_READY'){throw 'Terrain collision repair import failed'}
foreach($check in @('smoke','roam','controls')){
    $revision=if($check -eq 'roam'){'r04'}else{'r03'}
    $checkLog=Get-Content -LiteralPath (Join-Path $taskRoot ('Docs/brain-c15-'+$check+'-'+$revision+'.log')) -Raw
    if($checkLog -notmatch '"passed":true'){throw ('C15 check failed: '+$check)}
}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C15-20260907'
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c15-package.log')
exit $LASTEXITCODE
