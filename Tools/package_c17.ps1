$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
foreach($review in @('smoke','controls','roam')){
    $log=Join-Path $taskRoot ('Docs/brain-c17-'+$review+'-r03.log')
    if(-not (Select-String -LiteralPath $log -Pattern '"passed":true' -Quiet)){throw ('Native check did not pass: '+$review)}
}
$archive=Join-Path $taskRoot 'Builds/BrainAdventure-C17-20260907'
if(Test-Path -LiteralPath $archive){throw 'Preserve the existing C17 archive.'}
& 'C:/Program Files/Epic Games/UE_5.8/Engine/Build/BatchFiles/RunUAT.bat' -WaitForUATMutex BuildCookRun ('-project='+(Join-Path $taskRoot 'ThatBodyGame.uproject')) -noP4 -platform=Win64 -clientconfig=Development -build -cook -map=/Game/Maps/BrainCraft -CookMapsOnly -stage -pak -iostore -archive ('-archivedirectory='+$archive) -unattended -utf8output *> (Join-Path $taskRoot 'Docs/brain-c17-package.log')
$result=$LASTEXITCODE
$result | Set-Content -LiteralPath (Join-Path $taskRoot 'Docs/brain-c17-package-exit.txt')
exit $result
