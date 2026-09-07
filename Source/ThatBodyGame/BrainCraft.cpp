#include "BrainCraft.h"
#include "Animation/BWGait.h"
#include "Animation/AttentionCape.h"
#include "BrainCraftLayout.inl"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/PointLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Engine/PointLight.h"
#include "Engine/PostProcessVolume.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/TextureCube.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/GameViewportClient.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Materials/Material.h"
#include "MaterialShared.h"
#include "PhysicsEngine/PhysicsHandleComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundWave.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/FileHelper.h"
#if WITH_EDITOR
#include "AssetCompilingManager.h"
#include "ShaderCompiler.h"
#endif

static const FVector TreeCare(0,-365,520),Lotus(1580,-1390,330),ReleasePool(2070,-1150,330),Entry(-1810,-2470,140);
static float CraftGround(UWorld* World,FVector P)
{FHitResult Hit;return World->LineTraceSingleByChannel(Hit,FVector(P.X,P.Y,5000),FVector(P.X,P.Y,-600),ECC_GameTraceChannel1)?Hit.ImpactPoint.Z:P.Z;}
static UStaticMesh* CraftMesh(const FString& Key){return LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/BrainCraft/Models/SM_Craft_%s.SM_Craft_%s"),*Key,*Key));}
static UMaterialInterface* CraftMaterial(const FString& Key){return LoadObject<UMaterialInterface>(nullptr,*FString::Printf(TEXT("/Game/BrainCraft/Materials/M_Craft_%s.M_Craft_%s"),*Key,*Key));}

ABrainCraftGameMode::ABrainCraftGameMode(){DefaultPawnClass=AAttentionCharacter::StaticClass();HUDClass=ABrainCraftHUD::StaticClass();}

UAttentionPresentation::UAttentionPresentation()
{PrimaryComponentTick.bCanEverTick=true;PrimaryComponentTick.TickGroup=TG_PostPhysics;}
void UAttentionPresentation::TickComponent(float Dt,ELevelTick TickType,FActorComponentTickFunction* TickFunction)
{
    Super::TickComponent(Dt,TickType,TickFunction);
    auto Owner=Cast<AAttentionCharacter>(GetOwner());
    if(Owner&&!Owner->Paused&&Owner->Parts.Num()>=8){Owner->UpdateAnimation(Dt,Owner->PoseMove);Owner->UpdateEffects(Dt);}
}

ACraftThought::ACraftThought()
{
    PrimaryActorTick.bCanEverTick=true;
    Physics=CreateDefaultSubobject<USphereComponent>(TEXT("Physical thought"));SetRootComponent(Physics);Physics->SetSphereRadius(45);Physics->SetCollisionProfileName(TEXT("PhysicsActor"));Physics->SetCollisionResponseToChannel(ECC_Visibility,ECR_Ignore);Physics->SetSimulatePhysics(true);Physics->SetNotifyRigidBodyCollision(true);Physics->BodyInstance.bUseCCD=true;
    Appearance=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Sculpted thought"));Appearance->SetupAttachment(Physics);Appearance->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Face=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Thought expression"));Face->SetupAttachment(Appearance);Face->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    Physics->SetCollisionResponseToChannel(ECC_GameTraceChannel1,ECR_Ignore);Physics->OnComponentHit.AddDynamic(this,&ACraftThought::OnHit);
}
void ACraftThought::Configure(int32 Type,FVector Origin)
{
    Kind=Type;Home=Origin;SetActorLocation(Origin);const TCHAR* Keys[]={TEXT("ThoughtStar"),TEXT("ThoughtCloud"),TEXT("ThoughtWisp"),TEXT("ThoughtKnot")};const TCHAR* Faces[]={TEXT("ThoughtFaceBright"),TEXT("ThoughtFaceCloud"),TEXT("ThoughtFaceWisp"),TEXT("ThoughtFaceKnot")};
    CastBaseline=FParse::Param(FCommandLine::Get(),TEXT("CraftCastBaseline"));
    const TCHAR* NewFaces[]={TEXT("C16FaceBright"),TEXT("C16FaceCloud"),TEXT("C16FaceWisp"),TEXT("C16FaceKnot")};
    Appearance->SetStaticMesh(CraftMesh(CastBaseline?FString(Keys[Kind]):FString(TEXT("C16"))+Keys[Kind]));Face->SetStaticMesh(CraftMesh(CastBaseline?Faces[Kind]:NewFaces[Kind]));Face->SetVisibility(true);
    if(!CastBaseline&&Kind<3)
    {
        const TCHAR* EyeKeys[]={TEXT("C16EyeBright"),TEXT("C16EyeCloud"),TEXT("C16EyeWisp")};
        const FVector Anchors[3][2]={{FVector(24.18,-13,3),FVector(24.18,13,3)},{FVector(38.12,-19,1),FVector(39.63,19,1)},{FVector(16.83,-9,1),FVector(17.99,9,1)}};
        for(int Side=0;Side<2;Side++){auto Eye=NewObject<UStaticMeshComponent>(this);Eye->SetupAttachment(Appearance);Eye->SetStaticMesh(CraftMesh(EyeKeys[Kind]));Eye->SetRelativeLocation(Anchors[Kind][Side]);Eye->SetRelativeScale3D(FVector(1,Side?1:-1,1));Eye->SetCollisionEnabled(ECollisionEnabled::NoCollision);Eye->RegisterComponent();Eyes.Add(Eye);}
    }
    if(!CastBaseline&&Kind==2)for(int I=0;I<3;I++){auto Thread=NewObject<UStaticMeshComponent>(this);Thread->SetupAttachment(Appearance);Thread->SetStaticMesh(CraftMesh(FString::Printf(TEXT("C16WispThread%d"),I)));Thread->SetCollisionEnabled(ECollisionEnabled::NoCollision);Thread->SetCastShadow(false);Thread->RegisterComponent();Threads.Add(Thread);}
    Physics->SetSphereRadius(Kind==1?62:Kind==2?30:44);Physics->SetMassOverrideInKg(NAME_None,Kind==1?18:Kind==2?.7f:Kind==3?7:2,true);Physics->SetLinearDamping(Kind==1?2.5f:1.4f);Physics->SetAngularDamping(8);Tags.Add(TEXT("Interactive"));
    GlowMaterial=Appearance->CreateDynamicMaterialInstance(0);
}
void ACraftThought::OnHit(UPrimitiveComponent*,AActor*,UPrimitiveComponent*,FVector Impulse,const FHitResult&)
{Reaction=FMath::Clamp(float(Impulse.Size()/1200),.08f,.38f);}
void ACraftThought::ResolveTo(FVector Target)
{ResolveStart=GetActorLocation();ResolveTarget=Target;HasResolveTarget=true;Resolved=true;Held=false;Physics->SetSimulatePhysics(false);Physics->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
void ACraftThought::Tick(float Dt)
{
    Super::Tick(Dt);Age+=Dt;BirthAge+=Dt;Reaction=FMath::FInterpTo(Reaction,0,Dt,6);if(GlowMaterial)GlowMaterial->SetScalarParameterValue(TEXT("LifeGlow"),(Kind==0?1.2f:Kind==2?.75f:.1f)*(1+.16f*FMath::Sin(Age*2.6f)));
    if(Resolved&&ReturnIn>=0)
    {
        ReturnIn-=Dt;
        if(ReturnIn<=0){ReturnIn=-1;Resolved=HasResolveTarget=false;Pushes=0;Disappear=BirthAge=0;SetActorLocation(Home);SetActorHiddenInGame(false);Appearance->SetRelativeScale3D(FVector(.01));Physics->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);Physics->SetSimulatePhysics(true);Physics->SetPhysicsLinearVelocity(FVector::ZeroVector);UE_LOG(LogTemp,Display,TEXT("CRAFT_PERSISTENT_RETURNED"));}
    }
    if(Resolved){Disappear+=Dt;float T=FMath::Clamp(Disappear/1.0f,0.f,1.f);if(HasResolveTarget){float Ease=T*T*(3-2*T);SetActorLocation(FMath::Lerp(ResolveStart,ResolveTarget,Ease)+FVector(0,0,FMath::Sin(T*PI)*90));}Appearance->SetRelativeScale3D(FVector(FMath::Max(.001f,1-T*T)));if(T>=1){SetActorHiddenInGame(true);Physics->SetSimulatePhysics(false);Physics->SetCollisionEnabled(ECollisionEnabled::NoCollision);}return;}
    auto PC=GetWorld()->GetFirstPlayerController();auto Player=PC?Cast<AAttentionCharacter>(PC->GetPawn()):nullptr;
    const FVector P=GetActorLocation();FHitResult Hit;FCollisionQueryParams Params;Params.AddIgnoredActor(this);if(Player)Params.AddIgnoredActor(Player);
    if(!Held&&GetWorld()->LineTraceSingleByChannel(Hit,P+FVector(0,0,180),P-FVector(0,0,1600),ECC_GameTraceChannel1,Params))
    {
        const float Radius=Physics->GetScaledSphereRadius();float Target=Hit.ImpactPoint.Z+Radius+(Kind==1?8:Kind==2?55:35)+FMath::Sin(Age*(Kind==1?1.7f:2.7f))*8;
        const FVector V=Physics->GetPhysicsLinearVelocity();float Acc=980+FMath::Clamp((Target-P.Z)*65-V.Z*13,-1600.f,2000.f);Physics->AddForce(FVector(0,0,Acc*Physics->GetMass()));
        FVector ToHome=(Home-P);ToHome.Z=0;float Speed=Player&&Player->Focused?16:Kind==1?13:Kind==2?63:28;
        FVector Drift=ToHome.GetClampedToMaxSize(220)*1.1+FVector(FMath::Sin(Age*.7),FMath::Cos(Age*.6),0)*Speed*.65f;
        // Keep the live current within its designed handling court. A soft
        // physical return prevents a light thought drifting behind its portal.
        if(ToHome.Size2D()>90)Drift+=ToHome.GetSafeNormal2D()*(ToHome.Size2D()-90)*4;
        if(Kind==3&&Pushes>0)Drift*=.4;
        Physics->AddForce((Drift-FVector(V.X,V.Y,0))*Physics->GetMass()*1.4);
    }
    if(P.Z<-550){Physics->SetPhysicsLinearVelocity(FVector::ZeroVector);SetActorLocation(Home,false,nullptr,ETeleportType::TeleportPhysics);}
    const float Proximity=Player?1-FMath::Clamp((FVector::Dist2D(P,Player->GetActorLocation())-130)/420,0.f,1.f):0;
    AttentionBlend=FMath::FInterpTo(AttentionBlend,Held?1.f:Proximity,Dt,4);
    // A modest upward presentation keeps faces readable in the isometric view.
    // Gaze follows attention locally; the creature remains a shaded 3D volume.
    VisualPitch=FMath::FInterpTo(VisualPitch,Player?FMath::Clamp(Player->CamPitch*.62f,12.f,34.f):24.f,Dt,5);
    FRotator R(CastBaseline?0:VisualPitch,Player?Player->CamYaw+180:250,0);
    const FVector V=Physics->GetPhysicsLinearVelocity();
    R.Roll=FMath::Sin(Age*(Kind==1?1.2f:2.2f))*(Kind==1?3:6);
    if(!CastBaseline){R.Roll*=1-AttentionBlend*.5f;R.Pitch+=FMath::Clamp(-V.Z*.025f,-4.f,4.f);if(Kind==3)R.Roll+=Pushes*12+Reaction*35;}
    Appearance->SetWorldRotation(FMath::RInterpTo(Appearance->GetComponentRotation(),R,Dt,5));float Breathe=FMath::Sin(Age*(Kind==1?1.4f:2.4f))*.018f;Appearance->SetRelativeScale3D(FVector(1+Reaction*.3+Breathe,1+Reaction+Breathe,1-Reaction*.7-Breathe*.6));
    float Birth=FMath::Clamp(BirthAge/.85f,0.f,1.f);Birth=Birth*Birth*(3-2*Birth);Appearance->SetRelativeScale3D(Appearance->GetRelativeScale3D()*FMath::Max(.001f,Birth));
    const float Blink=FMath::Fmod(Age+Kind*.63f,4.4f);float Lid=1-.92f*FMath::Sin(FMath::Clamp(Blink/.18f,0.f,1.f)*PI);
    if(CastBaseline)Face->SetRelativeScale3D(FVector(1,1,Lid));
    else
    {
        Expression=FMath::FInterpTo(Expression,Kind==1?(Held?.75f:Player&&Player->Focused?1.2f:1.f):1+AttentionBlend*.12f,Dt,5);
        for(int Side=0;Side<Eyes.Num();Side++){Eyes[Side]->SetRelativeScale3D(FVector(1,Side?1:-1,FMath::Max(.06f,Lid*Expression)));Eyes[Side]->SetRelativeRotation(FRotator(0,0,Kind==1?(Side?1:-1)*AttentionBlend*7:0));}
        for(int I=0;I<Threads.Num();I++){float Calm=Player&&Player->Focused?.35f:1.f;Threads[I]->SetRelativeRotation(FRotator(FMath::Sin(Age*1.3f+I)*9*Calm,0,FMath::Sin(Age*(1.5f+I*.3f)+I)*16*Calm));Threads[I]->SetRelativeScale3D(FVector(1+Reaction*.8f));}
        if(Kind==3)Face->SetRelativeScale3D(FVector(1+.08f*FMath::Sin(Age*3)+Reaction));
    }
}

