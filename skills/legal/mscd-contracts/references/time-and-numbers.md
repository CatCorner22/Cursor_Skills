# References to time, numbers, and formulas

House style: digits for every number; U.S. dates (*January 1, 2027*). Key MSCD rules: state whether a point in time is inclusive or exclusive (10.22-10.28); *no later than X days after*, not *within* (10.69-10.71); for a minimum-notice period (*at least 20 days before*), name the deadline day and offer both counts, the 20th day before (1 end day, 10.65) and the 21st day before (clear days, 10.66), and ask which the parties intend; *until*, *to*, and *by* leave an end day in doubt, so write *through* or *before* (10.23-10.24); *midnight at the beginning of*, never *12:00 a.m.* (10.35-10.38); name the time zone (10.51-10.56); *promptly*, not *immediately* (10.118-10.131); state the time component of a reference, *as of the date of this agreement* or *then in effect* (10.152-10.156); never words and digits (14.5-14.11); *the result of* for order of operations (14.26-14.40); state whether tiered rates are stepped or shifting flat (14.69-14.77).

> **Book examples are in MSCD5's style, not house style.** They may use lowercase *schedule*, *1 January 2024*, spelled-out numbers, 1.1 numbering, *the* before party names, or a passive that MSCD accepts. Restate any example in house style (`house-style.md`) before you put it in a contract or a comment. For the other side's drafts, the house rule is to flag everything, whatever a rule's "let-pass" or "style-only" label says.


## Rules (106, generated from `data/rules.jsonl`)

Format: id, severity (1 = ambiguity or meaning-changing; 2 = vagueness or dispute risk; 3 = style), the rule, and its MSCD paragraphs and PDF page. `HOUSE` marks a rule that Blake's house style changes: apply the house rule. For a rule's full record (test, fix, exceptions, verified book examples), run `python3 scripts/rules_query.py --id <id>`.


### Introduction

- **R-intro-forthwith** [sev 3] Dispense with the Commonwealth usage forthwith. (Introduction; PDF p. 41)

### Chapter 2: The Introductory Clause

- **R-2.22-date-format** [sev 3] Use the date format 1 January 2022 in the introductory clause and for all other dates. (2.22; PDF p. 82)
  - HOUSE: U.S. date form: January 1, 2027. MSCD 10.11-10.14 still apply. See house-style.md section 7.

### Chapter 10: References to Time

- **R-10.1-four-functions** [sev 3] A reference to time does one of four things: gives a date to something; specifies a point in time; specifies a period of time that begins or ends at a stated point and has a stated duration; or apportions a quantity per unit of time. Paired points in time are equivalent to a period. (10.1, 10.2, 10.3...; PDF p. 469)
- **R-10.7-day-month-year** [sev 3] State dates in day-month-year format (1 January 2022); U.S. drafters should consider switching to it. (10.7, 10.8, 10.9...; PDF p. 470)
  - HOUSE: U.S. date form: January 1, 2027. MSCD 10.11-10.14 still apply. See house-style.md section 7.
- **R-10.11-no-this-day-of** [sev 3] Don't use the format this 24th day of October, 2022; it is archaic and long-winded. (10.11; PDF p. 470)
- **R-10.12-no-two-digit-day** [sev 3] Don't use two digits for the day (07 November 2022). (10.12; PDF p. 471)
- **R-10.13-no-numerical-dates** [sev 1] Don't use purely numerical dates (10/9/2022). (10.13; PDF p. 471)
  - Fix: Write the date as 9 October 2022 (or 10 September 2022).
- **R-10.14-no-ad** [sev 3] Don't add A.D. before the year; it is eccentric. (10.14; PDF p. 471)
- **R-10.15-day-not-date** [sev 3] If you refer to a day without anchoring it in time, use day rather than date. (10.15, 10.16; PDF p. 471)
- **R-10.17-no-date-that-is** [sev 3] Omit the date that is (before the date that is, no later than the date that is); it is almost always clutter. (10.17, 10.18; PDF p. 471)
- **R-10.19-no-date-notified** [sev 3] Don't use the date notified; say the date that ABC specifies by notice to XYZ. (10.19, 10.20; PDF p. 472)
- **R-10.21-points-in-time** [sev 3] Fix a point in time by reference to a date or other day (on 9 April 2024; the Closing Day) or an anniversary; on expresses something happening by reference to a day. (10.21, 10.22; PDF p. 472)
- **R-10.23-inclusive-exclusive-ambiguity** [sev 1] Inclusive-versus-exclusive ambiguity: a preposition marking the beginning or end of a period (from, after, until, to, by, between) can leave unclear whether the stated day is included. (10.23, 10.24, 10.25...; PDF p. 473)
  - Look for: a period bounded by a day using from, after, until, to, by, or between
  - Test: Ask whether the boundary day itself falls inside the period. Caselaw: from and after mostly exclusive; until, to, and by split; between mostly exclusive at both ends; starting and commences on likely inclusive; before likely exclusive; through likely inclusive.
  - Fix: State the time of day for each boundary (10.33), or use starting [day] and ending on or through [day], or say expressly inclusive or exclusive.
  - Exceptions: Even where caselaw is consistent, a court could hold otherwise on the circumstances, and the parties may not have had that effect in mind (10.27-.28).
