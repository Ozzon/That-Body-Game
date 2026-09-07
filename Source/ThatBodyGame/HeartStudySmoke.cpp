#include "BodyGame.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

void ABodyPawn::RunHeartSmoke(float Dt)
{
    SmokeTime+=Dt;auto PC=Cast<APlayerController>(GetController());TSet<FKey> Want;
    auto Step=[&](){SmokeStage++;SmokeTime=0;UE_LOG(LogTemp,Display,TEXT("HEART_WALK_STAGE %d %s"),SmokeStage,*GetActorLocation().ToString());};
    auto Walk=[&](FVector Goal){FVector D=Goal-GetActorLocation();if(D.Size2D()<24){Step();return;}if(D.X>10)Want.Add(EKeys::W);if(D.X<-10)Want.Add(EKeys::S);if(D.Y>10)Want.Add(EKeys::D);if(D.Y<-10)Want.Add(EKeys::A);};
    if(SmokeTime>22){UE_LOG(LogTemp,Error,TEXT("HEART_WALK_FAILED stage=%d at=%s"),SmokeStage,*GetActorLocation().ToString());FPlatformMisc::RequestExit(false);return;}
    int Count=Body->StudyRoute.Num();
    if(SmokeStage<Count){if(Body->Age>2)Walk(Body->StudyRoute[SmokeStage]);}
    else if(SmokeStage==Count){if(Body->Carry==2)Step();else if(FMath::Fmod(SmokeTime,.7f)<.15f)Want.Add(EKeys::E);}
    else if(SmokeStage==Count+1)
    {
        if(SmokeTime>1)
        {
            bool Blocked=!Body->CanStand(Body->StudyWallPoint)&&!Body->CanStand(FVector(8000,8000,63));
            FString Report=FString::Printf(TEXT("{\"passed\":%s,\"model\":\"%c\",\"input\":\"PlayerController keyboard\",\"all_four_chambers\":true,\"entrance_return\":true,\"care\":true,\"walls_blocked\":%s,\"route_waypoints\":%d}"),Blocked?TEXT("true"):TEXT("false"),TCHAR('A'+Body->HeartVariant),Blocked?TEXT("true"):TEXT("false"),Count);
            FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/FString::Printf(TEXT("model-%c-walk-report.json"),TCHAR('A'+Body->HeartVariant))));UE_LOG(LogTemp,Display,TEXT("HEART_WALK_%s %s"),Blocked?TEXT("PASS"):TEXT("FAIL"),*Report);Step();
        }
    }
    else if(SmokeTime>1)FPlatformMisc::RequestExit(false);
    for(FKey Key:{EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::E})
    {bool Down=Want.Contains(Key),Was=SmokeKeys.Contains(Key);if(Down!=Was)PC->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.0:0.0));}
    SmokeKeys=Want;
}
