$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
foreach($name in @('headless-r03','rendered-r03','controls-r01','roam-r01')){
    $log=Join-Path $taskRoot ('Docs/brain-c16-'+$name+'.log')
    if(-not (Select-String -LiteralPath $log -Pattern '"passed":true' -Quiet)){throw ('Native C16 check failed: '+$name)}
}
if(-not (Select-String -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-import-r02.log') -Pattern 'C16_NATIVE_CAST_READY' -Quiet)){throw 'C16 cast import did not complete.'}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C16-20260907'
if(Test-Path -LiteralPath $archive){throw 'Preserve the existing C16 archive.'}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c16-package.log')
$result=$LASTEXITCODE
$result | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c16-package-exit.txt')
exit $result