- **R-10.24-preposition-verdicts** [sev 1] Prefer prepositions courts read consistently: starting [day] and commences on (likely inclusive), through (likely inclusive), before (likely exclusive). Avoid until, to, and by for ending points and from, after, and between for beginning points, because courts split or default to exclusive. (10.24, 10.25, 10.26; PDF p. 473)
- **R-10.29-day-insufficiently-specific** [sev 1] Recognize that fixing a point in time by reference to a day is insufficiently specific: a beginning or ending point could fall at the midnight starting or ending the day, and a party might claim it had some other time in mind. (10.29, 10.30, 10.31...; PDF p. 474)
  - Look for: deadline or period stated by day with no time of day
  - Test: Ask at what moment on the day the period begins or ends.
  - Fix: State a time of day (10.33); or say from the beginning of 15 April 2023 to the end of 30 April 2023 (which could be read as business hours); or state inclusive or exclusive expressly (legalistic); or add a comprehensive interpretation section.
- **R-10.33-state-time-of-day** [sev 1] State a time of day for each beginning and ending point (the Option expires at 2:00 p.m. on 25 September 2022); avoid close of business and opening of business, which can cause disputes. (10.33, 10.34; PDF p. 475)
- **R-10.35-use-midnight** [sev 3] Prefer midnight as the time of day: it lets you deal in entire days and reduces disputes over when a notice or payment was received. (10.35; PDF p. 475)
- **R-10.36-no-12-am-pm** [sev 1] Don't refer to midnight or noon as 12:00 a.m. or 12:00 p.m.; they are boundaries between a.m. and p.m. hours. (10.36; PDF p. 475)
  - Fix: Say noon, or midnight at the beginning [or end] of [date].
- **R-10.37-midnight-ambiguity** [sev 1] Midnight ambiguity: midnight on [date] could mean the midnight beginning or the midnight ending that day; the convention that it means the end isn't clearly universal or known to the parties. (10.37, 10.38; PDF p. 476)
  - Look for: midnight on a date, or 12:01 a.m. / 11:59 p.m. used to dodge the issue
  - Test: Ask whether midnight on the date could be read as the start of that day.
  - Fix: Say midnight at the beginning [or end] of [date]. Don't use 12:01 a.m. or 11:59 p.m., which is clumsy.
- **R-10.39-time-is-boundary** [sev 2] Treat a time of day as a boundary between periods, not a minute-long period; don't state hours, minutes, and seconds, and watch for a draft that states a time a minute more or less than expected (5:01 p.m.). (10.39, 10.40, 10.41...; PDF p. 476)
- **R-10.45-no-at-deadline** [sev 1] Don't use at to state a deadline; use a beginning or ending point in time. (10.45, 10.46; PDF p. 477)
  - Fix: Say before [time] on [date], or no later than [time] on [date].
- **R-10.47-time-format** [sev 3] State a time of day in digits (5:30 p.m., not five thirty p.m. or both), without o'clock, with lowercase a.m. and p.m. with periods; use the 24-hour system (17:30) where customary, but without seconds. (10.47, 10.48, 10.49...; PDF p. 478)
- **R-10.51-time-zone** [sev 1] If the parties are in different time zones or business crosses them, specify the governing time zone, preferably by city (6:00 p.m., New York time) to avoid daylight-saving errors (PST versus PDT; Arizona) and states spanning more than one zone. (10.51, 10.52, 10.53...; PDF p. 478)
  - Book example: 1:00 p.m. PST on 5 July 2022 → 1:00 p.m. PDT on 5 July 2022
- **R-10.57-upon-only-automatic** [sev 1] Use upon (or on) for an event only to express something that happens automatically when it occurs (The Option will expire upon sale of the Acme Assets); when language of discretion or obligation is tied to an event, state a period for acting. (10.57, 10.58, 10.59...; PDF p. 480)
  - Book example: (none) → If during the 30 days after that 15-month period the Buyer notifies the Seller it wishes to sell the Property back to the Seller ...
- **R-10.62-forward-period** [sev 1] In a forward-looking period (from, following, after), the convention excludes the day you count from and includes the last day; be explicit about how the ending date is determined, and if you know both ends, use paired points in time instead. (10.62, 10.63, 10.64; PDF p. 480)
  - Exceptions: The convention doesn't apply if the period clearly must consist of entire days (both terminal days excluded) or the parties clearly intend the first day to be included (10.63).