AAttentionCharacter::AAttentionCharacter()
{
    PrimaryActorTick.bCanEverTick=true;PrimaryActorTick.bTickEvenWhenPaused=true;AutoPossessPlayer=EAutoReceiveInput::Player0;bUseControllerRotationYaw=false;
    GetCapsuleComponent()->InitCapsuleSize(34,92);GetCharacterMovement()->MaxWalkSpeed=560;GetCharacterMovement()->MaxStepHeight=45;GetCharacterMovement()->SetWalkableFloorAngle(48);GetCharacterMovement()->BrakingDecelerationWalking=1600;GetCharacterMovement()->MaxAcceleration=1600;GetCharacterMovement()->JumpZVelocity=410;GetCharacterMovement()->AirControl=.3;GetCharacterMovement()->bEnablePhysicsInteraction=false;GetCharacterMovement()->bOrientRotationToMovement=false;
    Puppet=CreateDefaultSubobject<USceneComponent>(TEXT("Attention animation rig"));Puppet->SetupAttachment(GetRootComponent());Puppet->SetRelativeLocation(FVector(0,0,-92));
    Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("Adventure camera"));Camera->SetupAttachment(GetRootComponent());Camera->SetAbsolute(true,true,true);Camera->ProjectionMode=ECameraProjectionMode::Orthographic;Camera->OrthoWidth=2900;Camera->bAutoCalculateOrthoPlanes=false;Camera->bUpdateOrthoPlanes=false;Camera->OrthoNearClipPlane=50;Camera->OrthoFarClipPlane=30000;Camera->bOverrideAspectRatioAxisConstraint=true;Camera->SetAspectRatioAxisConstraint(AspectRatio_MaintainXFOV);
    Hands=CreateDefaultSubobject<UPhysicsHandleComponent>(TEXT("Gentle physical hands"));Hands->SetLinearStiffness(1800);Hands->SetLinearDamping(120);Hands->SetAngularStiffness(500);Hands->SetAngularDamping(80);Hands->SetInterpolationSpeed(10);
    Presentation=CreateDefaultSubobject<UAttentionPresentation>(TEXT("Contact pose after physics"));
    GoldFX=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Warm thought sparks"));GoldFX->SetupAttachment(GetRootComponent());GoldFX->SetAbsolute(true,true,true);GoldFX->SetCollisionEnabled(ECollisionEnabled::NoCollision);GoldFX->SetCastShadow(false);
    VioletFX=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Neural current motes"));VioletFX->SetupAttachment(GetRootComponent());VioletFX->SetAbsolute(true,true,true);VioletFX->SetCollisionEnabled(ECollisionEnabled::NoCollision);VioletFX->SetCastShadow(false);
    RippleFX=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Garden water ripples"));RippleFX->SetupAttachment(GetRootComponent());RippleFX->SetAbsolute(true,true,true);RippleFX->SetCollisionEnabled(ECollisionEnabled::NoCollision);RippleFX->SetCastShadow(false);
    PetalFX=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Drifting garden petals"));PetalFX->SetupAttachment(GetRootComponent());PetalFX->SetAbsolute(true,true,true);PetalFX->SetCollisionEnabled(ECollisionEnabled::NoCollision);PetalFX->SetCastShadow(false);
}
UStaticMeshComponent* AAttentionCharacter::MeshPart(const FString& Key,USceneComponent* Parent,FVector P)
{
    auto M=NewObject<UStaticMeshComponent>(this);M->SetupAttachment(Parent);M->SetStaticMesh(CraftMesh(Key));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);M->SetRelativeLocation(P);M->SetRelativeScale3D(FVector(1,-1,1));M->RegisterComponent();return M;
}
void AAttentionCharacter::BeginPlay()
{
    Super::BeginPlay();GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_GameTraceChannel1,ECR_Ignore);SetActorLocation(Entry+FVector(0,0,110));LastSafe=GetActorLocation();CameraFocus=GetActorLocation();
    Capture=FParse::Param(FCommandLine::Get(),TEXT("CraftCapture"));Film=FParse::Param(FCommandLine::Get(),TEXT("CraftFilm"));Smoke=FParse::Param(FCommandLine::Get(),TEXT("CraftSmoke"))||Film;
    ControlsReview=FParse::Param(FCommandLine::Get(),TEXT("CraftControls"));
    RoamReview=FParse::Param(FCommandLine::Get(),TEXT("CraftRoam"));
    LegacyGrip=FParse::Param(FCommandLine::Get(),TEXT("CraftGripBaseline"));Hands->bInterpolateTarget=LegacyGrip;
    Hands->AddTickPrerequisiteActor(this);
    auto PC=Cast<APlayerController>(GetController());if(PC){PC->bShowMouseCursor=true;PC->SetInputMode(FInputModeGameAndUI());}
    // Deliberate pivots preserve head volume and cloth attachment through each action.
    const TCHAR* Keys[]={TEXT("AttentionBody"),TEXT("AttentionHead"),TEXT("AttentionEyes"),TEXT("AttentionCape"),TEXT("AttentionArmL"),TEXT("AttentionArmR"),TEXT("AttentionBootL"),TEXT("AttentionBootR")};
    const FVector Pivots[]={FVector(0,0,0),FVector(0,0,135),FVector(0,0,135),FVector(0,0,108),FVector(0,-37,103),FVector(0,37,103),FVector(0,-17,13),FVector(0,17,13)};
    for(int32 i=0;i<8;i++){auto Pivot=NewObject<USceneComponent>(this);Pivot->SetupAttachment(Puppet);Pivot->SetRelativeLocation(Pivots[i]);Pivot->RegisterComponent();MeshPart(Keys[i],Pivot,i<4?-Pivots[i]:FVector::ZeroVector);Parts.Add(Pivot);}
    for(int32 Side=0;Side<2;Side++)
    {
        auto F=NewObject<USceneComponent>(this);F->SetupAttachment(Puppet);F->SetAbsolute(true,true,true);F->RegisterComponent();MeshPart(Side?TEXT("AttentionForearmR"):TEXT("AttentionForearmL"),F);Forearms.Add(F);
        auto H=NewObject<USceneComponent>(this);H->SetupAttachment(Puppet);H->SetAbsolute(true,true,true);H->RegisterComponent();MeshPart(Side?TEXT("AttentionHandR"):TEXT("AttentionHandL"),H);Mittens.Add(H);
        auto Thigh=NewObject<USceneComponent>(this);Thigh->SetupAttachment(Puppet);Thigh->SetAbsolute(true,true,true);Thigh->RegisterComponent();MeshPart(Side?TEXT("AttentionThighR"):TEXT("AttentionThighL"),Thigh);Legs.Add(Thigh);
        auto Shin=NewObject<USceneComponent>(this);Shin->SetupAttachment(Puppet);Shin->SetAbsolute(true,true,true);Shin->RegisterComponent();MeshPart(Side?TEXT("AttentionShinR"):TEXT("AttentionShinL"),Shin);Shins.Add(Shin);
    }
    for(int32 i=0;i<9;i++)
    {auto Pivot=NewObject<USceneComponent>(this);Pivot->SetupAttachment(GetRootComponent());Pivot->SetAbsolute(true,true,true);Pivot->SetWorldLocation(Lotus+FVector(0,0,85));Pivot->RegisterComponent();MeshPart(FString::Printf(TEXT("LotusPetal%d"),i),Pivot);Petals.Add(Pivot);}
    for(TActorIterator<AStaticMeshActor> It(GetWorld());It;++It)
    {
        auto A=*It;auto M=A->GetStaticMeshComponent();
        FString HideKeys;if(FParse::Value(FCommandLine::Get(),TEXT("CraftHide="),HideKeys))for(const auto& Tag:A->Tags)if(HideKeys.Contains(Tag.ToString())&&Tag!=TEXT("BrainCraft"))M->SetVisibility(false);
        M->SetCollisionResponseToChannel(ECC_GameTraceChannel1,A->Tags.Contains(TEXT("Ground"))?ECR_Block:ECR_Ignore);
        if(A->Tags.Contains(TEXT("Foliage"))){M->SetCastShadow(A->Tags.Contains(TEXT("Canopy")));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
        if(A->Tags.Contains(TEXT("GroundCover"))){M->SetCastShadow(false);M->SetCollisionEnabled(ECollisionEnabled::NoCollision);for(int32 i=0;i<M->GetNumMaterials();i++)GroundCoverMaterials.Add(M->CreateDynamicMaterialInstance(i));}
        if(A->Tags.Contains(TEXT("Shortcut"))){M->SetVisibility(false);M->SetCollisionEnabled(ECollisionEnabled::NoCollision);Shortcut.Add(M);}
        if(A->Tags.Contains(TEXT("Occluder"))&&!A->Tags.Contains(TEXT("Interactive"))){FCraftFade F;F.Mesh=M;for(int32 i=0;i<M->GetNumMaterials();i++)F.Materials.Add(M->CreateDynamicMaterialInstance(i));Fades.Add(F);}
        if(A->Tags.Contains(TEXT("TreeLight")))for(int32 i=0;i<M->GetNumMaterials();i++)TreeLight.Add(M->CreateDynamicMaterialInstance(i));
    }
    UStaticMesh* Spark=LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Sphere.Sphere"));GoldFX->SetStaticMesh(Spark);VioletFX->SetStaticMesh(Spark);GoldFX->SetMaterial(0,CraftMaterial(TEXT("Light")));VioletFX->SetMaterial(0,CraftMaterial(TEXT("Current")));
    RippleFX->SetStaticMesh(CraftMesh(TEXT("FXRipple")));PetalFX->SetStaticMesh(CraftMesh(TEXT("FXPetal")));
    ResetMorning();
    Puppet->SetRelativeLocation(FVector(0,0,-92));ClothCape=NewObject<UAttentionCape>(this,TEXT("Simulated tailored cape"));ClothCape->SetupAttachment(GetRootComponent());ClothCape->SetAbsolute(true,true,true);ClothCape->RegisterComponent();ClothCape->SetWorldTransform(FTransform::Identity);
    if(!FParse::Param(FCommandLine::Get(),TEXT("CraftStaticCape"))&&ClothCape->Bind(CraftMesh(TEXT("AttentionCape")),Puppet->GetComponentTransform())){Parts[3]->SetVisibility(false,true);UE_LOG(LogTemp,Display,TEXT("CRAFT_CLOTH_READY: authored cape and embroidery bound to physical cloth"));}
    else UE_LOG(LogTemp,Warning,TEXT("CRAFT_CLOTH_MISSING_CPU_MESH"));
    const bool LightingBaseline=FParse::Param(FCommandLine::Get(),TEXT("CraftLightingBaseline"));
    const bool C16Lighting=FParse::Param(FCommandLine::Get(),TEXT("CraftC16Lighting"));
    auto Key=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,5000),FRotator(-35,-38,0));Key->GetLightComponent()->SetIntensity(LightingBaseline?3.8f:C16Lighting?3.2f:2.7f);Key->SetLightColor(FLinearColor(1,.87,.69));auto Sun=Cast<UDirectionalLightComponent>(Key->GetLightComponent());Sun->LightSourceAngle=LightingBaseline?3.6f:5.5f;Sun->DynamicShadowDistanceMovableLight=18000;Sun->ContactShadowLengthInWS=true;Sun->ContactShadowLength=LightingBaseline?45.f:20.f;
    auto Fill=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,4800),FRotator(-28,145,0));Fill->GetLightComponent()->SetIntensity(LightingBaseline?.10f:C16Lighting?.68f:.28f);Fill->SetLightColor(FLinearColor(.55,.69,1));Fill->GetLightComponent()->SetCastShadows(false);
    auto Sky=GetWorld()->SpawnActor<ASkyLight>();auto SL=Sky->GetLightComponent();UE_LOG(LogTemp,Display,TEXT("CRAFT_LIGHTING_MOBILITY sky_before=%d key_before=%d"),int(SL->Mobility),int(Sun->Mobility));SL->SetMobility(EComponentMobility::Movable);Sun->SetMobility(EComponentMobility::Movable);Fill->GetLightComponent()->SetMobility(EComponentMobility::Movable);
    SL->SourceType=ESkyLightSourceType::SLS_SpecifiedCubemap;SL->Cubemap=LoadObject<UTextureCube>(nullptr,TEXT("/Engine/MapTemplates/Sky/DaylightAmbientCubemap.DaylightAmbientCubemap"));SL->SetLightColor(FLinearColor(.64,.79,1));SL->SetIntensity(LightingBaseline?.60f:C16Lighting?1.35f:1.05f);if(!LightingBaseline)SL->SetLowerHemisphereColor(FLinearColor(.055,.072,.065));SL->RecaptureSky();UE_LOG(LogTemp,Display,TEXT("CRAFT_SKYLIGHT_CUBEMAP %s"),*GetNameSafe(SL->Cubemap));
    const FVector LightP[]={C16Lighting?FVector(0,90,1250):FVector(0,-610,970),FVector(-1600,1430,1490),FVector(1700,1600,1260),Lotus+FVector(0,0,280)};
    const FLinearColor LightC[]={FLinearColor(1,.52,.10),FLinearColor(.13,.72,1),FLinearColor(.48,.17,1),FLinearColor(.20,.65,1)};
    for(int32 i=0;i<4;i++){auto A=GetWorld()->SpawnActor<APointLight>(LightP[i],FRotator::ZeroRotator);auto L=A->PointLightComponent;L->SetMobility(EComponentMobility::Movable);if(i==0&&!C16Lighting)L->SetIntensityUnits(ELightUnits::Lumens);L->SetIntensity(i==0?(C16Lighting?18000:2000):28000);L->SetLightColor(LightC[i]);L->SetAttenuationRadius(i==0?1800:950);L->SetSourceRadius(i==0?180:110);L->SetCastShadows(true);}
    auto PP=GetWorld()->SpawnActor<APostProcessVolume>();PP->bUnbound=true;auto& S=PP->Settings;
    S.bOverride_AutoExposureMethod=true;S.AutoExposureMethod=AEM_Manual;S.bOverride_AutoExposureApplyPhysicalCameraExposure=true;S.AutoExposureApplyPhysicalCameraExposure=false;S.bOverride_AutoExposureBias=true;S.AutoExposureBias=.1;
    S.bOverride_BloomIntensity=true;S.BloomIntensity=.23;S.bOverride_VignetteIntensity=true;S.VignetteIntensity=.18;S.bOverride_MotionBlurAmount=true;S.MotionBlurAmount=0;S.bOverride_ColorSaturation=true;S.ColorSaturation=FVector4(1.03,1.03,1.03,1);
    S.bOverride_DynamicGlobalIlluminationMethod=true;S.DynamicGlobalIlluminationMethod=EDynamicGlobalIlluminationMethod::Lumen;S.bOverride_ReflectionMethod=true;S.ReflectionMethod=EReflectionMethod::Lumen;
    S.bOverride_LumenSceneLightingQuality=true;S.LumenSceneLightingQuality=2;S.bOverride_LumenSceneDetail=true;S.LumenSceneDetail=2;
    S.bOverride_LumenFinalGatherQuality=true;S.LumenFinalGatherQuality=2;S.bOverride_LumenReflectionQuality=true;S.LumenReflectionQuality=2;
    S.bOverride_LumenSceneViewDistance=true;S.LumenSceneViewDistance=20000;S.bOverride_LumenMaxTraceDistance=true;S.LumenMaxTraceDistance=20000;
    S.bOverride_AmbientOcclusionIntensity=true;S.AmbientOcclusionIntensity=LightingBaseline?.9f:.38f;S.bOverride_AmbientOcclusionRadius=true;S.AmbientOcclusionRadius=110;
    if(auto Cel=CraftMaterial(TEXT("CelLighting")))S.AddBlendable(Cel,LightingBaseline?1.f:.65f);
    UE_LOG(LogTemp,Display,TEXT("CRAFT_LIGHTING_C17 baseline=%d c16=%d key=%.2f sky=%.2f"),LightingBaseline,C16Lighting,Sun->Intensity,SL->Intensity);
    UE_LOG(LogTemp,Display,TEXT("CRAFT_READY: Character capsule, physical thoughts, generated concept-guided candidate. Art not accepted."));
    if(RoamReview||FParse::Param(FCommandLine::Get(),TEXT("CraftExplore")))AuditExploration();
