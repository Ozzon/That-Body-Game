#include "BodyGame.h"
#include "ProceduralMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/PostProcessVolume.h"
#include "Materials/MaterialInterface.h"
#include "UObject/ConstructorHelpers.h"

static TArray<FVector> Ellipse(FVector C,float X,float Y,float Z=0,int N=80)
{
    TArray<FVector> P;
    for(int i=0;i<N;i++){float a=2*PI*i/N;P.Add(C+FVector(X*FMath::Cos(a),Y*FMath::Sin(a),Z));}
    return P;
}

static TArray<FVector> OpenRim(FVector C,float X,float Y,float Gap=.36f)
{
    TArray<FVector> P;
    for(int i=0;i<=80;i++){float a=PI+Gap+(2*PI-2*Gap)*i/80;P.Add(C+FVector(X*FMath::Cos(a),Y*FMath::Sin(a),0));}
    return P;
}

void ABodyWorld::Path(const TArray<FVector>& P,float Width,int Mat)
{
    TArray<FVector> Curve;
    for(int i=0;i<P.Num()-1;i++)for(int k=0;k<8;k++)
    {float t=k/8.f;FVector a=P[FMath::Max(0,i-1)],b=P[i],c=P[i+1],d=P[FMath::Min(P.Num()-1,i+2)];Curve.Add(.5f*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));}
    Curve.Add(P.Last());
    TArray<FVector> V,N,L,R;TArray<int32>I;TArray<FVector2D>UV;
    for(int i=0;i<Curve.Num();i++)
    {
        FVector T=(Curve[FMath::Min(i+1,Curve.Num()-1)]-Curve[FMath::Max(i-1,0)]).GetSafeNormal();
        FVector Side=FVector::CrossProduct(T,FVector::UpVector).GetSafeNormal()*Width*.5;
        FVector A=Curve[i]+Side,B=Curve[i]-Side;A.Z=B.Z=49;
        V.Append({A,B});N.Append({FVector::UpVector,FVector::UpVector});UV.Append({FVector2D(0,i),FVector2D(1,i)});L.Add(A);R.Add(B);
        if(i<Curve.Num()-1){int j=i*2;I.Append({j,j+1,j+2,j+1,j+3,j+2});}
    }
    auto M=NewObject<UProceduralMeshComponent>(this);M->SetupAttachment(RootComponent);M->CreateMeshSection_LinearColor(0,V,I,N,UV,{}, {},false);M->SetMaterial(0,Mats[Mat]);M->RegisterComponent();
    Tube(L,3,8);Tube(R,3,8);
}

ABodyWorld::ABodyWorld()
{
    PrimaryActorTick.bCanEverTick=true;
    RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("LivingBody"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> S(TEXT("/Engine/BasicShapes/Sphere.Sphere"));Sphere=S.Object;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> C(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));Cylinder=C.Object;
    static ConstructorHelpers::FObjectFinder<UStaticMesh> B(TEXT("/Engine/BasicShapes/Cube.Cube"));Cube=B.Object;
}

UStaticMeshComponent* ABodyWorld::Shape(FVector P,FVector S,int Mat,USceneComponent* Parent,int Kind,FRotator R)
{
    auto M=NewObject<UStaticMeshComponent>(this);
    M->SetStaticMesh(Kind==1?Cylinder:Kind==2?Cube:Sphere);
    M->SetupAttachment(Parent?Parent:GetRootComponent());
    M->SetRelativeLocation(P);M->SetRelativeScale3D(S);M->SetRelativeRotation(R);
    M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    if(S.GetMax()<.8)M->SetCastShadow(false);
    M->SetMaterial(0,Mats.IsValidIndex(Mat)?Mats[Mat]:nullptr);
    M->RegisterComponent();
    return M;
}

