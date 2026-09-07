// Contact-driven steps for the native powered biped. Targets only: the robot's bodies remain simulated.
#pragma once
#include "CoreMinimal.h"

class UPrimitiveComponent;
class UWorld;
class AActor;

namespace BWBipedGait
{
 struct FFoot
 {
  FVector Target=FVector::ZeroVector, From=FVector::ZeroVector, Goal=FVector::ZeroVector;
  FVector AnchorLocal=FVector::ZeroVector;
  TWeakObjectPtr<UPrimitiveComponent> Surface;
  float Phase=1, Duration=.22f, Lift=0, Age=0;
  bool bSwing=false, bContact=false;
  int32 Steps=0;
 };

 struct FStepper
 {
  FFoot Feet[2];
  FVector Velocity=FVector::ZeroVector, PreviousCore=FVector::ZeroVector;
  bool bReady=false;
  int32 NextFoot=0;
  float Cycle=0;
  void Reset() { *this=FStepper(); }
  void Update(UWorld* World,AActor* Owner,const FVector& Core,const FVector* Roots,const FVector& Facing,
   const FVector& GroundVelocity,float GroundZ,float Clearance,float LegLength,float MaxExtension,
   float MaxStep,float MaxSpeed,float StartSpeed,bool bBrace,float Dt);
 };
}
