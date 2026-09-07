#include "BodyGame.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "GameFramework/PlayerController.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "BodyAdventureNav.inl"

void ABodyWorld::MakeAdventure()
{
    Organs.SetNum(7);BPM=96;Toast=TEXT("Welcome, little attention. Begin in the breathing glade.");ToastTime=9;
    const TCHAR* Names[]={TEXT("LUNGS"),TEXT("HEART"),TEXT("BRAIN"),TEXT("STOMACH"),TEXT("LIVER"),TEXT("CALM SPRING"),TEXT("ENERGY SPRING")};
    const FVector Positions[]={FVector(-1000,0,63),FVector(2050,750,63),FVector(8901.25,0,433),FVector(-3200,2500,63),FVector(-2860,-2850,63),FVector(-4930,-3560,63),FVector(-4930,3560,63)};
    const FLinearColor Colors[]={FLinearColor(.45,.85,.7),FLinearColor(1,.48,.32),FLinearColor(.73,.6,.95),FLinearColor(1,.72,.34),FLinearColor(.84,.58,.31),FLinearColor(.5,.85,.6),FLinearColor(1,.57,.4)};
    for(int i=0;i<7;i++){Organs[i].Name=Names[i];Organs[i].Station=Positions[i];Organs[i].Station.Z=GroundHeight(Positions[i]);Organs[i].Center=Positions[i];Organs[i].Color=Colors[i];}
    GardenPreview=GetWorld()->GetMapName().Contains(TEXT("BrainGarden"))||FParse::Param(FCommandLine::Get(),TEXT("BodyGardenStart"));
    GardenStars.SetNum(3);GardenStarPlaces={FVector(7235.000,325.500,0),FVector(10366.000,-1705.000,0),FVector(9947.500,2077.000,0)};
    for(auto& Pos:GardenStarPlaces)Pos.Z=GroundHeight(Pos)+110;
    if(GardenPreview){Toast=TEXT("Three bright thoughts are waiting. Carry them home to the tree.");ToastTime=12;}
    Organs[1].Center=FVector(1400,0,100);Organs[2].Center=FVector(9250,0,440);
    Shape(FVector(-3300,0,-610),FVector(2000,2000,1),7,nullptr,2);
    int MeshCount=0;
    for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)
    {
        if(!It->Tags.Contains(TEXT("AdventureMesh")))continue;
        auto C=It->GetStaticMeshComponent();C->SetMobility(EComponentMobility::Movable);C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);C->SetCollisionResponseToAllChannels(ECR_Ignore);C->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
        C->ComponentTags.Append(It->Tags);StudyMeshes.Add(C);MeshCount++;
        for(int i=0;i<3;i++)if(It->Tags.Contains(FName(*FString::Printf(TEXT("BrightThought%d"),i))))GardenStars[i]=C;
        if(It->Tags.Contains(TEXT("RootShortcut"))){GardenRoots.Add(C);C->SetVisibility(false);C->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
        if(It->Tags.Contains(TEXT("TreeGlow")))for(int j=0;j<C->GetNumMaterials();j++)GardenTreeMaterials.Add(C->CreateDynamicMaterialInstance(j));
        if(It->Tags.Contains(TEXT("Heart")))
        {
            if(!It->Tags.Contains(TEXT("Interactive")))Organs[1].Animated.Add(C);
            if(C->GetStaticMesh()->GetName().Contains(TEXT("PulseSeed")))PulseSeed=C;
        }
        if(It->Tags.Contains(TEXT("LungRight"))||It->Tags.Contains(TEXT("LungLeft")))Organs[0].Animated.Add(C);
    }
    for(int i=0;i<7;i++)
    {
        if(i==1||i==2){CareLights.Add(nullptr);continue;}
        auto C=Shape(Positions[i]+FVector(0,0,115),FVector(.34),i==4?4:i>=5?8:15);C->ComponentTags.Add(TEXT("Interactive"));CareLights.Add(C);
        auto L=NewObject<UPointLightComponent>(this);L->SetupAttachment(RootComponent);L->SetRelativeLocation(Positions[i]+FVector(0,0,230));L->SetLightColor(Colors[i]);L->SetIntensity(2800);L->SetAttenuationRadius(850);L->SetSourceRadius(90);L->SetCastShadows(false);L->RegisterComponent();
    }
    auto H=NewObject<UPointLightComponent>(this);H->SetupAttachment(RootComponent);H->SetRelativeLocation(Positions[1]+FVector(0,0,250));H->SetLightColor(FLinearColor(1,.53,.21));H->SetIntensity(6000);H->SetAttenuationRadius(1100);H->SetSourceRadius(90);H->SetCastShadows(false);H->RegisterComponent();
    for(int side:{-1,1})for(int i=0;i<4;i++){auto C=Shape(FVector(1500,side*3050,160),FVector(.32,.06,.06),15);C->SetCastShadow(false);WindMotes.Add(C);}
    const FVector ThoughtPlaces[]={FVector(8010.000,2015.000,0),FVector(8568.000,2681.500,0),FVector(9141.500,2340.500,0),FVector(8614.500,1736.000,0)};
    for(int i=0;i<4;i++)
    {
        auto Root=NewObject<USceneComponent>(this);Root->SetupAttachment(RootComponent);Root->SetRelativeLocation(FVector(ThoughtPlaces[i].X,ThoughtPlaces[i].Y,GroundHeight(ThoughtPlaces[i])+115));Root->RegisterComponent();Thoughts.Add(Root);
        Blob(FVector(0,0,0),FVector(92,74,56),5,i,.04,Root);Shape(FVector(-62,8,-20),FVector(.70,.6,.5),5,Root);Shape(FVector(61,0,-6),FVector(.8,.7,.7),5,Root);
        for(int Side:{-1,1})
        {
            Blob(FVector(-84,Side*22,9),FVector(8,9,13),7,0,.01,Root);
            Blob(FVector(-91,Side*22-2,13),FVector(2,3,4),6,0,.01,Root);
            Blob(FVector(-28,Side*72,-26),FVector(22,15,13),5,i,.035,Root);
        }
    }
    auto Cloud=NewObject<USceneComponent>(this);Cloud->SetupAttachment(RootComponent);Cloud->SetRelativeLocation(FVector(650,-730,180));Cloud->RegisterComponent();StressCloud=Cloud;
    Blob(FVector::ZeroVector,FVector(95,76,58),12,4,.045,Cloud);Shape(FVector(58,10,0),FVector(.8,.7,.7),12,Cloud);
    AdventureTravel.Append(BodyAdventureNav::Travel,UE_ARRAY_COUNT(BodyAdventureNav::Travel));
    auto Route=[&](const FVector* Points,int Count){TArray<FVector> P;P.Append(Points,Count);AdventureCareRoutes.Add(P);};
    Route(BodyAdventureNav::Care0,UE_ARRAY_COUNT(BodyAdventureNav::Care0));Route(BodyAdventureNav::Care1,UE_ARRAY_COUNT(BodyAdventureNav::Care1));Route(BodyAdventureNav::Care2,UE_ARRAY_COUNT(BodyAdventureNav::Care2));Route(BodyAdventureNav::Care3,UE_ARRAY_COUNT(BodyAdventureNav::Care3));Route(BodyAdventureNav::Care4,UE_ARRAY_COUNT(BodyAdventureNav::Care4));Route(BodyAdventureNav::Care5,UE_ARRAY_COUNT(BodyAdventureNav::Care5));
    Route(BodyAdventureNav::Extra0,UE_ARRAY_COUNT(BodyAdventureNav::Extra0));Route(BodyAdventureNav::Extra1,UE_ARRAY_COUNT(BodyAdventureNav::Extra1));Route(BodyAdventureNav::Extra2,UE_ARRAY_COUNT(BodyAdventureNav::Extra2));Route(BodyAdventureNav::Extra3,UE_ARRAY_COUNT(BodyAdventureNav::Extra3));Route(BodyAdventureNav::Extra4,UE_ARRAY_COUNT(BodyAdventureNav::Extra4));Route(BodyAdventureNav::Extra5,UE_ARRAY_COUNT(BodyAdventureNav::Extra5));
    UE_LOG(LogTemp,Display,TEXT("ADVENTURE_READY meshes=%d organs=10 bridges=18 care_stations=7 route_waypoints=%d"),MeshCount,AdventureTravel.Num());
}