- **R-10.65-minimum-notice-ambiguity** [sev 1] Minimum-notice ambiguity: when a provision requires at least (or no fewer than, or not less than) N days' notice before an event, courts split between counting 1 terminal day (the Nth day before the event is the last valid day, 10.66) and requiring "clear" days that exclude both (the N+1th day before). A plain backward deadline (no later than 10 days before the audit; during the 10 days before the Exclusivity Period expires) follows the convention in 10.65 (count 1 terminal day, not the other): it is not the court split, and making the count explicit there is at most a low-severity improvement. (10.65, 10.66, 10.67; PDF p. 481)
  - Look for: minimum notice: at least, no fewer than or not less than N days' notice (or N days before an event, where the provision sets how much notice a party must give)
  - Test: For a minimum-notice period, count back both ways (exclude 1 terminal day; exclude both) and see whether the last valid day differs (for a 31 December transfer with at least 10 days' notice: 21 December versus 20 December). For a plain deadline (no later than N days before), apply the 10.65 convention; flag it only if the parties' intent plainly differs.
  - Fix: Name the deadline day and offer both counts (the Nth day before; the N+1th day before) and ask which the parties intend; or denote the period in entire days.
- **R-10.68-no-confusing-points** [sev 1] Don't measure a period from a point in time that could cause argument over when or whether it occurred (final resolution of any disputes). (10.68; PDF p. 482)
  - Look for: period keyed to an event of uncertain timing
- **R-10.69-within-ambiguity** [sev 1] Within ambiguity: within X days of an event can denote a period running forward, backward, or both (within seven days of the first anniversary), and within X days prior to can mean "during the X days before" or "at least X days before." (10.69, 10.70, 10.71; PDF p. 483)
  - Look for: within X days (or months) of, or within X days prior to, an event or date
  - Test: Ask whether the period could run before the reference point, after it, or both.
  - Fix: Say no later than seven days after it receives a Sale Notice (or during the X days before, or at least X days before).
  - Book example: within seven days of receiving a Sale Notice → no later than seven days after it receives a Sale Notice
- **R-10.72-choose-unit** [sev 3] Choose the unit of time deliberately; for days, often prefer business days, defined as a day other than a weekend or public holiday in a specified jurisdiction, or a day banks are open. (10.72, 10.73; PDF p. 483)
- **R-10.74-no-calendar-days** [sev 3] Don't use calendar days instead of days; it is unnecessary and potentially confusing. (10.74; PDF p. 484)
- **R-10.75-no-nonbusiness-day** [sev 3] Don't use nonbusiness day; say a day other than a business day. (10.75; PDF p. 484)
- **R-10.76-months-period** [sev 3] Consider months for periods longer than about 90 days; a month counted forward ends at midnight at the beginning of the corresponding day of the next month (or the last day of that month if none corresponds). (10.76; PDF p. 484)
- **R-10.77-no-weeks** [sev 3] Don't use weeks for periods; they give no advantage over days or months. (10.77; PDF p. 484)
- **R-10.78-years-period** [sev 3] A period of years runs through the day before the relevant anniversary of the first day included; when a period is measured from a stated point, don't fear a court will read month or year as a calendar month or year. (10.78, 10.79; PDF p. 485)
- **R-10.80-bi-semi-ambiguity** [sev 1] Bi- and semi- ambiguity: biannual and semiannual both mean twice a year, but some dictionaries give biannual the meaning of biennial; bimonthly and biweekly invite similar confusion. (10.80; PDF p. 485)
  - Look for: a frequency word with the prefix bi- or semi-
  - Test: Ask whether the word could mean twice per unit or once every two units.
  - Fix: Say twice a year (month, week) or every two years (months, weeks).
- **R-10.81-no-year-and-a-day** [sev 3] Instead of agreeing not to start bankruptcy proceedings until one year and a day after repayment, say no sooner than one year after. (10.81, 10.82, 10.83; PDF p. 485)
- **R-10.84-on-day-long** [sev 3] When an act must occur on a specified date, the period is that day's 24 hours; no beginning or ending point need be stated, though you may add a time of day. (10.84; PDF p. 486)
- **R-10.85-not-less-than-obligation** [sev 1] To state how many units of time satisfy a condition, use at least X (not not less than X or X or more); don't use any of these in language of obligation or prohibition, where they suggest the duration is open-ended. (10.85, 10.86, 10.87; PDF p. 486)
  - Exceptions: If you use that form, say not less than, not no less than (10.85).
  - Book example: The Company shall retain copies ... for a period of not less than six years from the date thereof. → (see fix)
  - Book example: (none) → Each arbitrator must be a licensed commercial real estate broker with at least 15 years' experience ...
- **R-10.88-time-of-day-end-ambiguity** [sev 1] Time-of-day-at-end ambiguity: before 2:00 p.m. on the date that is 20 Business Days after the Closing can mean any time up to 2:00 p.m. on day 20, or only on day 20 before 2:00 p.m. (10.88, 10.89, 10.90; PDF p. 487)
  - Look for: before [time] on the [date] that is X days after [event]
  - Test: Ask whether delivery on day 19 (or earlier) counts, or only delivery on day 20 before the stated time.
  - Fix: For the first meaning: between the Closing and 2:00 p.m. 20 Business Days after the Closing. For the second: on the 20th Business Day after the Closing, before 2:00 p.m.
- **R-10.91-point-instead-of-period** [sev 1] Point-for-period ambiguity: tying a figure that pertains to a period to the point marking its end (the Revenues as of the 24-Month Revenue Measurement Point) invites a fight over which part of the period the figure covers. (10.91; PDF p. 487)
  - Look for: a cumulative figure (revenues, sales, income) measured "as of" a point that ends a multi-part period
  - Test: Ask whether the figure covers the whole period or only the last segment before the point.
  - Fix: Refer to the period itself (the Revenues for the 24 months ending ...).
- **R-10.92-during-the-period** [sev 3] Don't use during the period or during a period to establish a period; use while or from ... to. (10.92, 10.93; PDF p. 488)
- **R-10.94-will-have-ambiguity** [sev 1] Will-have ambiguity: saying a party will have a period to do something leaves unclear whether you mean an obligation or a condition. (10.94; PDF p. 488)
  - Look for: a party will have (or shall have) a period to do something
  - Test: Ask whether failing to act is a breach (obligation) or just loss of a right (condition).
  - Fix: For an obligation: No later than 60 days after termination, Acme shall return ... For a condition: To validly exercise the Option, Acme must no later than 60 days after termination notify Widgetco that it is doing so.
- **R-10.95-before-period-ambiguity** [sev 1] Before-scope ambiguity: a condition such as If any of the Assets are destroyed or damaged prior to Completion can cover only damage between signing and completion, or any time before completion, including before signing. (10.95, 10.96, 10.97; PDF p. 489)
  - Look for: a condition about something happening before (prior to) Closing or Completion, with no start date
  - Test: Ask whether the period could start before signing.
  - Fix: Address the condition of the assets at signing expressly.
- **R-10.98-apportioning-issues** [sev 2] When apportioning a quantity per unit of time, address two issues: the alternative meanings of the unit, and short periods at the beginning or end of the contract. (10.98; PDF p. 489)
- **R-10.99-year-month-ambiguity** [sev 1] Unit-of-time ambiguity in apportioning: year (per year, annual) can mean a year from the agreement date and each anniversary, or the 12 months from any 1 January (most courts); month can mean to the corresponding day of the next month, or a calendar month; week can mean any seven consecutive days or a traditional week. (10.99, 10.100, 10.101...; PDF p. 489)
  - Look for: a quantity, payment, or limit apportioned per year, month, or week
  - Test: Ask whether the unit runs from the contract date or from the calendar boundary.
  - Fix: State what year or month means, by a more specific alternative (each 12-month period starting on the date of this agreement or an anniversary; each calendar quarter) or a defined term if used several times.
- **R-10.102-calendar-year-month** [sev 1] Don't rely on calendar year, civil year, calendar month, or a reference to the Gregorian calendar to fix the meaning: U.S. courts likely read calendar year as 1 January-31 December and calendar month as a month of the year, but English courts tend to read calendar month as running to the corresponding day of the next month. (10.102, 10.103, 10.104; PDF p. 490)
  - Fix: State the period expressly (1 January through 31 December).
- **R-10.106-short-periods** [sev 1] If year or month means a calendar year or month, state how to treat a short period between signing and the next unit and between the last complete unit and termination (prorate the number or amount, with rounding; apply the percentage to the short-period portion of the index; or prorate the percentage of the full index), or arrange beginning and ending short periods. (10.106, 10.107, 10.108...; PDF p. 491)
  - Look for: annual or monthly entitlement, bonus, or cap with no provision for partial periods
- **R-10.111-consecutive-ambiguity** [sev 1] Block-of-time ambiguity: when the thing apportioned is itself a unit of time (two months of each year), it is unclear whether it must be taken as a single block. (10.111, 10.112, 10.113; PDF p. 492)
  - Look for: a number of days, weeks, or months to be taken within a year or month
  - Test: Ask whether the time may be split into several shorter blocks.
  - Fix: To require a block, use consecutive (two consecutive months each year; convert one month to 30 consecutive days). If not, say so (over the course of one or more visits, each no shorter than five business days).
  - Book example: (none) → Over the course of one or more visits, each no shorter than five business days, excluding travel days, the Employee shall work in Acme's Budapest office for two months of each year.
- **R-10.114-promptly-equals-immediately** [sev 2] Treat promptly and immediately (and prompt and immediate) as meaning the same thing in contracts: courts apply a reasonableness standard to both. (10.114, 10.115, 10.116...; PDF p. 493)
  - Exceptions: Immediately also means "without intermediary" (the immediately preceding Business Day); that use is not a speed standard (10.119).
- **R-10.118-no-as-promptly-as-possible** [sev 3] Don't say as promptly as possible [or practicable]; promptly already depends on the circumstances. (10.118; PDF p. 494)
- **R-10.129-omit-immediately** [sev 2] Omit immediately and use promptly; don't use both promptly and immediately in one contract. (10.129; PDF p. 497)
- **R-10.130-no-promptly-synonyms** [sev 2] Don't use synonyms of promptly (quickly, as soon as practicable, expeditiously, forthwith, right away) or without undue delay. (10.130; PDF p. 497)
  - Fix: Use promptly, or a precise deadline.
  - Exceptions: Under German law, without undue delay may be appropriate as the English equivalent of unverzüglich (10.130).
- **R-10.131-precise-deadline** [sev 2] If you can state a precise deadline, do so; if promptly may not convey enough urgency, use a precise deadline (no later than 60 minutes after learning of that event) or combine vague and absolute limits (promptly, but not later than x days after). (10.131; PDF p. 497)
  - Book example: (none) → promptly, but not later than x days after ...
- **R-10.132-at-any-time** [sev 3] Don't use at any time in language of discretion (may already lets the party act whenever it wishes) or in language of obligation or conditional clauses. (10.132, 10.133, 10.134; PDF p. 497)
- **R-10.135-one-or-more-occasions** [sev 2] To make explicit that a right (or obligation or condition) isn't one-time-only, use on one or more occasions instead of from time to time. (10.135, 10.136, 10.137...; PDF p. 498)
  - Exceptions: Unnecessary for a right that can be exercised only once or an ongoing process (10.137).
  - Book example: The Bank may from time to time adjust the Advance Rate ... → The Bank may on one or more occasions adjust the Advance Rate ...
- **R-10.141-at-all-times** [sev 2] Don't use at all times: an ongoing obligation applies at all times without saying so; if a provision could be read as applying only at one moment, use always; for a statement of fact, state a time period (since 1 January 2022). (10.141, 10.142, 10.143...; PDF p. 499)
- **R-10.145-so-long-as** [sev 3] Use if instead of so long as, whether it means "on condition that" or "for as long as." (10.145, 10.146; PDF p. 500)
- **R-10.147-no-periodically** [sev 2] Don't use periodically; be specific (state intervals, or whenever the client asks); to express that something changes over time, use then (the Agent's loan procedures then in effect). (10.147, 10.148, 10.149...; PDF p. 500)
  - Book example: the Agent's loan procedures periodically in effect → the Agent's loan procedures then in effect
