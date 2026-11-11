# 01. US Legal and Standards Landscape

Not legal advice. Dates verified against Federal Register, eCFR, HHS, and ADA.gov search results on 2026-11-11.

## Summary table

| Regime | Applies to | Standard | Deadline / status | Source (grade) |
|---|---|---|---|---|
| **ADA Title II web rule** (28 CFR part 35) | State and local governments and their web content and mobile apps, including via contractors | **WCAG 2.1 Level AA** | Population ≥ 50,000: **April 26, 2027**. Population < 50,000 and special districts: **April 26, 2028**. Extended by one year via Interim Final Rule effective April 20, 2026. Scope and standard unchanged. | [Federal Register 2026-07663](https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web), [ADA.gov first steps](https://www.ada.gov/resources/web-rule-first-steps/) (A) |
| **Section 504 (HHS)** 45 CFR 84.84 | Recipients of HHS financial assistance: web content and mobile apps | **WCAG 2.1 Level A and AA** | ≥ 15 employees: **May 11, 2027**. < 15 employees: **May 10, 2028**. Extended one year by IFR (HHS announcement May 7, 2026). Exceptions: fundamental alteration or undue burden. | [eCFR 84.84](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-84/subpart-I/section-84.84), [HHS press release](https://www.hhs.gov/press-room/hhs-extends-mobile-and-web-accessibility-deadline.html) (A) |
| **Section 508** (Revised 508 Standards, 36 CFR 1194) | Federal agencies' ICT (web and non-web, documents, software) and procurement | **WCAG 2.0 Level A and AA** (38 success criteria applicable). A page failing even one criterion does not conform. | In effect since January 18, 2018 | [Section508.gov](https://www.section508.gov/develop/applicability-conformance/), [Access Board](https://www.access-board.gov/ict/) (A) |
| **ADA Title III** | Private businesses that are "places of public accommodation" | No finalized federal web rule | Courts often treat business websites as covered. DOJ consent decrees and courts commonly use WCAG 2.1/2.2 AA as benchmark. High-volume litigation (one secondary source cites ~2,500 federal suits in 2024 and ~2,019 in H1 2025 from UsableNet). State laws like California's Unruh Act add damages. | [LegalClarity summaries](https://legalclarity.org/marketing-compliance-ftc-rules-privacy-laws-and-dark-patterns/) (C/D, secondary; verify with counsel) |
| **FTC deceptive design ("dark patterns")** | Commercial interfaces | FTC Act §5 (unfair or deceptive acts), ROSCA, CAN-SPAM, COPPA, others | Case-by-case enforcement; FTC staff report 2022 | [FTC Bringing Dark Patterns to Light](https://search.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf), [CRS IF12246](https://www.congress.gov/crs-product/IF12246) (A/B) |
| **WCAG 3.0** | Future W3C standard | Not a standard yet | Still a Working Draft in 2026; charter expects a Candidate Recommendation Snapshot, completion listed as Q4 2027. Not citable for compliance. | [W3C AG WG Charter 2026](https://www.w3.org/2026/06/ag-wg-charter.html) (A) |

## What to build to

**Build to WCAG 2.2 AA.** It is backward compatible with 2.1 and 2.0 A/AA success criteria (2.2 adds nine criteria and removes obsolete 4.1.1 parsing), so one build satisfies Section 508, Title II, and Section 504, and matches the most common benchmark in private-sector settlements. **(judgment on strategy; the criteria list is from W3C "What's New in WCAG 2.2".)**

WCAG 2.2 additions (A/AA unless noted): 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum), 3.2.6 Consistent Help (A), 3.3.7 Redundant Entry (A), 3.3.8 Accessible Authentication (Minimum). Also 2.4.12/2.4.13 (AAA), 3.3.9 (AAA).

## Practical compliance notes

1. **Conformance is per page and per process.** Section508.gov: a multi-step sequence (e.g., select and pay for a ticket) does not conform if any step fails. Test full flows, not only pages.
2. **Third-party content counts.** Title II covers content provided "directly or through contractual, licensing, or other arrangements." Vendor widgets, embedded forms, payment pages, and PDFs need review and contract language. The Section 508 program offers the free Accessibility Requirements Tool (ART) for procurement.
3. **Overlays are not compliance.** Roughly a quarter of 2024 accessibility lawsuits reportedly involved sites that used automated overlay widgets (secondary source, grade D); code-level fixes are what standards test. **(judgment: treat overlays as unproven.)**
4. **Keep an accessibility statement and a feedback path** and fix reported barriers. (USWDS guidance: "Be responsive. Fix accessibility issues when you discover them.")
5. **Test with the federal methods.** Section 508 ICT Testing Baseline and the Trusted Tester process are free federal manual-test methods (referenced by USWDS).
6. **Keep the evidence.** Save audit reports, remediation tickets, and VPAT/ACR documents. These matter in procurement and disputes. **(judgment)**

## Dark patterns and consent: design for lawful clarity

FTC report (2022): dark patterns are "design practices that trick or manipulate users into making choices they would not otherwise have made and that may cause harm." Examples cited: pre-checked boxes, hard-to-find disclosures, confusing cancellation, hidden fees, fake countdown timers, fake scarcity or "others are viewing this," ads disguised as content. A workshop study found dark patterns doubled the share of consumers signing up for a dubious service, and effects grew with multiple patterns.

Design rules that follow:
- Cancel as easily as you sign up; no maze of screens.
- Show total price early; no drip pricing.
- No pre-checked consent or add-ons; symmetric Accept/Decline.
- No fake urgency or false social proof.
- Disclosures in readable size and contrast, near the decision point.

## Regulatory source index (free)

- ADA.gov web rule: https://www.ada.gov/resources/web-rule-first-steps/
- Federal Register IFR (Title II): https://www.federalregister.gov/documents/2026/04/20/2026-07663/...
- eCFR 45 CFR 84.84: https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-84/subpart-I/section-84.84
- Section508.gov: https://www.section508.gov/
- Access Board ICT: https://www.access-board.gov/ict/
- W3C WCAG 2.2: https://www.w3.org/TR/WCAG22/ and What's New: https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- USWDS accessibility: https://designsystem.digital.gov/documentation/accessibility/
- plainlanguage.gov, digital.gov plain language guides
