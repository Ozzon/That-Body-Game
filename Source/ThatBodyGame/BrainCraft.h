#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "Components/ActorComponent.h"
#include "Animation/BWBipedGait.h"
#include "BrainCraft.generated.h"

class UStaticMeshComponent;
class USphereComponent;
class UCameraComponent;
class UPhysicsHandleComponent;
class UInstancedStaticMeshComponent;
class UMaterialInstanceDynamic;
class UAttentionCape;

// Visual contact must use the body's completed physics transform for this frame.
UCLASS()
class UAttentionPresentation : public UActorComponent
{
    GENERATED_BODY()
public:
    UAttentionPresentation();
    virtual void TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction) override;
};

UCLASS()
class ACraftThought : public AActor
{
    GENERATED_BODY()
public:
    ACraftThought();
    virtual void Tick(float Dt) override;
    void Configure(int32 Type,FVector Origin);
    UPROPERTY() USphereComponent* Physics;
    UPROPERTY() UStaticMeshComponent* Appearance;
    UPROPERTY() UStaticMeshComponent* Face;
    UPROPERTY() TArray<UStaticMeshComponent*> Eyes;
    UPROPERTY() TArray<UStaticMeshComponent*> Threads;
    UPROPERTY() UMaterialInstanceDynamic* GlowMaterial;
    int32 Kind=0,Pushes=0;
    float Age=0,Reaction=0,Disappear=0,ReturnIn=-1,BirthAge=0;
    bool Held=false,Resolved=false;
    bool CastBaseline=false;
    float AttentionBlend=0,Expression=1,VisualPitch=24;
    FVector Home=FVector::ZeroVector;
    FVector ResolveStart=FVector::ZeroVector,ResolveTarget=FVector::ZeroVector;
    bool HasResolveTarget=false;
    void ResolveTo(FVector Target);
    UFUNCTION() void OnHit(UPrimitiveComponent* HitComponent,AActor* OtherActor,UPrimitiveComponent* OtherComp,FVector Impulse,const FHitResult& Hit);
};

USTRUCT()
struct FCraftFade
{
    GENERATED_BODY()
    UPROPERTY() UStaticMeshComponent* Mesh=nullptr;
    UPROPERTY() TArray<UMaterialInstanceDynamic*> Materials;
    float Alpha=1;
};

struct FCraftSpark
{
    FVector P,V;float Age=0,Life=1,Scale=1;bool Gold=true;
};

UCLASS()
class AAttentionCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AAttentionCharacter();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    virtual void Landed(const FHitResult& Hit) override;
    UPROPERTY() UCameraComponent* Camera;
    UPROPERTY() UPhysicsHandleComponent* Hands;
    UPROPERTY() USceneComponent* Puppet;
    UPROPERTY() UAttentionCape* ClothCape=nullptr;
    UPROPERTY() UAttentionPresentation* Presentation=nullptr;
    FVector PoseMove=FVector::ZeroVector;
    UPROPERTY() TArray<USceneComponent*> Parts;
    UPROPERTY() TArray<USceneComponent*> Forearms;
    UPROPERTY() TArray<USceneComponent*> Mittens;
    UPROPERTY() TArray<UMaterialInstanceDynamic*> GroundCoverMaterials;
    UPROPERTY() TArray<ACraftThought*> Thoughts;
    UPROPERTY() ACraftThought* HeldThought=nullptr;
    UPROPERTY() TArray<FCraftFade> Fades;
    UPROPERTY() TArray<UStaticMeshComponent*> Shortcut;
    UPROPERTY() TArray<USceneComponent*> Petals;
    UPROPERTY() TArray<UMaterialInstanceDynamic*> TreeLight;
    UPROPERTY() UInstancedStaticMeshComponent* GoldFX;
    UPROPERTY() UInstancedStaticMeshComponent* VioletFX;
    UPROPERTY() UInstancedStaticMeshComponent* RippleFX;
    UPROPERTY() UInstancedStaticMeshComponent* PetalFX;
    TArray<FCraftSpark> Sparks;
    float Age=0,CamYaw=80,CamPitch=49,Zoom=1,StepPhase=0,SwatAge=10,LandAge=10,Focus=0,TreeCharge=0,CapeAngle=0,CapeVelocity=0,FootBeat=0;
    FVector CameraFocus=FVector::ZeroVector,Pan=FVector::ZeroVector,LastSafe=FVector(-1810,-2470,245),LastVelocity=FVector::ZeroVector;
    bool Overview=false,Help=false,Photo=false,Focused=false,BridgeOpen=false,Complete=false,Paused=false;
    int32 Delivered=0,Released=0,Nearest=-1,CaptureStage=-1,Recoveries=0,PhysicalGrabs=0;
    float MaxHandError=0;
    bool LegacyGrip=false;
    float GripAge=0,MaxGripError=0,MaxSteadyHandleLag=0;
    double GripErrorSum=0;int32 GripSamples=0;
    float CarryBlend=0,ContactError=0,GroundedGrace=0,JumpBuffer=0;
    float SmoothedMove=0,BodyLean=0,BodyRoll=0,PreviousYaw=0,LookYaw=0,LookPitch=0;
    BWBipedGait::FStepper ContactSteps;
    FVector CarryTarget=FVector::ZeroVector;
    UPROPERTY() TArray<USceneComponent*> Legs;
    UPROPERTY() TArray<USceneComponent*> Shins;
    FVector HandPose[2]={FVector::ZeroVector,FVector::ZeroVector};
    FVector ReleaseHandLocal[2]={FVector::ZeroVector,FVector::ZeroVector};
    float ReleaseBlend=0;
    bool WasHolding=false;
    FVector FootAnchor[2]={FVector::ZeroVector,FVector::ZeroVector};
    bool FootStance[2]={false,false};
    int32 PendingSwat=-1;
    FString Prompt,Message="A thought is waiting by the path. Give it a little attention.";
    float MessageTime=8;
    bool Capture=false,Smoke=false,Film=false;
    bool ControlsReview=false;
    bool RoamReview=false;
    TArray<FVector> RoamRoute;
    TArray<int32> RoamCheckpoints;
    int32 RoamWaypoint=0,RoamVisited=0;
    bool CameraDragging=false;
    FVector2D CameraCursor=FVector2D::ZeroVector;
    int32 ControlPhase=-1,ControlFlags=0;
    float ControlYaw=0,ControlZoom=1;
    float FilmClock=0;int32 FilmFrame=0;
    int32 SmokeStage=0;float SmokeClock=0;
    bool ReviewActionIssued=false;
    TSet<FKey> TestKeys;
    void Interact();void Swat();void SwatImpact();void ResetMorning();void Burst(FVector P,bool Gold,int32 Count=16,float Power=160);void Tone(int32 I,float Volume=.25);
    void UpdateAnimation(float Dt,FVector Move);void UpdateEffects(float Dt);void UpdateVisibility(float Dt);void RunReview(float Dt);
    void AuditExploration();
    UStaticMeshComponent* MeshPart(const FString& Key,USceneComponent* Parent,FVector P=FVector::ZeroVector);
    FString Task() const;
};

UCLASS()
class ABrainCraftHUD : public AHUD
{
    GENERATED_BODY()
public: virtual void DrawHUD() override;
};

UCLASS()
class ABrainCraftGameMode : public AGameModeBase
{
    GENERATED_BODY()
public: ABrainCraftGameMode();
};