- **R-10.152-time-component-ambiguity** [sev 1] Time-component ambiguity: a reference to things that pertain to a party (affiliates, subsidiaries, clients, shares, applicable law) can mean those existing at signing or those existing at some later time. (10.152, 10.153, 10.154...; PDF p. 501)
  - Look for: a class of persons or things belonging to a party (affiliates, subsidiaries, clients, shares) or applicable law, with no time reference
  - Test: Ask whether the class could grow or change after signing, and which members the provision should cover.
  - Fix: Say so in the provision or definition: "Subsidiary" means, for a Person [on the date of this agreement] [at a given time], ... ; say whether shares includes shares acquired later.

### Chapter 10: Blog: Revisiting "Date" and "Day"

- **R-rider-date-day** [sev 3] Use date for the point on a calendar that a given day occupies and day for a unit of time; but because using date for day can't cause confusion, don't insist on either. Closing date is fine; don't change closing day to closing date either. (10.15, 10.16; elaboration)

### Chapter 13: Selected Usages

- **R-13.258-during-the-term** [sev 3] Usually omit during the term of this agreement when it modifies language of obligation, discretion, or prohibition; by default, provisions addressing party actions apply only during the term. (13.258; PDF p. 634)
- **R-13.259-during-term-duration** [sev 3] Use during the term of this agreement when deviating from the default rule to specify duration, as in During the term of this agreement and for five years thereafter, the Recipient shall not disclose ... (13.259; PDF p. 635)
- **R-13.260-continuance** [sev 3] Don't use during continuance of this agreement, and don't use continuance to mean duration; in legal usage continuance usually means postponement of a proceeding. (13.260; PDF p. 635)
- **R-13.261-effluxion-of-time** [sev 3] Don't use effluxion (or efflux or affluxion) of time. You could use passage of time, but better refer specifically to the relevant period or date, or overhaul the provision so no substitute is needed. (13.261, 13.262, 13.263; PDF p. 635)
- **R-13.415-perpetually** [sev 2] Use perpetually, not indefinitely, to mean 'perpetually'; indefinitely also means 'without limit' (a limit could be set later). (13.415, 13.416; PDF p. 671)
  - Fix: perpetually
  - Exceptions: Indefinitely in the 'without limit' sense is unobjectionable (13.415): if Acme discontinues or indefinitely suspends development.
  - Book example: During the term of this agreement and indefinitely thereafter → During the term of this agreement and perpetually thereafter
