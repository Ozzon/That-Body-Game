using UnrealBuildTool;
public class ThatBodyGameTarget : TargetRules
{
    public ThatBodyGameTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("ThatBodyGame");
    }
}