void ABodyWorld::TickAdventure(float Dt)
{
    TickGarden(Dt);
    auto PC=GetWorld()->GetFirstPlayerController();auto P=PC?Cast<ABodyPawn>(PC->GetPawn()):nullptr;
    bool Held=P&&P->Nearest==0&&PC->IsInputKeyDown(EKeys::E)&&Carry==0;
    if(Held)
    {
        Pull=FMath::Min(1.f,Pull+Dt/2.4f);
        if(Pull>=1&&!Pulled){Carry=1;Pulled=true;Organs[0].Cared=true;PlayTone(0,.45f);Notify("A deep breath. Take the short light bridge into the heart.",6);UE_LOG(LogTemp,Display,TEXT("ADVENTURE_BREATH_CREATED"));}
    }
    else {Pull=FMath::Max(0.f,Pull-Dt*.6f);if(!PC||!PC->IsInputKeyDown(EKeys::E))Pulled=false;}
    float Breath=1+.004f*FMath::Sin(Age*1.3f)+Pull*.009f;
    for(auto C:Organs[0].Animated)C->SetRelativeScale3D(FVector(Breath,-Breath,1+Pull*.012f));
    BeatAge+=Dt;if(BeatAge>60/FMath::Max(BPM,45.f)){BeatAge=0;if(P&&FVector::Dist2D(P->GetActorLocation(),Organs[1].Center)<2100)PlayTone(1,.10f);}
    float Beat=FMath::Exp(-BeatAge*12);
    for(auto C:Organs[1].Animated)C->SetRelativeScale3D(FVector(1+Beat*.0025f,-1-Beat*.0025f,1+Beat*.0035f));
    if(PulseSeed){PulseSeed->SetRelativeScale3D(FVector(1+Beat*.025f,-1-Beat*.025f,1+Beat*.025f));PulseSeed->SetVisibility(Carry!=2);}
    if(BreathDelivered)BPM=FMath::FInterpTo(BPM,72,Dt,.04f);
    for(int i=0;i<WindMotes.Num();i++)
    {float T=FMath::Fmod(Age*.12f+i*.23f,1.f);int Side=i<4?-1:1;WindMotes[i]->SetRelativeLocation(FVector(1000+2400*T,Side*3050+FMath::Sin(T*PI*2)*160,190+FMath::Sin(T*PI)*70));WindMotes[i]->SetRelativeScale3D(FVector(.42*FMath::Sin(T*PI),.055,.055));}
    for(int i=0;i<CareLights.Num();i++)if(CareLights[i]){CareLights[i]->SetRelativeLocation(Organs[i].Station+FVector(0,0,115+FMath::Sin(Age*1.8+i)*12));CareLights[i]->SetRelativeScale3D(FVector(.31+.035*FMath::Sin(Age*2+i)));}
    for(int i=0;i<Thoughts.Num();i++){float T=Age*(GardenFocused?.45f:1.f);Thoughts[i]->SetVisibility((ThoughtMask&(1u<<i))!=0,true);Thoughts[i]->SetRelativeScale3D(FVector(1+.045f*FMath::Sin(T*1.8+i)));Thoughts[i]->SetRelativeRotation(FRotator(0,FMath::Sin(T*.4+i)*9,0));}
    if(StressCloud){StressCloud->SetVisibility(Carry!=4&&!Organs[4].Cared,true);StressCloud->SetRelativeScale3D(FVector(1+.04f*FMath::Sin(Age*2)));}
    if(P&&(P->Nearest==5||P->Nearest==6)&&PC->IsInputKeyDown(EKeys::E))
    {
        ReleaseTime+=Dt;
        if(ReleaseTime>1.5f){int i=P->Nearest;ReleaseTime=-20;Organs[i].Cared=true;BPM=FMath::Clamp(BPM+(i==5?-15:10),60.f,115.f);PlayTone(2,.35);Notify(i==5?"A soft calm pulse reaches the heart.":"A little energy stirs through the body.",5);}
    }else ReleaseTime=0;
    if(BreathDelivered&&ThoughtCleared&&HeartDelivered&&!HasCompleted){HasCompleted=true;PlayTone(2,.6f);Notify("The body settles. There is a whole world below to explore.",10);UE_LOG(LogTemp,Display,TEXT("ADVENTURE_CARE_LOOP_COMPLETE"));}
}

