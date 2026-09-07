// Adapted from the user's BOTWRECKED contact stepper for Attention's floor channel.
#include "BWBipedGait.h"
#include "Components/PrimitiveComponent.h"
#include "Engine/World.h"
#include "GameFramework/Pawn.h"

namespace BWBipedGait
{
namespace
{
 bool Ground(UWorld* World,AActor* Owner,const FVector& Wanted,float MaxStep,FHitResult& Out)
 {
  FCollisionQueryParams Query(SCENE_QUERY_STAT(BWBipedGround),false,Owner);
  // Pawns are not floor: stepping on another robot creates the very kick/shuffle feedback this solves.
  const FVector From=Wanted+FVector(0,0,MaxStep+12),To=Wanted-FVector(0,0,MaxStep*2+20);
  for(int Pass=0;Pass<6;++Pass)
  {
   if(!World->LineTraceSingleByChannel(Out,From,To,ECC_GameTraceChannel1,Query)) return false;
   if(Cast<APawn>(Out.GetActor())) { Query.AddIgnoredActor(Out.GetActor()); continue; }
   return Out.ImpactNormal.Z>.55f;
  }
  return false;
 }
 void Plant(FFoot& Foot,const FVector& Point,const FHitResult* Hit,float Clearance)
 {
  Foot.Target=Point; Foot.bSwing=false; Foot.bContact=Hit!=nullptr; Foot.Phase=1; Foot.Age=0;
  Foot.Surface=Hit?Hit->GetComponent():nullptr;
  if(Foot.Surface.IsValid()) Foot.AnchorLocal=Foot.Surface->GetComponentTransform().InverseTransformPosition(Point);
 }
 float Ease(float T) { return T*T*T*(T*(T*6-15)+10); }
}

void FStepper::Update(UWorld* World,AActor* Owner,const FVector& Core,const FVector* Roots,const FVector& Facing,
 const FVector& GroundVelocity,float GroundZ,float Clearance,float LegLength,float MaxExtension,
 float MaxStep,float MaxSpeed,float StartSpeed,bool bBrace,float Dt)
{
 if(!World||Dt<=0) return;
 const FVector Right=FVector::CrossProduct(FVector::UpVector,Facing);
 // Reinitialize only after leaving locomotion or teleporting; a turn never discards a planted anchor.
 if(!bReady||FVector::DistSquared(Core,PreviousCore)>FMath::Square(200.f))
 {
  Reset(); bReady=true; PreviousCore=Core;
  for(int I=0;I<2;++I)
  {
   FVector Rest(Roots[I].X,Roots[I].Y,GroundZ); FHitResult Hit;
   const bool Found=Ground(World,Owner,Rest,MaxStep,Hit);
   Plant(Feet[I],(Found?Hit.ImpactPoint:Rest)+FVector(0,0,Clearance),Found?&Hit:nullptr,Clearance);
  }
 }
 const FVector Measured=(Core-PreviousCore)/Dt-GroundVelocity; PreviousCore=Core;
 const FVector Flat(Measured.X,Measured.Y,0);
 // Short smoothing removes support-spring noise without hiding a real start, stop or change of direction.
 Velocity=FMath::Lerp(Velocity,Flat,1-FMath::Exp(-18.f*Dt));
 const float Speed=Velocity.Size2D();
 const bool Moving=Speed>StartSpeed;
 const float Run=FMath::Clamp((Speed-100.f)/FMath::Max(MaxSpeed-100.f,1.f),0.f,1.f);
 const FVector Travel=Moving?Velocity.GetSafeNormal2D():Facing;
 const float Duration=FMath::Lerp(.22f,.13f,Run);
 FVector Rest[2]; float Reach[2];
 for(int I=0;I<2;++I)
 {
  Rest[I]=FVector(Roots[I].X,Roots[I].Y,GroundZ+Clearance)+Right*((I?1.f:-1.f)*(bBrace?7.f:1.5f));
  const float Stand=FMath::Max(float(Roots[I].Z-Rest[I].Z),15.f);
  Reach[I]=FMath::Clamp(FMath::Sqrt(FMath::Max(FMath::Square(LegLength*MaxExtension)-Stand*Stand,100.f))*.9f,12.f,32.f);
  FFoot& Foot=Feet[I]; Foot.Age+=Dt;
  if(!Foot.bSwing)
  {
   if(Foot.Surface.IsValid()) Foot.Target=Foot.Surface->GetComponentTransform().TransformPosition(Foot.AnchorLocal);
   else if(Foot.bContact) Foot.bContact=false;
   continue;
  }
  Foot.Phase=FMath::Min(Foot.Phase+Dt/Foot.Duration,1.f);
  const float P=Foot.Phase;
  // Retarget early for braking/corners; the final third commits to a clean plant.
  if(P<.7f)
  {
   FVector Wanted=Rest[I]+Velocity*(Foot.Duration*(1-P))+Travel*(Moving?Reach[I]*.85f:0.f);
   Wanted.Z=GroundZ;
   FHitResult Hit;
   if(Ground(World,Owner,Wanted,MaxStep,Hit)) Wanted.Z=Hit.ImpactPoint.Z;
   Wanted.Z+=Clearance;
   Foot.Goal=FMath::Lerp(Foot.Goal,Wanted,1-FMath::Exp(-16.f*Dt));
  }
  const float Arc=16.f*P*P*(1-P)*(1-P); // zero height AND vertical velocity at lift-off and contact
  Foot.Target=FMath::Lerp(Foot.From,Foot.Goal,Ease(P))+FVector(0,0,Foot.Lift*Arc);
  if(P>=1)
  {
   FHitResult Hit; FVector Probe=Foot.Goal-FVector(0,0,Clearance);
   const bool Found=Ground(World,Owner,Probe,MaxStep,Hit);
   Plant(Foot,(Found?Hit.ImpactPoint:Probe)+FVector(0,0,Clearance),Found?&Hit:nullptr,Clearance);
  }
 }
 // Alternate support. At speed the second foot may lift late in the other swing; slow steps always keep support.
 for(int Attempt=0;Attempt<2;++Attempt)
 {
  const int I=(NextFoot+Attempt)%2,Other=1-I;
  FFoot& Foot=Feet[I]; if(Foot.bSwing) continue;
  const FVector Offset=Foot.Target-Rest[I];
  const float Behind=FVector::DotProduct(Offset,Travel);
  const bool NeedsStep=Moving?(Behind<-Reach[I]*.65f||Offset.Size2D()>Reach[I]*1.05f):Offset.Size2D()>9.f;
  if(!NeedsStep&&Foot.bContact) continue;
  if(Feet[Other].bSwing&&(Run<.4f||Feet[Other].Phase<.62f)) continue;
  if(Foot.Age<.045f) continue;
  FVector Wanted=Rest[I]+Velocity*Duration+Travel*(Moving?Reach[I]*.85f:0.f);
  Wanted.Z=GroundZ; FHitResult Hit;
  // No invisible foothold beyond a drop. Leave the support foot behind until the core is actually airborne.
  if(!Ground(World,Owner,Wanted,MaxStep,Hit)) continue;
  Foot.From=Foot.Target; Foot.Goal=Hit.ImpactPoint+FVector(0,0,Clearance);
  Foot.Duration=Moving?Duration:.24f; Foot.Phase=0; Foot.Age=0;
  Foot.Lift=Moving?FMath::Lerp(17.f,26.f,Run):12.f;
  Foot.Lift=FMath::Max(Foot.Lift,FMath::Min(MaxStep,float(Foot.Goal.Z-Foot.From.Z)+8.f));
  Foot.bSwing=true; Foot.bContact=false; Foot.Surface=nullptr; ++Foot.Steps; NextFoot=Other;
  break;
 }
 // Arm counter-swing and the small torso sway follow the actual stepping rhythm.
 const int Active=Feet[0].bSwing?0:Feet[1].bSwing?1:-1;
 if(Active>=0) Cycle=FMath::Fmod((Active? .5f:0.f)+Feet[Active].Phase*.5f,1.f);
}
}
