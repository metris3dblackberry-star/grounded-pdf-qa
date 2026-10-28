# Evaluation report

Model: `claude-opus-5-5` (effort `low`) · top_k=6 · relevance threshold=-2.0 · 20 answerable + 6 unanswerable questions

| Metric | Result |
|---|---|
| Retrieval hit@1 | 15/20 (75%) |
| Retrieval hit@6 | 20/20 (100%) |
| Answered (answerable questions) | 19/20 (95%) |
| Facts correct | 19/20 (95%) |
| Citation points to the right document/page | 18/19 (95%) |
| Every number verified in cited text | 19/19 (100%) |
| Declined unanswerable questions | 6/6 (100%) |
| …of which declined before any LLM call | 4/6 (67%) |
| Median latency | 4.9 s |
| LLM cost for the whole run | $0.37 (62,918 input + 6,048 output tokens) |

## Per question

| ID | Question | Result |
|---|---|---|
| a01 | What is the social security wage base for 2026? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a02 | What is the standard mileage rate for business use of a car in 2025? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a03 | How much employer-provided educational assistance can be excluded from an employee's income? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a04 | Under the simplified method for the home office deduction, what is the rate and the maximum area? | hit@1 ✗ · hit@6 ✓ · facts ✓ · cite ✓ |
| a05 | How much can I deduct for a business gift to a client? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a06 | What are the limits for excluding employee achievement awards? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a07 | What is the FUTA tax rate for 2026 and on how much of each employee's wages does it apply? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a08 | What percentage of business meal expenses can I usually deduct? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a09 | How do I know whether I am a monthly or semiweekly schedule depositor? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a10 | How do I get an employer identification number? | hit@1 ✗ · hit@6 ✓ · facts ✓ · cite ✗ |
| a11 | What is the self-employment tax rate? | hit@1 ✗ · hit@6 ✓ · facts ✓ · cite ✓ |
| a12 | How long do I have to keep employment tax records? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a13 | When must an employer start withholding Additional Medicare Tax? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a14 | What is the maximum section 179 deduction for 2025? | hit@1 ✗ · hit@6 ✓ · facts ✓ · cite ✓ |
| a15 | What is the Medicare tax rate for employers and employees? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a16 | Which areas does the CISA Cyber Essentials Starter Kit ask small businesses to focus on? | hit@1 ✓ · hit@6 ✓ · facts ✗ missing staff, data, crisis · cite ✓ |
| a17 | According to CISA, what kinds of threat actors increasingly target managed service providers? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a18 | What are the exceptions to the exclusive use rule for a home office? | hit@1 ✗ · hit@6 ✓ · facts ✓ · cite ✓ |
| a19 | Which form do employers use to report FUTA tax? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| a20 | Can I deduct a home office that I also use as a guest bedroom? | hit@1 ✓ · hit@6 ✓ · facts ✓ · cite ✓ |
| u01 | What is the corporate tax rate in Germany? | best score -7.92 · declined ✓ |
| u02 | How do I reset my iPhone password? | best score -9.26 · declined ✓ |
| u03 | What is the minimum wage in California? | best score -6.37 · declined ✓ |
| u04 | Which accounting software is best for a small business? | best score 1.32 · declined ✓ |
| u05 | How large are GDPR fines for a data breach? | best score -10.01 · declined ✓ |
| u06 | What is the standard mileage rate for 2027? | best score 5.59 · declined ✓ |

## Answers

**a01. What is the social security wage base for 2026?**

> For 2026, the social security wage base limit is $184,500 [1]. The social security tax rate is 6.2% each for the employer and employee (12.4% total) [1]. The wage base limit is the maximum wage subject to the tax for the year, and only social security tax has one. There is no wage base limit for Medicare tax [1]. For comparison, the limit was $176,100 in 2025 [2].

**a02. What is the standard mileage rate for business use of a car in 2025?**

> For 2025, the standard mileage rate for business use of a car is 70 cents ($0.70) per mile [1]. It applies to the cost of operating your car, van, pickup, or panel truck for each mile of business use during 2025 [2], and covers business miles driven from January 1–December 31 for 2025 [3]. If you choose the standard mileage rate for a year, you can't deduct your actual expenses for that year except for business-related parking fees and tolls, though you may still be able to deduct interest paid on a car loan [4]. For a car you own, you must choose the standard mileage rate in the first year the car is available for use in your business; for a leased car, you must use it for the entire lease period (including renewals) [5]. You can't use the standard mileage rate if, for example, you operate five or more cars at the same time or claimed a section 179 deduction on the car [5].

**a03. How much employer-provided educational assistance can be excluded from an employee's income?**

