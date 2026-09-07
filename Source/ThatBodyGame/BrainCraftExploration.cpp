#include "BrainCraft.h"
#include "BrainCraftLayout.inl"
#include "Components/SphereComponent.h"
#include "Engine/World.h"
#include "Engine/OverlapResult.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"

// Read actual native collision, including architecture. This is a navigation
// audit, separate from the input-driven playthrough and visual acceptance.
void AAttentionCharacter::AuditExploration()
{
    constexpr int NX=75,NY=83;constexpr float Step=80;
    struct FSite{FVector P;bool Stand=false,Reached=false;};TArray<FSite> Sites;Sites.SetNum(NX*NY);
    FCollisionQueryParams Q(SCENE_QUERY_STAT(BrainGardenExplore),false,this);for(auto T:Thoughts)Q.AddIgnoredActor(T);
    const FCollisionShape Capsule=FCollisionShape::MakeCapsule(34,92);int32 Standable=0,Start=INDEX_NONE;float Best=MAX_flt;
    auto StandPosition=[&](FVector Floor,FVector& Position){FHitResult Contact;if(!GetWorld()->SweepSingleByChannel(Contact,Floor+FVector(0,0,250),Floor+FVector(0,0,40),FQuat::Identity,ECC_Pawn,Capsule,Q)||Contact.bStartPenetrating||Contact.ImpactNormal.Z<.68f)return false;Position=Contact.Location+FVector(0,0,2.5f);return !GetWorld()->OverlapBlockingTestByChannel(Position,FQuat::Identity,ECC_Pawn,Capsule,Q);};
    for(int X=0;X<NX;X++)for(int Y=0;Y<NY;Y++)
    {
        auto& S=Sites[X*NY+Y];float Px=-2960+X*Step,Py=-3280+Y*Step;FHitResult Hit;
        // The awareness tree's raised root bed is a landmark, not a shortcut.
        // Leave a capsule-width margin around its visible root and stone rim.
        if(FVector2D(Px,Py-90).SizeSquared()<FMath::Square(410.f))continue;
        // Thoughts are physical moving actors. Keep the exploration route out
        // of their home footprint rather than asking the player to occupy them.
        bool ThoughtFootprint=false;
        for(auto Thought:Thoughts)if(FVector2D(Px-Thought->Home.X,Py-Thought->Home.Y).Size()<Thought->Physics->GetScaledSphereRadius()+76.f){ThoughtFootprint=true;break;}
        if(ThoughtFootprint)continue;
        if(!GetWorld()->LineTraceSingleByChannel(Hit,FVector(Px,Py,4000),FVector(Px,Py,-700),ECC_GameTraceChannel1,Q)||Hit.ImpactNormal.Z<.68f)continue;
        S.Stand=StandPosition(Hit.ImpactPoint,S.P);
        if(S.Stand){Standable++;float D=FVector::DistSquared(S.P,GetActorLocation());if(D<Best){Start=X*NY+Y;Best=D;}}
    }
    TArray<int32> Queue,Parents;Parents.Init(INDEX_NONE,NX*NY);if(Start!=INDEX_NONE){Queue.Add(Start);Sites[Start].Reached=true;}
    for(int32 I=0;I<Queue.Num();I++)
    {
        int32 U=Queue[I],X=U/NY,Y=U%NY;
        for(FIntPoint D:{FIntPoint(1,0),FIntPoint(-1,0),FIntPoint(0,1),FIntPoint(0,-1)})
        {
            int32 Vx=X+D.X,Vy=Y+D.Y;if(Vx<0||Vx>=NX||Vy<0||Vy>=NY)continue;int32 V=Vx*NY+Vy;auto& S=Sites[V];
            if(!S.Stand||S.Reached||FMath::Abs(S.P.Z-Sites[U].P.Z)>Step*.70f)continue;
            // A raised sweep alone can fly over a bank lip that walking cannot
            // climb. Resolve the floor between grid sites at capsule scale.
            bool Continuous=true;FVector Previous=Sites[U].P;
            for(int Sample=1;Sample<=4;Sample++)
            {
                const FVector At=FMath::Lerp(Sites[U].P,S.P,Sample/4.f);FHitResult Floor;FVector StandAt;
                if(!GetWorld()->LineTraceSingleByChannel(Floor,At+FVector(0,0,180),At-FVector(0,0,240),ECC_GameTraceChannel1,Q)||Floor.ImpactNormal.Z<.73f||!StandPosition(Floor.ImpactPoint,StandAt)||FMath::Abs(StandAt.Z-Previous.Z)>20.f){Continuous=false;break;}
                Previous=StandAt;
            }
            if(!Continuous)continue;
            FHitResult Hit;if(GetWorld()->SweepSingleByChannel(Hit,Sites[U].P+FVector(0,0,38),S.P+FVector(0,0,38),FQuat::Identity,ECC_Pawn,Capsule,Q))continue;
            S.Reached=true;Parents[V]=U;Queue.Add(V);
        }
    }
    const TCHAR* Names[]={TEXT("arrival"),TEXT("awareness"),TEXT("spring"),TEXT("memory"),TEXT("release"),TEXT("lower_front"),TEXT("lower_west"),TEXT("lower_north"),TEXT("lower_east"),TEXT("dawn_gate"),TEXT("spring_gate"),TEXT("memory_gate")};
    const FVector Targets[]={FVector(-1810,-2470,140),FVector(0,-365,520),FVector(-1100,1500,1100),FVector(1960,1400,950),FVector(1550,-1780,330),FVector(-920,-1800,0),FVector(-1570,-650,350),FVector(0,1640,900),FVector(1100,-650,220),CraftLayout::PortalApproaches[0],CraftLayout::PortalApproaches[1],CraftLayout::PortalApproaches[2]};
    auto Root=MakeShared<FJsonObject>();Root->SetStringField(TEXT("method"),TEXT("Native floor traces, capsule clearance and swept neighbor connections; not a player playthrough"));Root->SetNumberField(TEXT("standable_cells"),Standable);Root->SetNumberField(TEXT("reachable_cells"),Queue.Num());
    TArray<TSharedPtr<FJsonValue>> Destinations,Disconnected;TArray<int32> TargetNodes;bool All=true;
    for(int I=0;I<UE_ARRAY_COUNT(Targets);I++)
    {
        FHitResult Floor;const auto At=Targets[I];bool HasFloor=GetWorld()->LineTraceSingleByChannel(Floor,FVector(At.X,At.Y,4000),FVector(At.X,At.Y,-700),ECC_GameTraceChannel1,Q);
        FVector StandAt=HasFloor?Floor.ImpactPoint+FVector(0,0,94):At;bool CanStand=HasFloor&&StandPosition(Floor.ImpactPoint,StandAt);
        float Near=MAX_flt;FVector Found;int32 Closest=INDEX_NONE;for(int J:Queue){float D=FVector::Dist(Sites[J].P,StandAt);if(D<Near){Near=D;Found=Sites[J].P;Closest=J;}}TargetNodes.Add(Closest);
        bool Reach=CanStand&&Near<160;All&=Reach;auto O=MakeShared<FJsonObject>();O->SetStringField(TEXT("name"),Names[I]);O->SetBoolField(TEXT("reachable"),Reach);O->SetNumberField(TEXT("nearest_cm"),Near);O->SetStringField(TEXT("position"),Found.ToString());
        if(HasFloor)
        {
            O->SetStringField(TEXT("floor_actor"),GetNameSafe(Floor.GetActor()));O->SetStringField(TEXT("floor_point"),Floor.ImpactPoint.ToString());O->SetStringField(TEXT("floor_normal"),Floor.ImpactNormal.ToString());
            TArray<FOverlapResult> Overlaps;GetWorld()->OverlapMultiByChannel(Overlaps,StandAt,FQuat::Identity,ECC_Pawn,Capsule,Q);TArray<TSharedPtr<FJsonValue>> Blockers;
            for(const auto& Hit:Overlaps)if(Hit.bBlockingHit&&Hit.GetActor()){FString Name=Hit.GetActor()->GetName();for(auto Tag:Hit.GetActor()->Tags)Name+=TEXT(" / ")+Tag.ToString();Blockers.Add(MakeShared<FJsonValueString>(Name));}
            O->SetArrayField(TEXT("overlap_blockers"),Blockers);
            if(Blockers.Num()>0){O->SetBoolField(TEXT("reachable"),false);All=false;}
        }
        else{O->SetBoolField(TEXT("reachable"),false);All=false;}
        Destinations.Add(MakeShared<FJsonValueObject>(O));
    }
    for(const auto& S:Sites)if(S.Stand&&!S.Reached){TArray<TSharedPtr<FJsonValue>> V;V.Add(MakeShared<FJsonValueNumber>(S.P.X));V.Add(MakeShared<FJsonValueNumber>(S.P.Y));V.Add(MakeShared<FJsonValueNumber>(S.P.Z));Disconnected.Add(MakeShared<FJsonValueArray>(V));}
    TArray<TSharedPtr<FJsonValue>> AllSites;for(const auto& S:Sites)if(S.Stand){TArray<TSharedPtr<FJsonValue>> V;V.Add(MakeShared<FJsonValueNumber>(S.P.X));V.Add(MakeShared<FJsonValueNumber>(S.P.Y));V.Add(MakeShared<FJsonValueNumber>(S.P.Z));V.Add(MakeShared<FJsonValueNumber>(S.Reached?1:0));AllSites.Add(MakeShared<FJsonValueArray>(V));}
    Root->SetBoolField(TEXT("all_destinations_reachable"),All);Root->SetArrayField(TEXT("destinations"),Destinations);Root->SetArrayField(TEXT("disconnected_samples"),Disconnected);Root->SetArrayField(TEXT("all_samples"),AllSites);FString Json;FJsonSerializer::Serialize(Root,TJsonWriterFactory<>::Create(&Json));FFileHelper::SaveStringToFile(Json,*(FPaths::ProjectSavedDir()/TEXT("brain-c15-exploration.json")));UE_LOG(LogTemp,Display,TEXT("CRAFT_EXPLORATION destinations=%d reachable=%d standable=%d"),All,Queue.Num(),Standable);
    if(RoamReview&&All)
    {
        int32 Last=Start;
        for(int32 Target:TargetNodes)
        {
            TArray<int32> From,To;for(int32 P=Last;P!=INDEX_NONE;P=Parents[P])From.Add(P);for(int32 P=Target;P!=INDEX_NONE;P=Parents[P])To.Add(P);
            int32 A=From.Num()-1,B=To.Num()-1;while(A>=0&&B>=0&&From[A]==To[B]){A--;B--;}
            for(int32 I=0;I<=A;I++)RoamRoute.Add(Sites[From[I]].P);
            if(A+1<From.Num())RoamRoute.Add(Sites[From[A+1]].P);
            for(int32 I=B;I>=0;I--)RoamRoute.Add(Sites[To[I]].P);
            RoamCheckpoints.Add(RoamRoute.Num()-1);Last=Target;
        }
        UE_LOG(LogTemp,Display,TEXT("CRAFT_ROAM_READY waypoints=%d destinations=%d"),RoamRoute.Num(),RoamCheckpoints.Num());return;
    }
    FPlatformMisc::RequestExit(false);
}
