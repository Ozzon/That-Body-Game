#include "BodyGame.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "ProceduralMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Engine/GameViewportClient.h"

ABodyGameMode::ABodyGameMode(){DefaultPawnClass=ABodyPawn::StaticClass();HUDClass=ABodyHUD::StaticClass();}
void ABodyGameMode::BeginPlay(){Super::BeginPlay();if(!TActorIterator<ABodyWorld>(GetWorld()))GetWorld()->SpawnActor<ABodyWorld>();}

void ABodyWorld::BeginPlay()
{
    Super::BeginPlay();MakeWorld();
    for(const TCHAR* N:{TEXT("Breath"),TEXT("Heart"),TEXT("Chime"),TEXT("Swat")})Sounds.Add(LoadObject<USoundWave>(nullptr,*FString::Printf(TEXT("/Game/Audio/%s.%s"),N,N)));
    UE_LOG(LogTemp,Display,TEXT("BODY_READY: 3 active organ interiors, 12 context structures, 220-250cm transit paths, 60cm character footprint"));
}

FVector ABodyWorld::FlowPosition(int32 I,float T)const
{
    const bool Blue=I%3==0;
    float a=T*(Blue?.19f:.26f)+I*2*PI/45;
    return FVector(530+1270*FMath::Cos(a),(Blue?-1:1)*(230+70*FMath::Sin(a*2)),35);
}

void ABodyWorld::PlayTone(int32 I,float Volume){if(!Muted&&Sounds.IsValidIndex(I)&&Sounds[I])UGameplayStatics::PlaySound2D(this,Sounds[I],Volume);}
void ABodyWorld::Notify(FString T,float Duration){Toast=T;ToastTime=Duration;}