UProceduralMeshComponent* ABodyWorld::Blob(FVector P,FVector S,int Mat,float Seed,float Detail,USceneComponent* Parent)
{
    TArray<FVector> V,N;TArray<int32> I;TArray<FVector2D> UV;
    const int Rows=24,Cols=48;
    for(int r=0;r<=Rows;r++)for(int c=0;c<=Cols;c++)
    {
        const float a=PI*r/Rows,b=2*PI*c/Cols;
        FVector D(FMath::Sin(a)*FMath::Cos(b),FMath::Sin(a)*FMath::Sin(b),FMath::Cos(a));
        float W=1+Detail*(FMath::Sin(b*3+Seed)*FMath::Sin(a*4+Seed)+.5f*FMath::Cos(b*5-a*3));
        V.Add(D*S*W);N.Add((D/S).GetSafeNormal());UV.Add(FVector2D(float(c)/Cols,float(r)/Rows));
        if(r<Rows&&c<Cols){int j=r*(Cols+1)+c;I.Append({j,j+1,j+Cols+1,j+1,j+Cols+2,j+Cols+1});}
    }
    auto M=NewObject<UProceduralMeshComponent>(this);
    M->SetupAttachment(Parent?Parent:GetRootComponent());M->SetRelativeLocation(P);
    M->CreateMeshSection_LinearColor(0,V,I,N,UV,{}, {},false);
    M->SetMaterial(0,Mats.IsValidIndex(Mat)?Mats[Mat]:nullptr);if(S.GetMax()<40)M->SetCastShadow(false);M->RegisterComponent();return M;
}

UProceduralMeshComponent* ABodyWorld::Tube(const TArray<FVector>& P,float Radius,int Mat,bool Closed)
{
    TArray<FVector> V,N;TArray<int32> I;TArray<FVector2D> UV;
    int Count=P.Num(),Sides=12;
    if(Count<2)return nullptr;
    for(int a=0;a<Count;a++)
    {
        FVector T=(P[(a+1)%Count]-P[(a+Count-1)%Count]).GetSafeNormal();
        if(!Closed&&a==0)T=(P[1]-P[0]).GetSafeNormal();
        if(!Closed&&a==Count-1)T=(P[a]-P[a-1]).GetSafeNormal();
        FVector U=FVector::CrossProduct(T,FVector::UpVector).GetSafeNormal();
        if(U.IsNearlyZero())U=FVector::RightVector;
        FVector B=FVector::CrossProduct(T,U).GetSafeNormal();
        for(int s=0;s<Sides;s++){float b=2*PI*s/Sides;FVector D=U*FMath::Cos(b)+B*FMath::Sin(b);V.Add(P[a]+Radius*D);N.Add(D);UV.Add(FVector2D(float(s)/Sides,float(a)/Count));}
    }
    for(int a=0;a<(Closed?Count:Count-1);a++)for(int s=0;s<Sides;s++)
    {int j=a*Sides+s,k=a*Sides+(s+1)%Sides,l=((a+1)%Count)*Sides+s,m=((a+1)%Count)*Sides+(s+1)%Sides;I.Append({j,l,k,k,l,m});}
    auto M=NewObject<UProceduralMeshComponent>(this);M->SetupAttachment(RootComponent);
    M->CreateMeshSection_LinearColor(0,V,I,N,UV,{}, {},false);M->SetMaterial(0,Mats.IsValidIndex(Mat)?Mats[Mat]:nullptr);M->RegisterComponent();return M;
}

void ABodyWorld::Label(FString T,FVector P,float Size,FColor Color)
{
    auto M=NewObject<UTextRenderComponent>(this);M->SetupAttachment(RootComponent);M->SetRelativeLocation(P);
    M->SetRelativeRotation(FRotator(58,180,0));M->SetText(FText::FromString(T));M->SetWorldSize(Size);M->SetTextRenderColor(Color);
    M->SetHorizontalAlignment(EHTA_Center);M->SetVerticalAlignment(EVRTA_TextCenter);M->RegisterComponent();
}