void ABodyWorld::AdventureCare(int I)
{
    if(I>=8&&I<=10)
    {
        int Index=I-8;
        if(Carry==0&&(GardenStarMask&(1u<<Index))){GardenStarMask&=~(1u<<Index);Carry=5;PlayTone(2,.3);Notify("A bright little thought. Carry it to the tree's front roots.",6);UE_LOG(LogTemp,Display,TEXT("GARDEN_STAR_PICKUP %d"),Index);}
        return;
    }
    if(I==11){Notify("Hold E. Let the lotus open at its own pace.",3);return;}
    if(I==7){if(Carry==0&&!Organs[4].Cared){Carry=4;PlayTone(3,.3f);Notify("A heavy little cloud. Bring it to the liver's recovery pool.",7);}return;}
    if(I==0){if(Carry==2){Carry=0;Organs[0].Cared=true;PlayTone(2);Notify("A heartbeat opens a little more room to breathe.");}else if(Carry==0)Notify("Hold E. Let the breathing glade fill slowly.",3);return;}
    if(I==1)
    {
        if(Carry==1){Carry=0;BPM=74;BreathDelivered=true;Organs[1].Cared=true;PlayTone(2,.5f);Notify("The rhythm settles. E again to carry a heartbeat to the brain.",7);}
        else if(Carry==3){Carry=0;Organs[3].Cared=true;PlayTone(2);Notify("A little warm energy reaches the heart.");}
        else if(Carry==0&&BPM<=80){Carry=2;PlayTone(1,.4f);Notify("Carry the heartbeat through the rear arch and up to the brain.",8);}
        else if(Carry==0){BPM=FMath::Max(72.f,BPM-4);PlayTone(1,.3);Notify("A gentle pacing tap. A deep breath will help.");}
        else Notify("Take the cloud to the liver's recovery pool.");return;
    }
    if(I==2)
    {
        if(Carry==5)
        {
            Carry=0;GardenDelivered++;PlayTone(2,.45);Organs[2].Cared=true;
            if(GardenDelivered==3){GardenRestored=true;Notify("The tree stretches a root across the stream. A new way home.",8);UE_LOG(LogTemp,Display,TEXT("GARDEN_ROOT_SHORTCUT_OPEN"));}
            else Notify(FString::Printf(TEXT("The tree takes a breath of light. %d of 3 bright thoughts home."),GardenDelivered),6);
            return;
        }
        if(Carry>0&&Carry!=4){if(Carry==2)HeartDelivered=true;Carry=0;Organs[2].Cared=true;PlayTone(2,.4);Notify("The garden brightens. Walk to each thought and tap SPACE.",7);}
        else Action();return;
    }
    if(I==3){if(Carry==0){Carry=3;Organs[3].Cared=true;PlayTone(2,.3);Notify("Warm energy. Carry it to the heart or the awareness garden.",6);}else if(Carry==2){Carry=3;Organs[3].Cared=true;PlayTone(2);Notify("The digestion hearth brightens. A little energy is ready.");}return;}
    if(I==4){if(Carry==4||Carry==0){Carry=0;Organs[4].Cared=true;PlayTone(2,.4);Notify("The recovery pool clears. A little weight lifts.",6);}else Notify("This pool receives the heavy cloud from the heart.");return;}
    if(I==5||I==6)Notify(I==5?"Hold E to release a gentle calm pulse.":"Hold E to release a little energy.",3);
}

