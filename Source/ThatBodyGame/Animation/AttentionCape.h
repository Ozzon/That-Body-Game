#pragma once
#include "CoreMinimal.h"
#include "ProceduralMeshComponent.h"
#include "AttentionCape.generated.h"

struct FCapeParticle { FVector Rest,P,Previous;float InvMass=1; };
struct FCapeLink { int32 A,B;float Length,Compliance,Lambda=0; };
struct FCapeBinding { int32 A,B,C,D;float U,V; };
struct FCapeRenderSection
{
    TArray<FVector> Rest,Vertices,Normals;
    TArray<int32> Triangles;
    TArray<FVector2D> UV;
    TArray<FProcMeshTangent> Tangents;
    TArray<FCapeBinding> Bindings;
};

// The tailored cape, hem and embroidery share a physical cloth lattice.
// XPBD stretch, shear and bend constraints preserve their authored detail.
UCLASS()
class UAttentionCape : public UProceduralMeshComponent
{
    GENERATED_BODY()
public:
    bool Bind(UStaticMesh* Source,const FTransform& Pose);
    void Simulate(const FTransform& Pose,float Dt,float FloorZ,FVector Thought,float ThoughtRadius);
    void ResetCloth(const FTransform& Pose);
    float MaxStretch=1,MaxTravel=0;int32 RecoveryCount=0;
private:
    static constexpr int Cols=21,Rows=15;
    TArray<FCapeParticle> Particles;
    TArray<FCapeLink> Links;
    TArray<FCapeRenderSection> Sections;
    FVector LastOrigin=FVector::ZeroVector;
    FVector LastRootVelocity=FVector::ZeroVector;
    FTransform PreviousPose=FTransform::Identity;
    float Age=0;
    float PreviousStep=1.f/120.f;
    void Render(const FTransform& Pose,bool Create);
};
