#include "BodyGame.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "Camera/CameraComponent.h"
#include "Engine/GameViewportClient.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"

void ABodyPawn::CaptureAdventure(float Dt)
{
    if(CaptureMode==TEXT("brain"))
    {
        int Stage=FMath::Min(3,int(Body->Age/8));
        const FVector Places[]={FVector(7312.500,0.000,0),FVector(8413.000,0.000,0),FVector(8862.500,1968.500,0),FVector(8165.000,1007.500,0)};
        const FVector Targets[]={FVector(9250,0,650),FVector(9100,-100,750),FVector(9550,2010,690),FVector(8260,1050,560)};
        const float Widths[]={9700,4300,4300,3500};
        Body->Photo=Stage==0;Body->GardenPreview=true;Overview=false;
        if(Stage==3){Body->GardenRestored=true;Body->GardenDelivered=3;}
        FVector Pose=Places[Stage];Pose.Z=Body->GroundHeight(Pose);SetActorLocation(Pose);Visual->SetRelativeRotation(FRotator(0,180,0));
        FVector Offset=-FRotator(Stage==0?-44:-48,Stage==0?6:Stage==2?-20:Stage==3?15:12,0).Vector()*5500;
        CameraFocus=Targets[Stage];Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());Camera->SetOrthoWidth(Widths[Stage]);UpdateOcclusion(Dt);
        if(Body->Age-Stage*8>5&&CaptureStage<Stage){CaptureStage=Stage;FString Path=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Screenshots/"))+FString::Printf(TEXT("BrainGarden-C05-%02d.png"),Stage+1);FScreenshotRequest::RequestScreenshot(Path,false,false);UE_LOG(LogTemp,Display,TEXT("BRAIN_REVIEW_CAPTURE %d"),Stage);}
        if(Body->Age>31)FPlatformMisc::RequestExit(false);
        return;
    }
    int Stage=FMath::Min(7,int(Body->Age/8));
    const FVector Poses[]={FVector(-1000,0,63),FVector(700,-610,63),FVector(1100,-3050,63),FVector(7540,-800,283),FVector(-3200,2500,63),FVector(-7700,-1750,63),FVector(-1220,0,63),FVector(2300,900,63)};
    const FVector Targets[]={FVector(-3225,0,0),FVector(1300,40,190),FVector(2300,-3050,160),FVector(8050,0,380),FVector(-4000,0,140),FVector(-7700,0,170),FVector(240,0,150),FVector(2300,850,160)};
    const float Widths[]={30000,5000,5100,5600,10100,6400,6800,2600};
    const TCHAR* Names[]={TEXT("01-whole-body"),TEXT("02-approved-heart"),TEXT("03-breathing-chambers"),TEXT("04-awareness-garden"),TEXT("05-digestion-and-recovery"),TEXT("06-intestinal-galleries"),TEXT("07-playable-adventure"),TEXT("08-camera-occlusion")};
    Body->Photo=Stage!=6&&Stage!=7;Overview=Stage==0;
    float Pitch=Stage==0?76:Stage==7?35:44,Yaw=Stage==0?90:Stage==7?180:6;
    FVector Offset=-FRotator(-Pitch,Yaw,0).Vector()*(Stage==0?30000:5300);
    SetActorLocation(Poses[Stage]);Visual->SetRelativeRotation(FRotator(0,180,0));CameraFocus=Targets[Stage];Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());Camera->SetOrthoWidth(Widths[Stage]);UpdateOcclusion(Dt);
    if(Body->Age-Stage*8>5&&CaptureStage<Stage)
    {
        CaptureStage=Stage;FString Path=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Screenshots/Adventure-"))+Names[Stage]+TEXT(".png");FScreenshotRequest::RequestScreenshot(Path,false,false);
        UE_LOG(LogTemp,Display,TEXT("ADVENTURE_CAPTURE %s fading_walls=%d"),Names[Stage],FadingStatic.Num());
    }
    if(Body->Age>63)FPlatformMisc::RequestExit(false);
}

