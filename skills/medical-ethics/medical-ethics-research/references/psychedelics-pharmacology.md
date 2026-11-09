# Psychedelics: Pharmacology, Safety, Law, and Measurement

This is background knowledge for reviews. It is stable, mechanism-level material from training knowledge, so **most entries are [M]**. Verify specific numbers (durations, doses, scheduling dates) against a current primary source before they appear in a memo. For regulatory *status*, use fda-pipeline.md, which is dated.

This file is for analysis and education. It does not give dosing guidance for non-medical use, and the skill must not produce any.

## Contents
1. Classes and mechanisms
2. Compound profiles
3. Safety: what is and is not known
4. Drug interactions that matter clinically
5. Legal status (U.S.)
6. Measurement instruments used in trials
7. Proposed therapeutic mechanisms (and their evidence status)

---

## 1. Classes and mechanisms

| Class | Prototypes | Primary mechanism [M] | Subjective profile |
|---|---|---|---|
| Classic (serotonergic) psychedelics | Psilocybin/psilocin, LSD, DMT, 5-MeO-DMT, mescaline | 5-HT2A receptor agonism (5-MeO-DMT also strongly 5-HT1A) | Perceptual change, altered self-experience, emotional intensity, "mystical-type" experiences |
| Entactogens / empathogens | MDMA (midomafetamine), methylone, R-MDMA | Release of serotonin, norepinephrine, and dopamine via monoamine transporters; oxytocin release | Prosocial feelings, reduced fear response, minimal hallucination |
| Dissociatives | Ketamine, esketamine | NMDA receptor antagonism | Dissociation, detachment |
| Atypical / oneirogenic | Ibogaine (and its metabolite noribogaine) | Multiple targets (NMDA, kappa-opioid, serotonin transporter, nicotinic receptors) | Long, dream-like state |
| "Non-hallucinogenic" analogs / neuroplastogens | Investigational | Designed to keep the plasticity effects without the subjective trip | — (debate whether the trip is necessary) |

## 2. Compound profiles

Durations are approximate oral ranges unless noted [M].
- **Psilocybin.**
  - Prodrug, dephosphorylated to psilocin.
  - Onset 20–40 min; duration 4–6 h.
  - Trial doses: 25 mg (COMP360, Usona); 1 mg and 5 mg used as low-dose controls.
  - Common acute effects: anxiety, nausea, headache (often the following day), transient rises in blood pressure and heart rate.
- **LSD (lysergide).**
  - Microgram potency; duration about 8–12 h at 100 µg (DT120 ODT is 100 µg).
  - Partial agonist at 5-HT2A, plus dopaminergic activity.
- **MDMA (midomafetamine).**
  - Duration 3–6 h. Trial dosing: 80–120 mg plus an optional supplemental dose (MAPP trials) [V: registry].
  - Risks: cardiovascular strain, hyperthermia, hyponatremia, bruxism, post-session low mood.
  - Moderate abuse liability (the reason "positive" adverse events mattered in the CRL).
- **Methylone (TSND-201).**
  - A β-keto analog of MDMA (a cathinone); monoamine releaser.
  - Described by its sponsor as non-hallucinogenic, with no 5-HT2A activity [S].
- **DMT.**
  - Inactive orally unless combined with an MAO inhibitor (as in ayahuasca).
  - Inhaled or IV effects last about 15–30 min. Buccal (VLS-01) and deuterated (HLP004) forms aim to adjust duration.
- **5-MeO-DMT (mebufotenin).**
  - Very rapid and short when inhaled or intranasal: median psychoactive experience about 11 min reported for GH001 [V: company].
  - Natural source: *Incilius (Bufo) alvarius* toad secretion. This raises conservation and animal-welfare concerns [M].
- **Ibogaine.**
  - From *Tabernanthe iboga*. Very long acute phase (24–36 h).
  - **QT prolongation and documented cardiac deaths** [M]. Noribogaine, its active metabolite, has a long half-life.
  - Studied for opioid withdrawal and use disorder.
- **Mescaline.** From peyote (*Lophophora williamsii*, slow-growing and conservation-threatened) and San Pedro cacti. Duration about 8–12 h.
- **Ketamine / esketamine.**
  - Schedule III.
  - Esketamine (Spravato) nasal spray: FDA-approved, REMS, certified settings, 2-hour monitoring [M].
  - The regulatory precedent most often cited for psychedelic REMS design.
- **Ayahuasca.** DMT plus β-carbolines (harmine, harmaline: reversible MAO-A inhibitors). Religious use protected in U.S. cases (*Gonzales v. O Centro Espírita*, 2006 [M]).

## 3. Safety: what is and is not known

**Physiological toxicity.**
- Classic psychedelics have low physiological toxicity and no established lethal dose in ordinary use [M].
- MDMA and ibogaine carry real physical risks (cardiovascular; for ibogaine, cardiac rhythm).

**Psychological risks** [M]:
- acute anxiety and panic ("challenging experiences");
- risky behavior while impaired;
- precipitation of psychosis or mania in predisposed people (hence the exclusion of personal or family history of psychotic and bipolar I disorders);
- hallucinogen persisting perception disorder (HPPD), uncommon, and its incidence is uncertain;
- prolonged distress after difficult sessions;
- destabilization of beliefs or identity.