> You can exclude up to $5,250 of educational assistance you provide to an employee under an educational assistance program from the employee's wages each year [1]. Per Publication 15-B (2026), P.L. 119-21 permanently extends the $5,250 exclusion, including employer payments of student loans, for payments made after 2025 [2]. If you don't have an educational assistance plan, or you provide more than $5,250, you must include the value of the benefits as wages unless they qualify as working condition benefits [1]. Key program conditions include: no more than 5% of benefits during the year may go to shareholders or owners (more than 5% owners) or their spouses or dependents; employees cannot choose cash or other taxable benefits instead; and you must give eligible employees reasonable notice of the program [3]. If not every other employee receives the full $5,250, the amount an owner/employee may exclude is reduced to keep within the 5% limit [4].

**a04. Under the simplified method for the home office deduction, what is the rate and the maximum area?**

> Under the simplified method, you generally multiply $5, the prescribed rate, by the area of your home (in square feet) used for a qualified business use, and the area is limited to 300 square feet [1][2]. Publication 587 (2025) gives the same $5 rate and 300-square-foot limit [2]. The allowable area is the smaller of the actual area of your home used in conducting the business and 300 square feet [3]. If you have more than one qualified business use, the 300-square-foot maximum applies to all of the businesses combined [4]. Your deduction is the smaller of this amount and the gross income limitation [3].

**a05. How much can I deduct for a business gift to a client?**

> Under IRS Publication 463 (2025), you can deduct no more than $25 for business gifts you give directly or indirectly to each person during your tax year [1]. A gift to a company that is meant for the eventual personal use or benefit of a particular person, or of a limited class of people, is treated as an indirect gift to that person or to the individuals in that class who receive it [1]. For records, you don't always have to note each recipient's name. A general listing is enough if it is evident you aren't trying to avoid the $25 annual limit per person [2].

**a06. What are the limits for excluding employee achievement awards?**