void ABodyWorld::Tick(float Dt)
{
    Super::Tick(Dt);if(Paused)return;
    Age+=Dt;ToastTime=FMath::Max(0.f,ToastTime-Dt);SwatCooldown=FMath::Max(0.f,SwatCooldown-Dt);BreatheBuff=FMath::Max(0.f,BreatheBuff-Dt);
    auto PC=GetWorld()->GetFirstPlayerController();auto Pawn=PC?Cast<ABodyPawn>(PC->GetPawn()):nullptr;
    const bool Holding=Pawn&&Pawn->Nearest==0&&PC->IsInputKeyDown(EKeys::E)&&Carry==0;
    if(Holding)
    {
        Pull=FMath::Min(1.f,Pull+Dt/2.4f);
        if(Pull>=1&&!Pulled){Carry=1;Pulled=true;CareCount++;Organs[0].Cared=true;PlayTone(0,.5);Notify("A deep breath. Carry it to the heart, then press E.",7);UE_LOG(LogTemp,Display,TEXT("BODY_BREATH_CREATED"));}
    }
    else {Pull=FMath::Max(0.f,Pull-Dt*.6f);if(!PC||!PC->IsInputKeyDown(EKeys::E))Pulled=false;}
    if(Diaphragm)Diaphragm->SetRelativeLocation(FVector(-Pull*100,0,0));
    float Breath=1+.012f*FMath::Sin(Age*1.3f)+Pull*.07f;
    for(auto* C:Organs[0].Animated)if(C){C->SetRelativeScale3D(FVector(Breath,Breath,1+Pull*.14f));}
    float Beat=FMath::Fmod(Age*BPM/60,1.f);float BeatScale=1+.032f*FMath::Exp(-Beat*14.f);
    for(auto* C:Organs[1].Animated)if(C)C->SetRelativeScale3D(FVector(BeatScale));
    BeatAge+=Dt;
    if(BeatAge>=60/FMath::Max(BPM,45.f)){BeatAge=0;if(Pawn&&FVector::Dist2D(Pawn->GetActorLocation(),Organs[1].Center)<1000)PlayTone(1,.16);}
    if(BreathDelivered)BPM=FMath::FInterpTo(BPM,72,Dt,.055);
    for(int i=0;i<3;i++)Organs[i].Health=FMath::FInterpTo(Organs[i].Health,i==0?(Organs[0].Cared?1.f:.45f):i==1?(1-FMath::Abs(BPM-72)/45):1-ThoughtCount*.18f,Dt,1);
    if(BpmLabel)BpmLabel->SetText(FText::FromString(FString::Printf(TEXT("%02d  BPM"),FMath::RoundToInt(BPM))));
    for(int i=0;i<FlowCells.Num();i++)FlowCells[i]->SetRelativeLocation(FlowPosition(i,Age));
    for(int i=0;i<WindMotes.Num();i++)
    {
        int S=i%2?1:-1;float T=FMath::Fmod(Age*(.19f+Pull*.15f)+i*.137f,1.f);
        FVector Q(FMath::Lerp(1060.f,170.f,T),S*(200+T*650)+FMath::Sin(T*PI*3+i)*20,136+FMath::Sin(T*PI)*30);
        WindMotes[i]->SetRelativeLocation(Q);WindMotes[i]->SetRelativeRotation(FRotator(0,S*140,0));
        float L=FMath::Sin(T*PI);WindMotes[i]->SetRelativeScale3D(FVector(.72*L,.075,.075));
    }
    for(int i=0;i<HeartCells.Num();i++)
    {
        int Chamber=i/6;float A=Age*BPM/60+i*PI/3;
        FVector Q(460+(Chamber<2?-155:155),100+(Chamber%2?132:-132),105);
        HeartCells[i]->SetRelativeLocation(Q+FVector(FMath::Cos(A)*95,FMath::Sin(A)*72,0));HeartCells[i]->SetRelativeRotation(FRotator(12,Age*50+i*30,0));
    }
    for(int i=0;i<BrightMotes.Num();i++)
    {float A=Age*.6+i*2*PI/12,R=45+(4-ThoughtCount)*18;BrightMotes[i]->SetRelativeLocation(FVector(2110+FMath::Cos(A)*R,FMath::Sin(A)*R,130+i*7+10*FMath::Sin(A*2)));}
    for(int i=0;i<Thoughts.Num();i++)if(Thoughts[i])
    {
        Thoughts[i]->SetVisibility(i<ThoughtCount,true);
        Thoughts[i]->SetRelativeScale3D(FVector(1+.075*FMath::Sin(Age*2+i)));
        Thoughts[i]->SetRelativeRotation(FRotator(0,Age*20,0));
    }
    if(Awareness){float S=1.8+(4-ThoughtCount)*.17f;Awareness->SetRelativeScale3D(FVector(S,S,.2));}
    if(BreathDelivered&&ThoughtCleared&&HeartDelivered&&!HasCompleted)
    {HasCompleted=true;PlayTone(2,.7);Notify("The body settles. A little care changes the whole day.",12);UE_LOG(LogTemp,Display,TEXT("BODY_LOOP_COMPLETE"));}
}

FString ABodyWorld::Status(int I)const
{
    if(I==0)return Organs[0].Cared?"Breath is flowing":"A deeper breath";
    if(I==1)return BPM<=80?"A steady rhythm":"A racing heart";
    return ThoughtCount==0?"Room to think":"Thoughts are gathering";
}

void ABodyWorld::BeginCare(int32 I)
{
    if(I<0)return;
    if(I==0)
    {
        if(Carry==2){Carry=0;BreatheBuff=20;PlayTone(2);Notify("Heartbeat received. The lungs open into a deeper rhythm.");}
        else if(Carry==1)Notify("You are carrying breath. Bring it to the heart or brain.");
    }
    else if(I==1)
    {
        if(Carry==1)
        {Carry=0;BPM=FMath::Max(65.f,BPM-22);BreathDelivered=true;Organs[1].Cared=true;PlayTone(2);Notify("Breath settles the heart. Press E again to catch a heartbeat.",7);UE_LOG(LogTemp,Display,TEXT("BODY_BREATH_DELIVERED: BPM=%.1f"),BPM);}
        else if(Carry==0&&BPM<=80)
        {Carry=2;PlayTone(1,.5);Notify("A heartbeat in your hands. Carry it to the brain or lungs.",7);UE_LOG(LogTemp,Display,TEXT("BODY_HEARTBEAT_CREATED"));}
        else if(Carry==0){BPM=FMath::Max(65.f,BPM-3);PlayTone(1,.4);Notify("A gentle pacing tap. Bring breath here to settle the rhythm.",4);}
        else Notify("Carry this heartbeat to the brain or lungs.");
    }
    else if(I==2)
    {
        if(Carry==1||Carry==2)
        {if(Carry==2)HeartDelivered=true;Carry=0;CareCount++;Organs[2].Cared=true;PlayTone(2);Notify("The awareness garden opens. Tap SPACE to let small thoughts go.",6);UE_LOG(LogTemp,Display,TEXT("BODY_BRAIN_RECEIVED_RESOURCE"));}
        else Action();
    }
}

