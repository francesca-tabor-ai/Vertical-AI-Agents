# Problem Discovery Checklist

## Objective
Identify high-value, repeatable problems suitable for vertical AI agents that require minimal ongoing human intervention.

---

## ✅ Problem Qualification Criteria

### 1. REPEATABILITY
- [ ] Problem occurs on a predictable schedule (daily/weekly/monthly)
- [ ] Same type of analysis/decision required each cycle
- [ ] Clear input → process → output workflow
- [ ] Similar patterns across multiple companies in the industry

**Red Flags:**
- One-off projects
- Highly variable workflows
- Requires creative/strategic thinking each time

---

### 2. AUTOMATION POTENTIAL
- [ ] Decision rules can be articulated (even if complex)
- [ ] Success can be measured quantitatively
- [ ] Humans currently spend 5+ hours/week on this task
- [ ] Task involves data analysis, pattern recognition, or rule application

**Red Flags:**
- Requires physical presence
- Needs human negotiation/persuasion
- Highly dependent on unstated context/politics

---

### 3. FINANCIAL VIABILITY
- [ ] Current cost to business: $10,000+ annually (labor + errors)
- [ ] Potential to charge $500-3,000/month for automated solution
- [ ] Clear ROI within 3-6 months for customer
- [ ] Market size: 10,000+ potential customers globally

**Red Flags:**
- Businesses can't articulate cost of current approach
- Solution saves <2 hours/week
- Industry is declining or very small

---

### 4. DATA AVAILABILITY
- [ ] Required data exists in digital format
- [ ] Data is accessible via API, export, or email
- [ ] Historical data available for testing (6+ months)
- [ ] Data refresh cadence matches decision cadence

**Red Flags:**
- Data locked in legacy systems with no export
- Requires manual data entry
- Data quality is inconsistent
- Privacy/compliance issues prevent automation

---

### 5. DELIVERY SIMPLICITY
- [ ] Can deliver results via existing tools (Slack, email, spreadsheet)
- [ ] No custom dashboard required initially
- [ ] Users comfortable with "approve/reject" workflow
- [ ] Integration can be done via Zapier/n8n/Make

**Red Flags:**
- Requires custom mobile app
- Needs real-time visualization
- Users demand white-glove service
- Integration requires custom enterprise APIs

---

### 6. COMPETITIVE MOAT
- [ ] Domain expertise required (not just tech skills)
- [ ] Incumbent solutions are expensive/complex
- [ ] Underserved niche within larger market
- [ ] Network effects or data moat potential

**Red Flags:**
- Well-funded competitors already dominating
- Easy for others to replicate
- Commoditized problem space

---

## 🎯 HIGH-POTENTIAL PROBLEM PATTERNS

### Pattern 1: Time-Series Forecasting + Adjustment
**Examples:**
- Inventory reorder optimization
- Demand planning
- Budget variance analysis
- Sales quota setting

**Why It Works:**
- Historical data readily available
- Clear success metrics (accuracy)
- Conservative approach valued
- Cyclical nature = recurring revenue

---

### Pattern 2: Anomaly Detection + Flagging
**Examples:**
- Expense report review
- Quality control alerts
- Compliance checking
- Fraud detection

**Why It Works:**
- High cost of errors
- Low false-positive tolerance (conservative = good)
- Easy to measure (catch rate)
- Risk reduction valued by CFOs

---

### Pattern 3: Document/Data Reconciliation
**Examples:**
- Invoice matching
- Contract clause verification
- Data validation across systems
- Report generation

**Why It Works:**
- Tedious manual work
- Clear rules to follow
- Easy to automate delivery
- Immediate time savings visible

---

### Pattern 4: Prioritization + Recommendation
**Examples:**
- Lead scoring
- Maintenance scheduling
- Content moderation queues
- Customer support routing

**Why It Works:**
- Humans already doing triage
- Can measure lift vs. baseline
- Reduces decision fatigue
- Easy A/B testing

---

## 📋 NICHE DISCOVERY WORKSHEET

### Step 1: Industry Selection
Industry to explore: ____________________

**Quick Research:**
- Average company size: ____________________
- Tech adoption level (1-10): ____________________
- Pain points mentioned in forums: ____________________
- Existing software solutions: ____________________

