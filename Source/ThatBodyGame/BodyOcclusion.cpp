#include "BodyGame.h"
#include "Components/StaticMeshComponent.h"
#include "ProceduralMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Camera/CameraComponent.h"

void ABodyPawn::UpdateOcclusion(float Dt)
{
    if(!Body||!Camera)return;
    // Orthographic rays run parallel. Begin behind the character along the view direction.
    FVector Target=GetActorLocation()+FVector(0,0,98);
    FVector Eye=Target-Camera->GetForwardVector()*6000;
    auto ShouldFade=[&](UPrimitiveComponent* C)
    {
        if(C->ComponentHasTag(TEXT("Interactive"))||C->IsAttachedTo(Visual))return false;
        if(C->Bounds.Origin.Z+C->Bounds.BoxExtent.Z<Target.Z-65)return false;
        if(C->Bounds.SphereRadius>4000)return false;
        FBox Bounds=C->Bounds.GetBox().ExpandBy(FVector(22,22,12));
        // Stop just short of the character so ground beneath their feet cannot fade.
        FVector End=Target-Camera->GetForwardVector()*35;
        return FMath::LineBoxIntersection(Bounds,Eye,End,End-Eye);
    };
    FadeClock+=Dt;
    if(FadeClock>.12f)
    {
        FadeClock=0;
        TArray<UStaticMeshComponent*> Statics;Body->GetComponents(Statics);
        for(auto C:Statics)if(ShouldFade(C)&&!FadingStatic.Contains(C))FadingStatic.Add(C,C->CreateDynamicMaterialInstance(0));
        TArray<UProceduralMeshComponent*> Procs;Body->GetComponents(Procs);
        for(auto C:Procs)if(ShouldFade(C)&&!FadingProcedural.Contains(C))FadingProcedural.Add(C,C->CreateDynamicMaterialInstance(0));
    }
    auto Fade=[&](UPrimitiveComponent* C,UMaterialInstanceDynamic* Mat)
    {
        if(!C||!Mat)return;
        float Value=Mat->K2_GetScalarParameterValue(TEXT("Visibility"));
        Mat->SetScalarParameterValue(TEXT("Visibility"),FMath::FInterpTo(Value,ShouldFade(C)?.18f:1.f,Dt,7));
    };
    for(auto& Item:FadingStatic)Fade(Item.Key,Item.Value);
    for(auto& Item:FadingProcedural)Fade(Item.Key,Item.Value);
}