void ABodyWorld::Action(int32 Direction)
{
    if(SwatCooldown>0)return;SwatCooldown=.3;
    if(ThoughtCount>0){ThoughtCount--;PlayTone(3,.45);if(ThoughtCount==0){ThoughtCleared=true;Notify("Quiet, at last. There is space for something bright.",6);PlayTone(2,.4);UE_LOG(LogTemp,Display,TEXT("BODY_THOUGHTS_CLEARED"));}else Notify("Let it go. One thought at a time.",2);}
    else Notify("The garden is quiet. Bring it a heartbeat to nourish awareness.");
}

void ABodyWorld::CompleteCare(){}
void ABodyWorld::ResetCare()
{
    BPM=99;Carry=0;ThoughtCount=4;CareCount=0;Pull=0;Pulled=false;BreathDelivered=ThoughtCleared=HeartDelivered=HasCompleted=false;
    for(auto& O:Organs){O.Cared=false;O.Health=.4;}
    Notify("A new morning. Begin with a deep breath at the lungs.",7);
}

bool ABodyWorld::CanStand(FVector P)const
{
    // The playable edge is the same contour that creates the visible body mesh.
    bool Inside=false;
    for(int i=0,j=Boundary.Num()-1;i<Boundary.Num();j=i++)
    {
        const FVector A=Boundary[i],C=Boundary[j];
        if(((A.Y>P.Y)!=(C.Y>P.Y))&&P.X<(C.X-A.X)*(P.Y-A.Y)/(C.Y-A.Y)+A.X)Inside=!Inside;
        FVector Closest=FMath::ClosestPointOnSegment(FVector(P.X,P.Y,0),FVector(A.X,A.Y,0),FVector(C.X,C.Y,0));
        if(FVector::DistSquared2D(P,Closest)<105*105)return false;
    }
    if(!Inside)return false;
    // Solid context organs are obstacles, unlike the deliberately open playable organs.
    const FVector Solids[]={FVector(-455,-620,0),FVector(-430,650,0),FVector(-1000,-840,0),FVector(-1000,840,0)};
    const FVector Radii[]={FVector(295,360,0),FVector(250,210,0),FVector(180,100,0),FVector(180,100,0)};
    for(int i=0;i<4;i++)if(FMath::Square((P.X-Solids[i].X)/Radii[i].X)+FMath::Square((P.Y-Solids[i].Y)/Radii[i].Y)<1)return false;
    return true;
}

float ABodyWorld::GroundHeight(FVector P)const
{
    // Shared accessible floor through the organ cutaways; visual structures rise above it.
    if(P.X<-1680||FMath::Abs(P.Y)>1160)return -48;
    if(P.X>1550)return 66;
    if(P.X>100&&P.X<800&&FMath::Abs(P.Y-100)<335)return 125;
    return 62;
}

FString ABodyWorld::TaskInstruction()const
{
    if(HasCompleted)return "Morning, in balance. Explore, or press R for a new morning.";
    if(Carry==1)return "Carry breath to the heart  /  E to place";
    if(Carry==2)return "Carry heartbeat to the brain  /  E to place";
    if(!Organs[0].Cared)return "Visit the diaphragm  /  Hold E to draw a deep breath";
    if(!BreathDelivered)return "Take breath to the heart  /  E to place";
    if(!HeartDelivered)return "Catch a heartbeat at the heart  /  E, then carry to brain";
    if(!ThoughtCleared)return "Visit the brain  /  SPACE to swat the small thoughts";
    return "Give the body a moment to settle.";
}