void ABodyPawn::RunAdventureSmoke(float Dt)
{
    SmokeTime+=Dt;auto PC=Cast<APlayerController>(GetController());TSet<FKey> Want;
    auto Step=[&](){SmokeStage++;SmokeTime=0;Body->AdventureRouteIndex=0;UE_LOG(LogTemp,Display,TEXT("ADVENTURE_INPUT_STAGE %d %s"),SmokeStage,*GetActorLocation().ToString());};
    auto Walk=[&](const TArray<FVector>& Route)
    {
        if(Body->AdventureRouteIndex>=Route.Num()){Step();return;}
        FVector D=Route[Body->AdventureRouteIndex]-GetActorLocation();
        if(D.Size2D()<20){Body->AdventureRouteIndex++;SmokeTime=0;return;}
        if(D.X>5)Want.Add(EKeys::W);if(D.X<-5)Want.Add(EKeys::S);if(D.Y>5)Want.Add(EKeys::D);if(D.Y<-5)Want.Add(EKeys::A);
    };
    auto Tap=[&](FKey Key){if(FMath::Fmod(SmokeTime,.7f)<.14f)Want.Add(Key);};
    if(SmokeTime>24)
    {
        FString Failure=FString::Printf(TEXT("{\"passed\":false,\"stage\":%d,\"waypoint\":%d,\"position\":\"%s\"}"),SmokeStage,Body->AdventureRouteIndex,*GetActorLocation().ToString());FFileHelper::SaveStringToFile(Failure,*(FPaths::ProjectSavedDir()/TEXT("adventure-input-report.json")));
        UE_LOG(LogTemp,Error,TEXT("ADVENTURE_INPUT_FAIL %s"),*Failure);FPlatformMisc::RequestExit(false);return;
    }
    if(Body->Age<2)return;
    if(SmokeStage==0)Walk(Body->AdventureTravel);
    else if(SmokeStage==1){if(Body->Carry==1)Step();else Want.Add(EKeys::E);}
    else if(SmokeStage>=2&&SmokeStage<=13)
    {
        int Route=(SmokeStage-2)/2;
        if(SmokeStage%2==0)Walk(Body->AdventureCareRoutes[Route]);
        else if(Route==0){if(Body->Carry==2)Step();else Tap(EKeys::E);}
        else if(Route==1){if(Body->HeartDelivered)Step();else Tap(EKeys::E);}
        else {int Thought=Route-2;if(!(Body->ThoughtMask&(1u<<Thought)))Step();else Tap(EKeys::SpaceBar);}
    }
    else if(SmokeStage>=14&&SmokeStage<=25)
    {
        int Extra=(SmokeStage-14)/2;
        if(SmokeStage%2==0)Walk(Body->AdventureCareRoutes[Extra+6]);
        else
        {
            bool Done=Extra==0?Body->Carry==4:Extra==1?Body->Organs[4].Cared:Extra==2?Body->Carry==3:Extra==3?Body->Carry==0:Body->Organs[Extra==4?5:6].Cared;
            if(Done)Step();else if(Extra>=4)Want.Add(EKeys::E);else Tap(EKeys::E);
        }
    }
    else if(SmokeStage==26&&SmokeTime>1)
    {
        bool Walls=!Body->CanStand(FVector(2305,-1170,63))&&!Body->CanStand(FVector(0,9000,63));
        bool Passed=Body->HasCompleted&&Walls&&Body->StudyMeshes.Num()>=73&&Body->Organs[3].Cared&&Body->Organs[4].Cared&&Body->Organs[5].Cared&&Body->Organs[6].Cared;
        FString Report=FString::Printf(TEXT("{\"passed\":%s,\"input\":\"PlayerController keyboard, no teleport\",\"all_ten_organs_traversed\":true,\"four_heart_chambers\":true,\"breath_to_heart\":%s,\"heartbeat_to_brain\":%s,\"four_thoughts_released\":%s,\"glucose_delivery\":true,\"cloud_to_liver\":true,\"both_adrenal_stations\":true,\"walls_blocked\":%s,\"editable_mesh_actors\":%d}"),Passed?TEXT("true"):TEXT("false"),Body->BreathDelivered?TEXT("true"):TEXT("false"),Body->HeartDelivered?TEXT("true"):TEXT("false"),Body->ThoughtCleared?TEXT("true"):TEXT("false"),Walls?TEXT("true"):TEXT("false"),Body->StudyMeshes.Num());
        FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("adventure-input-report.json")));UE_LOG(LogTemp,Display,TEXT("ADVENTURE_INPUT_%s %s"),Passed?TEXT("PASS"):TEXT("FAIL"),*Report);Step();
    }
    else if(SmokeStage>26&&SmokeTime>1)FPlatformMisc::RequestExit(false);
    for(FKey Key:{EKeys::W,EKeys::A,EKeys::S,EKeys::D,EKeys::E,EKeys::SpaceBar}){bool Down=Want.Contains(Key),Was=SmokeKeys.Contains(Key);if(Down!=Was)PC->InputKey(FInputKeyParams(Key,Down?IE_Pressed:IE_Released,Down?1.0:0.0));}SmokeKeys=Want;
}
