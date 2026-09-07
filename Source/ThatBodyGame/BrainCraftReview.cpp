#include "BrainCraft.h"
#include "Animation/AttentionCape.h"
#include "Camera/CameraComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Engine/GameViewportClient.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/FileManager.h"
#include "BrainCraftRoutes.inl"

void AAttentionCharacter::RunReview(float Dt)
{
    if(RoamReview)
    {
        if(Age<1)return;auto PC=Cast<APlayerController>(GetController());if(!PC)return;
        auto Keys=[&](TSet<FKey> Want){for(FKey K:TestKeys)if(!Want.Contains(K))PC->InputKey(FInputKeyParams(K,IE_Released,0,false));for(FKey K:Want)if(!TestKeys.Contains(K))PC->InputKey(FInputKeyParams(K,IE_Pressed,1,false));TestKeys=Want;};
        if(RoamWaypoint>=RoamRoute.Num()||Age>900)
        {
            Keys({});bool Passed=RoamVisited==RoamCheckpoints.Num()&&RoamVisited>0&&Recoveries==0;FString Report=FString::Printf(TEXT("{\"passed\":%s,\"input\":\"PlayerController keyboard on native swept collision graph\",\"visited\":%d,\"expected\":%d,\"waypoint\":%d,\"total_waypoints\":%d,\"fall_recoveries\":%d,\"art_accepted\":false}"),Passed?TEXT("true"):TEXT("false"),RoamVisited,RoamCheckpoints.Num(),RoamWaypoint,RoamRoute.Num(),Recoveries);FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("brain-c15-roam-report.json")));UE_LOG(LogTemp,Display,TEXT("CRAFT_ROAM_REPORT %s"),*Report);FPlatformMisc::RequestExit(false);return;
        }
        FVector D=RoamRoute[RoamWaypoint]-GetActorLocation();
        if(D.Size2D()<(RoamCheckpoints.Contains(RoamWaypoint)?112:20)&&FMath::Abs(D.Z)<80){if(RoamCheckpoints.Contains(RoamWaypoint)){RoamVisited++;UE_LOG(LogTemp,Display,TEXT("CRAFT_ROAM_VISITED %d %s"),RoamVisited,*GetActorLocation().ToString());}RoamWaypoint++;}
        FVector Local=FRotator(0,-CamYaw,0).RotateVector(D.GetSafeNormal2D());TSet<FKey> Want;if(Local.X>.32)Want.Add(EKeys::W);if(Local.X<-.32)Want.Add(EKeys::S);if(Local.Y>.32)Want.Add(EKeys::D);if(Local.Y<-.32)Want.Add(EKeys::A);Keys(Want);
        if(FMath::Fmod(Age,10)<Dt)UE_LOG(LogTemp,Display,TEXT("CRAFT_ROAM_PROGRESS waypoint=%d target=%s position=%s"),RoamWaypoint,*RoamRoute[FMath::Min(RoamWaypoint,RoamRoute.Num()-1)].ToString(),*GetActorLocation().ToString());return;
    }
    if(ControlsReview)
    {
        auto PC=Cast<APlayerController>(GetController());if(!PC||Age<1)return;int32 Phase=FMath::Min(7,int(Age-1));
        auto Key=[&](FKey K,EInputEvent Event,double Value=1){auto Args=FInputKeyEventArgs::CreateSimulated(K,Event,float(Value),Event==IE_Axis?1:0);Args.DeltaTime=Dt;PC->InputKey(Args);};
        if(Phase!=ControlPhase)
        {
            float Dx=0,Dy=0;PC->GetInputMouseDelta(Dx,Dy);UE_LOG(LogTemp,Display,TEXT("CRAFT_CAMERA_PHASE %d yaw=%.2f pitch=%.2f zoom=%.2f pan=%.2f mouse=%.2f,%.2f rmb=%d mmb=%d"),ControlPhase,CamYaw,CamPitch,Zoom,Pan.Size(),Dx,Dy,PC->IsInputKeyDown(EKeys::RightMouseButton),PC->IsInputKeyDown(EKeys::MiddleMouseButton));
            if(ControlPhase==0&&Zoom<.95f)ControlFlags|=1;
            if(ControlPhase==1&&FMath::Abs(CamYaw-ControlYaw)>3)ControlFlags|=2;
            if(ControlPhase==2&&Pan.Size()>10)ControlFlags|=4;
            if(ControlPhase==3&&Overview)ControlFlags|=8;
            if(ControlPhase==4&&!Overview&&Pan.IsNearlyZero()&&FMath::IsNearlyEqual(Zoom,1.f)&&FMath::IsNearlyEqual(CamYaw,80.f))ControlFlags|=16;
            if(ControlPhase==5&&FMath::Abs(CamYaw-ControlYaw)>10&&Zoom>ControlZoom+.1f)ControlFlags|=32;
            if(ControlPhase==1)Key(EKeys::RightMouseButton,IE_Released,0);
            if(ControlPhase==2)Key(EKeys::MiddleMouseButton,IE_Released,0);
            if(ControlPhase==3)Key(EKeys::Tab,IE_Released,0);
            if(ControlPhase==4)Key(EKeys::Home,IE_Released,0);
            if(ControlPhase==0)Key(EKeys::MouseScrollUp,IE_Released,0);
            Key(EKeys::Gamepad_RightX,IE_Axis,0);Key(EKeys::Gamepad_RightY,IE_Axis,0);Key(EKeys::Gamepad_LeftTriggerAxis,IE_Axis,0);ControlPhase=Phase;ControlYaw=CamYaw;ControlZoom=Zoom;
            if(Phase==0)Key(EKeys::MouseScrollUp,IE_Pressed);
            if(Phase==1)Key(EKeys::RightMouseButton,IE_Pressed);
            if(Phase==2)Key(EKeys::MiddleMouseButton,IE_Pressed);
            if(Phase==3)Key(EKeys::Tab,IE_Pressed);
            if(Phase==4)Key(EKeys::Home,IE_Pressed);
        }
        if(Phase==1||Phase==2){Key(EKeys::MouseX,IE_Axis,5);Key(EKeys::MouseY,IE_Axis,Phase==1?1:-2);}
        if(Phase==5){Key(EKeys::Gamepad_RightX,IE_Axis,.6);Key(EKeys::Gamepad_RightY,IE_Axis,.2);Key(EKeys::Gamepad_LeftTriggerAxis,IE_Axis,.7);}
        if(Phase==6){if(CamPitch>=30&&CamPitch<=80&&Zoom>=.5f&&Zoom<=2.7f)ControlFlags|=64;}
        if(Phase==7){const FString Report=FString::Printf(TEXT("{\"passed\":%s,\"flags\":%d,\"expected_flags\":127,\"input\":\"PlayerController mouse, keyboard and gamepad axis injection\",\"physical_controller_tested\":false}"),ControlFlags==127?TEXT("true"):TEXT("false"),ControlFlags);FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/TEXT("brain-c15-camera-report.json")));UE_LOG(LogTemp,Display,TEXT("CRAFT_CAMERA_REPORT %s"),*Report);FPlatformMisc::RequestExit(false);}return;
    }
    if(Film)
    {
        const bool Front=FParse::Param(FCommandLine::Get(),TEXT("CraftFilmFront"));CamYaw=Front?230:65;CamPitch=Front?35:46;Overview=false;Zoom=Front?.44f:.64f;FilmClock+=Dt;int32 Leg=SmokeStage/2;
        const bool Moment=(SmokeStage==1&&SmokeClock<1.3f)||(SmokeStage==2&&SmokeClock>1&&SmokeClock<5)||(SmokeStage==13&&SmokeClock<3)||(SmokeStage==16&&SmokeClock>1&&SmokeClock<6)||(SmokeStage==19)||(SmokeStage==21)||(SmokeStage==24&&SmokeClock>1&&SmokeClock<5);
        if(Moment&&FilmClock>.05f){FilmClock=0;FString Dir=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/(Front?TEXT("BrainFilm/C16-Front/"):TEXT("BrainFilm/C16/")));IFileManager::Get().MakeDirectory(*Dir,true);FString Row=FString::Printf(TEXT("%d,%.4f,%d,%.4f,%.4f,%.3f\n"),FilmFrame,Age,SmokeStage,SmokeClock,Dt,ContactError);FFileHelper::SaveStringToFile(Row,*(Dir/TEXT("frames.csv")),FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM,&IFileManager::Get(),FILEWRITE_Append);FScreenshotRequest::RequestScreenshot(Dir+FString::Printf(TEXT("Frame%05d.png"),FilmFrame++),false,false);}
    }
    if(Capture)
    {
        static TArray<float> ViewFrameMs;
        // Sample settled views before screenshot readback. This is an offscreen
        // diagnostic, not a claim about representative player performance.
        const float ViewAge=FMath::Fmod(Age,9.f);
        if(ViewAge>2.f&&ViewAge<5.f)ViewFrameMs.Add(Dt*1000.f);
        int32 Stage=FMath::Min(3,int(Age/9));const FVector Focuses[]={FVector(0,100,730),FVector(-1740,-2140,310),FVector(0,90,1090),FVector(-1450,1430,1240)};const FVector Poses[]={FVector(-1810,-2470,242),FVector(-1770,-2210,250),FVector(-340,-460,624),FVector(-1010,1280,1204)};const float Widths[]={11800,2100,3100,3300};
        Photo=Stage==0;Overview=Stage==0;CamYaw=Stage==0?82:65;CamPitch=Stage==0?54:48;SetActorLocation(Poses[Stage]);GetCharacterMovement()->StopMovementImmediately();CameraFocus=Focuses[Stage];FVector Offset=-FRotator(-CamPitch,CamYaw,0).Vector()*8000;Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());Camera->SetOrthoWidth(Widths[Stage]);
        const bool CastPortraits=FParse::Param(FCommandLine::Get(),TEXT("CraftCastPortraits"));
        if(CastPortraits){const int Indices[]={0,3,4,5};auto Thought=Thoughts[Indices[Stage]];Photo=true;Overview=false;CamYaw=230;CamPitch=37;CameraFocus=Thought->GetActorLocation();FVector CloseOffset=-FRotator(-CamPitch,CamYaw,0).Vector()*8000;Camera->SetWorldLocation(CameraFocus+CloseOffset);Camera->SetWorldRotation((-CloseOffset).Rotation());Camera->SetOrthoWidth(530);}
        if(Age-Stage*9>6&&CaptureStage<Stage){CaptureStage=Stage;FScreenshotRequest::RequestScreenshot(FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Screenshots/"))+FString::Printf(TEXT("%s-C17-%02d.png"),CastPortraits?TEXT("Cast"):TEXT("Brain"),Stage+1),false,false);}
        if(Age>35){ViewFrameMs.Sort();if(ViewFrameMs.Num()>0)UE_LOG(LogTemp,Display,TEXT("CRAFT_VIEW_TIMING samples=%d median_ms=%.2f p95_ms=%.2f offscreen=1 representative_playtest=0"),ViewFrameMs.Num(),ViewFrameMs[ViewFrameMs.Num()/2],ViewFrameMs[FMath::Min(ViewFrameMs.Num()-1,int(ViewFrameMs.Num()*.95f))]);FPlatformMisc::RequestExit(false);}return;
    }
    if(!Smoke)return;SmokeClock+=Dt;auto PC=Cast<APlayerController>(GetController());if(!PC)return;
    auto Keys=[&](TSet<FKey> Want){for(FKey K:TestKeys)if(!Want.Contains(K))PC->InputKey(FInputKeyParams(K,IE_Released,0,false));for(FKey K:Want)if(!TestKeys.Contains(K))PC->InputKey(FInputKeyParams(K,IE_Pressed,1,false));TestKeys=Want;};
    auto Finish=[&](bool OK)
    {
        Keys({});OK=OK&&Recoveries==0&&PhysicalGrabs>=4&&MaxHandError<220;
        if(ClothCape)UE_LOG(LogTemp,Display,TEXT("CRAFT_CAPE_REPORT stretch=%.4f travel_cm=%.2f resets=%d"),ClothCape->MaxStretch,ClothCape->MaxTravel,ClothCape->RecoveryCount);
        const float MeanGrip=GripSamples>0?GripErrorSum/GripSamples:0;
        FString Report=FString::Printf(TEXT("{\"passed\":%s,\"input\":\"PlayerController keyboard; CharacterMovement and Chaos\",\"stage\":%d,\"stars\":%d,\"released\":%d,\"focused\":%s,\"bridge_open\":%s,\"complete\":%s,\"end\":\"%s\",\"art_accepted\":false,\"fall_recoveries\":%d,\"physical_grabs\":%d,\"legacy_grip\":%s,\"max_handle_lag_cm\":%.2f,\"max_steady_handle_lag_cm\":%.2f,\"max_wrist_contact_error_cm\":%.2f,\"mean_wrist_contact_error_cm\":%.2f,\"contact_samples\":%d}"),OK?TEXT("true"):TEXT("false"),SmokeStage,Delivered,Released,Focused?TEXT("true"):TEXT("false"),BridgeOpen?TEXT("true"):TEXT("false"),Complete?TEXT("true"):TEXT("false"),*GetActorLocation().ToString(),Recoveries,PhysicalGrabs,LegacyGrip?TEXT("true"):TEXT("false"),MaxHandError,MaxSteadyHandleLag,MaxGripError,MeanGrip,GripSamples);
        FFileHelper::SaveStringToFile(Report,*(FPaths::ProjectSavedDir()/(LegacyGrip?TEXT("brain-c15-grip-baseline.json"):TEXT("brain-c15-input-report.json"))));UE_LOG(LogTemp,Display,TEXT("CRAFT_INPUT_REPORT %s"),*Report);FPlatformMisc::RequestExit(false);
    };
    auto MoveKeys=[&](FVector Delta){FVector Local=FRotator(0,-CamYaw,0).RotateVector(Delta.GetSafeNormal2D());TSet<FKey> Want;if(Local.X>.32)Want.Add(EKeys::W);if(Local.X<-.32)Want.Add(EKeys::S);if(Local.Y>.32)Want.Add(EKeys::D);if(Local.Y<-.32)Want.Add(EKeys::A);Keys(Want);};
    if(Age<1)return;if(Age>720){Finish(false);return;}
    int Leg=SmokeStage/2;static int Waypoint=0;static TArray<FVector> Path;
    if(SmokeStage%2==0)
    {
        if(Path.IsEmpty())Path=CraftRoutes::Route(Leg);
        if(Path.IsEmpty()){Finish(false);return;}
        FVector Target=Path[FMath::Min(Waypoint,Path.Num()-1)];FVector Delta=Target-GetActorLocation();Delta.Z=0;
        const bool ThoughtLanding=Leg==0||Leg==2||Leg==4||Leg==7||Leg==9||Leg==10;
        // Stop at the actual interaction reach on a thought landing. Requiring
        // the capsule to occupy a heavy thought's physical sphere blocks care.
        const float ArrivalRadius=ThoughtLanding&&Waypoint==Path.Num()-1?112.f:62.f;
        if(Delta.Size()<ArrivalRadius){Waypoint++;if(Waypoint>=Path.Num()){Keys({});Waypoint=0;Path.Empty();SmokeStage++;SmokeClock=0;ReviewActionIssued=false;UE_LOG(LogTemp,Display,TEXT("CRAFT_ROUTE_ARRIVED %d %s"),Leg,*GetActorLocation().ToString());return;}}
        if(FMath::Fmod(SmokeClock,8)<Dt)UE_LOG(LogTemp,Display,TEXT("CRAFT_ROUTE_PROGRESS leg=%d waypoint=%d target=%s position=%s"),Leg,Waypoint,*Target.ToString(),*GetActorLocation().ToString());MoveKeys(Delta);return;
    }
    // Chase small natural drift at the action landing; movement still uses input.
    int ThoughtIndex=Leg==0?0:Leg==2?1:Leg==4?2:Leg==7?3:Leg==9?4:Leg==10?5:-1;
    if(ThoughtIndex>=0&&Thoughts.IsValidIndex(ThoughtIndex)&&!Thoughts[ThoughtIndex]->Resolved&&!HeldThought)
    {
        FVector Delta=Thoughts[ThoughtIndex]->GetActorLocation()-GetActorLocation();Delta.Z=0;
        if(Delta.Size()>108){SmokeClock=0;MoveKeys(Delta);return;}
    }
    if(Leg==6)Keys({EKeys::E});else if(Leg==9||Leg==10)Keys(FMath::Fmod(SmokeClock,.8f)<.18f?TSet<FKey>{EKeys::SpaceBar}:TSet<FKey>{});else {Keys(!ReviewActionIssued||SmokeClock<.2?TSet<FKey>{EKeys::E}:TSet<FKey>{});ReviewActionIssued=true;}
    bool Done=Leg==0||Leg==2||Leg==4||Leg==7?HeldThought!=nullptr:Leg==1?Delivered>=1:Leg==3?Delivered>=2:Leg==5?Delivered>=3:Leg==6?Focused:Leg==8?Thoughts[3]->Resolved:Leg==9?Thoughts[4]->Resolved:Leg==10?Thoughts[5]->Resolved:Leg==11?BridgeOpen:Complete;
    if(Done&&SmokeClock>.5){Keys({});SmokeStage++;SmokeClock=0;if(Leg==12){Finish(Complete&&BridgeOpen&&Released==3&&Delivered==3);return;}}
}