ABodyPawn::ABodyPawn()
{
    PrimaryActorTick.bCanEverTick=true;AutoPossessPlayer=EAutoReceiveInput::Player0;
    RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Attention"));
    Visual=CreateDefaultSubobject<USceneComponent>(TEXT("Ranger"));Visual->SetupAttachment(RootComponent);
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));Camera->SetupAttachment(RootComponent);
    Camera->SetUsingAbsoluteLocation(true);Camera->SetUsingAbsoluteRotation(true);Camera->SetProjectionMode(ECameraProjectionMode::Orthographic);Camera->OrthoWidth=4400;Camera->bAutoCalculateOrthoPlanes=true;
}

void ABodyPawn::BeginPlay()
{
    Super::BeginPlay();SetActorLocation(FVector(-180,-240,62));Overview=false;Help=false;
    CameraFocus=FVector(780,0,50);
    FParse::Value(FCommandLine::Get(),TEXT("BodyCapture="),CaptureMode);
    Smoke=FParse::Param(FCommandLine::Get(),TEXT("BodySmoke"));
    auto PC=Cast<APlayerController>(GetController());if(PC){PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameAndUI());}
}

void ABodyPawn::JumpTo(int32 I)
{
    if(!Body||!Body->Organs.IsValidIndex(I))return;
    SetActorLocation(Body->Organs[I].Station);HasTarget=false;Overview=false;
}

