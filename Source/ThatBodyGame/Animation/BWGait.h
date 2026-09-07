// BOTWRECKED - the walk cycle and two-bone limb solve.
// Ported from Botathlon Core/BRGait.h (itself from the Insects project). The load-bearing findings, kept:
//   * A LEG DRIVEN BY A SINE NEVER STOPS. A planted foot is not moving; the body travels over it. Stance moves the
//     foot backwards in body space at exactly ground rate; swing returns it over the shorter cycle part.
//   * PHASE ADVANCES WITH MEASURED DISTANCE, NOT TIME. Legs stop when the robot stops.
//   * reach = Duty * Stride / 2 is DERIVED, never authored.
//   * SolveLimb: past the reach ceiling the FOOT is re-spanned down the chord. Bones never stretch.
// In BOTWRECKED these produce TARGETS for simulated two-segment limbs whose joint drives chase them.
#pragma once

#include "CoreMinimal.h"

namespace BWGait
{
	struct FParams
	{
		float StrideLength = 100.f;   // ground covered by one full cycle of one leg, cm
		float Duty = 0.6f;            // fraction of the cycle a foot is planted
		float MaxReach = 1.e6f;       // the largest fore/aft travel the limb can make, cm
	};

	struct FFoot
	{
		float Along = 0.f;   // fore/aft offset from the rest position, cm; positive is forward
		float Lift = 0.f;    // height above the rest position, cm; zero whenever planted
		bool bPlanted = true;
	};

	inline float ZeroSkateReach(const FParams& P)
	{
		return FMath::Max(P.StrideLength, 0.f) * FMath::Clamp(P.Duty, 0.f, 1.f) * 0.5f;
	}

	inline float EffectiveReach(const FParams& P)
	{
		return FMath::Min(ZeroSkateReach(P), FMath::Max(P.MaxReach, 0.f));
	}

	inline float CadenceHz(float Speed, const FParams& P)
	{
		return (P.StrideLength > UE_KINDA_SMALL_NUMBER) ? FMath::Abs(Speed) / P.StrideLength : 0.f;
	}

	/** Advance the cycle by the ground actually covered (feed measured speed, never intent). Phase in [0,1). */
	inline float AdvancePhase(float Phase, float Speed, float DeltaSeconds, const FParams& P)
	{
		if (P.StrideLength <= UE_KINDA_SMALL_NUMBER) { return Phase; }
		const float Advance = (FMath::Abs(Speed) * FMath::Max(DeltaSeconds, 0.f)) / P.StrideLength;
		return FMath::Fmod(Phase + Advance, 1.f);
	}

	/** Sample one foot. Offset = this leg's place in the cycle. Amount 0 restores the rest pose. */
	inline FFoot Sample(float Phase, float Offset, const FParams& P, float Amount = 1.f, bool bGrounded = true)
	{
		const float A = FMath::Clamp(Amount, 0.f, 1.f);
		const float D = FMath::Clamp(P.Duty, 0.05f, 0.95f);
		const float Reach = EffectiveReach(P) * A;
		const float P01 = FMath::Fmod(FMath::Fmod(Phase + Offset, 1.f) + 1.f, 1.f);

		FFoot Out;
		if (P01 < D)
		{
			// STANCE: linear, because every mismatch from ground rate is skate.
			Out.Along = FMath::Lerp(Reach, -Reach, P01 / D);
			Out.Lift = 0.f;
			Out.bPlanted = true;
		}
		else
		{
			// SWING: over the shorter part of the cycle, ease-out on the reach so the foot arrives near ground rate.
			const float T = (P01 - D) / (1.f - D);
			const float TE = 1.f - (1.f - T) * (1.f - T);
			Out.Along = FMath::Lerp(-Reach, Reach, TE);
			Out.Lift = FMath::Sin(T * PI) * Reach * 0.35f;
			Out.bPlanted = false;
		}
		if (!bGrounded) { Out.bPlanted = false; }
		return Out;
	}

	/** Duty falls with speed: walk ~Duty, run Duty-0.09 (never below 0.5). */
	inline float DutyAtSpeed(float WalkDuty, float Speed01)
	{
		const float RunDuty = FMath::Min(FMath::Max(WalkDuty - 0.09f, 0.5f), WalkDuty);
		const float T = FMath::Clamp((Speed01 - 0.30f) / 0.25f, 0.f, 1.f);
		return FMath::Lerp(WalkDuty, RunDuty, T);
	}

	struct FLimb
	{
		FVector Knee = FVector::ZeroVector;
		FVector Foot = FVector::ZeroVector;   // where the foot ended up (moved down the chord if clamped)
		float KneeDeg = 0.f;                  // interior angle at the knee; 180 is a straight stick
		bool bClamped = false;
		float Excess = 0.f;
	};

	/**
	 * Two bones, one knee, and a ceiling the limb cannot straighten past.
	 * Pole = WHICH WAY THE KNEE BENDS, a direction; only its component across hip->foot survives.
	 * MaxExt = fraction of (L1+L2) the limb may span, never 1.
	 */
	inline FLimb SolveLimb(const FVector& Hip, const FVector& Foot, float L1, float L2, const FVector& Pole, float MaxExt)
	{
		FLimb Out;
		Out.Foot = Foot;
		const FVector ToFoot = Foot - Hip;
		const FVector Dir = ToFoot.GetSafeNormal();
		if (Dir.IsNearlyZero())
		{
			Out.Knee = Hip + FVector(0.f, 0.f, L1);
			return Out;
		}
		const float Demand = static_cast<float>(ToFoot.Size());
		const float Ceil = (L1 + L2) * FMath::Clamp(MaxExt, 0.1f, 0.999f);
		const float D = FMath::Clamp(Demand, FMath::Abs(L1 - L2) + 0.01f, Ceil);
		Out.bClamped = (Demand > Ceil);
		Out.Excess = FMath::Max(Demand - Ceil, 0.f);
		Out.Foot = Hip + Dir * D;

		const float A = FMath::Clamp((L1 * L1 - L2 * L2 + D * D) / (2.f * D), -L1, L1);
		const float H = FMath::Sqrt(FMath::Max(L1 * L1 - A * A, 0.f));
		const float CosKnee = FMath::Clamp((L1 * L1 + L2 * L2 - D * D) / (2.f * L1 * L2), -1.f, 1.f);
		Out.KneeDeg = FMath::RadiansToDegrees(FMath::Acos(CosKnee));

		FVector Perp = Pole;
		Perp -= Dir * (Perp | Dir);
		if (!Perp.Normalize())
		{
			Perp = FVector::CrossProduct(Dir, FVector::UpVector);
			if (!Perp.Normalize()) { Perp = FVector::RightVector; }
		}
		Out.Knee = Hip + Dir * A + Perp * H;
		return Out;
	}

	/** Turn lean (Botathlon D49): lean = atan(v * w / g), capped. Speed cm/s, yaw rate rad/s. */
	inline float TurnLeanDeg(float Speed, float YawRateRad, float MaxDeg = 28.f, float GravityCm = 980.f)
	{
		return FMath::Clamp(FMath::RadiansToDegrees(FMath::Atan(Speed * YawRateRad / GravityCm)), -MaxDeg, MaxDeg);
	}
}
