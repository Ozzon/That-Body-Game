#include "BodyGame.h"
#include "Engine/Canvas.h"
#include "GameFramework/PlayerController.h"

void ABodyHUD::DrawHeartStudy(ABodyPawn* P)
{
    const FLinearColor Cream(.97,.90,.78),Quiet(.63,.68,.68),Gold(1,.70,.34),Ink(.025,.04,.06,.82);
    auto B=P->Body;float H=Canvas->SizeY/Scale;
    Text(B->StudyTitle,49,43,27,Cream);
    Text("1  Reference    2  Anatomical    3  Open courtyard",51,82,13,Quiet);
    Text("Right drag  Orbit    Wheel  Zoom",1570,46,13,Quiet);
    Text("Middle drag  Pan    HOME  Recenter",1570,71,12,Quiet);
    Text("H  Guide    F8  Hide interface",1570,96,12,Quiet);
    Ring(68,H-78,20,Gold,1,2);
    Text(FString::FromInt(FMath::RoundToInt(B->BPM)),55,H-90,20,Cream);
    Text(B->HasCompleted?"A steadier rhythm":"A little attention helps",106,H-95,17,Cream);
    Text(B->Carry?"A heartbeat in your hands":"Explore the four chambers",106,H-68,12,Quiet);
    if(P->Nearest==1)
    {
        Box(672,H-108,576,53,Ink);
        Text(B->Carry?"E  Return the heartbeat":B->BPM>76?"E  Gently steady the rhythm":"E  Hold a heartbeat",710,H-91,17,Cream);
    }
    else Text("WASD / arrows  Walk    SHIFT  Hurry    SPACE  Hop",665,H-67,14,Quiet);
    if(P->Help||B->Paused)
    {
        Box(0,0,1920,H,FLinearColor(.018,.03,.043,.72));Box(550,H*.5-220,820,440,Ink);
        Text(B->Paused?"A moment to pause.":"Inside the heart.",600,H*.5-174,32,Cream);
        Text("Walk through the arched passages to explore all four chambers.",600,H*.5-106,18,Cream);
        Text("Find the glowing valve. Press E to gently settle its rhythm.",600,H*.5-61,17,Quiet);
        Text("WASD  Walk     SHIFT  Hurry     SPACE  A little hop",600,H*.5-16,17,Quiet);
        Text("Right drag  Orbit     Wheel  Zoom     Middle drag  Pan",600,H*.5+29,17,Quiet);
        Text("TAB  Overview     HOME  Recenter     R  Reset the rhythm",600,H*.5+74,17,Quiet);
        Text(B->Paused?"ESC  Continue":"H  Close",600,H*.5+145,17,Gold);
    }
}