int32 ABodyWorld::GardenNearest(FVector P)const
{
    if(Carry==0)for(int i=0;i<GardenStarPlaces.Num();i++)if((GardenStarMask&(1u<<i))&&FVector::Dist2D(P,GardenStarPlaces[i])<230)return 8+i;
    if(!GardenFocused&&FVector::Dist2D(P,FVector(10567.500,2030.500,0))<360)return 11;
    return -1;
}

bool ABodyWorld::GardenBridgeHeight(FVector P,float& OutHeight)const
{
    if(!GardenRestored)return false;
    const FVector A=FVector(8320.000,1643.000,0),B=FVector(7994.500,325.500,0),D=B-A;
    const float T=FMath::Clamp(float(FVector::DotProduct(FVector(P.X,P.Y,0)-A,D)/D.SizeSquared()),0.f,1.f);
    if(FVector::Dist2D(P,A+D*T)>225)return false;
    auto Base=[](FVector V){int X=FMath::RoundToInt((V.X-BodyAdventureNav::X0)/BodyAdventureNav::Step),Y=FMath::RoundToInt((V.Y-BodyAdventureNav::Y0)/BodyAdventureNav::Step);return float(BodyAdventureNav::Height[X][Y]);};
    OutHeight=FMath::Lerp(Base(A),Base(B),T)+75*FMath::Sin(T*PI)+7;
    return true;
}

