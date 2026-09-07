#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/HUD.h"
#include "BodyGame.generated.h"

class UProceduralMeshComponent;
class UMaterialInterface;
class UCameraComponent;
class UStaticMeshComponent;
class UTextRenderComponent;
class USoundWave;
class UMaterialInstanceDynamic;

USTRUCT()
struct FBodyOrgan
{
    GENERATED_BODY()
    FString Name;
    FVector Center=FVector::ZeroVector;
    FVector Station=FVector::ZeroVector;
    FLinearColor Color=FLinearColor::White;
    float Health=0.4f;
    bool Cared=false;
    UPROPERTY() TArray<USceneComponent*> Animated;
    UPROPERTY() TArray<USceneComponent*> Debris;
};

UCLASS()
class ABodyWorld : public AActor
{
    GENERATED_BODY()
public:
    ABodyWorld();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    UPROPERTY() TArray<FBodyOrgan> Organs;
    UPROPERTY() TArray<UMaterialInterface*> Mats;
    UPROPERTY() TArray<UStaticMeshComponent*> FlowCells;
    UPROPERTY() TArray<UStaticMeshComponent*> WindMotes;
    UPROPERTY() TArray<UStaticMeshComponent*> HeartCells;
    UPROPERTY() TArray<UStaticMeshComponent*> BrightMotes;
    UPROPERTY() TArray<USoundWave*> Sounds;
    UPROPERTY() UStaticMesh* Sphere;
    UPROPERTY() UStaticMesh* Cylinder;
    UPROPERTY() UStaticMesh* Cube;
    TArray<FVector> Boundary;
    float Age=0, ToastTime=10, TaskTime=0, Progress=0, BeatAge=0;
    int32 Active=-1, Score=0, Mistakes=0, SequenceStep=0;
    bool Paused=false, Photo=false, Muted=false, HasCompleted=false;
    int32 Carry=0, ThoughtCount=4, CareCount=0;
    float BPM=99, Pull=0, CalmTime=0, BreatheBuff=0, SwatCooldown=0;
    bool Pulled=false, BreathDelivered=false, ThoughtCleared=false, HeartDelivered=false;
    UPROPERTY() USceneComponent* Diaphragm;
    UPROPERTY() TArray<USceneComponent*> Thoughts;
    UPROPERTY() USceneComponent* Awareness;
    UPROPERTY() UTextRenderComponent* BpmLabel;
    FString Toast="Welcome, little caretaker. Start with the lungs.";
    FString Feedback;
    TArray<int32> Sequence={0,2,1,3};
    UStaticMeshComponent* Shape(FVector P,FVector S,int Mat,USceneComponent* Parent=nullptr,int Kind=0,FRotator R=FRotator::ZeroRotator);
    UProceduralMeshComponent* Blob(FVector P,FVector S,int Mat,float Seed=0,float Detail=0.03f,USceneComponent* Parent=nullptr);
    UProceduralMeshComponent* Tube(const TArray<FVector>& P,float Radius,int Mat,bool Closed=false);
    void Path(const TArray<FVector>& P,float Width=230,int Mat=14);
    float GroundHeight(FVector P) const;
    void Label(FString Text,FVector P,float Size,FColor Color);
    void MakeWorld();
    void MakeBrain();
    void MakeLungs();
    void MakeHeart();
    void MakeAbdomen();
    void BeginCare(int32 Index);
    void Action(int32 Direction=-1);
    void CompleteCare();
    void ResetCare();
    void PlayTone(int32 Index,float Volume=0.4f);
    void Notify(FString Text,float Duration=5);
    FVector FlowPosition(int32 I,float T) const;
    bool CanStand(FVector P) const;
    FString TaskInstruction() const;
    FString Status(int I) const;
};

UCLASS()
class ABodyPawn : public APawn
{
    GENERATED_BODY()
public:
    ABodyPawn();
    virtual void BeginPlay() override;
    virtual void Tick(float Dt) override;
    UPROPERTY() UCameraComponent* Camera;
    UPROPERTY() USceneComponent* Visual;
    UPROPERTY() ABodyWorld* Body;
    UPROPERTY() TArray<USceneComponent*> Limbs;
    UPROPERTY() USceneComponent* CarryVisual;
    UPROPERTY() USceneComponent* Hood;
    UPROPERTY() USceneComponent* Cape;
    FVector SmoothedMove=FVector::ZeroVector;
    float HopAge=2;
    float CamPitch=65;
    FVector PanOffset=FVector::ZeroVector;
    UPROPERTY() TMap<UStaticMeshComponent*,UMaterialInstanceDynamic*> FadingStatic;
    UPROPERTY() TMap<UProceduralMeshComponent*,UMaterialInstanceDynamic*> FadingProcedural;
    float FadeClock=0;
    void UpdateOcclusion(float Dt);
    FString CaptureMode;
    int32 CaptureStage=-1;
    bool Smoke=false;
    int32 SmokeStage=0;
    float SmokeTime=0;
    TSet<FKey> SmokeKeys;
    void RunSmoke(float Dt);
    float Zoom=1, CamYaw=0, WalkAge=0;
    bool Overview=true, Help=true, HasTarget=false;
    FVector MoveTarget=FVector::ZeroVector, CameraFocus=FVector::ZeroVector;
    int32 Nearest=-1;
    void JumpTo(int32 I);
};

UCLASS()
class ABodyHUD : public AHUD
{
    GENERATED_BODY()
public:
    virtual void DrawHUD() override;
    void Text(FString S,float X,float Y,float Size,FLinearColor C=FLinearColor::White);
    void Box(float X,float Y,float W,float H,FLinearColor C);
    void Line(float X,float Y,float X2,float Y2,FLinearColor C,float Thick=1);
    void Ring(float X,float Y,float R,FLinearColor C,float Fraction=1,float Thick=3);
    float Scale=1;
};

UCLASS()
class ABodyGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    ABodyGameMode();
    virtual void BeginPlay() override;
};