---

### Step 2: Problem Identification
What repetitive task are you targeting? ____________________

**Validate Repeatability:**
- How often does this happen? ____________________
- Who currently does it? ____________________
- Time spent per cycle: ____________________
- Cost of errors: ____________________

---

### Step 3: Automation Feasibility
**Data Sources:**
1. ____________________
2. ____________________
3. ____________________

**Decision Rules:**
- Can you write them down? [ ] Yes [ ] No
- Are they consistent across companies? [ ] Yes [ ] No
- Do exceptions exist? [ ] Yes [ ] No (If yes, how many?)

---

### Step 4: Quick Financial Model
**Costs (Monthly):**
- AI API calls: $____________________
- Hosting/automation: $____________________
- Your time (hours × rate): $____________________
**TOTAL COST:** $____________________

**Revenue (Monthly):**
- Price per customer: $____________________
- Expected customers (Month 3): ____________________
- Expected customers (Month 6): ____________________
- Expected customers (Month 12): ____________________

**Break-even:** ____________________ customers

---

### Step 5: Validation Checkpoint
Score each criterion (0-10):

- [ ] Repeatability: ____/10
- [ ] Automation Potential: ____/10
- [ ] Financial Viability: ____/10
- [ ] Data Availability: ____/10
- [ ] Delivery Simplicity: ____/10
- [ ] Competitive Moat: ____/10

**TOTAL SCORE:** ____/60

**Decision:**
- 50+: Proceed to customer validation
- 35-49: Refine or explore alternative angle
- <35: Move to different niche

---

## 🚀 TOP 20 VALIDATED NICHES (Starter List)

### Manufacturing & Supply Chain
1. ✅ **Inventory Reorder Optimization** - Score: 54/60
2. ✅ **Supplier Quality Score Updates** - Score: 51/60
3. ✅ **Production Schedule Anomaly Detection** - Score: 49/60

### Finance & Accounting
4. ✅ **Expense Report Anomaly Flagging** - Score: 56/60
5. ✅ **Invoice-PO Matching** - Score: 52/60
6. ✅ **Budget Variance Analysis** - Score: 50/60

### Sales & Marketing
7. ✅ **Lead Scoring Refinement** - Score: 48/60
8. ✅ **Sales Forecast Adjustment** - Score: 53/60
9. ✅ **Email Campaign Performance Analysis** - Score: 45/60

### Professional Services
10. ✅ **Contract Compliance Checking** - Score: 51/60
11. ✅ **Timesheet Anomaly Detection** - Score: 47/60
12. ✅ **Client Health Score Updates** - Score: 49/60

### Healthcare (Non-Clinical)
13. ✅ **Appointment No-Show Prediction** - Score: 50/60
14. ✅ **Billing Code Verification** - Score: 52/60
15. ✅ **Supply Reorder (Medical Supplies)** - Score: 48/60

### Real Estate
16. ✅ **Property Valuation Adjustments** - Score: 46/60
17. ✅ **Lease Renewal Likelihood** - Score: 47/60
18. ✅ **Maintenance Priority Scoring** - Score: 49/60

### Logistics
19. ✅ **Route Optimization Suggestions** - Score: 51/60
20. ✅ **Delivery Delay Prediction** - Score: 48/60

---

## 📞 Next Steps

Once you've scored 50+:
1. Move to `02-Industry-Research-Template.md`
2. Conduct deeper industry analysis
3. Then proceed to `03-Customer-Validation-Script.md`

---

## 💡 Pro Tips

**Leverage Your GEO Expertise:**
- Industries struggling with AI adoption need the most help
- Your experience with AI visibility = you understand how to make AI valuable
- Look for industries where you already have connections

**Start Small:**
- Pick ONE niche for first 90 days
- Get to 3-5 paying customers
- Then clone to adjacent niche

**Red Flags to Avoid:**
- "We'd love to try it for free" (Will never convert)
- "This sounds interesting" (Not a pain point)
- "Can you customize it for us?" (Will suck your time)

**Green Flags to Pursue:**
- "We're currently paying $X for this" (Willingness to pay)
- "This takes us Y hours per week" (Quantified pain)
- "When can we start?" (Urgency)