- **R-13.417-perpetually-until** [sev 3] Where the idea of 'perpetually' is followed by until, drop it; until already sets the end point. (13.417; PDF p. 672)
- **R-13.543-money-digits** [sev 3] State amounts of money in digits only, even though numbers up to ten are otherwise stated in words; don't use words and digits together (One Million Dollars ($1,000,000)). (13.543, 13.544, 13.545; PDF p. 702)
- **R-13.546-money-decimals** [sev 3] Use zeros after a decimal point only when fractional amounts appear in the same context ($2, not $2.00, unless the provision also refers to, say, $3.94); don't add and 00/100 dollars; for less than a whole unit, use $0.32, not 32 cents written with the cent sign. (13.546, 13.547; PDF p. 702)
- **R-13.548-money-separators** [sev 2] Decimal and thousands separators vary by country; pick conventions and apply them consistently. (13.548; PDF p. 702)
  - Look for: amounts using both 1,000.00 and 1.000,00 styles
  - Fix: Use one separator convention throughout.
- **R-13.549-money-large-amounts** [sev 3] A mix of words and digits for large amounts ($4.4 billion; $3 million) is acceptable and can aid reading, but don't switch to it if other numbers in the same context use all digits, and don't go beyond two decimal places. (13.549; PDF p. 703)
- **R-13.550-billion** [sev 1] Billion means a thousand million in the U.S. but a million million in Germany and many non-English-speaking regions; if confusion might arise in an international transaction, use only digits for amounts of one thousand million units or more. (13.550; PDF p. 703)
  - Fix: Digits only (1,000,000,000)