#if WITH_EDITOR
    if(Capture||Film){FAssetCompilingManager::Get().FinishAllCompilation();if(GShaderCompilingManager)GShaderCompilingManager->FinishAllCompilation();}
    for(const TCHAR* K : {TEXT("C13_Stone"),TEXT("C13_Turf"),TEXT("C13_Tissue"),TEXT("C13_LeafGold"),TEXT("C13_WaterBlue"),TEXT("C17_Stone"),TEXT("C17_Moss"),TEXT("C17_Bark"),TEXT("C17_Leaf"),TEXT("C17_Glow")})
    {
        if(auto I=CraftMaterial(K))if(auto M=I->GetMaterial())if(auto R=M->GetMaterialResource(GMaxRHIShaderPlatform))
        {
            UE_LOG(LogTemp,Display,TEXT("CRAFT_MATERIAL %s path=%s complete=%d default=%d shader=%d"),K,*M->GetPathName(),R->IsGameThreadShaderMapComplete(),R->IsDefaultMaterial(),R->GetGameThreadShaderMap()!=nullptr);
            for(const auto& E:R->GetCompileErrors())UE_LOG(LogTemp,Error,TEXT("CRAFT_MATERIAL_ERROR %s %s"),K,*E);
        }
    }
#endif
}
void AAttentionCharacter::Tone(int32 I,float Volume)
{
    const TCHAR* Names[]={TEXT("Chime"),TEXT("Swat"),TEXT("Breath"),TEXT("Heart")};if(I<0||I>3)return;
    if(auto S=LoadObject<USoundWave>(nullptr,*FString::Printf(TEXT("/Game/Audio/%s.%s"),Names[I],Names[I])))UGameplayStatics::PlaySound2D(this,S,Volume);
}
void AAttentionCharacter::ResetMorning()
{
    Hands->ReleaseComponent();HeldThought=nullptr;for(auto T:Thoughts)if(T)T->Destroy();Thoughts.Empty();Delivered=Released=0;Focused=BridgeOpen=Complete=false;Focus=TreeCharge=0;
    GripAge=MaxGripError=MaxSteadyHandleLag=0;GripErrorSum=0;GripSamples=0;WasHolding=false;ReleaseBlend=0;ReleaseHandLocal[0]=ReleaseHandLocal[1]=FVector::ZeroVector;
    const FVector* Places=CraftLayout::Thoughts;
    for(int i=0;i<6;i++){FVector P=Places[i];P.Z=CraftGround(GetWorld(),P)+95;auto T=GetWorld()->SpawnActor<ACraftThought>(P,FRotator::ZeroRotator);T->Configure(i<3?0:i==3?1:i==4?2:3,P);Thoughts.Add(T);}
    for(auto M:Shortcut){M->SetVisibility(false);M->SetCollisionEnabled(ECollisionEnabled::NoCollision);}
    SetActorLocation(Entry+FVector(0,0,110),false,nullptr,ETeleportType::TeleportPhysics);GetCharacterMovement()->StopMovementImmediately();LastSafe=GetActorLocation();Recoveries=PhysicalGrabs=0;MaxHandError=ContactError=0;FootStance[0]=FootStance[1]=false;CarryBlend=0;HandPose[0]=HandPose[1]=FVector::ZeroVector;ContactSteps.Reset();CarryTarget=FVector::ZeroVector;PreviousYaw=GetActorRotation().Yaw;
    Message="A thought is waiting by the path. Give it a little attention.";MessageTime=8;
}
void AAttentionCharacter::Burst(FVector P,bool Gold,int32 Count,float Power)
{
    for(int32 i=0;i<Count;i++){FCraftSpark S;S.P=P;S.V=FMath::VRand()*Power+FVector(0,0,Power*.55);S.Life=FMath::FRandRange(.45,1.1);S.Scale=FMath::FRandRange(.035,.09);S.Gold=Gold;Sparks.Add(S);}
}
void AAttentionCharacter::Interact()
{
    if(HeldThought)
    {
        ACraftThought* T=HeldThought;
        if(T->Kind==0&&FVector::Dist2D(GetActorLocation(),TreeCare)<440&&FVector::Dist2D(T->GetActorLocation(),TreeCare)<580)
        {Hands->ReleaseComponent();T->ResolveTo(FVector(0,20,720));HeldThought=nullptr;Delivered++;TreeCharge=1;Burst(T->GetActorLocation(),true,26,220);Tone(0,.4);Message=Delivered==3?"Three bright thoughts. Now make room for the heavy ones.":"The tree remembers this little kindness.";MessageTime=5;UE_LOG(LogTemp,Display,TEXT("CRAFT_STAR_DELIVERED %d"),Delivered);return;}
        if(T->Kind==1&&Focused&&FVector::Dist2D(GetActorLocation(),ReleasePool)<420)
        {Hands->ReleaseComponent();T->ResolveTo(ReleasePool+FVector(0,0,20));HeldThought=nullptr;Released++;Burst(ReleasePool+FVector(0,0,45),false,30,170);Tone(0,.4);Message="The water carries that weight onward.";MessageTime=6;UE_LOG(LogTemp,Display,TEXT("CRAFT_HEAVY_RELEASED by care input"));return;}
        Hands->ReleaseComponent();T->Held=false;T->Physics->SetCollisionResponseToChannel(ECC_Pawn,ECR_Block);HeldThought=nullptr;Tone(1,.08);return;
    }
    if(Nearest>=0&&Thoughts.IsValidIndex(Nearest))
    {
        auto T=Thoughts[Nearest];if(T->Resolved)return;
        if(T->Kind>1){Message=T->Kind==2?"A light worry. SPACE to brush it gently away.":"A stubborn loop. Three gentle SPACE pushes.";MessageTime=3;return;}
        HeldThought=T;T->Held=true;GripAge=0;PhysicalGrabs++;T->Physics->SetCollisionResponseToChannel(ECC_Pawn,ECR_Ignore);Hands->GrabComponentAtLocationWithRotation(T->Physics,NAME_None,T->GetActorLocation(),FRotator::ZeroRotator);Hands->SetLinearStiffness(LegacyGrip?(T->Kind==1?1000:2200):(T->Kind==1?4800:6500));Hands->SetLinearDamping(LegacyGrip?(T->Kind==1?180:120):(T->Kind==1?120:105));Tone(1,.1);Message=T->Kind==1?"It has weight. Bring it gently to the blue release pool.":"A bright thought. Bring it to the tree's front roots.";MessageTime=5;
    }
}
void AAttentionCharacter::Swat()
{
    if(SwatAge<.55f||HeldThought)return;SwatAge=0;
    PendingSwat=Nearest>=0&&Thoughts[Nearest]->Kind>=2?Nearest:-1;
    if(PendingSwat<0)JumpBuffer=.16f;
}
void AAttentionCharacter::SwatImpact()
{
    const int32 Target=PendingSwat;PendingSwat=-1;
    if(Target>=0&&Thoughts.IsValidIndex(Target))
    {
        auto T=Thoughts[Target];if(T->Kind<2||T->Resolved||FVector::Dist2D(GetActorLocation(),T->GetActorLocation())>165)return;FVector D=(T->GetActorLocation()-GetActorLocation()).GetSafeNormal2D();T->Physics->AddImpulse((D*440+FVector(0,0,135))*T->Physics->GetMass());T->Reaction=.3;Burst(T->GetActorLocation(),T->Kind==3,12,170);Tone(1,.3);
        if(T->Kind==2||++T->Pushes>=3)
        {
            T->ResolveTo(T->GetActorLocation()+D*170+FVector(0,0,100));
            if(T->Kind==3&&!Focused){T->ReturnIn=30;Message="A loop can return. Find calm at the lotus before letting it go.";UE_LOG(LogTemp,Display,TEXT("CRAFT_PERSISTENT_DEFERRED seconds=30"));}
            else{Released++;Message=T->Kind==2?"A little space opens up.":"With a quiet mind, the old loop finally loosens.";UE_LOG(LogTemp,Display,TEXT("CRAFT_THOUGHT_RELEASED type=%d count=%d"),T->Kind,Released);}
            MessageTime=5;
        }
    }
}
FString AAttentionCharacter::Task() const
{
    if(Complete)return TEXT("A little room to think. R begins another morning.");
    if(BridgeOpen)return TEXT("Follow the new root crossing back to the arrival garden.");
    if(HeldThought)return HeldThought->Kind==1?TEXT("Bring the heavy thought to the blue release pool."):TEXT("Carry the bright thought to the awareness tree. E to place.");
    if(Delivered<3)return FString::Printf(TEXT("Bring bright thoughts to the tree   %d / 3"),Delivered);
    if(!Focused)return TEXT("Visit the focus lotus. Hold E and let the currents settle.");
    return FString::Printf(TEXT("Make room: brush the wisp, loosen the knot, release the cloud   %d / 3"),Released);
}
void AAttentionCharacter::Landed(const FHitResult& Hit){Super::Landed(Hit);LandAge=0;Burst(Hit.ImpactPoint+FVector(0,0,6),true,7,60);Tone(1,.05);}