> Under IRS Publication 15-B (2026), you can generally exclude the value of achievement awards from an employee's wages if their cost isn't more than the amount you can deduct as a business expense for the year. The excludable annual amount is $1,600 ($400 for awards that aren't "qualified plan awards") [1]. The deduction limit per employee per tax year is $400 for awards that aren't qualified plan awards and $1,600 for all awards, whether or not qualified plan awards [2]. A qualified plan award is given under an established written plan or program that doesn't favor highly compensated employees. It isn't a qualified plan award if the average cost of all such awards given during the tax year is more than $400; awards of nominal value are ignored when figuring this average [2][3]. For 2026, treat any employee who received more than $160,000 in pay for 2025 as a highly compensated employee [3]. To qualify, the award must be tangible personal property given for length of service or safety achievement, as part of a meaningful presentation, and under conditions that don't create a significant likelihood of disguised pay [4]. The exclusion doesn't apply to cash, cash equivalents, gift cards, gift coupons, gift certificates, vacations, meals, lodging, tickets, stocks, bonds or other securities [4]. A 2% shareholder of an S corporation isn't treated as an employee for this exclusion [5]. If award costs exceed your allowable deduction, include in the employee's wages the larger of: the part of the cost that is more than your allowable deduction (up to the value of the awards), or the amount by which the value of the awards exceeds your allowable deduction [3].

**a07. What is the FUTA tax rate for 2026 and on how much of each employee's wages does it apply?**

> For 2026, the FUTA tax rate is 6.0%, and it applies to the first $7,000 you pay to each employee as wages during the year (the federal wage base) [1]. Your state wage base limit may be different [1]. You can generally take a credit of up to 5.4% of FUTA taxable wages for amounts paid into state unemployment funds, which reduces the rate to 0.6% if you get the maximum credit [1]. To get the maximum credit, you must have paid your state unemployment taxes in full, on time, and on all the same wages as are subject to FUTA tax, and the state must not be a credit reduction state [1]. Only the employer pays FUTA tax; it isn't withheld from the employee's wages [2]. Stop depositing FUTA tax on an employee's wages once taxable wages reach $7,000 for the calendar year [3].

**a08. What percentage of business meal expenses can I usually deduct?**

> Generally, you can deduct only 50% of your business-related meal expenses, unless an exception applies [1]. This applies whether you use the actual cost method or the standard meal allowance [2][3]. Taxes and tips on a business meal count as part of the meal cost and are subject to the 50% limit, but transportation to and from the meal is not [1]. If you are subject to the Department of Transportation's "hours of service" limits, you can deduct 80% instead [1]. Meals that are lavish or extravagant can't be deducted [2]. For example, if $110 of a $200 meal is disallowed as lavish, the deduction can't be more than $45 (50% of the remaining $90) [4]. Entertainment expenses, such as concert tickets, are not deductible at all [4]. These figures are from the 2025 editions of IRS Publications 463 and 334 [1][3].

**a09. How do I know whether I am a monthly or semiweekly schedule depositor?**

> Your deposit schedule depends on the total taxes you reported during your lookback period. If you reported $50,000 or less of taxes for the lookback period, you're a monthly schedule depositor; if you reported more than $50,000, you're a semiweekly schedule depositor [1]. For Form 941 filers, the test uses total taxes on Form 941, line 12, during the lookback period; for Form 943, 944, or 945 filers, it uses Form 943, line 13; Form 944, line 9; or Form 945, line 3 [2]. For 2026, the lookback period for a Form 943, Form 944, or Form 945 filer is calendar year 2024 [1]. The passages provided do not state the lookback period for Form 941 filers. Adjustments made on Form 941-X, 943-X, 944-X, and 945-X don't change the prior-period liability used for the lookback rule [1]. New businesses: Form 941 filers are monthly schedule depositors for the first calendar year, and Form 943, 944, or 945 filers for the first and second calendar years, because the lookback liability before you started or acquired the business is treated as zero [2]. The terms describe which set of deposit rules you follow, not how often you pay employees or make deposits [3]. Regardless of schedule, if you accumulate $100,000 or more in taxes on any day during a deposit period, you must deposit by the next business day [4].

**a10. How do I get an employer identification number?**

> You can apply for an EIN online by going to IRS.gov/EIN [1][2]. You may also apply by faxing or mailing Form SS-4 to the IRS [1]. If the principal business was created or organized outside of the United States or U.S. territories, you may also apply by calling 267-941-1099 (toll call) [1]. You get an EIN at no cost [3]. You need an EIN if you pay wages to one or more employees or file pension or excise tax returns [2], or if you're required to report employment taxes or give tax statements to employees or annuitants [1]. The EIN is a nine-digit number in the format 00-0000000 [1]. If you indicate a federal tax deposit obligation when requesting an EIN, you'll be pre-enrolled in EFTPS [4].

**a11. What is the self-employment tax rate?**

> The self-employment tax rate on net earnings is 15.3%, made up of 12.4% social security tax plus 2.9% Medicare tax; Publication 334 (2025) gives this as the 2025 rate [1][2]. For 2025, only the first $176,100 of your combined wages, tips, and net earnings is subject to the 12.4% social security part, while all of those combined earnings are subject to the 2.9% Medicare part [2]. For 2026, the maximum net self-employment earnings subject to the social security part is $184,500 [3]. You generally must pay SE tax and file Schedule SE (Form 1040) if your net earnings from self-employment were $400 or more [1][2]. An Additional Medicare Tax may also apply if your net earnings from self-employment exceed $250,000 (married filing jointly), $125,000 (married filing separately), or $200,000 (single, head of household, or qualifying surviving spouse) [4].

**a12. How long do I have to keep employment tax records?**

> You must keep all employment tax records for at least 4 years after the date the tax becomes due or is paid, whichever is later [1]. These records should be available for IRS review [2]. They should include, among other things, your EIN, amounts and dates of all wage, annuity, and pension payments, tips reported by employees, employee names, addresses, SSNs and occupations, copies of Forms W-4, dates and amounts of tax deposits, and copies of returns filed [2]. Some records must be kept longer. Records related to qualified sick leave wages and qualified family leave wages for leave taken after March 31, 2021, and before October 1, 2021, should be kept for at least 6 years [3]. Records related to qualified wages for the COVID-19 related employee retention credit paid after June 30, 2021, should be kept for at least 7 years [3]. If a crew leader furnished you with farmworkers, you must also keep a record of the crew leader's name, permanent mailing address, and EIN [3].

**a13. When must an employer start withholding Additional Medicare Tax?**

> An employer must begin withholding the 0.9% Additional Medicare Tax in the pay period in which it pays an employee wages in excess of $200,000 in a calendar year, and must continue withholding it each pay period until the end of that calendar year [1][2]. This is per IRS Publication 15 (2026) and Publication 15-B (2026). All wages subject to Medicare tax count toward the $200,000 withholding threshold [1][3]. The tax is imposed only on the employee; there is no employer share [1][2]. In qualifying corporate acquisitions, wages paid by the predecessor are treated as paid by the successor when applying the $200,000 threshold [1].

**a14. What is the maximum section 179 deduction for 2025?**

> For tax years beginning in 2025, the maximum section 179 deduction is generally $2,500,000 [1][2]. This limit is reduced (but not below zero) by the amount by which the cost of section 179 property placed in service during the 2025 tax year exceeds $4,000,000 [2][3]. If that cost is $6,500,000 or more, you can't take a section 179 deduction [2]. The deduction also cannot be more than the taxable income from the active conduct of any trade or business during the year [4]. For a sport utility vehicle, the cost that may be taken into account under section 179 cannot exceed $31,300 [3]. For a passenger automobile first placed in service in 2025, total depreciation including the section 179 deduction is limited to $12,200, or $20,200 if you take the special depreciation allowance [1].

**a15. What is the Medicare tax rate for employers and employees?**

> For 2026, the Medicare tax rate is 1.45% each for the employee and employer (2.9% total), unchanged from 2025 [1][2]. There is no wage base limit for Medicare tax; all covered wages are subject to it [2]. In addition, employers must withhold a 0.9% Additional Medicare Tax from wages paid to an employee in excess of $200,000 in a calendar year, starting in the pay period in which wages exceed $200,000 [2][3]. Additional Medicare Tax is imposed only on the employee; there is no employer share [3].

**a16. Which areas does the CISA Cyber Essentials Starter Kit ask small businesses to focus on?**

> The passages don't contain the Starter Kit's overall list of focus areas, so they can't answer the question in full. They name only one essential element: "Yourself, The Leader: Drive Cybersecurity Strategy, Investment and Culture." [1] That section says being a cyber leader does not require technical expertise, but rather an ability to change the culture of your organization, and that reducing cyber risks requires awareness of cybersecurity basics [1]. The other passages list outside resources, such as policy templates covering phishing, patching, passwords/authentication and USB use [2], and an incident response plan template [3], rather than the kit's own focus areas.

**a17. According to CISA, what kinds of threat actors increasingly target managed service providers?**

> According to CISA, cyber threat actors, including state-sponsored advanced persistent threat (APT) actors, increasingly target managed service providers (MSPs) [1]. MSPs make valuable targets because they generally have direct access to their customers' networks and data, and these actors can exploit trust relationships in MSP networks to gain access to a large number of the victim MSP's customers [1][2]. Compromises of MSPs can have globally cascading effects and introduce significant risk, such as ransomware and cyber espionage, to their customers [2].

**a18. What are the exceptions to the exclusive use rule for a home office?**

> There are two exceptions; in either case you do not have to meet the exclusive use test. The first is when you use the part of your home for the storage of inventory or product samples [1][2]. The second is when you use the part of your home as a daycare facility [1][2]. Apart from these two uses, any part of the home used for business must meet the exclusive use test [2]. That test requires you to use a specific area of your home only for your trade or business, and using the area for both business and personal purposes fails it [2][3]. Pub. 587 explains both exceptions in more detail [1].

**a19. Which form do employers use to report FUTA tax?**

> Employers report federal unemployment (FUTA) tax on Form 940, Employer's Annual Federal Unemployment (FUTA) Tax Return [1][2]. FUTA tax is reported and paid separately from social security and Medicare taxes and withheld income tax, and it is paid only from the employer's own funds; employees do not pay it or have it withheld [1]. The 2025 Form 940 is due by February 2, 2026, or by February 10, 2026 if all FUTA tax was deposited when due [2][3]. Form 940 can be filed electronically, including amended returns [3]. For household employees whose employment taxes weren't reported on Forms 941, 943, or 944, FUTA tax is reported on Schedule H (Form 1040) instead, which requires an EIN [3]. CPEOs must e-file Form 940 with Schedule R (Form 940) [3].

**a20. Can I deduct a home office that I also use as a guest bedroom?**

> Generally no, not for the part of the room used as a guest bedroom. The deduction applies only to the part of your home used exclusively and regularly for business [1][2]. You can use a home office for more than one trade or business activity, but you cannot use it for any activities that are not related to a trade or business [1]. Personal use as a guest bedroom is not a business activity. Even a separate free-standing structure qualifies only if you use it exclusively and regularly for your business [3]. Besides exclusive and regular use, the space must also meet one of these purposes: it is your principal place of business, a place where you meet or deal with patients, clients, or customers in the normal course of business, or a separate structure used in connection with your business [2]. The passages do not say how to handle a room that is only partly used for business, such as whether a separately defined business area within the room could qualify.

**u01. What is the corporate tax rate in Germany?**

> I couldn't find this in the documents. Try rephrasing, or ask about a topic the knowledge base covers.

**u02. How do I reset my iPhone password?**

> I couldn't find this in the documents. Try rephrasing, or ask about a topic the knowledge base covers.

**u03. What is the minimum wage in California?**

> I couldn't find this in the documents. Try rephrasing, or ask about a topic the knowledge base covers.

**u04. Which accounting software is best for a small business?**

> The documents do not recommend any accounting software for small businesses. They cover accounting methods (such as the cash method, an accrual method, special methods, or a combination method) rather than software products [1], and the only software they mention is tax return preparation software for filing and paying federal taxes [2][3].

**u05. How large are GDPR fines for a data breach?**

> I couldn't find this in the documents. Try rephrasing, or ask about a topic the knowledge base covers.

**u06. What is the standard mileage rate for 2027?**

> The documents do not give a standard mileage rate for 2027. They only state the 2025 rate of 70 cents ($0.70) per mile [1][2], and for 2026 they direct you to IRS.gov rather than stating a figure [3][4].