- **R-13.551-currency** [sev 1] Specify the currency, by currency sign or ISO 4217 three-letter code (EUR; NOK), but not both. Where a sign is shared (the dollar sign for dollar and peso currencies), use a code or a modified sign (A$, Mex$) in contracts between parties from different countries. An autonomous definition ("Dollars" and "$" mean United States dollars) is another way, but don't use a definition as an excuse to use a bare $ for Australian dollars; use A$ every time. (13.551, 13.552, 13.555...; PDF p. 703)
  - Look for: bare $ or dollars in a cross-border contract
  - Test: Could the currency sign refer to more than one currency? Is both a sign and a code used for one amount?
  - Fix: US$ / A$ / Mex$ or USD / AUD / MXN
- **R-13.553-currency-spacing** [sev 3] Spacing: always a space between a code and the number (EUR 2,400,000); a space after a letter sign (SFr. 334,583); no space after a symbol, even with prefixed letters (C$655,000). Placement of the sign before or after the amount varies; pick one and apply it consistently. (13.553, 13.554; PDF p. 704)
- **R-13.623-termination-prior-notice** [sev 1] Don't say Acme may terminate this agreement upon (or by giving, or with) 60 days' prior notice; upon and by giving suggest termination when notice is given, and with is unclear. A date or event restriction (After X, Acme may terminate ...) leaves unclear whether it applies to terminating or to giving notice. State that if the party notifies the other that it is terminating, the agreement terminates a stated period after the other party receives that notice. (13.623, 13.624, 13.625...; PDF p. 720)
  - Fix: If [after X] Acme notifies Widgetco that Acme is terminating this agreement in accordance with this section 4, this agreement will terminate 60 days after the day Widgetco receives that notice.
- **R-13.668-percentages** [sev 3] Don't use 100% where it would be simpler to omit it or use all (all outstanding shares; fully covered). Use half rather than 50%, and drop of if you can (half the shares). (13.668, 13.669; PDF p. 732)
- **R-13.670-percentages-in-context** [sev 3] Use 100% and 50% when the provision includes one or more other percentages (a target award-date value of 100% of the Base Salary and a maximum award value of 150% of the Base Salary). (13.670; PDF p. 732)
- **R-13.671-fractions-percentages** [sev 3] Don't use fractions other than half (one-quarter, one-fifth); use percentages. But use a fraction that would require a recurring decimal as a percentage, such as one-third or two-sevenths. (13.671; PDF p. 732)
- **R-13.832-terminates-not-expires** [sev 2] Use terminates, not expires, in termination provisions, and treat expiration as one form of termination; This agreement terminates on [date] is unambiguous. Using expires forces ponderous constructions (expires or is terminated) elsewhere, and failing to use them can cause disputes. (13.832, 13.834, 13.835...; PDF p. 769)
  - Fix: terminates; termination
- **R-13.839-terminate-and-expire** [sev 3] Don't use terminate and expire together; it shows inconsistency or redundancy. (13.839; PDF p. 771)
- **R-13.840-referring-to-termination** [sev 1] Be careful how you refer to termination. If the contract states its term with the noun term, refer explicitly to both the end of the term and party termination if you mean both (better, refer to the sections). If you mean only termination without party action, refer to those sections. If you mean only termination by a party, use the active voice (if either party terminates this agreement), not if this agreement is terminated. (13.840, 13.841, 13.842...; PDF p. 771)
  - Test: Does the reference mean end of term, termination by a party, or both? Can a disgruntled party argue end of term is expiration?
  - Fix: if either party terminates this agreement; on termination of this agreement under section 9.2 or 9.3
- **R-13.884-time-of-the-essence** [sev 2] Don't rely on time is of the essence (or of the essence); it is jargon, too general, silent on consequences, may have no legal effect, and courts have ignored it. Use a termination provision instead, supplemented if appropriate by an acknowledgment that breach of specified sections is material breach; for a drop-dead date, have the parties acknowledge that no time beyond that date will be required. (13.884, 13.885, 13.886...; PDF p. 781)
  - Fix: Termination provision; acknowledgment that breach of section x is material breach; drop-dead-date acknowledgment (13.895)
  - Exceptions: Termination for any tardiness might make sense in some contexts (13.892).

### Chapter 14: Numbers and Formulas

- **R-14.1-words-digits-mismatch** [sev 1] If a number stated in words and digits disagrees, flag it: under the judicial principle and statutes such as UCC s. 3-114 ('words prevail over numbers'), the words govern, which may yield a meaning contrary to intent because a mismatch more likely comes from changed digits. Big numbers are more prone to mismatch, since few read the words. (14.1, 14.2, 14.3...; PDF p. 801)
  - Look for: words and digits for the same number that differ
  - Test: Convert the words to a number and compare with the digits.
  - Fix: Correct the mismatch; then state the number once (digits for amounts of money).