void AAttentionCharacter::Tick(float Dt)
{
    Super::Tick(Dt);auto PC=Cast<APlayerController>(GetController());if(!PC)return;
    if(PC->WasInputKeyJustPressed(EKeys::Escape)||PC->WasInputKeyJustPressed(EKeys::Gamepad_Special_Right)){Paused=!Paused;UGameplayStatics::SetGamePaused(this,Paused);}
    if(Paused)return;
    Age+=Dt;SwatAge+=Dt;LandAge+=Dt;MessageTime=FMath::Max(0.f,MessageTime-Dt);if(PendingSwat>=0&&SwatAge>=.14f)SwatImpact();
    if(PC->WasInputKeyJustPressed(EKeys::H))Help=!Help;if(PC->WasInputKeyJustPressed(EKeys::F8))Photo=!Photo;if(PC->WasInputKeyJustPressed(EKeys::R))ResetMorning();
    if(PC->WasInputKeyJustPressed(EKeys::Tab))Overview=!Overview;
    const bool DragNow=PC->IsInputKeyDown(EKeys::RightMouseButton)||PC->IsInputKeyDown(EKeys::MiddleMouseButton);
    if(DragNow!=CameraDragging)
    {
        CameraDragging=DragNow;
        if(DragNow){float X=0,Y=0;PC->GetMousePosition(X,Y);CameraCursor=FVector2D(X,Y);FInputModeGameOnly Mode;Mode.SetConsumeCaptureMouseDown(false);PC->SetInputMode(Mode);PC->bShowMouseCursor=false;}
        else{FInputModeGameAndUI Mode;Mode.SetHideCursorDuringCapture(false);PC->SetInputMode(Mode);PC->bShowMouseCursor=true;PC->SetMouseLocation(int(CameraCursor.X),int(CameraCursor.Y));}
    }
    if(PC->WasInputKeyJustPressed(EKeys::MouseScrollUp))Zoom=FMath::Clamp(Zoom*.88f,.5f,2.7f);if(PC->WasInputKeyJustPressed(EKeys::MouseScrollDown))Zoom=FMath::Clamp(Zoom*1.13f,.5f,2.7f);
    float MX=0,MY=0;PC->GetInputMouseDelta(MX,MY);if(PC->IsInputKeyDown(EKeys::RightMouseButton)){CamYaw+=MX*.22;CamPitch=FMath::Clamp(CamPitch+MY*.2f,30.f,80.f);}
    auto Stick=[](float V){return FMath::Abs(V)<.16f?0.f:FMath::Sign(V)*(FMath::Abs(V)-.16f)/.84f;};CamYaw+=Stick(PC->GetInputAnalogKeyState(EKeys::Gamepad_RightX))*110*Dt;CamPitch=FMath::Clamp(CamPitch-Stick(PC->GetInputAnalogKeyState(EKeys::Gamepad_RightY))*70*Dt,30.f,80.f);Zoom=FMath::Clamp(Zoom+Dt*(PC->GetInputAnalogKeyState(EKeys::Gamepad_LeftTriggerAxis)-PC->GetInputAnalogKeyState(EKeys::Gamepad_RightTriggerAxis)),.5f,2.7f);
    if(PC->IsInputKeyDown(EKeys::MiddleMouseButton))Pan+=FRotator(0,CamYaw,0).RotateVector(FVector(MY,-MX,0))*Camera->OrthoWidth/1600;
    if(PC->WasInputKeyJustPressed(EKeys::Home)){CamYaw=80;CamPitch=49;Zoom=1;Pan=FVector::ZeroVector;Overview=false;}
    FVector Move;float X=(PC->IsInputKeyDown(EKeys::W)||PC->IsInputKeyDown(EKeys::Up)?1:0)-(PC->IsInputKeyDown(EKeys::S)||PC->IsInputKeyDown(EKeys::Down)?1:0);float Y=(PC->IsInputKeyDown(EKeys::D)||PC->IsInputKeyDown(EKeys::Right)?1:0)-(PC->IsInputKeyDown(EKeys::A)||PC->IsInputKeyDown(EKeys::Left)?1:0);Move=FRotator(0,CamYaw,0).RotateVector(FVector(X,Y,0)).GetSafeNormal();
    FVector Pad=FRotator(0,CamYaw,0).RotateVector(FVector(Stick(PC->GetInputAnalogKeyState(EKeys::Gamepad_LeftY)),Stick(PC->GetInputAnalogKeyState(EKeys::Gamepad_LeftX)),0));if(!Pad.IsNearlyZero())Move=Pad.GetClampedToMaxSize(1);
    GetCharacterMovement()->MaxWalkSpeed=HeldThought?(HeldThought->Kind==1?300:450):(PC->IsInputKeyDown(EKeys::LeftShift)||PC->IsInputKeyDown(EKeys::Gamepad_LeftShoulder))?800:560;GetCharacterMovement()->MaxAcceleration=HeldThought?(HeldThought->Kind==1?900:1600):2300;GetCharacterMovement()->BrakingDecelerationWalking=HeldThought?1450:2100;AddMovementInput(Move.GetSafeNormal(),Move.Size());
    if(!Move.IsNearlyZero()){FVector Facing=HeldThought&&HeldThought->Kind==1?(HeldThought->GetActorLocation()-GetActorLocation()).GetSafeNormal2D():Move;FRotator Turn=FMath::RInterpTo(GetActorRotation(),Facing.Rotation(),Dt,9);if(HeldThought&&!LegacyGrip){float Delta=FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,Turn.Yaw);Turn.Yaw=GetActorRotation().Yaw+FMath::Clamp(Delta,-240.f*Dt,240.f*Dt);}SetActorRotation(Turn);Help=false;}
    GroundedGrace=GetCharacterMovement()->IsMovingOnGround()?.12f:FMath::Max(0.f,GroundedGrace-Dt);JumpBuffer=FMath::Max(0.f,JumpBuffer-Dt);if(JumpBuffer>0&&GroundedGrace>0){LaunchCharacter(FVector(0,0,410),false,true);JumpBuffer=GroundedGrace=0;}
    Nearest=-1;float Best=145;for(int32 i=0;i<Thoughts.Num();i++)if(Thoughts[i]&&!Thoughts[i]->Resolved){float D=FVector::Dist2D(GetActorLocation(),Thoughts[i]->GetActorLocation());if(D<Best){Best=D;Nearest=i;}}
    Prompt=HeldThought?TEXT("E  Place / let go"):Nearest>=0?(Thoughts[Nearest]->Kind<2?TEXT("E  Hold gently"):TEXT("SPACE  Brush / push")):TEXT("");
    if(HeldThought&&HeldThought->Kind==1&&Focused&&FVector::Dist2D(GetActorLocation(),ReleasePool)<420)Prompt=TEXT("E / X  Lower gently into the water");
    const bool AtLotus=FVector::Dist2D(GetActorLocation(),Lotus)<430;
    if(AtLotus&&!Focused&&!HeldThought){Prompt="Hold E / X  Find a quiet moment";if(PC->IsInputKeyDown(EKeys::E)||PC->IsInputKeyDown(EKeys::Gamepad_FaceButton_Left)){Focus=FMath::Min(1.f,Focus+Dt/2.4f);if(Focus>=1){Focused=true;Burst(Lotus+FVector(0,0,180),false,32,200);Tone(2,.35);Message="The currents settle. There is room for each thought.";MessageTime=6;UE_LOG(LogTemp,Display,TEXT("CRAFT_FOCUS_COMPLETE"));}}else Focus=FMath::Max(0.f,Focus-Dt*.5f);}
    if((PC->WasInputKeyJustPressed(EKeys::E)||PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Left))&&(!AtLotus||HeldThought))Interact();
    if(PC->WasInputKeyJustPressed(EKeys::SpaceBar)||PC->WasInputKeyJustPressed(EKeys::Gamepad_FaceButton_Bottom))Swat();
    if(HeldThought)
    {
        GripAge+=Dt;
        FVector Target=GetActorLocation()+GetActorForwardVector()*(LegacyGrip?(HeldThought->Kind==1?98:68):(HeldThought->Kind==1?110:88));Target.Z+=HeldThought->Kind==1?-17:9;Target.Z=FMath::Max(Target.Z,CraftGround(GetWorld(),Target)+HeldThought->Physics->GetScaledSphereRadius()+10);if(CarryTarget.IsNearlyZero())CarryTarget=HeldThought->GetActorLocation();CarryTarget=FMath::Lerp(CarryTarget,Target,1-FMath::Exp(-(LegacyGrip?14.f:GripAge<.35f?10.f:32.f)*Dt));Hands->SetTargetLocationAndRotation(CarryTarget+(LegacyGrip?FVector::ZeroVector:GetVelocity().GetClampedToMaxSize(500)*.035f),FRotator::ZeroRotator);
        MaxHandError=FMath::Max(MaxHandError,float(FVector::Dist(Target,HeldThought->GetActorLocation())));
        if(GripAge>.6f)MaxSteadyHandleLag=FMath::Max(MaxSteadyHandleLag,float(FVector::Dist(Target,HeldThought->GetActorLocation())));
        if(HeldThought->Kind==1&&Focused&&FVector::Dist2D(HeldThought->GetActorLocation(),ReleasePool)<310)
        {auto T=HeldThought;Hands->ReleaseComponent();HeldThought=nullptr;T->ResolveTo(ReleasePool+FVector(0,0,20));Released++;Burst(T->GetActorLocation(),false,30,180);Tone(0,.35);Message="Heavy does not mean forever. The pool carries it onward.";MessageTime=6;UE_LOG(LogTemp,Display,TEXT("CRAFT_HEAVY_RELEASED"));}
    }
    for(int32 i=0;i<Petals.Num();i++){float Angle=i*2*PI/9;Petals[i]->SetWorldRotation(FRotator(FMath::Sin(Angle)*Focus*25,0,FMath::Cos(Angle)*Focus*25));}
    if(Delivered>=3&&Released>=3&&Focused&&!BridgeOpen)
    {BridgeOpen=true;for(auto M:Shortcut){M->SetVisibility(true);M->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);}Burst(FVector(-1100,-1200,420),true,40,300);Tone(0,.6);Message="The roots find a way home. Walk the new crossing.";MessageTime=8;UE_LOG(LogTemp,Display,TEXT("CRAFT_SHORTCUT_OPEN"));}
    if(BridgeOpen&&!Complete&&FVector::Dist2D(GetActorLocation(),Entry)<400){Complete=true;Tone(0,.5);Message="A little care. A lighter morning.";MessageTime=12;UE_LOG(LogTemp,Display,TEXT("CRAFT_MORNING_COMPLETE"));}
    if(GetActorLocation().Z<-450){Recoveries++;SetActorLocation(LastSafe,false,nullptr,ETeleportType::TeleportPhysics);GetCharacterMovement()->StopMovementImmediately();Message="Back on the path.";MessageTime=2;UE_LOG(LogTemp,Warning,TEXT("CRAFT_RECOVERY %d %s"),Recoveries,*LastSafe.ToString());}
    else if(GetCharacterMovement()->IsMovingOnGround())LastSafe=GetActorLocation();
    TreeCharge=FMath::FInterpTo(TreeCharge,0,Dt,1.7);for(auto M:TreeLight)if(M)M->SetScalarParameterValue(TEXT("LifeGlow"),.35+Delivered*.75+TreeCharge*2);
    PoseMove=Move;
    FVector FocusP=(Overview?FVector(0,100,730):GetActorLocation()+FVector(0,0,100)+GetVelocity().GetClampedToMaxSize(800)*.12f)+Pan;CameraFocus=FMath::VInterpTo(CameraFocus,FocusP,Dt,5.2);FVector Offset=-FRotator(-CamPitch,CamYaw,0).Vector()*8000;Camera->SetWorldLocation(CameraFocus+Offset);Camera->SetWorldRotation((-Offset).Rotation());Camera->SetOrthoWidth(FMath::FInterpTo(Camera->OrthoWidth,(Overview?10800:2700)*Zoom,Dt,4));UpdateVisibility(Dt);
    if(Capture||Smoke||ControlsReview||RoamReview)RunReview(Dt);
}

