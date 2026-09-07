#include "AttentionCape.h"
#include "KismetProceduralMeshLibrary.h"
#include "Engine/StaticMesh.h"

bool UAttentionCape::Bind(UStaticMesh* Source,const FTransform& Pose)
{
    if(!Source||!Source->bAllowCPUAccess)return false;
    Particles.Empty();Links.Empty();Sections.Empty();SetCollisionEnabled(ECollisionEnabled::NoCollision);SetCastShadow(true);
    for(int Row=0;Row<Rows;Row++)for(int Col=0;Col<Cols;Col++)
    {
        float T=float(Row)/(Rows-1),A=.66f+(2*PI-1.32f)*Col/(Cols-1),Z=111-73*T;
        const float Heights[]={38,43,61,83,104,111},Rx[]={51,50,45,37,29,27},Ry[]={48,47,43,35,29,27};int K=0;while(K<4&&Z>Heights[K+1])K++;float U=FMath::Clamp((Z-Heights[K])/(Heights[K+1]-Heights[K]),0.f,1.f);
        FCapeParticle P;P.Rest=FVector(-3*T+FMath::Lerp(Rx[K],Rx[K+1],U)*FMath::Cos(A),FMath::Lerp(Ry[K],Ry[K+1],U)*FMath::Sin(A),Z);P.InvMass=Row==0?0:Row==1?.2f:1;Particles.Add(P);
    }
    auto Link=[&](int A,int B,float Compliance){FCapeLink L;L.A=A;L.B=B;L.Length=FVector::Dist(Particles[A].Rest,Particles[B].Rest);L.Compliance=Compliance;Links.Add(L);};
    for(int R=0;R<Rows;R++)for(int C=0;C<Cols;C++)
    {
        int I=R*Cols+C;if(C+1<Cols)Link(I,I+1,2e-7f);if(R+1<Rows)Link(I,I+Cols,2e-7f);
        if(C+1<Cols&&R+1<Rows){Link(I,I+Cols+1,2e-6f);Link(I+1,I+Cols,2e-6f);}
        if(C+2<Cols)Link(I,I+2,2e-5f);if(R+2<Rows)Link(I,I+Cols*2,2e-5f);
    }
    for(int Section=0;Section<Source->GetNumSections(0);Section++)
    {
        FCapeRenderSection S;UKismetProceduralMeshLibrary::GetSectionFromStaticMesh(Source,0,Section,S.Rest,S.Triangles,S.Normals,S.UV,S.Tangents);if(S.Rest.IsEmpty())continue;
        for(auto& P:S.Rest)P.Y=-P.Y;for(int I=0;I<S.Triangles.Num();I+=3)Swap(S.Triangles[I+1],S.Triangles[I+2]);
        for(const auto& P:S.Rest)
        {
            float T=FMath::Clamp((111-P.Z)/73,0.f,1.f),A=FMath::Atan2(P.Y,P.X+3*T);if(A<0)A+=2*PI;
            float X=FMath::Clamp((A-.66f)/(2*PI-1.32f),0.f,1.f)*(Cols-1),Y=T*(Rows-1);int C=FMath::Min(int(X),Cols-2),R=FMath::Min(int(Y),Rows-2);
            S.Bindings.Add({R*Cols+C,R*Cols+C+1,(R+1)*Cols+C,(R+1)*Cols+C+1,X-C,Y-R});
        }
        S.Vertices.SetNum(S.Rest.Num());S.Normals.SetNum(S.Rest.Num());Sections.Add(MoveTemp(S));SetMaterial(Sections.Num()-1,Source->GetMaterial(Section));
    }
    if(Sections.IsEmpty())return false;ResetCloth(Pose);Render(Pose,true);return true;
}
void UAttentionCape::ResetCloth(const FTransform& Pose)
{for(auto& P:Particles)P.Previous=P.P=Pose.TransformPosition(P.Rest);LastOrigin=Pose.GetLocation();PreviousPose=Pose;PreviousStep=1.f/120.f;LastRootVelocity=FVector::ZeroVector;}
void UAttentionCape::Simulate(const FTransform& Pose,float Dt,float FloorZ,FVector Thought,float ThoughtRadius)
{
    if(Particles.IsEmpty()||Dt<=0)return;Age+=Dt;
    if(FVector::DistSquared(LastOrigin,Pose.GetLocation())>FMath::Square(220.f)||Dt>.2f){ResetCloth(Pose);RecoveryCount++;}
    const FVector RootVelocity=(Pose.GetLocation()-LastOrigin)/FMath::Max(Dt,.001f);
    const FVector Inertia=(-(RootVelocity-LastRootVelocity)/FMath::Max(Dt,.001f)*.22f).GetClampedToMaxSize(1500);
    // Integrate cloth in a transported body frame. Translation and sharp turns
    // cannot rip the pinned row away before constraints solve. Relative wind
    // and acceleration still create physical lag, folding and follow-through.
    for(auto& P:Particles){P.P=Pose.TransformPosition(PreviousPose.InverseTransformPosition(P.P));P.Previous=Pose.TransformPosition(PreviousPose.InverseTransformPosition(P.Previous));}
    PreviousPose=Pose;LastRootVelocity=RootVelocity;
    LastOrigin=Pose.GetLocation();int Steps=FMath::Clamp(FMath::CeilToInt(Dt*120),1,5);float H=FMath::Min(Dt,.05f)/Steps;
    for(int Step=0;Step<Steps;Step++)
    {
        for(auto& P:Particles)
        {
            FVector Anchor=Pose.TransformPosition(P.Rest);if(P.InvMass==0){P.P=P.Previous=Anchor;continue;}
            // Verlet displacement belongs to the previous step duration. Reuse
            // its velocity, not its raw displacement, when frame time changes.
            FVector V=(P.P-P.Previous)*(H/FMath::Max(PreviousStep,.001f))*FMath::Exp(-2.8f*H);P.Previous=P.P;
            FVector Air=FVector(30+20*FMath::Sin(Age*1.7f+P.Rest.Y*.04f),18*FMath::Sin(Age*1.1f+P.Rest.Z*.025f),0)-RootVelocity.GetClampedToMaxSize(800)*1.7f+Inertia;
            P.P+=V+(FVector(0,0,-550)+Air+(Anchor-P.P)*2.3f)*H*H;
        }
        for(auto& L:Links)L.Lambda=0;
        for(int Iter=0;Iter<18;Iter++)
        {
            for(auto& L:Links)
            {
                auto& A=Particles[L.A];auto& B=Particles[L.B];FVector D=B.P-A.P;float Length=D.Size(),W=A.InvMass+B.InvMass;if(Length<.001f||W==0)continue;
                float Alpha=L.Compliance/(H*H),Delta=(-(Length-L.Length)-Alpha*L.Lambda)/(W+Alpha);L.Lambda+=Delta;FVector Correction=D*(Delta/Length);A.P-=Correction*A.InvMass;B.P+=Correction*B.InvMass;
            }
            for(auto& P:Particles)
            {
                if(P.InvMass==0){P.P=Pose.TransformPosition(P.Rest);continue;}
                const FVector Anchor=Pose.TransformPosition(P.Rest);const float Freedom=2+FMath::Clamp((111-P.Rest.Z)/73,0.f,1.f)*28;
                P.P=Anchor+(P.P-Anchor).GetClampedToMaxSize(Freedom);
                FVector Local=Pose.InverseTransformPosition(P.P);float Radius=FMath::Lerp(42.f,25.f,FMath::Clamp((Local.Z-40)/70,0.f,1.f));
                if(Local.Z>28&&Local.Z<117){float R=FMath::Sqrt(Local.X*Local.X+Local.Y*Local.Y);if(R<Radius&&R>.001){Local.X*=Radius/R;Local.Y*=Radius/R;P.P=Pose.TransformPosition(Local);}}
                P.P.Z=FMath::Max(P.P.Z,FloorZ+4);
                if(ThoughtRadius>0){FVector D=P.P-Thought;float Len=D.Size();if(Len<ThoughtRadius+3&&Len>.001f)P.P=Thought+D*((ThoughtRadius+3)/Len);}
            }
        }
        for(const auto& L:Links)if(L.Compliance<1e-6f)MaxStretch=FMath::Max(MaxStretch,float(FVector::Dist(Particles[L.A].P,Particles[L.B].P)/L.Length));
        PreviousStep=H;
    }
    for(const auto& P:Particles){if(P.P.ContainsNaN()){ResetCloth(Pose);RecoveryCount++;break;}MaxTravel=FMath::Max(MaxTravel,float(FVector::Dist(P.P,Pose.TransformPosition(P.Rest))));}
    Render(Pose,false);
}
void UAttentionCape::Render(const FTransform& Pose,bool Create)
{
    TArray<FVector> Displacement;Displacement.Reserve(Particles.Num());for(const auto& P:Particles)Displacement.Add(P.P-Pose.TransformPosition(P.Rest));
    for(int I=0;I<Sections.Num();I++)
    {
        auto& S=Sections[I];for(int J=0;J<S.Rest.Num();J++){auto& B=S.Bindings[J];FVector D=FMath::Lerp(FMath::Lerp(Displacement[B.A],Displacement[B.B],B.U),FMath::Lerp(Displacement[B.C],Displacement[B.D],B.U),B.V);S.Vertices[J]=Pose.TransformPosition(S.Rest[J])+D;S.Normals[J]=FVector::ZeroVector;}
        for(int J=0;J<S.Triangles.Num();J+=3){int A=S.Triangles[J],B=S.Triangles[J+1],C=S.Triangles[J+2];FVector N=FVector::CrossProduct(S.Vertices[B]-S.Vertices[A],S.Vertices[C]-S.Vertices[A]);S.Normals[A]+=N;S.Normals[B]+=N;S.Normals[C]+=N;}
        for(auto& N:S.Normals)N.Normalize();TArray<FLinearColor> Colors;
        if(Create)CreateMeshSection_LinearColor(I,S.Vertices,S.Triangles,S.Normals,S.UV,Colors,{},false);else UpdateMeshSection_LinearColor(I,S.Vertices,S.Normals,S.UV,Colors,{});
    }
}
