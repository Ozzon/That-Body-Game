from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[1];p=root/'Art/BrainCraft/Source/navigation.npz';d=np.load(p);x=d['x'];y=d['y'];h=d['h'];mask=d['walk'];X,Y=np.meshgrid(x,y,indexing='ij');mask&=np.hypot(X-1580,Y+1390)>342
np.savez_compressed(p,x=x,y=y,h=h,walk=mask)
p=root/'Tools/craft_routes.py';s=p.read_text().replace('(1530,-1670)','(1530,-1775)');p.write_text(s)
p=root/'Source/ThatBodyGame/BrainCraft.cpp';s=p.read_text().replace('GetCharacterMovement()->MaxStepHeight=30','GetCharacterMovement()->MaxStepHeight=45').replace('GetActorLocation(),Lotus)<360','GetActorLocation(),Lotus)<430');p.write_text(s)
p=root/'Source/ThatBodyGame/BrainCraftReview.cpp';s=p.read_text().replace('Brain-C07-','Brain-C08-').replace('brain-c07-input-report','brain-c08-input-report');s=s.replace('MoveKeys(Delta);return;\n    }','if(FMath::Fmod(SmokeClock,8)<Dt)UE_LOG(LogTemp,Display,TEXT("CRAFT_ROUTE_PROGRESS leg=%d waypoint=%d target=%s position=%s"),Leg,Waypoint,*Target.ToString(),*GetActorLocation().ToString());MoveKeys(Delta);return;\n    }',1);p.write_text(s)
