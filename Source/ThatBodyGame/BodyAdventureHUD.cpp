#include "BodyGame.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"

void ABodyHUD::DrawAdventure(ABodyPawn* P)
{
    auto B=P->Body;float H=Canvas->SizeY/Scale;
    const FLinearColor Cream(.98,.93,.83),Quiet(.67,.74,.72),Mint(.56,.89,.74),Gold(1,.75,.39),Ink(.025,.04,.065,.83);
    if(P->Overview&&B->GardenPreview)
    {
        Box(0,0,1920,H,FLinearColor(.024,.042,.06,.99));
        Text("A LIVING WORLD",90,72,15,Mint);Text("The body atlas",90,113,38,Cream);
        Text("Every organ, a place to care for.",90,171,17,Quiet);
        const FVector2D Nodes[]={FVector2D(565,255),FVector2D(390,435),FVector2D(740,435),FVector2D(565,470),FVector2D(430,630),FVector2D(700,630),FVector2D(565,790),FVector2D(365,795),FVector2D(765,795),FVector2D(565,920)};
        for(int i=1;i<10;i++){int Parent=i<4?0:i<6?3:i==9?6:4;Line(Nodes[Parent].X,Nodes[Parent].Y,Nodes[i].X,Nodes[i].Y,FLinearColor(.19,.36,.32),3);}
        const TCHAR* Labels[]={TEXT("BRAIN"),TEXT("RIGHT LUNG"),TEXT("LEFT LUNG"),TEXT("HEART"),TEXT("LIVER"),TEXT("STOMACH"),TEXT("INTESTINES"),TEXT("KIDNEY"),TEXT("KIDNEY"),TEXT("BLADDER")};
        for(int i=0;i<10;i++){auto Q=Nodes[i];Ring(Q.X,Q.Y,i==0?36:23,i==0?Gold:Mint,1,3);Text(Labels[i],Q.X-45,Q.Y+42,13,i==0?Cream:Quiet);}
        Box(1020,270,710,555,FLinearColor(.05,.077,.09,.96));Text("YOU ARE HERE",1060,312,13,Gold);Text("The Awareness Garden",1060,358,30,Cream);
        Text("A meadow to arrive in.",1060,438,20,Cream);Text("A tree to bring bright thoughts home to.",1060,481,20,Cream);Text("A quiet garden across the water.",1060,524,20,Cream);
        Text("Care opens a shorter way home.",1060,610,17,Mint);
        Text("TAB  Return to the garden",1060,734,19,Gold);
        Text("Light passages connect the body. Each interior has its own landscape.",90,H-60,15,Quiet);
        return;
    }
    Text("THAT BODY GAME",43,32,27,Cream);Text("A LITTLE CARE. A LIVING WORLD.",45,69,11,Quiet);
    Text(P->Overview?"THE BODY ATLAS":B->AdventurePlace(P->GetActorLocation()),43,111,16,Mint);
    Text("Right drag  Orbit   Wheel  Zoom",1550,39,13,Quiet);Text("Middle drag  Pan   HOME  Recenter",1550,64,12,Quiet);Text("TAB  Atlas   H  Guide",1550,89,12,Quiet);
    if(!P->Overview)
    {
        if(B->GardenPreview)
        {Text(FString::Printf(TEXT("THOUGHTS  %d / 3"),B->GardenDelivered),45,H-48,13,Mint);Text(B->GardenFocused?TEXT("LOTUS  OPEN"):TEXT("LOTUS  RESTING"),210,H-48,13,Quiet);Text(FString::Printf(TEXT("WORRIES  %d / 4"),4-B->ThoughtCount),390,H-48,13,Quiet);}
        else for(int i=0;i<3;i++){float X=45+i*151;Ring(X+8,H-43,7,B->Organs[i].Cared?Mint:Quiet,B->Organs[i].Cared?1:.22,2);Text(B->Organs[i].Name,X+25,H-51,12,B->Organs[i].Cared?Mint:Quiet);}
        Box(490,H-112,960,55,Ink);Text(B->TaskInstruction(),515,H-94,16,Cream);
        if(P->Nearest>=0)
        {
            FString Prompt;
            switch(P->Nearest){case 0:Prompt=TEXT("HOLD E  Draw a deep breath");break;case 1:Prompt=B->Carry?TEXT("E  Place what you carry"):B->BPM<=80?TEXT("E  Catch a heartbeat"):TEXT("E  Gently steady the rhythm");break;case 2:Prompt=B->Carry?TEXT("E  Nourish awareness"):TEXT("SPACE  Let a nearby thought go");break;case 3:Prompt=TEXT("E  Gather warm energy");break;case 4:Prompt=TEXT("E  Clear the recovery pool");break;case 5:Prompt=TEXT("HOLD E  Release calm");break;case 6:Prompt=TEXT("HOLD E  Release energy");break;case 7:Prompt=TEXT("E  Carry the heavy cloud");break;}
            Text(Prompt,715,H-155,18,Gold);
            if(P->Nearest>=8&&P->Nearest<=10)Text("E  Carry the bright thought",715,H-155,18,Gold);
            if(P->Nearest==11){Text("HOLD E  Open the focus lotus",715,H-155,18,Gold);Box(810,H-180,290,5,Ink);Box(810,H-180,290*B->GardenFocusPull,5,Mint);}
            if(P->Nearest==0&&B->Pull>0){Box(810,H-180,290,5,Ink);Box(810,H-180,290*B->Pull,5,Mint);}
        }
        Text("WASD  Walk   SHIFT  Hurry   SPACE  Hop",1460,H-46,12,Quiet);
        if(B->ToastTime>0)Text(B->Toast,45,149,14,Quiet);
    }
    else
    {
        const FVector At[]={FVector(9250,0,700),FVector(2300,-3050,550),FVector(2300,3050,550),FVector(1400,0,550),FVector(-2900,-2050,550),FVector(-2900,2250,550),FVector(-5850,-3400,550),FVector(-5850,3400,550),FVector(-7700,0,550),FVector(-10700,0,550)};
        const TCHAR* Names[]={TEXT("BRAIN"),TEXT("RIGHT LUNG"),TEXT("LEFT LUNG"),TEXT("HEART"),TEXT("LIVER"),TEXT("STOMACH"),TEXT("KIDNEY"),TEXT("KIDNEY"),TEXT("INTESTINES"),TEXT("BLADDER")};
        auto PC=GetOwningPlayerController();for(int i=0;i<10;i++){FVector2D Q;if(PC->ProjectWorldLocationToScreen(At[i],Q)){Q/=Scale;Text(Names[i],Q.X-25,Q.Y-13,12,Cream);}}
        Text("1  Breathing   2  Heart   3  Brain   4  Stomach   5  Liver   6  Calm spring",530,H-65,16,Cream);
    }
    if(P->Help||B->Paused)
    {
        Box(0,0,1920,H,FLinearColor(.018,.028,.04,.8));Box(480,H*.5-240,960,480,Ink);
        Text(B->Paused?"A moment to pause.":"Play attention.",530,H*.5-194,34,Cream);
        Text("Draw breath in the glade, bring it to the heart, then carry a",530,H*.5-125,19,Cream);Text("heartbeat up to the brain. Let its four small thoughts go.",530,H*.5-92,19,Cream);
        Text("Explore the lower body for warm energy, recovery and calm.",530,H*.5-43,17,Mint);
        Text("WASD  Walk   SHIFT  Hurry   E  Care / carry   SPACE  Hop / release thought",530,H*.5+8,16,Quiet);
        Text("Right drag  Orbit   Wheel  Zoom   Middle drag  Pan   HOME  Recenter",530,H*.5+46,16,Quiet);
        Text("TAB  Atlas   1-6  Visit an organ   F8  Hide UI   F11  Fullscreen   R  Restart",530,H*.5+84,16,Quiet);
        Text(B->Paused?"ESC  Continue":"H  Close guide",530,H*.5+167,17,Gold);
    }
}
