# Deny Probability Model

## Calculation
1. Score each factor 0-10
2. Apply department-specific weights
3. Weighted sum / Max possible = Raw probability
4. Adjust by department base rate

## Department Weights (sum = 1.0)
| Factor | Cath Lab | OR | ER | ICU | Dialysis | Chemo | OPD |
|--------|---------|-----|-----|-----|----------|-------|-----|
| Dx-Proc | 0.15 | 0.15 | 0.10 | 0.10 | 0.10 | 0.15 | 0.10 |
| CC/MCC | 0.15 | 0.10 | 0.05 | 0.20 | 0.05 | 0.05 | 0.05 |
| LOS | 0.05 | 0.10 | 0.05 | 0.15 | 0.02 | 0.05 | 0.02 |
| Docs | 0.15 | 0.15 | 0.15 | 0.10 | 0.08 | 0.15 | 0.08 |
| Timing | 0.10 | 0.10 | 0.15 | 0.05 | 0.15 | 0.10 | 0.15 |
| Drugs | 0.05 | 0.02 | 0.05 | 0.05 | 0.20 | 0.20 | 0.25 |
| Device | 0.15 | 0.15 | 0.02 | 0.02 | 0.02 | 0.02 | 0.02 |
| DRG | 0.10 | 0.10 | 0.08 | 0.10 | 0.08 | 0.08 | 0.08 |
| History | 0.05 | 0.08 | 0.15 | 0.08 | 0.10 | 0.10 | 0.10 |
| Payer | 0.05 | 0.05 | 0.20 | 0.15 | 0.20 | 0.10 | 0.15 |

## Risk Levels
- 0-25%: LOW → submit with confidence
- 26-50%: MEDIUM → review before submit
- 51-75%: HIGH → fix issues before submit
- 76-100%: VERY HIGH → do not submit until fixed
