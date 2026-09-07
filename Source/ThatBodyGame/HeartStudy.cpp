#include "BodyGame.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInterface.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "StaticMeshResources.h"
#include "Components/PointLightComponent.h"
#include "HeartModelANav.inl"
#include "HeartModelBNav.inl"
#include "HeartModelCNav.inl"

void ABodyWorld::MakeHeartStudy()
{
    BPM=88;Toast=TEXT("A quiet place to feel the rhythm.");ToastTime=5;
    Organs[1].Center=FVector(0,0,65);
    auto Layout=[&](float X,float Y,float SX,float SY,float WX,float WY){StudySpawn=FVector(X,Y,63);Organs[1].Station=FVector(SX,SY,GroundHeight(FVector(SX,SY,0)));StudyWallPoint=FVector(WX,WY,63);};
    if(HeartVariant==0){Layout(HeartModelA::SpawnX,HeartModelA::SpawnY,HeartModelA::StationX,HeartModelA::StationY,HeartModelA::WallX,HeartModelA::WallY);StudyRoute.Append(HeartModelA::Route,UE_ARRAY_COUNT(HeartModelA::Route));StudyTitle=TEXT("A / REFERENCE CHAMBERS");}
    else if(HeartVariant==1){Layout(HeartModelB::SpawnX,HeartModelB::SpawnY,HeartModelB::StationX,HeartModelB::StationY,HeartModelB::WallX,HeartModelB::WallY);StudyRoute.Append(HeartModelB::Route,UE_ARRAY_COUNT(HeartModelB::Route));StudyTitle=TEXT("B / ANATOMICAL CHAMBERS");}
    else {Layout(HeartModelC::SpawnX,HeartModelC::SpawnY,HeartModelC::StationX,HeartModelC::StationY,HeartModelC::WallX,HeartModelC::WallY);StudyRoute.Append(HeartModelC::Route,UE_ARRAY_COUNT(HeartModelC::Route));StudyTitle=TEXT("C / OPEN HEART COURTYARD");}
    Shape(FVector(0,0,-260),FVector(160,160,1),7,nullptr,2);
    auto Surface=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/HeartModels/M_HeartAuthored.M_HeartAuthored"));
    const TCHAR* Parts[]={TEXT("SM_Heart_Foundation"),TEXT("SM_Heart_WallFrontRight"),TEXT("SM_Heart_WallFrontLeft"),TEXT("SM_Heart_WallBackRight"),TEXT("SM_Heart_WallBackLeft"),TEXT("SM_Heart_Aorta"),TEXT("SM_Heart_PacingValve"),TEXT("SM_Heart_PulseSeed")};
    for(int i=0;i<8;i++)
    {
        const FString Name=Parts[i];auto Mesh=LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/HeartModels/%c/%s.%s"),TCHAR('A'+HeartVariant),*Name,*Name));
        if(!Mesh){UE_LOG(LogTemp,Error,TEXT("HEART_ASSET_MISSING %s"),*Name);continue;}
        if(Mesh->GetRenderData()&&Mesh->GetRenderData()->LODResources.Num())
        {auto& Colors=Mesh->GetRenderData()->LODResources[0].VertexBuffers.ColorVertexBuffer;UE_LOG(LogTemp,Display,TEXT("HEART_VERTEX_COLOR %s COUNT=%u FIRST=%s"),*Name,Colors.GetNumVertices(),Colors.GetNumVertices()?*Colors.VertexColor(0).ToString():TEXT("none"));}
        UStaticMeshComponent* C=nullptr;
        for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)if(It->Tags.Contains(TEXT("HeartPart"))&&It->GetStaticMeshComponent()->GetStaticMesh()==Mesh){C=It->GetStaticMeshComponent();break;}
        if(!C){C=NewObject<UStaticMeshComponent>(this);C->SetupAttachment(RootComponent);C->SetStaticMesh(Mesh);C->SetRelativeScale3D(FVector(1,-1,1));C->RegisterComponent();}
        C->SetMobility(EComponentMobility::Movable);C->SetCollisionEnabled(ECollisionEnabled::QueryOnly);C->SetCollisionResponseToAllChannels(ECR_Ignore);C->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
        for(int Slot=0;Slot<Mesh->GetStaticMaterials().Num();Slot++)C->SetMaterial(Slot,Surface);
        if(i>=6)C->ComponentTags.Add(TEXT("Interactive"));
        if(i==7){auto Glow=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/HeartModels/M_Heartbeat.M_Heartbeat"));C->SetMaterial(0,Glow?Glow:Mats[8]);PulseSeed=C;}
        if(i<6)Organs[1].Animated.Add(C);
        StudyMeshes.Add(C);
        UE_LOG(LogTemp,Display,TEXT("HEART_AUTHORED_ASSET %s EXTENT %s"),*Name,*Mesh->GetBounds().BoxExtent.ToString());
    }
    // The only external route in this focused study is a soft light bridge into the apex.
    Path({StudySpawn+FVector(-90,0,-49),StudySpawn+FVector(150,0,-49),StudySpawn+FVector(440,0,-49)},350);
    auto GlowLight=NewObject<UPointLightComponent>(this);GlowLight->SetupAttachment(RootComponent);GlowLight->SetRelativeLocation(Organs[1].Station+FVector(0,0,260));GlowLight->SetIntensity(8500);GlowLight->SetLightColor(FLinearColor(1,.44,.16));GlowLight->SetAttenuationRadius(1350);GlowLight->SetSourceRadius(110);GlowLight->SetCastShadows(false);GlowLight->RegisterComponent();
    UE_LOG(LogTemp,Display,TEXT("HEART_STUDY_READY: model %c, four sculpted chambers, route points %d"),TCHAR('A'+HeartVariant),StudyRoute.Num());
}
