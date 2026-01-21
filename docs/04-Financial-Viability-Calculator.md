# Financial Viability Calculator

## Instructions
This calculator helps you model the financial viability of your vertical AI agent business.

Copy the sections below into Google Sheets or Excel, or use this as a reference for your own spreadsheet.

---

## SECTION 1: REVENUE MODEL

### Pricing Tiers

| Tier | Monthly Price | Features | Target Customers | Expected Mix % |
|------|---------------|----------|------------------|----------------|
| Starter | $500 | 1 use case, email delivery | Small companies | 40% |
| Growth | $1,500 | 3 use cases, Slack integration | Mid-market | 40% |
| Enterprise | $3,000 | Unlimited, API access | Large companies | 20% |

---

### Revenue Projections (12 Months)

| Month | Starter ($500) | Growth ($1,500) | Enterprise ($3,000) | Total Customers | Monthly Revenue | Cumulative Revenue |
|-------|----------------|-----------------|---------------------|-----------------|-----------------|-------------------|
| 1 | 2 | 0 | 0 | 2 | $1,000 | $1,000 |
| 2 | 3 | 1 | 0 | 4 | $2,000 | $3,000 |
| 3 | 5 | 2 | 0 | 7 | $5,500 | $8,500 |
| 4 | 6 | 3 | 1 | 10 | $10,000 | $18,500 |
| 5 | 7 | 4 | 1 | 12 | $12,500 | $31,000 |
| 6 | 8 | 5 | 1 | 14 | $14,500 | $45,500 |
| 7 | 9 | 6 | 2 | 17 | $19,500 | $65,000 |
| 8 | 10 | 7 | 2 | 19 | $22,000 | $87,000 |
| 9 | 11 | 8 | 2 | 21 | $23,500 | $110,500 |
| 10 | 12 | 9 | 3 | 24 | $28,500 | $139,000 |
| 11 | 13 | 10 | 3 | 26 | $30,500 | $169,500 |
| 12 | 14 | 11 | 4 | 29 | $35,500 | $205,000 |

**Year 1 Total Revenue:** $205,000
**Month 12 MRR:** $35,500
**Average Revenue Per Customer:** $1,224/month

---

## SECTION 2: COST STRUCTURE

### Fixed Monthly Costs

| Category | Item | Monthly Cost | Notes |
|----------|------|--------------|-------|
| **Software/Tools** | n8n hosting | $20 | Self-hosted option = $0 |
| | Claude API (base) | $100 | Scales with usage |
| | Airtable/Database | $20 | Pro plan |
| | Slack/Email APIs | $0 | Free tiers |
| | Domain/hosting | $10 | Annual = $120 |
| **Subscriptions** | LinkedIn Sales Nav | $80 | For customer acquisition |
| | Design tools (Canva) | $15 | Marketing materials |
| | Analytics/tracking | $20 | Posthog or similar |
| **TOTAL FIXED** | | **$265/month** | |

---

### Variable Costs (Per Customer)

| Category | Cost per Customer/Month | Notes |
|----------|-------------------------|-------|
| Claude API usage | $15-50 | Depends on data volume |
| Data processing/storage | $5 | Scales linearly |
| Support time (your hours) | $25 | ~30 min/customer at $50/hr |
| **TOTAL VARIABLE** | **$45-80/customer** | Use $60 average |

---

### Monthly Cost Projections

| Month | Customers | Fixed Costs | Variable Costs | Total Costs | Revenue | Profit | Cumulative Profit |
|-------|-----------|-------------|----------------|-------------|---------|--------|-------------------|
| 1 | 2 | $265 | $120 | $385 | $1,000 | $615 | $615 |
| 2 | 4 | $265 | $240 | $505 | $2,000 | $1,495 | $2,110 |
| 3 | 7 | $265 | $420 | $685 | $5,500 | $4,815 | $6,925 |
| 4 | 10 | $265 | $600 | $865 | $10,000 | $9,135 | $16,060 |
| 5 | 12 | $265 | $720 | $985 | $12,500 | $11,515 | $27,575 |
| 6 | 14 | $265 | $840 | $1,105 | $14,500 | $13,395 | $40,970 |
| 7 | 17 | $265 | $1,020 | $1,285 | $19,500 | $18,215 | $59,185 |
| 8 | 19 | $265 | $1,140 | $1,405 | $22,000 | $20,595 | $79,780 |
| 9 | 21 | $265 | $1,260 | $1,525 | $23,500 | $21,975 | $101,755 |
| 10 | 24 | $265 | $1,440 | $1,705 | $28,500 | $26,795 | $128,550 |
| 11 | 26 | $265 | $1,560 | $1,825 | $30,500 | $28,675 | $157,225 |
| 12 | 29 | $265 | $1,740 | $2,005 | $35,500 | $33,495 | $190,720 |