void ABodyPawn::Tick(float Dt)
{
    Super::Tick(Dt);
    auto PC=Cast<APlayerController>(GetController());if(!PC)return;
    if(!Body)
    {
        for(TActorIterator<ABodyWorld> It(GetWorld());It;++It){Body=*It;break;}
        if(!Body||Body->Mats.Num()==0){Body=nullptr;return;}
        // A silent, lit-from-within ranger: broad hood, short cape, tiny boots.
        Body->Blob(FVector(0,0,61),FVector(27,32,37),11,0,.025,Visual);
        Hood=Body->Blob(FVector(0,0,111),FVector(39,41,42),11,0,.025,Visual);
        Body->Blob(FVector(30,0,111),FVector(17,29,28),8,0,.02,Visual);
        Body->Shape(FVector(44,-10,116),FVector(.055,.055,.1),7,Visual);
        Body->Shape(FVector(44,10,116),FVector(.055,.055,.1),7,Visual);
        Cape=Body->Blob(FVector(-22,0,74),FVector(15,38,39),4,1,.05,Visual);
        Body->Shape(FVector(-25,0,48),FVector(.35,.59,.15),8,Visual);
        for(int s:{-1,1})
        {
            Limbs.Add(Body->Blob(FVector(0,s*38,63),FVector(12,12,25),11,0,.02,Visual));
            Limbs.Add(Body->Blob(FVector(8,s*16,22),FVector(18,14,20),7,0,.02,Visual));
        }
        CarryVisual=Body->Shape(FVector(54,0,77),FVector(.45),15,Visual);CarryVisual->SetVisibility(false);
        Visual->SetRelativeRotation(FRotator(0,180,0));
    }
    if(PC->WasInputKeyJustPressed(EKeys::Escape)){Body->Paused=!Body->Paused;HasTarget=false;}
    if(PC->WasInputKeyJustPressed(EKeys::F8)){Body->Photo=!Body->Photo;}
    if(PC->WasInputKeyJustPressed(EKeys::H))Help=!Help;
    if(PC->WasInputKeyJustPressed(EKeys::M))Body->Muted=!Body->Muted;
    if(PC->WasInputKeyJustPressed(EKeys::F11))PC->ConsoleCommand(TEXT("TOGGLEFULLSCREEN"));
    if(PC->WasInputKeyJustPressed(EKeys::R)){Body->ResetCare();}
    if(PC->WasInputKeyJustPressed(EKeys::Tab)){Overview=!Overview;Zoom=1;}
    if(Body->Paused)return;
    if(Smoke)RunSmoke(Dt);
    if(PC->WasInputKeyJustPressed(EKeys::MouseScrollUp))Zoom=FMath::Clamp(Zoom*.88f,.3f,3.6f);
    if(PC->WasInputKeyJustPressed(EKeys::MouseScrollDown))Zoom=FMath::Clamp(Zoom*1.13f,.3f,3.6f);
    if(PC->IsInputKeyDown(EKeys::RightMouseButton)){float DX,DY;PC->GetInputMouseDelta(DX,DY);CamYaw+=DX*.22f;CamPitch=FMath::Clamp(CamPitch+DY*.18f,30.f,85.f);}
    if(PC->IsInputKeyDown(EKeys::MiddleMouseButton))
    {float DX,DY;PC->GetInputMouseDelta(DX,DY);PanOffset+=FRotator(0,CamYaw,0).RotateVector(FVector(DY,-DX,0))*Camera->OrthoWidth/1800.f;PanOffset=PanOffset.GetClampedToMaxSize(2600);}
    if(PC->WasInputKeyJustPressed(EKeys::Home)){CamYaw=0;CamPitch=65;Zoom=1;PanOffset=FVector::ZeroVector;Overview=false;}
    FVector P=GetActorLocation();Nearest=-1;float Best=340;
    for(int i=0;i<3;i++)
    {
        float D=FVector::Dist2D(P,Body->Organs[i].Station);
        // In the brain the entire inner garden is an interaction space.
        if(i==2&&P.X>1620)D=100;
        if(D<Best){Best=D;Nearest=i;}
    }
    if(PC->WasInputKeyJustPressed(EKeys::E))Body->BeginCare(Nearest);
    if(PC->WasInputKeyJustPressed(EKeys::SpaceBar)&&Nearest==2)Body->Action();
    if(PC->WasInputKeyJustPressed(EKeys::SpaceBar)&&Nearest!=2&&HopAge>.65f){HopAge=0;Body->PlayTone(3,.15);}
    if(PC->WasInputKeyJustPressed(EKeys::Q)&&Nearest==1){Body->BPM=FMath::Clamp(Body->BPM+3,55.f,120.f);Body->PlayTone(1);}
    if(PC->WasInputKeyJustPressed(EKeys::LeftMouseButton)&&!Help)
    {
        FVector O,D;
        if(PC->DeprojectMousePositionToWorld(O,D)&&FMath::Abs(D.Z)>.01f)
        {FVector T=O+D*((62-O.Z)/D.Z);if(Body->CanStand(T)){MoveTarget=T;HasTarget=true;}}
    }
    float X=(PC->IsInputKeyDown(EKeys::W)||PC->IsInputKeyDown(EKeys::Up)?1:0)-(PC->IsInputKeyDown(EKeys::S)||PC->IsInputKeyDown(EKeys::Down)?1:0);
    float Y=(PC->IsInputKeyDown(EKeys::D)||PC->IsInputKeyDown(EKeys::Right)?1:0)-(PC->IsInputKeyDown(EKeys::A)||PC->IsInputKeyDown(EKeys::Left)?1:0);
    FVector Move=FRotator(0,CamYaw,0).RotateVector(FVector(X,Y,0)).GetSafeNormal();
    if(!Move.IsNearlyZero()){HasTarget=false;Help=false;}
    if(HasTarget){Move=(MoveTarget-P).GetSafeNormal2D();if(FVector::Dist2D(MoveTarget,P)<25){HasTarget=false;Move=FVector::ZeroVector;}}
    float Speed=(PC->IsInputKeyDown(EKeys::LeftShift)?710.f:465.f)*(Body->Carry?.85f:1.f);
    SmoothedMove=FMath::VInterpTo(SmoothedMove,Move,Dt,Move.IsNearlyZero()?15.f:9.f);
    Move=SmoothedMove;HopAge+=Dt;
    FVector Next=P+Move*Speed*Dt;
    if(Body->CanStand(Next)){Next.Z=FMath::FInterpTo(P.Z,Body->GroundHeight(Next),Dt,9);SetActorLocation(Next);}
    else if(!Move.IsNearlyZero())
    {
        FVector NX=P+FVector(Move.X*Speed*Dt,0,0),NY=P+FVector(0,Move.Y*Speed*Dt,0);
        if(Body->CanStand(NX))SetActorLocation(NX);else if(Body->CanStand(NY))SetActorLocation(NY);else HasTarget=false;
    }
    bool Moving=Move.SizeSquared()>.004f;
    float Waddle=FMath::Sin(WalkAge),Hop=HopAge<.65f?FMath::Sin(HopAge/.65f*PI)*92:0;
    if(Moving){WalkAge+=Dt*(Speed>500?14:11);FRotator Aim=Move.Rotation();Aim.Pitch=Body->Carry?7:11;Aim.Roll=Waddle*8;Visual->SetRelativeRotation(FMath::RInterpTo(Visual->GetRelativeRotation(),Aim,Dt,10));}
    else {FRotator Rest=Visual->GetRelativeRotation();Rest.Pitch=0;Rest.Roll=FMath::Sin(Body->Age*1.8f)*2;Visual->SetRelativeRotation(FMath::RInterpTo(Visual->GetRelativeRotation(),Rest,Dt,6));}
    float Bounce=Moving?FMath::Abs(Waddle)*11:2.5*FMath::Sin(Body->Age*2);
    Visual->SetRelativeLocation(FVector(0,0,Bounce+Hop));
    float Squash=Moving?.055f*FMath::Cos(WalkAge*2):.018f*FMath::Sin(Body->Age*2);
    if(HopAge<.65f)Squash=-.10f*FMath::Cos(HopAge/.65f*PI*2);
    Visual->SetRelativeScale3D(FVector(1+Squash,1+Squash,1-Squash));
    if(Hood)Hood->SetRelativeRotation(FRotator(Moving?Waddle*3:0,0,Moving?-Waddle*5:0));
    if(Cape)Cape->SetRelativeRotation(FRotator(Moving?-12+Waddle*10:0,0,Waddle*3));
    for(int i=0;i<Limbs.Num();i++)Limbs[i]->SetRelativeRotation(FRotator(Moving?FMath::Sin(WalkAge+(i<2?0:PI))*(i%2?30:40):0,0,i%2?0:(i<2?-12:12)));
    CarryVisual->SetVisibility(Body->Carry>0);auto SM=Cast<UStaticMeshComponent>(CarryVisual);
    if(SM)SM->SetMaterial(0,Body->Mats[Body->Carry==2?3:15]);
    CarryVisual->SetRelativeLocation(FVector(53,0,85+FMath::Sin(Body->Age*3)*5));
    FVector Focus=(Overview?FVector(-120,0,30):GetActorLocation()+FVector(300,0,0))+PanOffset;
    CameraFocus=FMath::VInterpTo(CameraFocus,Focus,Dt,Overview?2.f:3.f);
    FVector Offset=-FRotator(-CamPitch,CamYaw,0).Vector()*5300;
    Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());
    Camera->SetOrthoWidth(FMath::FInterpTo(Camera->OrthoWidth,(Overview?10600.f:3200.f)*Zoom,Dt,3));
    UpdateOcclusion(Dt);
    if(!CaptureMode.IsEmpty())
    {
        int Stage=FMath::Min(3,int(Body->Age/8));
        const FVector Positions[]={FVector(-180,-240,62),FVector(250,-650,62),FVector(180,100,125),FVector(1820,0,66)};
        const FVector Focuses[]={FVector(580,0,40),FVector(620,0,40),FVector(460,100,60),FVector(2140,0,50)};
        const float Widths[]={7900,3350,2050,2650};
        const TCHAR* Names[]={TEXT("01-body-atlas"),TEXT("02-lungs"),TEXT("03-heart"),TEXT("04-brain")};
        SetActorLocation(Positions[Stage]);Visual->SetRelativeRotation(FRotator(0,180,0));
        CameraFocus=Focuses[Stage];Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());Camera->SetOrthoWidth(Widths[Stage]);
        if(Body->Age-Stage*8>5&&CaptureStage<Stage)
        {CaptureStage=Stage;FString Path=FPaths::ConvertRelativePathToFull(FPaths::ProjectSavedDir()/TEXT("Screenshots/"))+Names[Stage]+TEXT(".png");FScreenshotRequest::RequestScreenshot(Path,false,false);UE_LOG(LogTemp,Display,TEXT("BODY_CAPTURE %s"),*Path);}
        if(Body->Age>31)FPlatformMisc::RequestExit(false);
    }
}