void ABodyWorld::MakeWorld()
{
    // Palette: tissue, inner tissue, peach, coral, teal, lilac, cream, navy,
    // gold, blood, sky, sage, plum, blue, warm stone, emissive aqua.
    const TCHAR* Names[]={TEXT("Tissue"),TEXT("Cavity"),TEXT("Peach"),TEXT("Coral"),TEXT("Teal"),TEXT("Lilac"),TEXT("Cream"),TEXT("Navy"),TEXT("Gold"),TEXT("Blood"),TEXT("Sky"),TEXT("Sage"),TEXT("Plum"),TEXT("Blue"),TEXT("Stone"),TEXT("Glow")};
    for(auto Name:Names)Mats.Add(LoadObject<UMaterialInterface>(nullptr,*FString::Printf(TEXT("/Game/Materials/M_%s.M_%s"),Name,Name)));
    Organs.SetNum(3);
    Organs[0].Name="LUNGS";Organs[0].Center=FVector(520,0,60);Organs[0].Station=FVector(-110,-500,60);Organs[0].Color=FLinearColor(.45,.9,.85);
    Organs[1].Name="HEART";Organs[1].Center=FVector(440,70,60);Organs[1].Station=FVector(80,130,60);Organs[1].Color=FLinearColor(1,.46,.39);
    Organs[2].Name="BRAIN";Organs[2].Center=FVector(2040,0,60);Organs[2].Station=FVector(1690,0,60);Organs[2].Color=FLinearColor(.77,.63,1);

    auto Light=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,3000),FRotator(-52,-38,0));
    Light->GetLightComponent()->SetIntensity(3.5);Light->SetLightColor(FLinearColor(1,.88,.74));
    auto Sky=GetWorld()->SpawnActor<ASkyLight>();Sky->GetLightComponent()->SetIntensity(.65);
    Sky->GetLightComponent()->SetLightColor(FLinearColor(.65,.76,1));Sky->GetLightComponent()->SetRealTimeCaptureEnabled(true);
    auto PP=GetWorld()->SpawnActor<APostProcessVolume>();PP->bUnbound=true;
    PP->Settings.bOverride_AutoExposureMethod=true;PP->Settings.AutoExposureMethod=EAutoExposureMethod::AEM_Manual;
    PP->Settings.bOverride_AutoExposureBias=true;PP->Settings.AutoExposureBias=0;
    PP->Settings.bOverride_AutoExposureApplyPhysicalCameraExposure=true;PP->Settings.AutoExposureApplyPhysicalCameraExposure=false;
    PP->Settings.bOverride_BloomIntensity=true;PP->Settings.BloomIntensity=.28;
    PP->Settings.bOverride_VignetteIntensity=true;PP->Settings.VignetteIntensity=.27;
    PP->Settings.bOverride_AmbientOcclusionIntensity=true;PP->Settings.AmbientOcclusionIntensity=.7f;
    PP->Settings.bOverride_AmbientOcclusionRadius=true;PP->Settings.AmbientOcclusionRadius=80;
    PP->Settings.bOverride_ColorSaturation=true;PP->Settings.ColorSaturation=FVector4(1.08,1.08,1.08,1);

    Shape(FVector(300,0,-190),FVector(240,240,1),7,nullptr,2);
    // Continuous full-body silhouette. Head, neck, shoulders, arms, pelvis, legs.
    TArray<FVector> Half={FVector(2880,0,-65),FVector(2800,460,-65),FVector(2550,680,-65),FVector(2140,720,-65),FVector(1810,590,-65),FVector(1580,290,-65),FVector(1350,290,-65),FVector(1240,840,-65),FVector(960,1250,-65),FVector(500,1390,-65),FVector(-200,1570,-65),FVector(-880,1630,-65),FVector(-1250,1470,-65),FVector(-1280,1310,-65),FVector(-850,1190,-65),FVector(-370,1150,-65),FVector(-980,1030,-65),FVector(-1420,930,-65),FVector(-1680,820,-65),FVector(-2250,790,-65),FVector(-2960,640,-65),FVector(-3200,340,-65),FVector(-3130,160,-65),FVector(-2320,220,-65),FVector(-1770,170,-65),FVector(-1600,0,-65)};
    TArray<FVector> Outline=Half;
    for(int i=Half.Num()-2;i>0;i--)Outline.Add(FVector(Half[i].X,-Half[i].Y,Half[i].Z));
    // Catmull-Rom smooths the organic outline, preserving the hand-shaped silhouette.
    TArray<FVector> Smooth;
    for(int i=0;i<Outline.Num();i++)for(int j=0;j<8;j++)
    {float t=j/8.f;FVector a=Outline[(i+Outline.Num()-1)%Outline.Num()],b=Outline[i],c=Outline[(i+1)%Outline.Num()],d=Outline[(i+2)%Outline.Num()];Smooth.Add(.5f*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t));}
    TArray<FVector> V={FVector(0,0,-65)},N={FVector::UpVector};TArray<int32> Ind;TArray<FVector2D> UV={FVector2D(.5,.5)};
    for(auto P:Smooth){V.Add(P);N.Add(FVector::UpVector);UV.Add(FVector2D(P.X/7000+.5,P.Y/4000+.5));}
    Boundary=Smooth;
    // Ear clipping preserves the concave gaps between arms, torso and legs.
    TArray<int32> Poly;for(int i=0;i<Smooth.Num();i++)Poly.Add(i+1);
    auto Cross=[](FVector A,FVector B,FVector C){return (B.X-A.X)*(C.Y-A.Y)-(B.Y-A.Y)*(C.X-A.X);};
    double SignedArea=0;for(int i=0;i<Smooth.Num();i++){auto A=Smooth[i],B=Smooth[(i+1)%Smooth.Num()];SignedArea+=A.X*B.Y-B.X*A.Y;}
    if(SignedArea<0)Algo::Reverse(Poly);
    int Guard=0;
    while(Poly.Num()>2&&Guard++<Smooth.Num()*3)
    {
        bool Found=false;
        for(int i=0;i<Poly.Num();i++)
        {
            int A=Poly[(i+Poly.Num()-1)%Poly.Num()],B=Poly[i],C=Poly[(i+1)%Poly.Num()];
            if(Cross(V[A],V[B],V[C])<=.001)continue;
            bool Inside=false;for(int D:Poly){if(D==A||D==B||D==C)continue;if(Cross(V[A],V[B],V[D])>=0&&Cross(V[B],V[C],V[D])>=0&&Cross(V[C],V[A],V[D])>=0){Inside=true;break;}}
            if(!Inside){Ind.Append({A,C,B});Poly.RemoveAt(i);Found=true;break;}
        }
        if(!Found)break;
    }
    auto Floor=NewObject<UProceduralMeshComponent>(this);Floor->SetupAttachment(RootComponent);Floor->CreateMeshSection_LinearColor(0,V,Ind,N,UV,{}, {},false);Floor->SetMaterial(0,Mats[1]);Floor->RegisterComponent();
    Tube(Smooth,70,0,true);for(auto& P:Smooth)P.Z+=24;Tube(Smooth,22,2,true);
    // Soft tissue lining, paired limb vessels, and spine.
    for(int Side:{-1,1})
    {
        Tube({FVector(1100,Side*970,0),FVector(650,Side*1200,-5),FVector(-250,Side*1420,-5),FVector(-1100,Side*1450,0)},23,9);
        Tube({FVector(1050,Side*1050,0),FVector(600,Side*1280,0),FVector(-200,Side*1510,0),FVector(-1000,Side*1540,0)},18,13);
        Tube({FVector(-1450,Side*340,0),FVector(-1950,Side*470,0),FVector(-2550,Side*440,0),FVector(-2960,Side*400,0)},25,9);
        Tube({FVector(-1450,Side*420,-10),FVector(-1950,Side*560,-10),FVector(-2550,Side*530,-10),FVector(-2960,Side*500,-10)},20,13);
    }
    for(int i=0;i<19;i++)Shape(FVector(-1420+i*140,0,-30),FVector(.75,1.6,.6),2);
    // Gold-edged pale circulation paths form the walkable connections.
    TArray<FVector> Main={FVector(-1480,0,5),FVector(-1000,-130,5),FVector(-500,-140,5),FVector(-100,-70,5),FVector(200,-170,5),FVector(700,-130,5),FVector(1250,0,5),FVector(1660,0,5),FVector(2050,0,5)};
    Path(Main,250);
    Path({FVector(-110,-80,5),FVector(-170,-350,5),FVector(-110,-500,5),FVector(180,-630,5),FVector(640,-700,5)},245);
    Path({FVector(-120,-50,5),FVector(-80,260,5),FVector(-70,560,5),FVector(300,730,5),FVector(900,700,5)},245);
    Path({FVector(1250,0,6),FVector(960,-390,6),FVector(700,-600,6)},220);
    Path({FVector(1250,0,6),FVector(960,390,6),FVector(850,670,6)},220);
    // Main red/blue channels retain their anatomical route alongside the footpath.
    Tube({FVector(-1400,180,25),FVector(-600,180,25),FVector(200,340,50),FVector(820,210,50),FVector(1450,130,30),FVector(1960,160,30)},20,9);
    Tube({FVector(-1400,-250,22),FVector(-600,-260,22),FVector(200,-330,40),FVector(820,-200,40),FVector(1450,-140,22),FVector(1960,-160,22)},19,13);
    MakeAbdomen();MakeLungs();MakeHeart();MakeBrain();
    // Neck: trachea with cartilage rings, esophagus, thyroid, thymus, shoulder muscle.
    Tube({FVector(1800,-55,25),FVector(1550,-55,25),FVector(1250,-55,25),FVector(1050,-55,25)},42,10);
    for(int i=0;i<8;i++)Tube(Ellipse(FVector(1260+i*55,-55,27),14,57),8,6,true);
    Tube({FVector(1800,135,0),FVector(1450,140,0),FVector(1000,180,0),FVector(50,750,0),FVector(-400,650,0)},22,2);
    Blob(FVector(1380,-160,50),FVector(84,60,43),11);Blob(FVector(1380,60,50),FVector(84,60,43),11);
    Blob(FVector(1120,20,50),FVector(100,90,40),2);
    Label("THYROID",FVector(1440,200,95),27,FColor(188,214,189));
    Label("THYMUS",FVector(1180,210,95),24,FColor(225,177,150));
    for(int side:{-1,1})for(int i=0;i<3;i++)Blob(FVector(1190-i*80,side*(700+i*130),10),FVector(90,180,65),0,float(i),.04);
    // A low, partial rib cutaway frames the chest without covering interaction routes.
    for(int s:{-1,1})for(int i=0;i<5;i++)
    {float x=200+i*180;Tube({FVector(x,s*1010,10),FVector(x+30,s*1100,70),FVector(x+85,s*1130,120),FVector(x+115,s*1080,155)},26,2);}
    for(int i=0;i<45;i++)FlowCells.Add(Shape(FlowPosition(i,0),FVector(.38,.38,.17),i%3==0?10:9));
    for(int i=0;i<32;i++)WindMotes.Add(Shape(FVector(600,0,120),FVector(.52,.10,.10),15));
    for(int i=0;i<24;i++)HeartCells.Add(Shape(FVector(460,100,120),FVector(.28,.32,.11),i%2?3:10));
    for(int i=0;i<12;i++)BrightMotes.Add(Shape(FVector(2110,0,130),FVector(.08),8));
    for(int i=0;i<3;i++)
    {
        auto P=Organs[i].Station;
        Shape(P-FVector(0,0,35),FVector(1.9,1.9,.15),7,nullptr,1)->ComponentTags.Add(TEXT("Interactive"));
        Tube(Ellipse(P-FVector(0,0,22),103,103),6,i==0?15:i==1?8:5,true)->ComponentTags.Add(TEXT("Interactive"));
        for(int j=0;j<4;j++)Shape(P+FVector(FMath::Cos(j*PI/2)*120,FMath::Sin(j*PI/2)*120,-16),FVector(.13,.13,.17),8);
    }
    Label("DIAPHRAGM",FVector(-300,-590,110),37,FColor(157,233,222));
    Label("PACING CHAMBER",FVector(-100,210,110),30,FColor(251,195,167));
    Label("AWARENESS",FVector(1580,0,110),34,FColor(218,192,255));
}

