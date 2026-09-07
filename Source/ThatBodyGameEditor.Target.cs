using UnrealBuildTool;
public class ThatBodyGameEditorTarget : TargetRules
{
    public ThatBodyGameEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("ThatBodyGame");
    }
}
