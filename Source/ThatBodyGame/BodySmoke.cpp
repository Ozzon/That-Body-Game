#include "BodyGame.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Engine/GameViewportClient.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

void ABodyPawn::RunSmoke(float Dt)
{
    if(!Body)return;
    SmokeTime+=Dt;auto PC=Cast<APlayerController>(GetController());
    TSet<FKey> Want;
    auto Step=[&](){SmokeStage++;SmokeTime=0;UE_LOG(LogTemp,Display,TEXT("BODY_SMOKE_STAGE %d LOCATION %s"),SmokeStage,*GetActorLocation().ToString());};
    auto Walk=[&](FVector Goal)
    {
        FVector D=Goal-GetActorLocation();
        if(D.Size2D()<65){Step();return;}
        if(D.X>30)Want.Add(EKeys::W);if(D.X<-30)Want.Add(EKeys::S);
        if(D.Y>30)Want.Add(EKeys::D);if(D.Y<-30)Want.Add(EKeys::A);
    };
    if(SmokeTime>20)
    {
        FString Error=FString::Printf(TEXT("BODY_SMOKE_FAILED stage=%d location=%s nearest=%d carry=%d"),SmokeStage,*GetActorLocation().ToString(),Nearest,Body->Carry);
        UE_LOG(LogTemp,Error,TEXT("%s"),*Error);FFileHelper::SaveStringToFile(Error,*(FPaths::ProjectSavedDir()/TEXT("smoke-failed.txt")));FPlatformMisc::RequestExit(false);return;
    }
    switch(SmokeStage)
    {
    case 0:if(Body->Age>2)Walk(Body->Organs[0].Station);break;
    case 1:if(Body->Carry==1){Step();}else Want.Add(EKeys::E);break;
    case 2:Walk(Body->Organs[1].Station);break;
    case 3:if(Body->BreathDelivered){Step();}else if(FMath::Fmod(SmokeTime,1.f)<.2f)Want.Add(EKeys::E);break;
    case 4:if(Body->Carry==2){Step();}else if(SmokeTime>.5f&&FMath::Fmod(SmokeTime,1.f)<.2f)Want.Add(EKeys::E);break;
    case 5:Walk(FVector(1240,0,62));break;
    case 6:Walk(Body->Organs[2].Station);break;
    case 7:if(Body->HeartDelivered){Step();}else if(FMath::Fmod(SmokeTime,1.f)<.2f)Want.Add(EKeys::E);break;
    case 8:if(Body->HasCompleted){Step();}else if(FMath::Fmod(SmokeTime,.7f)<.15f)Want.Add(EKeys::SpaceBar);break;
    case 9:Walk(FVector(2100,235,66));break;
    case 10:Walk(FVector(2450,-180,66));break;
    case 11:Walk(FVector(1640,0,66));break;
    case 12:Walk(FVector(1180,0,62));break;
    case 13:Walk(FVector(850,650,62));break;
    case 14:Walk(FVector(220,750,62));break;
    case 15:Walk(FVector(-60,0,62));break;
    case 16:Walk(FVector(220,-680,62));break;
    case 17:Walk(FVector(900,-670,62));break;
    case 18:Walk(FVector(500,100,125));break;
    case 19:
        if(SmokeTime>1)
        {
            bool BoundaryOk=!Body->CanStand(FVector(4000,4000,0))&&!Body->CanStand(FVector(-460,-610,0));
            FString Report=FString::Printf(TEXT("{\"passed\":%s,\"input\":\"PlayerController keyboard input\",\"care_loop\":true,\"visited\":[\"diaphragm\",\"heart\",\"brain crown\",\"brain quadrants\",\"left lung interior\",\"right lung interior\",\"heart chambers\"],\"boundary_and_solid_organ_block\":%s,\"bpm\":%.2f,\"thoughts_remaining\":%d}"),BoundaryOk?TEXT("true"):TEXT("false"),BoundaryOk?TEXT("true"):TEXT("false"),Body->BPM,Body->ThoughtCount);
            FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("smoke-report.json")));
            UE_LOG(LogTemp,Display,TEXT("BODY_SMOKE_%s %s"),BoundaryOk?TEXT("PASS"):TEXT("FAIL"),*Report);
            FScreenshotRequest::RequestScreenshot(FPaths::ProjectSavedDir()/TEXT("Screenshots/05-care-complete.png"),false,false);Step();
        }break;
    default:if(SmokeTime>2)FPlatformMisc::RequestExit(false);break;
    }
    for(FKey Key:{EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::E,EKeys::SpaceBar})
    {
        bool Down=Want.Contains(Key),Was=SmokeKeys.Contains(Key);
        if(Down!=Was)PC->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.0:0.0));
    }
    SmokeKeys=Want;
}