void ABodyWorld::MakeLungs()
{
    for(int S:{-1,1})
    {
        FVector C(600,S*710,-25);
        Blob(C,FVector(660,365,72),0,2,.045);
        // Open inner beds leave room to read the bronchi and walk through their branches.
        Blob(C+FVector(0,0,38),FVector(586,308,25),S<0?4:11,2,.06);
        TArray<FVector> LungRim;
        for(int j=0;j<=92;j++)
        {
            float a=PI+.42f+(2*PI-.84f)*j/92;
            float X=610*FMath::Cos(a),Y=FMath::Sin(a)*(325-85*FMath::Cos(a));
            // Rounded apex, broad basal surface, and a cardiac notch on the left.
            if(S>0&&Y<0)Y+=60*FMath::Exp(-FMath::Square((X+100)/240));
            LungRim.Add(C+FVector(X,Y,84));
        }
        auto Rim=Tube(LungRim,42,2);Organs[0].Animated.Add(Rim);
        for(int L=0;L<(S<0?2:1);L++)
        {
            float X=340+L*380;
            Tube({FVector(X-80,S*985,70),FVector(X+10,S*830,75),FVector(X+80,S*600,75),FVector(X+150,S*430,60)},14,0);
        }
        // Airway tree. Porcelain-blue branches terminate in clustered alveoli.
        Tube({FVector(1050,-55,80),FVector(900,S*280,110),FVector(710,S*500,100),FVector(420,S*650,100)},37,10);
        for(int b=0;b<6;b++)
        {
            FVector Q(160+b*166,S*(750+65*FMath::Sin(b*2.f)),105);
            FVector K(470+b*70,S*(560+b*12),105);
            Tube({K,(K+Q)*.5+FVector(35,0,12),Q},18,10);
            for(int cluster=0;cluster<3;cluster++)
            {
                FVector A=Q+FVector((cluster-1)*65,S*85,0);
                Tube({Q,A},11,6);
                for(int k=0;k<7;k++)
                {float a=k*2*PI/6;FVector Pos=A+FVector(FMath::Cos(a)*37,FMath::Sin(a)*33,k==6?50:12);auto B=Blob(Pos,FVector(29,29,34),b%2?5:2,b,.04);Organs[0].Animated.Add(B);}
            }
        }
        Label(S<0?"RIGHT LUNG":"LEFT LUNG",FVector(280,S*1120,150),49,FColor(241,221,207));
    }
    TArray<FVector> D;
    for(int i=0;i<=32;i++){float y=-1040+2080*i/32.f;D.Add(FVector(-140+125*FMath::Square(y/1040),y,20));}
    Diaphragm=Tube(D,36,3);
    Diaphragm->ComponentTags.Add(TEXT("Interactive"));
    Label("BREATHE",FVector(-180,-940,105),25,FColor(213,214,195));
}