- **R-14.5-words-and-digits** [sev 3] Don't state numbers in words followed by digits (six (6)); it is tedious, says the same thing twice (a source of inconsistency), interferes with phrasal-adjective hyphens (five (5)-year periods), and a digit in parentheses can look like an enumerated clause. (14.5, 14.6, 14.9...; PDF p. 802)
- **R-14.12-big-number-digits** [sev 3] Use just digits for the big number in a contract (for example, the loan amount in loan documentation); don't assume words and digits help. A mix of words and digits can be appropriate for very large amounts of money. (14.12, 14.17; PDF p. 803)
- **R-14.15-words-then-digits** [sev 3] Use words for whole numbers one through ten and digits for 11 and above, for ordinal (seventh, 22nd) as well as cardinal numbers. The fix for digit errors is proofreading. (14.15, 14.16, 14.18; PDF p. 804)
  - HOUSE: Digits for every number, including 1-10 and ordinals that count (2nd anniversary). Never start a sentence with a digit; restructure. See house-style.md section 2.
- **R-14.16-number-exceptions** [sev 3] Use digits even for numbers below 11 in lists of numbers, where numbers occur frequently, in percentages, in amounts of money, and in times of day; use words for numbers 11 and over at the beginning of a sentence; above all, be consistent. (14.16; PDF p. 804)
  - HOUSE: Digits for every number, including 1-10 and ordinals that count (2nd anniversary). Never start a sentence with a digit; restructure. See house-style.md section 2.
- **R-14.19-digits-only-optional** [sev 3] The manual doesn't recommend using digits for all numbers (it can seem intrusive in prose), but you can elect to do so; it is a relatively harmless choice. (14.19, 14.20, 14.21; PDF p. 805)
  - HOUSE: Digits for every number, including 1-10 and ordinals that count (2nd anniversary). Never start a sentence with a digit; restructure. See house-style.md section 2.
- **R-14.22-simple-formula** [sev 3] For a single calculation, use an amount equal to X [plus] [minus] [multiplied by] [divided by] Y; don't put a comma before plus, minus, multiplied by, or divided by; when calculating money, insert an amount equal to; and with simple formulas, omit end-product phrases such as the sum of X plus Y or the excess of X over Y. A quantum can be a percentage (an amount equal to 5% of the Overdue Amount). (14.22, 14.23, 14.24; PDF p. 805)
- **R-14.25-order-of-operations** [sev 1] When a formula mixes operations, specify the order. In equations, use parentheses even where mathematical convention would make them unnecessary ((2 x 3) + 4; (10 - 4) + 2), because a lawyer may not know the convention and left-to-right can't be counted on. (14.25, 14.26, 14.27; PDF p. 806)
  - Look for: formula combining plus/minus with multiplied by/divided by
  - Test: Could the operations be performed in a different order and give a different result?
  - Fix: Use the result of, enumeration, or parentheses in an equation.
- **R-14.28-result-of** [sev 1] In prose, whenever priority is to be given to one or more operations, use the result of before the isolated operation, or enumeration (equivalent to parentheses around each enumerated clause). Express each operation as X [plus] [minus] [multiplied by] [divided by] Y; don't use and for addition. (14.28, 14.29, 14.30...; PDF p. 807)
  - Look for: formula in prose with mixed operations
  - Fix: ... multiplied by the result of the Parent Stock Value divided by the Parent Opening Stock Value; or (1) ... multiplied by (2) ...
  - Exceptions: Because the result of is open-ended, it eliminates ambiguity only if its operation occurs at the end of the formula (14.30).
- **R-14.31-result-vs-sum** [sev 3] Prefer the result of over the [sum] [difference] [product] [quotient] of; readers may not know those terms (other than sum), and the quotient of X divided by Y is tautological. (14.31; PDF p. 807)
- **R-14.32-amount-by-which** [sev 1] Whatever the context, avoid the amount by which A exceeds B (wordy), the excess of A over B (A over B can express a fraction), and the difference between A and B (5 and 7 could give 2 or -2). (14.32; PDF p. 808)
  - Fix: A minus B
- **R-14.33-result-variant** [sev 3] A variant way to fix order of operations: put the isolated operation first, refer afterward to its result, and use the present participle of the verb of calculation (by dividing X by Y and multiplying the result by Z). (14.33; PDF p. 808)
- **R-14.36-nested-operations** [sev 1] For nested operations, use enumeration ((1) and (A) act as opening parentheses), and insert the result of or another filler phrase between adjacent enumerations; don't place enumerations next to each other without intervening text. Where the result of would appear three times, use alternatives (the product of, the sum of) despite the tautology. (14.36, 14.37, 14.38...; PDF p. 809)
  - Look for: formula with three or more sequential operations
  - Fix: (1) the result of (A) ... divided by (B) ... plus (2) ...
- **R-14.41-formula-ambiguity** [sev 1] Watch for a percentage or multiplier followed by a phrase that could apply before or after another operation (23.4% of the price in excess of X less the Costs and Incentives); use enumeration to state the intended meaning unambiguously. Likewise watch whether a minimum or maximum modifies the whole product or only one factor. (14.41, 14.42, 14.43...; PDF p. 810)
  - Fix: Enumerate: (1) 23.4% of (A) ... minus (B) ...
