---
id: "trading/regulations/ai-communications/rules"
title: "AI Communications Compliance"
domain: "trading"
version: "1.0.0"
category: "regulations"
tags:
  - ai-supervision
  - finra-24-09
  - communications
  - rule-2210
  - model-risk
  - compliance
severity: "CRITICAL"
last_verified: "2026-03-15"
applies_to:
  - trading-agents
  - portfolio-management-systems
  - customer-facing-ai-tools
  - chatbots
related:
  - "trading/regulations/suitability/rules"
  - "trading/regulations/options-trading/rules"
---

# AI Communications Compliance

## Summary

FINRA Notice 24-09 (August 2024) explicitly states that AI-generated customer-facing content is subject to FINRA Rule 2210 (Communications with the Public). This means any AI agent, chatbot, or automated system that generates investment-related content for customers — including trade recommendations, market explanations, portfolio summaries, or risk alerts — must comply with the same rules as a human financial advisor's written communications. The firm is responsible for AI outputs regardless of whether the AI is built in-house or by a third-party vendor. This rule governs the agent itself.

## The Problem

An AI trading agent that generates customer-facing content without compliance controls will violate securities regulations: (1) making return predictions or guarantees ("this stock will go up 20%"), (2) omitting required risk disclosures, (3) providing recommendations without suitability analysis (Reg BI), (4) failing to retain AI interaction records for the required 3+ years, (5) discriminating in service quality by demographics. FINRA has explicitly stated that "the use of AI does not change a firm's obligations" — the agent IS the communication, and the firm IS liable.

## Rules

1. **FINRA Rule 2210 applies to ALL AI-generated customer-facing content.** This includes chatbot responses, automated alerts, trade confirmations with commentary, portfolio analysis summaries, educational content, and social media posts. If an AI produces text that a customer sees and it relates to securities, Rule 2210 applies. No exceptions for "it's just a chatbot."

2. **AI trade recommendations must meet Reg BI / suitability.** If the AI suggests, recommends, or implies a customer should buy, sell, or hold a security, that output must satisfy Regulation Best Interest (for broker-dealers) or the fiduciary standard (for investment advisers). The AI must consider the customer's investment profile, risk tolerance, financial situation, and investment objectives before making recommendations.

3. **Firm is responsible for third-party AI outputs.** A firm cannot disclaim liability by saying "our AI vendor generated that." FINRA Notice 24-09 explicitly states that firms bear responsibility for all AI-generated communications regardless of source. This applies to embedded third-party models, API-based AI services, and white-label chatbots.

4. **No guarantees, predictions, or promissory statements about returns.** AI must never state or imply: "this investment will return X%", "guaranteed income", "can't lose money", "sure thing." This includes hedged language that effectively makes predictions ("historically always recovers" as an implied guarantee). Probabilistic statements must include clear uncertainty disclaimers.

5. **Must disclose material risks on every investment-related output.** Every AI-generated message that discusses a specific investment must include or reference material risks. For options: risk of total loss. For margin: risk of losses exceeding initial investment. For crypto: no SIPC coverage. For concentrated positions: lack of diversification. Generic disclaimers are insufficient — risks must be specific to the investment discussed.

6. **Model risk management: governance, validation, monitoring, testing.** Firms must implement model risk management for AI systems (aligned with OCC/Fed SR 11-7 guidance). This includes: model documentation, independent validation, ongoing monitoring, change management, and regular testing. AI models that drift or degrade must be caught before producing non-compliant output.

7. **Record retention: AI interactions retained 3+ years.** FINRA Rule 4511 requires firms to retain business communications for at least 3 years (6 years for some categories). AI-generated content and the full interaction context (user query + AI response + model version) must be retained. This is not optional — it is auditable by FINRA examiners.

8. **AI must not discriminate in quality of service by demographics.** AI systems must not provide different quality of service, recommendations, or information based on protected characteristics (race, gender, age, etc.). This includes both intentional discrimination and disparate impact from biased training data. Fair lending and fair dealing obligations apply.

9. **Supervision requirements (Rule 3110) must cover AI tools.** The firm's supervisory system must include procedures for reviewing AI outputs. A registered principal must be designated to supervise AI-generated communications. The supervision can be pre-use (review before sending) or post-use (statistical sampling and review), but it must exist and be documented.

10. **Third-party AI tools carry same obligations as proprietary ones.** Using OpenAI, Anthropic, or any third-party AI does not reduce compliance obligations. The firm must: evaluate the third-party model, establish controls for its output, monitor for compliance, and retain records. "We used ChatGPT" is not a defense.

## Examples

### Compliant vs non-compliant AI output
```
NON-COMPLIANT:
"Based on strong earnings, AAPL is likely to reach $200 by year end.
 I recommend buying 100 shares."

COMPLIANT:
"AAPL reported earnings above consensus estimates. Past performance
 does not guarantee future results. Any investment in individual
 stocks carries risk of loss, including total loss of principal.
 This information is not a personalized recommendation. Please
 consider your investment objectives and risk tolerance before
 making investment decisions."
```

### Required disclaimer elements
```
Minimum AI-generated content disclaimer should include:
1. "AI-generated content" disclosure
2. "Not a personalized recommendation" (unless suitability was performed)
3. Material risk factors specific to the investment type
4. "Past performance does not guarantee future results"
5. Direction to consult financial advisor for personalized advice
```

### Record retention structure
```
AI Interaction Record:
  timestamp: "2026-03-15T14:30:00Z"
  customer_id: "anonymized_hash"
  model_version: "agent-v2.1.3"
  user_query: "Should I buy more TSLA?"
  ai_response: "..." (full text)
  compliance_flags: ["recommendation_detected", "disclaimer_included"]
  review_status: "pending_supervisory_review"
  retention_expiry: "2029-03-15"
```

## Agent Checklist

- [ ] Every AI-generated investment-related message includes risk disclaimers
- [ ] Never generate return predictions, guarantees, or promissory language
- [ ] Before generating recommendations, verify suitability/Reg BI analysis exists
- [ ] All AI interactions are logged with full context for 3+ year retention
- [ ] AI output is subject to supervisory review process (pre or post)
- [ ] Third-party AI outputs are monitored and controlled like proprietary ones
- [ ] Test AI outputs for bias and discriminatory patterns regularly
- [ ] AI-generated content is clearly labeled as AI-generated
- [ ] Model version is tracked in interaction records for audit trail

## Structured Checks

```yaml
checks:
  - id: ai_disclaimer_present
    condition: "is_ai_generated != 'true' OR has_risk_disclaimer == 'true'"
    severity: high
    message: "AI-generated investment content must include risk disclaimers"
  - id: ai_no_guarantees
    condition: "is_ai_generated != 'true' OR contains_return_prediction == 'false'"
    severity: critical
    message: "AI must not make guarantees or predictions about investment returns"
```

## Sources

- FINRA Notice 24-09 (AI in Securities Industry): https://www.finra.org/rules-guidance/notices/24-09
- FINRA Rule 2210 (Communications with the Public): https://www.finra.org/rules-guidance/rulebooks/finra-rules/2210
- FINRA Rule 3110 (Supervision): https://www.finra.org/rules-guidance/rulebooks/finra-rules/3110
- FINRA Rule 4511 (Books and Records): https://www.finra.org/rules-guidance/rulebooks/finra-rules/4511
- SEC Regulation Best Interest: https://www.sec.gov/regulation-best-interest
- OCC/Fed SR 11-7 (Model Risk Management): https://www.federalreserve.gov/supervisionreg/srletters/sr1107.htm