**Suicidality.**
- Monitored closely in depression trials; signals are mixed and small in number.
- Report per arm, with counts (e.g., COMP006: one suicidal-behavior event, in the 1 mg arm [S]).

**Cardiac valvulopathy.** 5-HT2B agonism is linked to valvulopathy with chronic exposure (cf. fenfluramine and pergolide). The risk is a theoretical concern for repeated or microdosing regimens. The 2026 FDA guidance asks sponsors to assess 5-HT2B activity [S].

**Abuse liability.**
- Classic psychedelics show low self-administration in animals [M]. The 2026 guidance says such studies are not usually required [S].
- MDMA has greater abuse liability.
- "Positive" subjective effects must be captured as adverse events [V].

**Vulnerability while impaired.** Suggestibility, emotional openness, and dependency on the facilitator. This is the foundation of the touch and boundary rules (psychedelic-ethics-issues.md §2).

**Unknowns** (state them in reviews):
- long-term effects of repeated dosing;
- effects in older adults, adolescents, and in pregnancy and breastfeeding (Oregon requires disclosure that risks are unknown [V]);
- effects in people excluded from trials (comorbid substance use, active suicidality, serious medical illness);
- real-world adverse event rates outside trial screening.

## 4. Drug interactions that matter clinically [M]

- **SSRIs / SNRIs** may blunt the subjective effects of classic psychedelics. Tapering them is common in trials, and it carries withdrawal and relapse risk. Adjunctive designs (HLP003) keep them.
- **Lithium** combined with classic psychedelics: seizure case reports. Generally contraindicated.
- **MAO inhibitors** combined with MDMA or other serotonergic drugs: serotonin syndrome and hypertensive crisis risk. MAOIs also potentiate DMT.
- **Ibogaine** with QT-prolonging drugs or electrolyte disturbance: arrhythmia risk.
- **Tramadol and other serotonergic agents** combined with MDMA: serotonin toxicity.
- **Antipsychotics** attenuate 5-HT2A effects; sometimes used as rescue medication.

## 5. Legal status (U.S.) [M unless tagged]

- **Controlled Substances Act.**
  - Psilocybin, psilocin, LSD, DMT, 5-MeO-DMT, mescaline (except peyote under the religious exemption for the Native American Church), MDMA, methylone, and ibogaine are **Schedule I**.
  - Ketamine is Schedule III.
- **After FDA approval,** the DEA must reschedule the approved product before marketing. A 2015 statute requires DEA to issue an interim final scheduling rule within 90 days of receiving HHS's recommendation [M]. That is why commentators say EO 14401's rescheduling language may add less than it seems [S: Psychedelics Today/POPLAR]. States must also reschedule under their own laws [S].
- **Religious use.** RFRA-based exemptions: the UDV case for ayahuasca; Santo Daime; the peyote exemption for the Native American Church.
- **State programs.** Oregon and Colorado regulated access; municipal decriminalization measures; state-funded trials (Texas ibogaine). See fda-pipeline.md §5.
- **Right to Try / expanded access.** EO 14401 references Right to Try pathways [S]. Schedule I status still requires DEA registration for any use.

## 6. Measurement instruments used in trials [M]

| Construct | Instruments |
|---|---|
| Depression | MADRS (0–60; common primary in psychedelic trials), HAM-D-17, QIDS-SR, PHQ-9 |
| Anxiety | HAM-A (0–56), GAD-7 |
| PTSD | CAPS-5 (clinician), PCL-5 (self-report) |
| Global | CGI-S / CGI-I |
| Suicidality | C-SSRS |
| Acute subjective effects | 5D-ASC / 11D-ASC; Mystical Experience Questionnaire (MEQ30); Ego Dissolution Inventory; Challenging Experience Questionnaire |
| Blinding / expectancy | Participant and rater arm-guess questionnaires (Bang / James blinding indices); expectancy scales (e.g., SETS) |
| Abuse-related subjective effects | Drug-liking scales (VAS), Addiction Research Center Inventory subscales |
| Functioning / QoL | Sheehan Disability Scale, EQ-5D |

**Appraisal note.** Clinician-rated scales are vulnerable to rater unblinding. Blinded central or remote raters reduce, but do not eliminate, the bias, because participants' self-reports to the rater can reveal their arm.

## 7. Proposed therapeutic mechanisms (and their evidence status) [M]

- **Neuroplasticity.** Psychedelics promote dendritic growth and synaptogenesis in preclinical models ("psychoplastogens"). One proposal involves direct TrkB binding. Human relevance is unproven.
- **Network effects.** Reduced default-mode-network integrity; increased global connectivity. Theoretical models include REBUS ("relaxed beliefs under psychedelics").
- **Psychological mediators.** Mystical-type experience, insight, emotional breakthrough, and psychological flexibility correlate with outcomes in several trials. Correlation with subjective intensity does not establish causation, and it confounds with unblinding.
- **"Is the trip necessary?"** Non-hallucinogenic analogs, and trials without psychotherapy (DT120, TSND-201), are testing this. The answer has ethical implications for consent, session staffing, and cost.
- **Expectancy.** May account for part of the effect. Separating expectancy from drug effect is the central methodological problem of the field.