void ABodyWorld::MakeHeart()
{
    FVector C(460,100,20);
    Blob(C,FVector(375,330,65),9,3,.11);
    Blob(C+FVector(-270,70,8),FVector(140,164,54),3,2,.08);
    // Four exposed chambers are differentiated by warm/cool blood and valve details.
    for(int x=0;x<2;x++)for(int y=0;y<2;y++)
    {
        FVector Q=C+FVector((x?1:-1)*155,(y?1:-1)*132,57);
        Blob(Q,FVector(x?142:158,122,17),y?9:13,x+y,.02);
        auto R=Tube(OpenRim(Q+FVector(0,0,15),x?147:163,125,.64),24,3);Organs[1].Animated.Add(R);
        // Tri-leaflet valve over a central blood pool.
        for(int k=0;k<3;k++){float a=k*2*PI/3;Blob(Q+FVector(FMath::Cos(a)*23,FMath::Sin(a)*23,21),FVector(29,22,9),6,k,.08);}
    }
    Tube({C+FVector(280,100,60),C+FVector(390,120,200),C+FVector(510,40,245),C+FVector(455,-65,210),C+FVector(360,-65,80)},43,3);
    for(int i=0;i<3;i++)Tube({C+FVector(430+i*35,10+i*40,235),C+FVector(490+i*40,10+i*40,325)},20,3);
    Tube({C+FVector(240,-170,55),C+FVector(300,-200,195),C+FVector(410,-340,160)},35,13);
    Tube({C+FVector(120,180,30),C+FVector(220,320,80),C+FVector(370,330,90)},27,9);
    // Coronary vessels and a heartbeat orbit.
    Tube({C+FVector(260,0,85),C+FVector(100,15,95),C+FVector(-40,35,90),C+FVector(-230,80,65)},9,8);
    Tube(Ellipse(C+FVector(0,0,50),392,346),5,8,true);
    Label("HEART",FVector(420,110,360),56,FColor(255,222,190));
    BpmLabel=NewObject<UTextRenderComponent>(this);BpmLabel->SetupAttachment(RootComponent);BpmLabel->SetRelativeLocation(FVector(270,100,295));
    BpmLabel->SetRelativeRotation(FRotator(58,180,0));BpmLabel->SetWorldSize(44);BpmLabel->SetHorizontalAlignment(EHTA_Center);BpmLabel->SetTextRenderColor(FColor(255,204,134));BpmLabel->RegisterComponent();
}

