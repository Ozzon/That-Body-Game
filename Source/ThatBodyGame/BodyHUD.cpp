#include "BodyGame.h"
#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "CanvasItem.h"
#include "GameFramework/PlayerController.h"

static const FLinearColor Ink(.045,.063,.075,.92),Cream(.95,.91,.82,1),Soft(.58,.66,.65,1),Mint(.53,.83,.74,1),Gold(.96,.74,.39,1);
void ABodyHUD::Text(FString S,float X,float Y,float Size,FLinearColor C)
{
    FCanvasTextItem Item(FVector2D(X*Scale,Y*Scale),FText::FromString(S),GEngine->GetLargeFont(),C);
    Item.Scale=FVector2D(Size/FMath::Max(1.f,float(GEngine->GetLargeFont()->GetMaxCharHeight()))*Scale);Item.EnableShadow(FLinearColor(0,0,0,.35));Canvas->DrawItem(Item);
}
void ABodyHUD::Box(float X,float Y,float W,float H,FLinearColor C){DrawRect(C,X*Scale,Y*Scale,W*Scale,H*Scale);}
void ABodyHUD::Line(float X,float Y,float X2,float Y2,FLinearColor C,float Thick){DrawLine(X*Scale,Y*Scale,X2*Scale,Y2*Scale,C,Thick*Scale);}
void ABodyHUD::Ring(float X,float Y,float R,FLinearColor C,float Frac,float Thick)
{
    int N=64;for(int i=0;i<FMath::RoundToInt(N*Frac);i++){float a=2*PI*i/N-PI/2,b=2*PI*(i+1)/N-PI/2;Line(X+R*FMath::Cos(a),Y+R*FMath::Sin(a),X+R*FMath::Cos(b),Y+R*FMath::Sin(b),C,Thick);}
}
void ABodyHUD::DrawHUD()
{
    Super::DrawHUD();if(!Canvas)return;
    auto P=Cast<ABodyPawn>(GetOwningPawn());if(!P||!P->Body)return;auto B=P->Body;if(B->Photo)return;
    Scale=Canvas->SizeX/1920.f;float H=Canvas->SizeY/Scale;
    Ring(61,64,24,Mint,1,2);Ring(61,64,11,Gold,.7,3);
    Text("THAT BODY GAME",103,36,30,Cream);
    Text("A LITTLE CARE. A LIVING WORLD.",104,77,12,Soft);
    Box(39,124,248,1,FLinearColor(.53,.83,.74,.25));
    Text("01  /  A GENTLE MORNING",41,144,15,Mint);
    Text("You play attention.",41,173,22,Cream);
    Text(B->HasCompleted?"The body feels lighter.":"Go where you are needed.",41,209,15,Soft);
    // State reads are compact and secondary to the living organ animation.
    for(int i=0;i<3;i++)
    {
        float Y=284+i*82;
        Ring(54,Y+13,8,B->Organs[i].Cared?Mint:Soft,1,2);
        if(B->Organs[i].Cared)Box(51,Y+10,6,6,Mint);
        Text(B->Organs[i].Name,78,Y-1,14,B->Organs[i].Color);
        Text(B->Status(i),78,Y+24,13,Soft);
    }
    Text(P->Overview?"BODY ATLAS":"INSIDE THE BODY",1603,43,15,Cream);
    Text(P->Overview?"TAB  Return to attention":"TAB  See the whole body",1603,72,12,Soft);
    Text("H  Controls     M  Sound",1603,97,12,Soft);
    if(B->Muted)Text("Sound off",1775,124,11,Gold);

    // Minimal task ribbon at the foot of the screen.
    Box(420,H-130,1080,66,Ink);Box(420,H-130,3,66,Mint);
    Text(B->TaskInstruction(),449,H-112,18,Cream);
    Text("WASD / arrows  Move     SHIFT  Hurry     E  Care / carry     SPACE  Let a thought go",468,H-45,13,Soft);
    if(B->Carry)
    {
        Box(40,H-206,285,114,Ink);Ring(72,H-170,15,B->Carry==1?Mint:Gold,1,3);
        Text("IN YOUR HANDS",104,H-191,12,Soft);
        Text(B->Carry==1?"A deep breath":"A heartbeat",104,H-166,21,Cream);
        Text("One thing at a time.",62,H-125,12,Soft);
    }
    if(B->ToastTime>0)
    {
        float A=FMath::Min(B->ToastTime,1.f);
        Box(555,31,830,55,FLinearColor(.045,.063,.075,.86*A));
        Text(B->Toast,577,49,14,FLinearColor(.95,.91,.82,A));
    }
    if(P->Nearest>=0)
    {
        FVector2D S;GetOwningPlayerController()->ProjectWorldLocationToScreen(P->GetActorLocation()+FVector(0,0,210),S);
        S/=Scale;
        FString Hint;
        if(P->Nearest==0)Hint=B->Carry==2?"E  Give heartbeat":B->Carry==1?"Carry breath to the heart":"HOLD E  Pull the diaphragm";
        if(P->Nearest==1)Hint=B->Carry==1?"E  Place breath":B->Carry==2?"Carry heartbeat to the brain":B->BPM<=80?"E  Catch a heartbeat":"E  Ease rhythm   Q  Raise rhythm";
        if(P->Nearest==2)Hint=B->Carry?"E  Place in the awareness garden":B->ThoughtCount?"SPACE  Swat a small thought":"A moment of quiet";
        float W=FMath::Clamp(Hint.Len()*8.f+34,220.f,360.f);
        Box(S.X-W*.5,S.Y-24,W,43,Ink);Text(Hint,S.X-W*.5+16,S.Y-12,13,Cream);
        if(P->Nearest==0&&B->Pull>.02)
        {Box(S.X-95,S.Y+23,190,5,FLinearColor(.1,.2,.21,1));Box(S.X-95,S.Y+23,190*B->Pull,5,Mint);}
    }
    // Label the player when pulled back, without adding a permanent marker over the figure.
    if(P->Overview)
    {
        FVector2D S;GetOwningPlayerController()->ProjectWorldLocationToScreen(P->GetActorLocation()+FVector(0,0,150),S);S/=Scale;
        Ring(S.X,S.Y,16,Gold,1,2);Text("YOU",S.X+23,S.Y-6,12,Gold);
    }
    if(P->Help||B->Paused)
    {
        Box(0,0,1920,H,FLinearColor(.018,.03,.043,.74));Box(610,H*.5-245,700,490,Ink);
        Text(B->Paused?"A moment to pause.":"A little field guide.",660,H*.5-200,32,Cream);
        Text("WASD / arrows     Walk through the body",660,H*.5-133,18,Cream);
        Text("Hold E at lungs    Pull the diaphragm for a deep breath",660,H*.5-88,16,Soft);
        Text("E at an organ      Pick up or place the token you carry",660,H*.5-48,16,Soft);
        Text("SPACE at brain     Let a small thought go",660,H*.5-8,16,Soft);
        Text("TAB / wheel        Body atlas / zoom",660,H*.5+32,16,Soft);
        Text("Right drag  Orbit    Middle drag  Pan    HOME  Recenter",660,H*.5+72,16,Soft);
        Text("F8  Hide UI    F11  Fullscreen    R  New morning",660,H*.5+119,15,Mint);
        Text(B->Paused?"ESC  Continue":"H  Close field guide",660,H*.5+180,17,Gold);
    }
}