void AAttentionCharacter::UpdateAnimation(float Dt,FVector Move)
{
    ContactError=0;
    float Speed=GetVelocity().Size2D();SmoothedMove=FMath::Lerp(SmoothedMove,FMath::Clamp(Speed/560,0.f,1.f),1-FMath::Exp(-10*Dt));float Moving=SmoothedMove;const bool Heavy=HeldThought&&HeldThought->Kind==1;const bool Grounded=GetCharacterMovement()->IsMovingOnGround();
    FVector Roots[2];for(int i=0;i<2;i++)Roots[i]=GetActorLocation()+GetActorRotation().RotateVector(FVector(0,i?17:-17,-38));
    if(Grounded)ContactSteps.Update(GetWorld(),this,GetActorLocation(),Roots,GetActorForwardVector(),FVector::ZeroVector,GetActorLocation().Z-92,8,68,.97,45,800,12,Heavy,Dt);else ContactSteps.Reset();
    StepPhase=ContactSteps.Cycle*2*PI;float Walk=FMath::Sin(StepPhase);float YawRate=FMath::DegreesToRadians(FMath::FindDeltaAngleDegrees(PreviousYaw,GetActorRotation().Yaw))/FMath::Max(Dt,.001f);PreviousYaw=GetActorRotation().Yaw;
    CarryBlend=FMath::Lerp(CarryBlend,HeldThought?1.f:0.f,1-FMath::Exp(-10*Dt));if(!HeldThought)CarryTarget=FVector::ZeroVector;
    if(WasHolding&&!HeldThought)ReleaseBlend=1;
    if(!HeldThought)ReleaseBlend=FMath::Max(0.f,ReleaseBlend-Dt/.34f);else ReleaseBlend=0;
    WasHolding=HeldThought!=nullptr;
    const float Accel=FVector::DotProduct((GetVelocity()-LastVelocity)/FMath::Max(Dt,.001f),GetActorForwardVector());float WeightLean=(Heavy?FMath::Clamp(FVector::DotProduct(GetVelocity(),GetActorForwardVector())/300,-1.f,1.f)*10:Moving*4)+FMath::Clamp(Accel*.003f,-5.f,6.f);
    BodyLean=FMath::Lerp(BodyLean,WeightLean,1-FMath::Exp(-8*Dt));BodyRoll=FMath::Lerp(BodyRoll,-BWGait::TurnLeanDeg(Speed,YawRate,9)+Walk*1.6f*Moving,1-FMath::Exp(-7*Dt));
    float Land=LandAge<.38?FMath::Sin(LandAge/.38*PI)*.095f:0;Puppet->SetRelativeScale3D(FVector(1+Land*.3,1+Land*.3,1-Land));
    FVector LoadOffset=FVector::ZeroVector;
    if(HeldThought&&!LegacyGrip){FVector Ideal=GetActorLocation()+GetActorForwardVector()*(Heavy?110:88);FVector Lag=HeldThought->GetActorLocation()-Ideal;Lag.Z=0;LoadOffset=GetActorRotation().UnrotateVector(Lag.GetClampedToMaxSize(12))*CarryBlend;}
    Puppet->SetRelativeLocation(LoadOffset+FVector(0,0,-92-(Heavy?2.5f:0)+FMath::Abs(Walk)*(Heavy?1:2.1)*Moving+FMath::Sin(Age*2)*.5));Puppet->SetRelativeRotation(FRotator(BodyLean,0,BodyRoll));
    float WantLook=0;if(Nearest>=0&&!HeldThought)WantLook=FMath::Clamp(FMath::FindDeltaAngleDegrees(GetActorRotation().Yaw,(Thoughts[Nearest]->GetActorLocation()-GetActorLocation()).Rotation().Yaw),-24.f,24.f);
    LookYaw=FMath::Lerp(LookYaw,WantLook,1-FMath::Exp(-5*Dt));Parts[1]->SetRelativeRotation(FRotator(-BodyLean*.35+FMath::Sin(Age*1.2f)*1.0,LookYaw,-BodyRoll*.55));Parts[2]->SetRelativeRotation(Parts[1]->GetRelativeRotation());float Blink=FMath::Fmod(Age,4.7f);Parts[2]->SetRelativeScale3D(FVector(1,1,1-.88f*FMath::Sin(FMath::Clamp(Blink/.19f,0.f,1.f)*PI)));
    float TargetCape=Moving*17+(GetVelocity().Z>0?11:0);float Force=(TargetCape-CapeAngle)*90-CapeVelocity*14;CapeVelocity+=Force*FMath::Min(Dt,.033f);CapeAngle+=CapeVelocity*FMath::Min(Dt,.033f);Parts[3]->SetRelativeRotation(FRotator(-CapeAngle,0,Walk*Moving*3));
    for(int32 Side=0;Side<2;Side++)
    {
        float Phase=StepPhase+Side*PI;const auto& Step=ContactSteps.Feet[Side];bool Stance=Grounded&&!Step.bSwing;
        FVector Foot=Grounded&&ContactSteps.bReady?Step.Target:GetActorLocation()+GetActorRotation().RotateVector(FVector(11,Side?18:-18,-72));
        if(Legs.IsValidIndex(Side))
        {
            FVector Hip=Puppet->GetComponentTransform().TransformPosition(FVector(0,Side?17:-17,54));const auto Leg=BWGait::SolveLimb(Hip,Foot,34,34,GetActorForwardVector(),.985);Foot=Leg.Foot;
            Legs[Side]->SetWorldLocation(Hip);Legs[Side]->SetWorldRotation(FQuat::FindBetweenNormals(-FVector::UpVector,(Leg.Knee-Hip).GetSafeNormal()));Shins[Side]->SetWorldLocation(Leg.Knee);Shins[Side]->SetWorldRotation(FQuat::FindBetweenNormals(-FVector::UpVector,(Foot-Leg.Knee).GetSafeNormal()));
        }
        Parts[6+Side]->SetWorldLocation(Foot);float Toe=Step.bSwing?-FMath::Sin(Step.Phase*PI)*12.f:0;Parts[6+Side]->SetWorldRotation(FMath::RInterpTo(Parts[6+Side]->GetComponentRotation(),GetActorRotation()+FRotator(Toe,0,0),Dt,18));
        if(Stance&&!FootStance[Side]&&Speed>40){Burst(Foot,true,2,18);Tone(1,Heavy?.025f:.016f);}FootStance[Side]=Stance;
        const float Sign=Side?1.f:-1.f;FVector Shoulder=Puppet->GetComponentTransform().TransformPosition(FVector(0,Sign*37,103));FVector Desired=Shoulder+GetActorRotation().RotateVector(FVector(FMath::Sin(Phase+PI)*Moving*19,Sign*6,-48));
        if(HeldThought){float Radius=HeldThought->Physics->GetScaledSphereRadius();FVector Contact=HeldThought->GetActorLocation()-GetActorForwardVector()*Radius*.76+GetActorRightVector()*Sign*Radius*.54-FVector(0,0,Heavy?5:8);Desired=FMath::Lerp(Desired,Contact,CarryBlend);}
        else if(Focus>0&&!Focused)Desired=Shoulder+GetActorRotation().RotateVector(FVector(32,-Sign*25,-22));
        else if(!Grounded)Desired=Shoulder+GetActorRotation().RotateVector(FVector(15,Sign*29,-18));
        if(Side==1&&SwatAge<.5f){float Stroke=SwatAge<.12f?-FMath::Sin(SwatAge/.12f*PI)*.45f:FMath::Sin(FMath::Clamp((SwatAge-.12f)/.38f,0.f,1.f)*PI);Desired=Shoulder+GetActorRotation().RotateVector(FVector(Stroke*57,10, -32+Stroke*28));}
        if(!HeldThought&&ReleaseBlend>0&&!LegacyGrip){float T=ReleaseBlend*ReleaseBlend*(3-2*ReleaseBlend);Desired=FMath::Lerp(Desired,GetActorTransform().TransformPosition(ReleaseHandLocal[Side]),T);}
        if(HandPose[Side].IsNearlyZero())HandPose[Side]=Desired;HandPose[Side]=HeldThought&&!LegacyGrip?Desired:FMath::Lerp(HandPose[Side],Desired,1-FMath::Exp(-26*Dt));FVector Pole=GetActorRightVector()*Sign*.7-GetActorForwardVector()*.5-FVector(0,0,.25);const auto Arm=BWGait::SolveLimb(Shoulder,HandPose[Side],31,32,Pole,.975);FVector Wrist=Arm.Foot,Elbow=Arm.Knee;
        if(HeldThought)ReleaseHandLocal[Side]=GetActorTransform().InverseTransformPosition(Wrist);
        Parts[4+Side]->SetWorldLocation(Shoulder);Parts[4+Side]->SetWorldRotation(FQuat::FindBetweenNormals(-FVector::UpVector,(Elbow-Shoulder).GetSafeNormal()));Forearms[Side]->SetWorldLocation(Elbow);Forearms[Side]->SetWorldRotation(FQuat::FindBetweenNormals(-FVector::UpVector,(Wrist-Elbow).GetSafeNormal()));Mittens[Side]->SetWorldLocation(Wrist);Mittens[Side]->SetWorldRotation(GetActorRotation()+FRotator(HeldThought?-80:0,0,Sign*9));
        if(HeldThought&&CarryBlend>.95)ContactError=FMath::Max(ContactError,float(FVector::Dist(Wrist,Desired)));
    }
    if(HeldThought&&GripAge>.6f){MaxGripError=FMath::Max(MaxGripError,ContactError);GripErrorSum+=ContactError;GripSamples++;}
    if(ClothCape)ClothCape->Simulate(Puppet->GetComponentTransform(),Dt,GetActorLocation().Z-92,HeldThought?HeldThought->GetActorLocation():FVector::ZeroVector,HeldThought?HeldThought->Physics->GetScaledSphereRadius():0);
    LastVelocity=GetVelocity();
}
void AAttentionCharacter::UpdateEffects(float Dt)
{
    FVector At=GetActorLocation()-FVector(0,0,70);for(auto M:GroundCoverMaterials)if(M)M->SetVectorParameterValue(TEXT("AttentionPosition"),FLinearColor(At.X,At.Y,At.Z,1));
    GoldFX->ClearInstances();VioletFX->ClearInstances();
    for(int32 i=Sparks.Num()-1;i>=0;i--){auto& S=Sparks[i];S.Age+=Dt;if(S.Age>S.Life){Sparks.RemoveAtSwap(i);continue;}S.V.Z-=85*Dt;S.P+=S.V*Dt;float Size=S.Scale*(1-S.Age/S.Life);(S.Gold?GoldFX:VioletFX)->AddInstance(FTransform(FRotator::ZeroRotator,S.P,FVector(Size)),true);}
    // Sparse directional currents travel from nests toward the gathering court.
    FVector Starts[3];for(int i=0;i<3;i++)Starts[i]=CraftLayout::Portals[i]+FVector(0,0,190);
    for(int32 i=0;i<42;i++){int32 Lane=i%3;float T=FMath::Fmod(Age*(Focused?.042f:.075f)+i/14.f,1.f);FVector P=FMath::Lerp(Starts[Lane],FVector(470,300,420),T);P+=FVector(FMath::Sin(T*PI*2+Lane)*80,FMath::Sin(T*PI)*100,0);float S=FMath::Sin(T*PI)*.035f;VioletFX->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(S)),true);}
    if(HeldThought&&HeldThought->Kind==0)for(int i=0;i<4;i++){float A=Age*2+i*PI/2;FVector P=HeldThought->GetActorLocation()+FVector(FMath::Cos(A)*58,FMath::Sin(A)*58,FMath::Sin(A*2)*16);GoldFX->AddInstance(FTransform(FRotator::ZeroRotator,P,FVector(.025)),true);}
    RippleFX->ClearInstances();const FVector Pools[]={FVector(-1680,1780,1393),FVector(-1680,1280,1193),ReleasePool-FVector(0,0,37)};
    for(int Pool=0;Pool<3;Pool++)for(int i=0;i<3;i++){float T=FMath::Fmod(Age*.17f+i/3.f,1.f);float Size=.25+T*(Pool==2?1.2f:1.8f);RippleFX->AddInstance(FTransform(FRotator::ZeroRotator,Pools[Pool]+FVector(0,0,i*.3f),FVector(Size,Size,1-T)),true);}
    PetalFX->ClearInstances();const FVector Groves[]={FVector(-1990,1890,1550),FVector(-2200,-1650,820),FVector(2130,-1830,750)};
    for(int i=0;i<24;i++){float T=FMath::Fmod(Age*.055f+i*.137f,1.f);float A=i*2.399f+T*3.2f;FVector P=Groves[i%3]+FVector(FMath::Cos(A)*140+T*160,FMath::Sin(A)*120,70-T*400);PetalFX->AddInstance(FTransform(FRotator(T*270,i*137+Age*13,FMath::Sin(Age*2+i)*32),P,FVector(.38f)),true);}
}
void AAttentionCharacter::UpdateVisibility(float Dt)
{
    FVector Start=Camera->GetComponentLocation(),End=GetActorLocation()+FVector(0,0,32);FCollisionQueryParams Params;Params.bTraceComplex=true;
    for(auto& F:Fades){FHitResult Hit;bool Hide=!Overview&&F.Mesh&&F.Mesh->LineTraceComponent(Hit,Start,End,Params);F.Alpha=FMath::FInterpTo(F.Alpha,Hide?.14f:1.f,Dt,7);for(auto M:F.Materials)if(M)M->SetScalarParameterValue(TEXT("Visibility"),F.Alpha);}
}