void ABodyWorld::MakeBrain()
{
    FVector C(2110,0,-18);
    Blob(C,FVector(630,570,75),5,4,.08);
    Blob(C+FVector(0,0,39),FVector(565,505,22),12,0,.025);
    Tube(OpenRim(C+FVector(0,0,91),596,534,.35),51,2);
    // Two continuous folded hemispheres frame the exposed awareness center.
    for(int s:{-1,1})for(int row=0;row<3;row++)
    {
        TArray<FVector> Fold;
        for(int j=0;j<=120;j++)
        {float t=j/120.f,x=1650+t*920;float y=295+row*53-135*FMath::Square(t*2-1)+27*FMath::Sin(t*PI*11+row*1.8f);Fold.Add(FVector(x,s*y,103+row*10+10*FMath::Sin(t*PI*7)));}
        Tube(Fold,22+row*2,2);
    }
    for(int s:{-1,1})for(int row=0;row<2;row++)
    {
        TArray<FVector> Fold;
        for(int j=0;j<=64;j++){float t=j/64.f;Fold.Add(FVector(2480+row*62+38*FMath::Sin(t*PI*7),s*(50+t*300),100+row*6+12*FMath::Sin(t*PI*6)));}
        Tube(Fold,25,2);
    }
    // Four thought groves are connected by flowing neural paths.
    for(int i=0;i<4;i++)
    {
        FVector Q=C+FVector((i<2?-1:1)*235,(i%2?-1:1)*235,58);
        Shape(Q,FVector(2.5,2.5,.19),i==0?4:i==1?12:i==2?11:13,nullptr,1);
        Tube(Ellipse(Q+FVector(0,0,17),132,132),9,5,true);
        Path({C+FVector(0,0,65),(C+Q)*.5+FVector(0,0,35),Q},150);
        Tube({C+FVector(0,0,86),(C+Q)*.5+FVector(0,0,55),Q+FVector(0,0,20)},4,15);
        for(int k=0;k<4;k++)
        {
            float a=k*2*PI/4;FVector B=Q+FVector(FMath::Cos(a)*95,FMath::Sin(a)*95,35);
            Tube({B,B+FVector(0,0,35)},7,8);
            for(int j=0;j<3;j++)Blob(B+FVector((j-1)*18,0,40+j*8),FVector(24,25,29),i%2?5:11,j,.1);
        }
        auto T=Blob(Q+FVector(0,0,120),FVector(49,49,43),3,i,.13);T->ComponentTags.Add(TEXT("Interactive"));Thoughts.Add(T);
    }
    Path({FVector(1500,0,35),FVector(1880,0,40),FVector(2110,0,45)},230);
    Awareness=Shape(C+FVector(0,0,76),FVector(1.8,1.8,.2),8,nullptr,1);
    Awareness->ComponentTags.Add(TEXT("Interactive"));
    Tube(Ellipse(C+FVector(0,0,102),145,145),9,8,true);
    // Luminous sprout as the awareness center's visual focus.
    Tube({C+FVector(0,0,80),C+FVector(0,0,145),C+FVector(12,0,215)},11,8);
    for(int s:{-1,1})Blob(C+FVector(0,s*32,175),FVector(22,52,14),11,s,.05);
    Blob(C+FVector(12,0,227),FVector(29,29,44),8,0,.06);
    Label("BRAIN",FVector(2660,0,200),58,FColor(239,218,243));
    Label("THOUGHT GARDEN",FVector(2480,0,150),27,FColor(212,197,223));
}