**Year 1 Profit:** $190,720
**Profit Margin (Month 12):** 94%
**Break-even:** Month 1 (very achievable with this model)

---

## SECTION 3: TIME INVESTMENT

### Startup Phase (Months 1-3)

| Activity | Hours/Week | Total Hours (12 weeks) |
|----------|------------|------------------------|
| Research & validation | 10 | 120 |
| Building agent/automation | 15 | 180 |
| Customer acquisition | 10 | 120 |
| Onboarding customers | 5 | 60 |
| Product refinement | 5 | 60 |
| **TOTAL** | **45** | **540 hours** |

**Equivalent to:** Full-time for 3 months

---

### Steady State (Months 4-12)

| Activity | Hours/Week | Notes |
|----------|------------|-------|
| Customer support | 5 | 30 min per customer avg |
| Sales & marketing | 10 | Outreach, demos |
| Product improvements | 3 | Monthly updates |
| Admin/invoicing | 2 | Automated mostly |
| **TOTAL** | **20/week** | Part-time |

**By Month 12:** ~15 hours/week as automation improves

---

### Hourly Rate Calculation

**Month 12:**
- Monthly Profit: $33,495
- Hours Worked: ~60/month
- **Effective Hourly Rate:** $558/hour

**Year 1 Average:**
- Total Profit: $190,720
- Total Hours: ~1,000
- **Effective Hourly Rate:** $191/hour

---

## SECTION 4: CUSTOMER ACQUISITION

### Customer Acquisition Cost (CAC)

| Channel | Cost per Customer | Conversion Rate | Time to Close |
|---------|-------------------|-----------------|---------------|
| LinkedIn outreach (warm) | $50 | 10% | 2 weeks |
| Referrals | $0 | 30% | 1 week |
| Content marketing | $100 | 5% | 4 weeks |
| Cold email | $75 | 3% | 3 weeks |
| **Blended CAC** | **$60** | | |

---

### Customer Lifetime Value (LTV)

**Assumptions:**
- Average customer stays: 18 months
- Average monthly payment: $1,224
- Gross margin: 90%

**Calculation:**
- LTV = $1,224 × 18 months × 90% = **$19,829**

**LTV:CAC Ratio:** 19,829 / 60 = **330:1**
(Excellent - anything above 3:1 is good)

---

### Monthly Customer Acquisition Targets

| Month | New Customers | CAC Budget | Total CAC Spend | Cumulative Customers |
|-------|---------------|------------|-----------------|---------------------|
| 1 | 2 | $120 | $120 | 2 |
| 2 | 2 | $120 | $240 | 4 |
| 3 | 3 | $180 | $420 | 7 |
| 4 | 3 | $180 | $600 | 10 |
| 5 | 2 | $120 | $720 | 12 |
| 6 | 2 | $120 | $840 | 14 |
| 7 | 3 | $180 | $1,020 | 17 |
| 8 | 2 | $120 | $1,140 | 19 |
| 9 | 2 | $120 | $1,260 | 21 |
| 10 | 3 | $180 | $1,440 | 24 |
| 11 | 2 | $120 | $1,560 | 26 |
| 12 | 3 | $180 | $1,740 | 29 |

**Note:** These CAC costs are included in the Variable Costs above

---

## SECTION 5: SENSITIVITY ANALYSIS

### Scenario Planning

| Scenario | Price Point | Customers (Mo 12) | Monthly Revenue | Annual Profit | Notes |
|----------|-------------|-------------------|-----------------|---------------|-------|
| **Conservative** | $800 avg | 20 | $16,000 | $140,000 | Slower growth |
| **Base Case** | $1,224 avg | 29 | $35,500 | $190,720 | Current model |
| **Optimistic** | $1,500 avg | 40 | $60,000 | $380,000 | Fast growth |

---

### Break-Even Analysis

**At different price points:**

| Monthly Price | Customers Needed | Achievable by Month |
|---------------|------------------|---------------------|
| $500 | 2 | Month 1 |
| $1,000 | 1 | Month 1 |
| $1,500 | 1 | Month 1 |
| $3,000 | 1 | Month 1 |

**Conclusion:** Break-even is immediate with any pricing model

---

### Churn Impact

**If churn rate is:**
- 0% (ideal): Revenue grows as modeled
- 5%/month (acceptable): Reduces Month 12 to 24 customers
- 10%/month (concerning): Reduces Month 12 to 18 customers

**Mitigation:**
- Focus on customer success
- Conservative agent approach (fewer errors)
- Regular check-ins
- Quick issue resolution

---

## SECTION 6: FUNDING REQUIREMENTS

### Bootstrap Scenario (Recommended)

**Initial Investment Needed:** $2,000

**Breakdown:**
- Tools/software (3 months): $800
- Marketing/CAC (first customers): $600
- Buffer for testing: $600