void ABodyWorld::TickGarden(float Dt)
{
    auto PC=GetWorld()->GetFirstPlayerController();auto P=PC?Cast<ABodyPawn>(PC->GetPawn()):nullptr;
    for(int i=0;i<GardenStars.Num();i++)if(GardenStars[i])
    {
        GardenStars[i]->SetVisibility((GardenStarMask&(1u<<i))!=0);
        GardenStars[i]->SetRelativeLocation(FVector(9250,0,220+FMath::Sin(Age*2+i)*11));
    }
    for(auto C:GardenRoots)C->SetVisibility(GardenRestored);
    for(auto M:GardenTreeMaterials)if(M)M->SetScalarParameterValue(TEXT("LifeGlow"),.6f+GardenDelivered*.7f+.15f*FMath::Sin(Age*1.7f));
    float Open=GardenFocused?1.f:GardenFocusPull;
    for(auto C:StudyMeshes)if(C->ComponentTags.Contains(TEXT("FocusPetals")))
    {float XY=1+Open*.30f,Z=1-Open*.38f;float Base=GroundHeight(FVector(10567.500,2030.500,0))-220-5;C->SetRelativeScale3D(FVector(XY,-XY,Z));C->SetRelativeLocation(FVector(9250+1317.5*(1-XY),2030.5*(1-XY),220+Base*(1-Z)));}
    if(P&&P->Nearest==11&&PC->IsInputKeyDown(EKeys::E)&&!GardenFocused)
    {
        GardenFocusPull=FMath::Min(1.f,GardenFocusPull+Dt/2.2f);
        if(GardenFocusPull>=1){GardenFocused=true;PlayTone(0,.4f);Notify("The lotus opens. The worry garden moves more gently.",6);UE_LOG(LogTemp,Display,TEXT("GARDEN_FOCUS_OPEN"));}
    }
    else if(!GardenFocused)GardenFocusPull=FMath::Max(0.f,GardenFocusPull-Dt*.7f);
}

FString ABodyWorld::AdventurePlace(FVector P)const
{
    if(P.X>6300)return TEXT("THE AWARENESS GARDEN");if(P.X>4300)return TEXT("THROAT PASS");
    if(P.X>450&&P.X<4100&&FMath::Abs(P.Y)>1900)return TEXT("THE BREATHING CHAMBERS");
    if(P.X>-300&&P.X<2900&&FMath::Abs(P.Y)<1700)return TEXT("INSIDE THE HEART");
    if(P.X>-1700)return TEXT("THE BREATHING GLADE");
    if(P.X>-4400&&P.Y<-600)return TEXT("THE LIVER'S RECOVERY POOLS");
    if(P.X>-4400&&P.Y>900)return TEXT("THE DIGESTION HEARTH");
    if(P.X>-7000&&FMath::Abs(P.Y)>2400)return TEXT("THE KIDNEY SPRINGS");
    if(P.X<-9800)return TEXT("THE QUIET PELVIS");if(P.X<-5900)return TEXT("THE INTESTINAL GALLERIES");
    return TEXT("THE DIGESTIVE CROSSING");
}