- **R-14.46-formula-mistake** [sev 1] Check where the amount by which sits relative to a multiplier: the amount by which (a) 4.8 times EBITDA exceeds (b) $2,000,000 is not 4.8 times the amount by which (a) EBITDA exceeds (b) $2,000,000. Consider an equation to catch such errors. (14.46, 14.47, 14.48...; PDF p. 811)
  - Test: Run sample numbers through the formula as written and as intended.
  - Fix: Restate as an equation or with enumeration.
- **R-14.50-fractions-proration** [sev 3] Use a fraction (a fraction, the numerator of which ... and the denominator of which ...) only when a number is being prorated; otherwise state the calculation as one number divided by another. (14.50, 14.51; PDF p. 812)
- **R-14.52-percentage-results** [sev 3] Express results as percentages where more comprehensible (22.45% rather than 0.2245), using a fraction, expressed as a percentage, the numerator of which ... or the result, expressed as a percentage, of X divided by Y; use division rather than the ratio, expressed as a percentage, of X to Y; and you needn't say multiplied by 100. (14.52, 14.53, 14.54...; PDF p. 812)
- **R-14.56-rounding** [sev 2] Generally provide for rounding of a formula's result: choose the increment by what is rounded (shares to the nearest whole share; interest rates often to 1/100th of 1%); say whether to round up, down, or to the nearest increment; say how to treat an amount exactly halfway; and address rounding inside the formula or, if there are several formulas, in an internal rule of interpretation. (14.56, 14.57, 14.58...; PDF p. 813)
  - Look for: formula with no rounding rule
  - Test: Does the formula say the increment, the direction, and the treatment of halves?
  - Fix: All calculations in this agreement are to the nearest cent (with $.005 being rounded upward) and to the nearest one-tenth of a share (with .05 of a share being rounded upward).
- **R-14.61-pro-rata-round-down** [sev 2] When a fixed quantity is allocated pro rata, round down; rounding up risks over-allocation, and purchasers would presumably accept an adjustment for leftovers. (14.61; PDF p. 814)
  - Fix: rounded down to the nearest whole share
- **R-14.62-tabulate-formula** [sev 3] You could tabulate a formula's enumerated clauses, but a formula complex enough to benefit from tabulation would likely benefit more from a mathematical equation. (14.62; PDF p. 815)
- **R-14.63-equations** [sev 3] The more complex the formula, the more likely an equation is clearer; use a prose lead-in, the equation, and a legend (In this formula, the following applies:). For a particularly complicated equation, consider a schedule with a sample set of calculations. (14.63, 14.64, 14.66; PDF p. 815)
- **R-14.65-no-percent-in-equation** [sev 1] Don't use the percent sign in equations (3 / 4% could mean 75% or 0.75%); if you want a percentage result, say so in the prose preamble. (14.65; PDF p. 815)
  - Look for: % inside an equation
  - Fix: State the percentage result in the lead-in.
- **R-14.67-stepped-vs-flat** [sev 1] A tiered rate schedule is ambiguous unless it says whether the rate for the band in which the total falls applies to the whole amount (a shifting flat rate) or each rate applies only to the amount within its band (a stepped rate). For a stepped rate, state increments in prose (5% of the first million dollars ...), use an IRS-style table with a cumulative base, or state in the preamble that each percentage applies only within its range; for a shifting flat rate, say the percentage for the range in which the year's revenue falls applies to all of it, or add of total gross annual revenue after each percentage. Incremental rates is not clear enough. (14.67, 14.68, 14.69...; PDF p. 816)
  - Look for: table or list of rates by revenue or volume band
  - Test: At a total in a higher band, does the higher rate apply to all of it or only to the excess?
  - Fix: ... of total gross annual revenue (flat); 5% of the first $1 million, 6% of the next $1 million ... (stepped)
- **R-14.75-range-gaps-overlaps** [sev 1] Avoid overlap between consecutive ranges (1-10 and 10-20 leave ten unclear; use 1-10 and 11-20). For ranges that can run to decimals (dollars), don't use from $1,000 to $2,000 and from $2,000 to $3,000; use over $1,000 but not over $2,000. Don't fix overlap by creating a gap (from $1,000 to $1,999 leaves $1,999.01-$1,999.99 unplaced). (14.75, 14.76, 14.77; PDF p. 818)
  - Look for: consecutive ranges sharing an endpoint, or leaving a gap
  - Test: Does every possible value fall in exactly one range?
  - Fix: over $1,000 but not over $2,000; over $2,000 but not over $3,000
  - Exceptions: A gap is appropriate if the unit comes only in whole units (1-10 / 11-20 widgets) (14.77). | Overlap matters more under a shifting flat rate than a stepped rate (14.75).
- **R-14.78-date-ranges** [sev 1] For consecutive date ranges, take care with ambiguous prepositions (from, to, until, through, between). (14.78; PDF p. 819)
  - Look for: consecutive date ranges
  - Fix: Use the time-reference rules in chapter 10.