**Funding Source:** Personal savings / side income

**Time to Profitability:** Month 1
**Time to ROI:** Month 3

---

### Self-Funded Growth

| Milestone | Cumulative Profit | Reinvest | Take Home |
|-----------|-------------------|----------|-----------|
| Month 3 | $6,925 | $2,000 | $4,925 |
| Month 6 | $40,970 | $5,000 | $35,970 |
| Month 9 | $101,755 | $10,000 | $91,755 |
| Month 12 | $190,720 | $20,000 | $170,720 |

**No external funding required**

---

## SECTION 7: RISK ANALYSIS

### Risk Register

| Risk | Probability | Impact | Mitigation | Cost of Mitigation |
|------|-------------|--------|------------|-------------------|
| Can't find customers | Medium | High | Validate before building | $0 (time only) |
| Customers won't pay price | Medium | High | Validate pricing in discovery | $0 (time only) |
| AI costs spike | Low | Medium | Use cheaper models (Haiku) | $0 (design choice) |
| Competitor launches | Medium | Medium | Build domain moat | $0 (focus) |
| Technical challenges | Medium | Medium | Start simple, iterate | $0 (process) |
| Churn too high | Medium | High | Focus on customer success | $0 (attention) |

---

### Worst Case Scenario

**If everything goes wrong:**
- Only get 5 customers by Month 12
- Price at $500/month (low end)
- 20% monthly churn

**Result:**
- Monthly Revenue: $2,500
- Monthly Costs: $565
- Monthly Profit: $1,935
- Annual Profit: $23,220

**Still profitable!** Low fixed costs = resilient model

---

## SECTION 8: DECISION METRICS

### Go/No-Go Criteria

**Proceed to build if:**
- [ ] Year 1 profit projection > $100K
- [ ] Break-even < 3 months
- [ ] LTV:CAC ratio > 5:1
- [ ] Time investment < 50 hours/week (Month 1-3)
- [ ] Steady state < 20 hours/week (Month 4+)
- [ ] Initial investment < $5,000
- [ ] 3+ pilot customers committed

**If 6/7 checked:** Strong go

---

### Key Performance Indicators (Track Weekly)

| KPI | Target | Month 3 | Month 6 | Month 12 |
|-----|--------|---------|---------|----------|
| MRR | | $5,500 | $14,500 | $35,500 |
| Customers | | 7 | 14 | 29 |
| CAC | < $100 | $60 | $60 | $60 |
| LTV | > $15K | $19,829 | $19,829 | $19,829 |
| Churn Rate | < 5% | 0% | 2% | 3% |
| Hours/Week | | 45 | 25 | 15 |
| Customer Health Score | > 8/10 | 9/10 | 8.5/10 | 8/10 |

---

## SECTION 9: YOUR CUSTOM MODEL

### Personalize This Calculator

**Your Variables:**

**Pricing:**
- Tier 1: $_____/month
- Tier 2: $_____/month
- Tier 3: $_____/month

**Costs:**
- Fixed monthly: $_____
- Variable per customer: $_____

**Growth:**
- Customers Month 1: _____
- Customers Month 6: _____
- Customers Month 12: _____

**Time:**
- Hours/week (Months 1-3): _____
- Hours/week (Months 4-12): _____

**Calculate your own:**
1. Revenue = (Customers × Avg Price)
2. Costs = (Fixed + Variable × Customers)
3. Profit = Revenue - Costs
4. Hourly Rate = Profit / Hours Worked

---

## SECTION 10: COMPARISON TO ALTERNATIVES

### Vs. Full-Time Job

| Metric | SaaS Business (Month 12) | Tech Job |
|--------|-------------------------|----------|
| Monthly Income | $33,495 | $10,000 |
| Hours/Week | 15 | 40 |
| Hourly Rate | $558 | $58 |
| Equity/Asset | Sellable business | Nothing |
| Control | Complete | None |

---

### Vs. Freelancing

| Metric | SaaS Business | Freelancing |
|--------|---------------|-------------|
| Revenue Ceiling | Unlimited | Hours × Rate |
| Scalability | High | None |
| Automation | Extensive | Minimal |
| Vacation Impact | Minimal | No income |
| Asset Value | $500K+ | $0 |

---

## 🎯 FINAL RECOMMENDATION

**This model shows:**
✅ Immediate profitability (Month 1)
✅ Strong margins (90%+)
✅ Minimal capital required (<$2K)
✅ Part-time commitment by Month 4
✅ Excellent LTV:CAC ratio (330:1)
✅ Resilient to worst-case scenarios

**Next Steps:**
1. Validate your specific niche numbers
2. Adjust pricing based on customer research
3. Track actuals vs. projections monthly
4. Iterate model based on real data

---

**Ready to build?** These numbers support moving forward with confidence.