void ABrainCraftHUD::DrawHUD()
{
    Super::DrawHUD();auto P=Cast<AAttentionCharacter>(GetOwningPawn());if(!P||P->Photo||!Canvas)return;float S=Canvas->ClipX/1920.f;
    auto Text=[&](FString T,float X,float Y,float Scale,FLinearColor C){DrawText(T,C,X*S,Y*S,GEngine->GetLargeFont(),Scale*S*1.5f,false);};
    auto Box=[&](float X,float Y,float W,float H,FLinearColor C){DrawRect(C,X*S,Y*S,W*S,H*S);};
    Box(28,30,340,100,FLinearColor(.035,.05,.075,.83));Text(TEXT("THE AWARENESS GARDEN"),48,46,1.05,FLinearColor(.97,.79,.43));Text(TEXT("A little care. A living world."),48,87,.75,FLinearColor(.72,.80,.75));
    float Y=Canvas->ClipY/S-132;Box(400,Y,1120,88,FLinearColor(.03,.045,.065,.84));Text(P->Task(),425,Y+16,.95,FLinearColor(.95,.90,.75));
    Text(TEXT("WASD Move   SHIFT Hurry   E Care   SPACE Brush / hop   RMB Orbit   Wheel Zoom   MMB Pan   TAB Map   H Help"),425,Y+54,.66,FLinearColor(.64,.76,.78));
    if(!P->Prompt.IsEmpty())Text(P->Prompt,800,Canvas->ClipY/S*.64,1.0,FLinearColor(1,.88,.50));
    if(P->MessageTime>0){Box(540,140,840,48,FLinearColor(.035,.05,.07,.72));Text(P->Message,560,155,.8,FLinearColor(.88,.91,.82));}
    if(P->Focus>0&&!P->Focused){Box(805,Canvas->ClipY/S*.69,310,6,FLinearColor(.12,.12,.2,.8));Box(805,Canvas->ClipY/S*.69,310*P->Focus,6,FLinearColor(.65,.48,1,1));}
    if(P->Help){Box(520,260,880,380,FLinearColor(.025,.035,.055,.96));Text(TEXT("A morning in the brain"),555,292,1.35,FLinearColor(1,.82,.45));const TCHAR* Lines[]={TEXT("Carry three bright stars to the tree. E picks up and places."),TEXT("Hold E by the lotus to calm the neural currents."),TEXT("Drag the heavy cloud to the blue pool beside the lotus."),TEXT("SPACE brushes away the light wisp; the amber knot needs three pushes."),TEXT("Care opens a root crossing. Follow it home to finish the morning."),TEXT("HOME resets the camera. F8 hides the interface. R starts again.")};for(int i=0;i<6;i++)Text(Lines[i],555,355+i*41,.83,FLinearColor(.8,.86,.84));}
    if(P->Paused){Box(660,400,600,150,FLinearColor(.03,.04,.06,.9));Text(TEXT("A quiet moment"),825,440,1.5,FLinearColor(1,.87,.6));Text(TEXT("ESC to continue"),845,495,.9,FLinearColor(.8,.85,.85));}
}

