#include "BodyGame.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Camera/CameraComponent.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "BrainGardenRoutes.inl"

void ABodyPawn::RunGardenSmoke(float Dt)
{
    SmokeTime+=Dt;auto PC=Cast<APlayerController>(GetController());TSet<FKey> Want;
    const FVector* Routes[]={BrainGardenRoutes::Route0,BrainGardenRoutes::Route1,BrainGardenRoutes::Route2,BrainGardenRoutes::Route3,BrainGardenRoutes::Route4,BrainGardenRoutes::Route5,BrainGardenRoutes::Route6,BrainGardenRoutes::Route7,BrainGardenRoutes::Route8,BrainGardenRoutes::Route9,BrainGardenRoutes::Route10,BrainGardenRoutes::Route11,BrainGardenRoutes::Route12};
    const int Counts[]={UE_ARRAY_COUNT(BrainGardenRoutes::Route0),UE_ARRAY_COUNT(BrainGardenRoutes::Route1),UE_ARRAY_COUNT(BrainGardenRoutes::Route2),UE_ARRAY_COUNT(BrainGardenRoutes::Route3),UE_ARRAY_COUNT(BrainGardenRoutes::Route4),UE_ARRAY_COUNT(BrainGardenRoutes::Route5),UE_ARRAY_COUNT(BrainGardenRoutes::Route6),UE_ARRAY_COUNT(BrainGardenRoutes::Route7),UE_ARRAY_COUNT(BrainGardenRoutes::Route8),UE_ARRAY_COUNT(BrainGardenRoutes::Route9),UE_ARRAY_COUNT(BrainGardenRoutes::Route10),UE_ARRAY_COUNT(BrainGardenRoutes::Route11),UE_ARRAY_COUNT(BrainGardenRoutes::Route12)};
    auto Step=[&](){SmokeStage++;SmokeTime=0;Body->AdventureRouteIndex=0;UE_LOG(LogTemp,Display,TEXT("GARDEN_INPUT_STAGE %d %s"),SmokeStage,*GetActorLocation().ToString());};
    auto Finish=[&](bool Passed)
    {
        FString Report=FString::Printf(TEXT("{\"passed\":%s,\"input\":\"PlayerController keyboard; no teleport\",\"stage\":%d,\"waypoint\":%d,\"bright_thoughts_delivered\":%d,\"lotus_opened\":%s,\"worries_released\":%d,\"root_bridge_open\":%s,\"end_position\":\"%s\",\"art_accepted\":false}"),Passed?TEXT("true"):TEXT("false"),SmokeStage,Body->AdventureRouteIndex,Body->GardenDelivered,Body->GardenFocused?TEXT("true"):TEXT("false"),4-Body->ThoughtCount,Body->GardenRestored?TEXT("true"):TEXT("false"),*GetActorLocation().ToString());
        FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("brain-garden-input-report.json")));UE_LOG(LogTemp,Display,TEXT("GARDEN_INPUT_%s %s"),Passed?TEXT("PASS"):TEXT("FAIL"),*Report);FPlatformMisc::RequestExit(false);
    };
    if(SmokeTime>20){Finish(false);return;}
    if(Body->Age<2)return;
    if(SmokeStage<26)
    {
        int Leg=SmokeStage/2;
        if(SmokeStage%2==0)
        {
            int& Index=Body->AdventureRouteIndex;
            if(Index>=Counts[Leg])Step();
            else
            {
                FVector D=Routes[Leg][Index]-GetActorLocation();
                if(D.Size2D()<24){Index++;SmokeTime=0;}
                else
                {
                    // Waypoints use eight headings; a small axial deadzone prevents jitter.
                    if(D.X>13)Want.Add(EKeys::W);if(D.X<-13)Want.Add(EKeys::S);if(D.Y>13)Want.Add(EKeys::D);if(D.Y<-13)Want.Add(EKeys::A);
                }
            }
        }
        else
        {
            bool Done=Leg==0||Leg==2||Leg==4?Body->Carry==5:Leg==1||Leg==3||Leg==5?Body->GardenDelivered>Leg/2:Leg==6?Body->GardenFocused:Leg>=7&&Leg<=10?!(Body->ThoughtMask&(1u<<(Leg-7))):true;
            if(Done)Step();else if(Leg==6)Want.Add(EKeys::E);else if(FMath::Fmod(SmokeTime,.7f)<.16f)Want.Add(Leg>=7?EKeys::SpaceBar:EKeys::E);
        }
    }
    else if(SmokeTime>1)
    {
        bool Passed=Body->GardenDelivered==3&&Body->GardenFocused&&Body->ThoughtCleared&&Body->GardenRestored&&FVector::Dist2D(GetActorLocation(),FVector(7994.500,325.500,0))<100;
        Finish(Passed);return;
    }
    for(FKey Key:{EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::E,EKeys::SpaceBar})
    {bool Down=Want.Contains(Key),Was=SmokeKeys.Contains(Key);if(Down!=Was)PC->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.0:0.0));}
    SmokeKeys=Want;
}