void ABodyWorld::MakeAbdomen()
{
    // Patient's right is screen-left; liver right, stomach/spleen left.
    Blob(FVector(-460,-610,45),FVector(320,405,109),9,1,.10);
    Blob(FVector(-370,-260,37),FVector(200,260,72),9,4,.1);
    Tube({FVector(-370,-940,97),FVector(-550,-680,138),FVector(-650,-420,98)},11,0);
    Label("LIVER",FVector(-770,-650,160),42,FColor(233,179,151));
    Blob(FVector(-620,-410,38),FVector(73,45,55),11,3,.18);
    Label("GALLBLADDER",FVector(-740,-270,75),21,FColor(195,211,169));
    Blob(FVector(-370,695,60),FVector(226,186,127),2,3,.035);
    Blob(FVector(-545,625,60),FVector(156,184,108),2,0,.035);
    Blob(FVector(-570,495,60),FVector(105,139,82),2,0,.02);
    Tube({FVector(-510,440,65),FVector(-700,350,35),FVector(-770,450,35)},42,2);
    Label("STOMACH",FVector(-740,700,180),39,FColor(242,206,163));
    Blob(FVector(-340,960,25),FVector(157,70,68),12,1,.13);
    Label("SPLEEN",FVector(-470,1080,100),23,FColor(212,183,229));
    Blob(FVector(-700,210,12),FVector(70,260,52),8,1,.15);
    Label("PANCREAS",FVector(-820,160,92),22,FColor(236,214,160));
    for(int s:{-1,1})
    {
        Blob(FVector(-1000,s*858,13),FVector(183,100,76),12,s,.065);
        Tube({FVector(-970,s*765,45),FVector(-1100,s*690,20),FVector(-1380,s*310,20),FVector(-1500,0,20)},12,8);
        Blob(FVector(-790,s*870,32),FVector(73,96,49),8,s,.2);
        Label("ADRENAL",FVector(-790,s*1060,90),22,FColor(235,213,133));
        Label("KIDNEY",FVector(-1150,s*1000,110),27,FColor(209,180,226));
    }
    // Coiled small intestine surrounded by segmented large intestine.
    Blob(FVector(-1110,0,-28),FVector(360,575,37),0,0,.05);
    TArray<FVector> Gut;
    for(int i=0;i<=170;i++)
    {float t=i/170.f;float a=t*PI*11;Gut.Add(FVector(-910-t*435+43*FMath::Sin(a*.5),FMath::Sin(a)*(420-80*t),24+15*FMath::Cos(a*2)));}
    Tube(Gut,35,2);
    TArray<FVector> Colon={FVector(-1420,-560,20),FVector(-1160,-620,25),FVector(-840,-580,30),FVector(-800,0,35),FVector(-850,540,30),FVector(-1120,610,25),FVector(-1400,520,20),FVector(-1490,180,10)};
    Tube(Colon,64,11);
    for(int j=0;j<Colon.Num()-1;j++)for(int k=0;k<5;k++)
    {FVector P=FMath::Lerp(Colon[j],Colon[j+1],k/5.f);Blob(P,FVector(69,72,63),11,k,.07);}
    Label("INTESTINES",FVector(-1260,0,150),37,FColor(241,214,169));
    Blob(FVector(-1550,0,26),FVector(119,146,64),10,0,.08);
    Label("BLADDER",FVector(-1690,0,100),27,FColor(186,219,217));
}
