# Knauf Fireboard – Functional Requirements Specification

**Version:** 1.0  
**Status:** For Review – Knauf Digital  
**Date:** 4 November 2026  
**Prototype handover:** Knauf Digital receives a ZIP copy of the prototype source code, including the referenced data, tests and documentation.  
**Purpose:** Functional requirements for the production application; suitable for adaptation into Confluence.

**Document navigation**

1. [Introduction and Purpose](#1-introduction-and-purpose)
2. [Scope and Intended Users](#2-scope-and-intended-users)
3. [User Workflow](#3-user-workflow)
4. [Functional Requirements](#4-functional-requirements)
5. [Project Management Requirements](#5-project-management-requirements)
6. [Material and Environmental Requirements](#6-material-and-environmental-requirements)
7. [Reports and Export Requirements](#7-reports-and-export-requirements)
8. [Localization and User Experience](#8-localization-and-user-experience)
9. [Calculation and Data Requirements](#9-calculation-and-data-requirements)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Prototype Reference and Known Limitations](#11-prototype-reference-and-known-limitations)
12. [Open Questions and Assumptions](#12-open-questions-and-assumptions)

## 1. Introduction and Purpose

### Executive Summary

Fireboard determines the required fire-protection thickness for supported steel profiles and provides indicative material estimates and project documentation. The existing prototype is the functional reference for the production application, including its calculation data, supported configurations and demonstrated workflows.

The production application must support standard and custom profiles, the four-step calculation workflow, project editing and local save/reopen, material and environmental information, Danish/English presentation, and the approved PDF, Excel, ZIP and editable project-file exports. This specification separates those requirements from prototype limitations and records acceptance criteria and outstanding decisions for formal handover review through Confluence. Knauf Digital is responsible for selecting and implementing the production technology, architecture and operational arrangements; the prototype's technology is not prescribed.

Fireboard supports the selection of Knauf Fireboard fire-protection thickness for steel profiles. It combines profile and fire-design inputs with calculation data to produce dimensioning results, indicative material consumption, product environmental information and project documentation.

This specification describes **what the production application must do**. The existing application is a functional prototype and reference implementation. Its framework, programming language, file organisation and deployment model are not production technology requirements. Knauf Digital will determine the production technology, architecture, hosting, security, deployment and operational arrangements.

The requirements draw on the functional and product-scope decisions supplied by Knauf Commercial / the designated product owner, the existing [as-built functional specification](functional-specification.md), and the source, data and tests in the prototype ZIP supplied to Knauf Digital. Approval of functional scope does not constitute engineering, regulatory or environmental approval; the relevant responsibility categories are distinguished in section 12. The as-built document describes an earlier baseline and has not been changed. Where it differs from the current code or the approved decisions, this document identifies the distinction rather than carrying obsolete statements into the target requirements.

### 1.1 Requirement conventions

| Prefix | Meaning |
| --- | --- |
| FR | Functional capability, project management, material and environmental functionality |
| DR | Calculation and data requirements |
| UX | User interaction and localization requirements |
| EX | Reports and export requirements |

Each numbered requirement includes a statement, priority, verifiable acceptance criteria and current prototype status. **Must** denotes essential functionality approved within the product scope by Knauf Commercial / the designated product owner, with existing reference behavior used to make that functionality testable. This review version does not introduce speculative features as Should or Could requirements. Unapproved extensions and unresolved policy details appear in section 12 without requirement priorities.

Prototype status has the following meaning:

- **Implemented:** the relevant behavior is present in the reviewed code; this is not a claim of production acceptance or independent engineering verification.
- **Partial:** some behavior is present, but an identified gap prevents full compliance with the requirement.
- **Gap:** the approved target behavior is not implemented.
- **Evidence incomplete:** the repository cannot establish compliance, for example the lifecycle coverage of individual environmental factors.

### 1.2 Calculation and metadata semantics

A **current calculation** is the calculation being entered or edited. A **saved calculation** is an entry explicitly added to or updated within a project. A **saved material snapshot** is the material result stored by that Add/Update action. Saving a project file preserves the project; it is not equivalent to updating its calculations.

The latest entered project name, author, company and description must be accepted as part of a report-download action without a separate field-application step. This does not silently update saved engineering results or saved material snapshots. Individual exports concern the current valid calculation; project exports concern the explicitly saved calculations. Section 12 records the need to confirm this interpretation of “latest committed calculation” during formal review.

## 2. Scope and Intended Users

The application supports people specifying, reviewing or estimating Fireboard protection for steel members, including designers, engineering consultants, technical advisers and estimating teams. These are intended activities, not prescribed account roles or access permissions. Formal audience restrictions remain for Knauf Commercial / the designated product owner to confirm; engineering responsibility wording requires input from the relevant Knauf technical/R&D owner.

The functional scope includes:

- Standard and custom profiles, supported cladding arrangements and table-based thickness determination.
- Indicative materials, length and waste allowances, alternative approved build-ups, CO₂ information and product-document links.
- Projects containing multiple calculations, explicit calculation updates, local project-file saving and reopening.
- Individual and project reports, material workbooks and documentation packages.
- Danish and English presentation.

The application does not determine structural capacity, loads or the design steel temperature. The temperature is supplied by the structural designer or responsible engineering consultant, typically through steel manufacturer's drawings or associated design documentation. The application does not verify the engineering suitability of that externally supplied temperature.

The requirements do not authorize general-purpose geometry modelling, custom-profile material estimation, automatic cutting or package optimization, purchasing, pricing, stock management or supplier ordering. These are absent from the prototype and are not approved additions. User accounts, server-side project storage and collaboration are not specified as required or prohibited production features; decisions concerning such services belong to the subsequent product and technical scope agreed with Knauf Digital.

A calculation result is not a certification, regulatory approval or independent engineering verification. Environmental information is not a complete building lifecycle assessment. References to BR18 describe the applied methodology approved for this product scope, not a guarantee of legal compliance.

## 3. User Workflow

| Step | User activity | Functional output |
| --- | --- | --- |
| Profile | Select a standard category and size, or define a custom profile and its Ap/V input method. | Profile identity and basis for the profile factor. |
| Cladding | Select a cladding method and the number of protected sides. | A supported protection arrangement and, where applicable, completed geometry-based Ap/V. |
| Fire Requirements | Select R30, R60, R90 or R120 and enter the externally determined design steel temperature. | Inputs for the appropriate thickness data. |
| Result | Review Ap/V and thickness, project information, and applicable material results; add/update a calculation or export. | A valid calculation result and the permitted project/export actions. |

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| UX-001 | Provide the four-step Profile, Cladding, Fire Requirements and Result workflow, with understandable navigation and input validation. | Must | Users can move between the four steps without losing applicable inputs. Opening Result with incomplete or unsupported inputs gives an actionable explanation and does not present an invalid thickness as a valid result. | Implemented workflow and checks; localization of some validation messages is partial. |

Returning to an earlier step permits review and editing. The production application need not reproduce the prototype's exact navigation widgets or page arrangement. Any changed input must be reflected in the current calculation before that result is presented or exported as current.

## 4. Functional Requirements

### 4.1 Profiles and fire dimensioning

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| FR-001 | Allow selection of standard steel profiles from the supplied category-specific catalogue. | Must | The catalogue exposes H profiles (HEA/HEB/HEM), I profiles (IPE/INP), U profiles (UNP), hot- and cold-rolled square and rectangular hollow sections, and medium and heavy circular hollow sections. The selected category and size remain distinguishable throughout calculation and reporting. | Implemented. Catalogue content is data-driven; the reviewed baseline has 3,050 distinct category/profile/method/sides configurations. |
| FR-002 | Support named custom profiles with directly entered Ap/V. | Must | A user can name a custom profile and enter a positive Ap/V in m²/m³. Round the value upward to the nearest whole number before thickness lookup; a result requires that rounded value to be at most 380 and a valid thickness to exist. Saved custom names and values can be restored. | Partial: entry and restoration exist, but the prototype truncates fractional direct Ap/V instead of applying the approved upward rounding. |
| FR-003 | Support custom profiles whose Ap/V is determined from the reference geometry inputs. | Must | Users can enter a and b in mm and steel area A in mm², select protected sides, obtain Ap/V and review guidance for the input convention. Round positive calculated Ap/V upward to the nearest whole number before thickness lookup and apply the maximum of 380. Invalid or incomplete geometry cannot produce a valid result. | Partial: geometry and Danish/English guidance exist, but the prototype rounds Ap/V to the nearest integer rather than always upward. It is a prescribed geometry convention, not arbitrary shape modelling. |
| FR-004 | Support clamp cladding and beam/PHL profile cladding with the permitted protected-side configurations. | Must | The selected method and sides are included in calculation matching. Unsupported combinations are rejected. Under the current data, circular standard profiles support clamp cladding on four sides; other categories support only combinations actually present in the data. | Implemented lookup validation. Some unsupported choices remain visible until validation. |
| FR-005 | Support fire resistance durations R30, R60, R90 and R120. | Must | Each duration selects the corresponding approved thickness data. The selected duration appears in results, saved calculations and calculation reports. | Implemented. |
| FR-006 | Accept design steel temperature as an external engineering input and explain its source and responsibility. | Must | Users enter the temperature supplied by the structural designer or responsible consultant. The application does not calculate it or imply it has verified structural adequacy. Values must be supported by the calculation data; the current reference accepts whole degrees from 350 to 750 °C inclusive. | Partial: input and range validation exist; the complete approved responsibility guidance is not established in the UI. |
| FR-007 | Present the calculated Ap/V and required total Fireboard thickness for valid inputs. | Must | A supported case displays Ap/V in m²/m³ and thickness in mm together with the selected engineering inputs. Unsupported or incomplete cases do not receive a valid thickness result. A changed input cannot be presented alongside an unrelated previous result. | Implemented dimensioning and result display; some error messages remain unlocalized. |

### 4.2 Custom-profile functional boundary

Custom profiles support thickness calculations, calculation reports and project persistence. The prototype does not calculate their material consumption or material CO₂, including for geometry-based custom profiles. This draft does not approve an extension to custom-profile quantities. Exports must identify unavailable quantities rather than imply that the requirement is zero; see FR-020 and EX-004.

## 5. Project Management Requirements

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| FR-008 | Maintain shared project metadata comprising project name, prepared by, company and multiline description. | Must | Metadata can be edited, saved and reopened. Generated calculation reports use the project information applicable to the export action. No user-entered report date overrides the generation date. | Partial: fields and persistence exist; immediate-download synchronization has a confirmed gap. The redundant date field has been removed. |
| FR-009 | Allow a project to contain multiple independent calculations, with one calculation able to document multiple profiles under identical engineering conditions. | Must | Adding a new valid calculation preserves existing entries and their stored material results. Standard and custom profiles can coexist. Ten HEB100 profiles of 6 m each, with identical category, size, fire duration, design temperature, cladding method and protected sides, can use one calculation and a combined material-estimation length of 60 m. No separate profile-count input or duplicate calculations are required for this case. | Implemented project entries and length-based estimates support the approved approach. Exact repetition of the most recently added calculation is suppressed by the prototype; no new duplicate-calculation feature is required. |
| FR-010 | Restore the selected saved calculation for review and editing. | Must | Selecting calculation A after B restores A's category, profile/name, method, protected sides, fire inputs and material settings. Custom profiles restore their Ap/V method and relevant direct or geometry values. Other saved entries remain intact. | Implemented, including corrected custom-profile restoration. |
| FR-011 | Provide an explicit Update Calculation action that replaces the selected saved calculation and its applicable material snapshot. | Must | Updating an existing entry changes that entry without increasing the project count. Its saved result and material quantities correspond to the reviewed valid inputs. Other calculations are unchanged. | Implemented with regression coverage. |
| FR-012 | Allow deletion of a selected saved calculation after confirmation. | Must | Confirmation identifies the intended deletion. Cancel leaves the project unchanged; confirm removes only that entry and removes its contribution from combined material quantities. | Partial: deletion and rebuilding totals exist; confirmation is a gap. |
| FR-013 | Provide New Calculation as an independent current calculation without modifying saved project calculations. | Must | After New Calculation, editing and adding the new calculation does not overwrite an existing entry. Saved calculations and shared project metadata remain intact. | Implemented independence. Some custom input values can remain visible; this prototype behavior was accepted and is not an unresolved defect. A fully blank draft is not imposed by this requirement. |
| FR-014 | Provide New Project to clear the current project after confirmation. | Must | Cancel preserves current project information and calculations. Confirm clears project calculations and metadata and resets the current workflow to its initial state. Previously downloaded local files are unaffected. | Partial: clearing/resetting exists, but the prototype acts without confirmation. |
| FR-015 | Allow projects to be saved locally and reopened, with understandable handling of incompatible or invalid files. | Must | A supported project file round-trips project metadata, multiple calculations and material snapshots. An invalid file produces an explanation rather than being accepted as a valid project. Existing supported `.fireboard` files are included in compatibility acceptance. | Implemented version-1 local save/open and structural validation. Production compatibility beyond the supplied file set is OQ-05. |
| FR-016 | Preserve previously saved results on opening, without automatic recalculation against newer data. | Must | Opening an older supported file retains its stored Ap/V, thickness and material quantities. Users must select, review and explicitly update an entry to apply current data. Unmodified entries remain unchanged. | Implemented preservation. Data-revision identification and historical-file guidance are limited. |
| FR-017 | Preserve each calculation's applicable material settings while navigating and switching calculations. | Must | Profile length, waste and valid selected build-up are restored for the selected calculation. Navigating away and back does not silently discard these settings or copy another calculation's settings. | Implemented. Retained settings and saved quantities can differ until Update Calculation. |

Historical engineering results must not be silently “corrected” merely because an old project is reopened or its report is downloaded. This includes files predating the category-specific lookup, clamp catalogue or maximum-Ap/V corrections. The user must explicitly review and update the affected calculations; presentation and guidance for historical files require the decisions in section 12.

## 6. Material and Environmental Requirements

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| FR-018 | Offer the valid material build-up variants for the required total Fireboard thickness. | Must | Only variants supported by the supplied layer rules are selectable. Changing a variant updates applicable products and quantities without changing the required total thickness. A previously selected variant is retained only if still valid. | Implemented. |
| FR-019 | Support decimal profile length in metres and decimal waste percentage as material-estimate inputs, defaulting to 6.0 m and 10%. | Must | Length must be greater than 0 m; waste must be at least 0%, with no separate upper waste limit. For multiple profiles with identical engineering conditions, use their combined total length. Both inputs and units remain visible and persist with the calculation. Invalid input produces a clear validation message and never silently becomes zero. | Partial: inputs, approved defaults and length-based estimates exist, but the prototype does not consistently enforce these ranges or reject invalid text instead of converting it to zero. |
| FR-020 | Refresh the current material result when length, waste or build-up changes, where material calculation is supported. | Must | After changing a valid input, the current table, applicable CO₂ and individual material export agree with that input. Invalid length or waste is explained rather than presented as a valid zero-quantity estimate. For custom profiles without material support, the application explicitly reports that quantities and material CO₂ are unavailable. | Partial: refresh and custom-profile exclusion exist; length/waste validation needs correction. Project workbook notes can still show numeric zero placeholders. |
| FR-021 | Update saved project material snapshots only through explicit Add/Update Calculation actions. | Must | For a saved 6 m calculation, editing the current length to 12 m refreshes the current estimate but leaves the saved 6 m material snapshot unchanged until Update Calculation. Saving/reopening the project alone does not substitute the 12 m quantities. | Implemented. The distinction needs clearer user communication. |
| FR-022 | Provide combined material quantities from saved project material snapshots and preserve a per-calculation breakdown. | Must | Combined totals equal the sum of included saved quantities for each material and unit. Deleting/updating an entry changes only its contribution. An unsaved current draft is not silently included. | Implemented totals and breakdown exports, with identity/localization limitations described in section 11. |
| FR-023 | Distinguish actual materials independently of translated descriptions and intentionally blank displayed article numbers. | Must | Distinct 50 mm and 64 mm clamps remain separate even when both display blank article numbers. Repeated identical clamps aggregate. Switching language cannot change material identity or split/merge quantities incorrectly. | Partial: corrected clamp catalogue and current-list aggregation are covered by tests; combined exports still fall back to displayed descriptions when article numbers are blank. |
| FR-024 | Describe material consumption as indicative rather than an exact purchasing list. | Must | Users are informed that actual consumption depends on installation, cutting methods, material utilisation and project conditions. Reported quantities are not presented as optimized board counts, stock lengths or package orders. | Partial: estimates are implemented; the complete approved explanation needs content review. No purchasing/cutting optimization exists. |
| FR-025 | Present product identification, quantities, CO₂ information and available supporting-document links for applicable materials. | Must | Material results identify the product, manufacturer, available article/DB numbers, unit, per-length rate and total quantity. Applicable numeric CO₂ uses kg CO₂e; available EPD and datasheet links are accessible, and missing links are not fabricated. | Implemented current tables and links, subject to localization and catalogue-quality limitations. |
| FR-026 | Present material CO₂ for lifecycle modules A1–A3 and C3–C4, applying the agreed BR18-related minor-component exclusions. | Must | The stated scope identifies A1–A3 and C3–C4. Applicable screws, clamps, joint tape and other specifically exempt minor components are marked excluded and do not add a numeric contribution. Inclusion/exclusion follows the approved product mapping, not a blanket assumption about all minor products. | Partial / evidence incomplete: factor-based CO₂ and `IGNORE` exclusions exist; the repository alone does not substantiate every factor's lifecycle coverage or the full methodology provenance. |

The current layer data provides the following reference build-ups. These are data content, not a requirement to hardcode the choices in the future application.

| Total thickness | Supported reference build-ups |
| --- | --- |
| 15 mm | 15 mm |
| 20 mm | 20 mm |
| 25 mm | 25 mm |
| 30 mm | 30 mm; 15 + 15 mm |
| 35 mm | 20 + 15 mm |
| 40 mm | 20 + 20 mm |
| 45 mm | 25 + 20 mm; 30 + 15 mm |
| 50 mm | 25 + 25 mm; 30 + 20 mm |

The catalogue at the reviewed baseline contains 23 unique article numbers. Article `90000005` is the minimum 50 × 9 × 1.5 mm steel clamp; `90000006` is the minimum 64 × 9 × 1.5 mm clamp. The former is selected for applicable 20 mm board constructions. These products are useful acceptance fixtures for identity and aggregation.

## 7. Reports and Export Requirements

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| EX-001 | Export an individual fire-protection dimensioning PDF for the current valid calculation, including custom profiles. | Must | The report identifies project metadata, profile category/name, cladding method, protected sides, fire duration, design temperature, Ap/V and required Fireboard thickness. It can be generated without first adding the calculation to the project. It does not include material tables or CO₂ schedules. | Implemented approved report content; latest-entered metadata at immediate download is a gap. |
| EX-002 | Export a combined fire-protection dimensioning PDF for saved project calculations. | Must | The report includes each saved calculation with its stored engineering result, shared project metadata and clear page numbering. It excludes an unsaved draft, material tables and CO₂ schedules, and does not automatically recalculate historical results. | Implemented one page per saved calculation and approved content boundaries; metadata synchronization is partial. |
| EX-003 | Export the current supported indicative material list to Excel. | Must | The workbook includes product identification, manufacturer, description, per-linear-metre consumption, unit and total quantity matching the current valid material result. Unsupported custom-profile quantities are not invented. CO₂, EPD and datasheet-link columns are excluded. | Implemented approved content boundaries; localization remains partial. |
| EX-004 | Export combined indicative project material quantities and a per-calculation material breakdown to Excel. | Must | Preserve both material-list options. Both views reconcile to saved material snapshots. Identical products combine correctly; distinct products remain distinct. Custom-profile or missing-snapshot quantities are identified as unavailable, not calculated zero. CO₂, EPD and datasheet-link columns are excluded. | Partial: both exports and approved content boundaries exist; description-based grouping, untranslated notes and zero placeholders need correction. The prototype's summed per-metre-rate column is not a meaningful project-wide consumption rate. |
| EX-005 | Export a project documentation ZIP containing the calculation report, applicable project material workbooks and available supporting documentation. | Must | The package contains the combined PDF, combined and per-calculation material workbooks where applicable, Fireboard design/installation sections, and applicable product EPD/datasheet documents. It uses the same saved project basis as the corresponding standalone exports. The editable `.fireboard` file is not automatically included. | Implemented approved package structure; latest metadata and localization are partial. |
| EX-006 | Handle unavailable external package documents explicitly without misrepresenting package completeness. | Must | A failed or empty external-document download does not silently appear as a successful inclusion. The generated package identifies omitted documents in the selected application language. Repeated product-document references do not create unnecessary duplicates of the same document type. | Implemented skipped-file README and URL deduplication; some descriptive filenames and underlying error text are not fully localized. |
| EX-007 | Export and reopen editable project data separately from PDF, Excel and ZIP documentation. | Must | The project file preserves metadata, current workflow information, saved calculations, material settings and stored snapshots required for continued review. Saving the file does not recalculate results or imply that a ZIP contains editable project data. | Implemented `.fireboard` format; compatibility and unresolved legacy identities are OQ-05. |
| EX-008 | Display the PDF generation date in Europe/Copenhagen using DD-MM-YYYY, consistently across the generated report. | Must | Test generation around UTC midnight and both daylight-saving transitions. All pages of a combined report have the same captured date. Downloading an unchanged previously generated/cached file later retains its original generation date. | Implemented and covered by automated tests. Live deployment timezone-data availability has not been directly verified. |
| EX-009 | Wrap project descriptions within the approved current PDF layout, with at most two lines and visible ellipsis for overflow. | Must | Short text retains its established position. Longer text wraps by rendered width; explicit line breaks are respected where possible; long words/URLs do not exceed the cell. Overflow ends with a fitted ellipsis. Danish characters and literal `<`, `>` and `&` are preserved. The stored full description is unchanged. Applies to both languages and PDF types. | Implemented shared rendering and coordinate-aware tests against both templates. |
| EX-010 | Ensure every generated export uses a coherent calculation/material snapshot and the project metadata accepted for that export action. | Must | Individual outputs reflect the current valid calculation; project outputs reflect explicitly saved calculation/material results. Latest entered metadata is included without a separate Apply action. A prior export must not be served as current after relevant metadata changes; unchanged historical files retain their original bytes/date. | Partial: calculation/snapshot boundaries and content-based caches exist, but the first download can contain stale metadata. |

### 7.1 Existing report design and content boundaries

The existing Danish and English PDF templates establish the approved description area and surrounding fields. Preserve the established appearance for short descriptions, fit wrapped text within that area and prevent overlap with neighbouring content. The reference templates and layout tests support visual acceptance without prescribing a rendering library or coordinate-based implementation.

Knauf Commercial / the designated product owner has approved preserving the existing export separation and content as functional scope. Individual and combined PDFs document fire-protection dimensioning, while individual, per-calculation and combined Excel material lists contain indicative material quantities. The ZIP combines calculation documentation, material lists and available supporting product documentation; the separate `.fireboard` file preserves editable project data.

Calculation PDFs do not include material tables or CO₂ schedules; the prototype also omits length/waste controls and custom geometry dimensions. Material Excel exports exclude CO₂, EPD and datasheet-link columns. The ZIP does not automatically include an editable `.fireboard` file and currently has no separate individual-calculation PDFs. No additional export types or content extensions are authorized by this specification.

The combined workbook currently sums per-linear-metre rates as well as total quantities. This is a prototype behavior: the summed rate must not be interpreted as a meaningful project-wide consumption rate. FR-022 requires correct combined total quantities. This specification introduces no alternative rate-aggregation formula.

## 8. Localization and User Experience

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| UX-002 | Support Danish and English for all application-controlled user-facing content. | Must | Switching language localizes workflow labels, guidance, validation, errors, warnings, confirmations, material notes, report labels and application-authored package explanations. Native framework/system messages may remain English where outside practical application control. | Partial: principal labels and PDF templates are bilingual; several validation and export messages remain Danish. |
| UX-003 | Use the existing catalogue's BESKRIVELSE_DK and BESKRIVELSE_EN values for material descriptions in the corresponding language without rewriting their contents. | Must | For a resolved product, Danish uses its DK field and English its EN field in applicable tables and exports. The application does not automatically translate, substitute phrases within or silently improve supplied descriptions. A change of language preserves identity and quantities. | Gap in consistent use: current tables start from Danish descriptions and apply substitutions; saved snapshots can retain prior-language text. Missing translations and catalogue wording quality require OQ-08. |
| UX-004 | Present decimal values using Danish commas and English points, without changing their numeric meaning. | Must | The same quantity is shown, for example, as 12,50 in Danish and 12.50 in English. Length and waste support decimal input. Numeric reports/material exports agree across languages. Language switching does not change calculated values. | Partial: material formatting currently uses commas in both languages. Accepted input separators and material/CO₂ precision remain OQ-09; Ap/V upward rounding and length/waste ranges and defaults are approved. |
| UX-005 | Localize Excel worksheet names and application-controlled descriptive report/document filenames. | Must | English exports use English worksheet/descriptive filenames and Danish exports use Danish equivalents. Application-authored custom-profile notes follow the selected language. User-entered portions of filenames are not automatically translated. | Partial: some titles and names are localized; worksheet names and several product-document filenames/notes remain Danish. |
| UX-006 | Preserve technical identifiers and user-authored names across language changes and project reopening. | Must | Article numbers, material codes, internal keys and the `SYSTEM` heading remain unchanged. User-entered or previously saved profile names and project text are not automatically translated. Display-label changes cannot alter engineering matching. | Partial: names and main technical identifiers are retained; legacy translated material descriptions are still involved in some grouping/resolution paths. |
| UX-007 | Accept the latest entered project metadata as part of the download action, without Ctrl+Enter or an unnecessary per-field Save/Apply step. | Must | With focus still in a changed multiline description, the user clicks Download Calculation directly; the first downloaded PDF contains the latest entered value, subject only to approved visible truncation. Repeat for combined PDFs and ZIP-contained reports, including existing cached downloads and clearing a field. No additional preparation/apply action is introduced solely to accommodate prototype framework behavior. | Gap: immediate downloads can use previously generated bytes. Sidebar project exports also precede the durable metadata update in the prototype. |
| UX-008 | Require confirmation before deleting a calculation or clearing the project with New Project. | Must | The confirmation explains the affected calculation or project. Cancel has no destructive effect; confirming performs only the stated action. | Gap: both actions currently execute immediately. This is an approved target requirement, not an unresolved product decision. |
| UX-009 | Make the difference between current edits, saved calculations and saved material snapshots clear and predictable. | Must | Users can identify which calculation is being edited and whether project quantities require Update Calculation. An update does not unexpectedly add an entry. New Calculation does not silently modify an existing saved entry. Report-generation metadata acceptance is not confused with updating saved material quantities. | Partial: add/update modes and independent calculations exist; snapshot freshness and export timing are insufficiently explicit. |
| UX-010 | Explain invalid, incomplete or unsupported inputs in the selected language without presenting diagnostics as normal user guidance. | Must | Missing engineering inputs, an unsupported configuration, upward-rounded Ap/V above 380 or an unavailable thickness produce an actionable localized message and no valid result for that case. Length at or below zero, negative waste and invalid numeric input produce clear validation messages; invalid input never silently becomes zero. Valid decimal length/waste and waste above 100% are not rejected merely for being fractional or above 100%. Application-controlled debug details are not the user's only explanation. | Partial: checks exist, but Ap/V rounding and length/waste validation do not meet the approved rules; some messages are hardcoded Danish and one unsupported lookup path displays debug details. |

External EPDs, datasheets and technical documents are not translated automatically. Their source language and content remain those of the supplier. This is distinct from localizing the application's link labels, explanatory notes and descriptive download names.

Production requirements must not inherit a requirement to press a particular framework shortcut, add an Apply button, or accept a second download attempt. UX-007 remains a target outcome for Knauf Digital to implement in its chosen technology. The prototype's synchronization limitation does not change that approved outcome.

## 9. Calculation and Data Requirements

| ID | Requirement | Priority | Acceptance criteria | Current prototype status |
| --- | --- | --- | --- | --- |
| DR-001 | Match standard-profile Ap/V and material-consumption data using category, profile, cladding method and protected sides together. | Must | All 3,050 reference configurations resolve to their own records independently of source row order. Cross-category name collisions never select another category. Missing configurations remain unsupported rather than falling back to a category-free match. | Implemented correction and exhaustive reference tests; no duplicate four-field keys at the baseline. |
| DR-002 | Round every positive Ap/V upward to the nearest whole number before thickness lookup and enforce a maximum of 380 m²/m³ for every standard and custom calculation and supported fire duration. | Must | Exact integers remain unchanged. Verify 125.0 → 125, 125.1 → 126, 125.7 → 126, 379.9 → 380, 380.0 → 380 and 380.1 → 381 → rejected. Test direct and geometry values across R30/R60/R90/R120 and both languages. Values 379 and 380 require a valid table cell; 381, 400 and 401 are rejected. A table entry above 380 cannot override the maximum. | Partial: the integer maximum is implemented, but direct truncation and nearest-integer geometry rounding differ from the approved upward-rounding rule. Standard integer catalogue values are unchanged by upward rounding. |
| DR-003 | Determine thickness only from the applicable approved fire-duration data and supported upward-rounded Ap/V/temperature coordinates. | Must | Results match the reference fixtures in section 10. Missing coordinates or blank cells are rejected even when rounded Ap/V is at or below 380. Apply DR-002 before lookup; rounding does not authorize interpolation, extrapolation or substitution for missing thickness data. | Partial: exact table lookup exists, but the prototype's preceding Ap/V normalization differs from DR-002. |
| DR-004 | Preserve the physical units and reference input meaning of custom-profile Ap/V, applying approved upward rounding to the resulting value. | Must | Direct input is in m²/m³. Geometry inputs are a/b in mm and A in mm². Invalid non-positive or incomplete geometry yields no result. Reference geometry examples reproduce the perimeter-to-area calculation described below, then round the positive result upward under DR-002 without prior nearest-integer rounding or truncation. | Partial: prescribed geometry is implemented; its final nearest-integer rounding must become upward rounding in production. Engineering confirmation of the reference geometry guidance is tracked under OQ-04. |
| DR-005 | Resolve material build-ups and associated products using the applicable layer and component rules. | Must | Each offered variant totals the required thickness. Screws/clamps are resolved by the appropriate board layer/thickness; beam and angle materials follow the relevant profile/side rules. Unsupported combinations do not create arbitrary products. | Implemented using layer, fastener, angle and beam data. |
| DR-006 | Preserve the reference quantity basis, including combined profile length, waste and repeated layers. | Must | For decimal length L > 0 and decimal waste w ≥ 0, an aggregated per-metre rate r produces r × L × (1 + w/100) in the applicable unit, without a separate upper waste limit. L can be the combined length of identical profiles under FR-009; ten 6 m members use L = 60 m without a separate count multiplier. Repeated layers contribute their full material rates. Finishing products retain their reference area basis rather than being multiplied indiscriminately by layer count. | Partial: supported standard-profile quantity formulas and total-length estimation exist, but input validation differs from FR-019. Material/CO₂ presentation precision remains OQ-09. |
| DR-007 | Apply area-based Fireboard CO₂ factors to the full aggregated board area including waste. | Must | For repeated identical Fireboard layers, reported area and CO₂ both include every layer. For an area factor f and aggregated area Q including waste, CO₂ equals Q × f before display rounding. Aggregating identical rows cannot discard their emissions. | Implemented correction with repeated-layer regression tests. |
| DR-008 | Apply each product's approved CO₂ calculation basis and exclusions consistently. | Must | Linear products use the appropriate total linear quantity; area-based products use their prescribed area basis; filler retains its reference-area treatment. Excluded products contribute no numeric CO₂. Displayed totals reconcile with the included rows under the agreed rounding policy and approved A1–A3/C3–C4 factor scope. | Partial / evidence incomplete: product-specific calculation types and exclusions exist; factor provenance and precision policy require confirmation. |
| DR-009 | Aggregate materials by stable actual identity and compatible units, independently of presentation language. | Must | Merging calculations with the same product in Danish and English preserves the summed quantity and applicable CO₂. The two clamp articles remain distinct despite blank display numbers. Reordering data or translating labels does not change totals. | Partial: current-list deduplication is covered; combined-export description fallback and legacy snapshot identity remain gaps. |
| DR-010 | Preserve the logical relationships between profile data, thickness data, component rules and the product catalogue. | Must | Every supported standard lookup has an unambiguous four-field identity. Products referenced by component rules resolve to the intended catalogue item. Data inconsistencies are not resolved by selecting an arbitrary conflicting record or inventing an engineering result. | Current dataset has 3,050 unique configuration keys, 23 unique catalogue articles and corrected clamp references. Comprehensive production data-release validation is not established. |
| DR-011 | Apply newer calculation data to a saved entry only after explicit user review and Update Calculation. | Must | An older project opens with its original results. Reviewing and updating one selected calculation uses current applicable data and replaces that entry's result/snapshot; other saved entries remain unchanged. Merely exporting or saving the project file does not recalculate it. | Implemented preservation/update behavior. Saved files do not contain a calculation-data revision identifier; introducing one is not mandated by this draft. |

### 9.1 Engineering reference conventions

The geometry reference uses exposed perimeter P = a + 2b for one or three protected sides, P = a + b for two sides, and P = 2a + 2b for four sides. The unrounded Ap/V is P × 1,000 / A. These conventions require the matching input guidance; they must not be represented as a universal model for every steel shape. Confirmation of that guidance as part of the engineering reference data remains under OQ-04.

**Approved production rule:** round every positive Ap/V upward to the nearest whole number, leaving exact integers unchanged. For geometry, apply this rule to the unrounded calculated value; for direct entry, apply it to the entered value. Validate the resulting integer against the maximum of 380 before looking up thickness. This rule applies across R30, R60, R90 and R120 and does not change category-specific selection or geometry formulas. Thus 379.9 becomes 380 and may receive a thickness if a valid cell exists, while 380.1 becomes 381 and is rejected.

**Prototype difference:** the current code truncates fractional direct Ap/V and rounds geometry-derived Ap/V to the nearest integer before checking the maximum. It therefore does not yet satisfy the approved production rounding rule. This documentation update does not change that code.

The current temperature reference is 350–750 °C in whole-degree values. The Fireboard thickness result is a total thickness in mm; layer selection is a subsequent material-build-up operation. Results outside the supported data remain unavailable even if they fall within a general input range.

For values above the maximum, the approved messages are:

- Danish: “Profilforholdet (Ap/V) overstiger 380 m²/m³, vælg et andet eller større profil”
- English: “The profile factor (Ap/V) exceeds 380 m²/m³. Select another or larger steel profile.”

### 9.2 Reference data inventory

These files identify the current reference content. CSV storage and these filenames are not prescribed as the production data architecture.

| Reference data | Purpose and relationship |
| --- | --- |
| [apv.csv](../data/apv.csv) | Standard profile categories/names, cladding and sides, Ap/V, and rates for Fireboard area, beam/PHL, angles, screws and clamps. |
| [fireboard_30.csv](../data/fireboard_30.csv), [fireboard_60.csv](../data/fireboard_60.csv), [fireboard_90.csv](../data/fireboard_90.csv), [fireboard_120.csv](../data/fireboard_120.csv) | Thickness values by design temperature and Ap/V for each duration. Underlying columns beyond 380 do not authorize their use. |
| [layer_logic.csv](../data/layer_logic.csv) | Valid layer thicknesses/order and build-up variants for a required total thickness. |
| [screw_clamp_logic.csv](../data/screw_clamp_logic.csv) | Layer/board-thickness rules referring to screw and clamp catalogue products. |
| [angle_profile_logic.csv](../data/angle_profile_logic.csv) | Angle-profile consumption associated with protected sides. |
| [beam_profile_logic.csv](../data/beam_profile_logic.csv) | Profile-related beam/PHL product selection. |
| [materials.csv](../data/materials.csv) | Product identity, manufacturer, Danish/English descriptions, CO₂ factors/types and external document links. It supports resolution of products selected by component rules. |

Engineering calculation data and fire-protection assumptions require the relevant Knauf technical/R&D owner; environmental factors, lifecycle scope and exclusions require the relevant Knauf sustainability/data owner. Formal owner assignments, maintenance arrangements and data-release approval processes remain to be agreed during handover. Functional acceptance is jointly agreed between Knauf Commercial and Knauf Digital and does not substitute for those data approvals. The presence of a value in a repository file alone is not evidence of independent engineering validation.

## 10. Acceptance Criteria

The criteria in each requirement row are normative for this draft. The following integrated scenarios support acceptance across calculation, project, export and language boundaries. Prototype test results are supporting evidence, not a substitute for production acceptance in the technology selected by Knauf Digital.

### 10.1 Calculation reference fixtures

The approved upward-rounding rule adds the following production acceptance cases. Exercise each value as direct input and as an unrounded geometry result, for all four fire durations and both languages. Permitted values still require a valid thickness at the rounded table coordinate.

| Positive Ap/V before rounding | Required lookup Ap/V | Limit outcome |
| --- | --- | --- |
| 125.0 | 125 | Permitted if the table cell is valid |
| 125.1 | 126 | Permitted if the table cell is valid |
| 125.7 | 126 | Permitted if the table cell is valid |
| 379.9 | 380 | Permitted if the table cell is valid |
| 380.0 | 380 | Permitted if the table cell is valid |
| 380.1 | 381 | Rejected before thickness lookup |

The following existing integer reference fixtures remain applicable; upward rounding leaves their Ap/V unchanged.

| Profile and arrangement | Required outcome |
| --- | --- |
| Heavy circular 100 mm, clamp, four sides | Ap/V 130 m²/m³; R60 / 350 °C gives 25 mm. |
| Medium circular 100 mm, clamp, four sides | Ap/V 154 m²/m³; it must not inherit the heavy category's value. |
| Cold-rolled square 100 × 100 × 4 mm, beam/PHL, three sides | Ap/V 242 m²/m³; R60 / 750 °C gives 20 mm. |
| Cold-rolled rectangular 100 × 60 × 5 mm, beam/PHL, three sides | R90 / 550 °C gives 35 mm. |
| Cold-rolled rectangular 180 × 100 × 5 mm, beam/PHL, four sides | Ap/V 258 m²/m³; R120 / 750 °C gives 40 mm. |
| HEB100 and IPE120, clamp, three sides | Ap/V remains 116 and 231 m²/m³ respectively. |
| Ap/V 379 and 380, temperature 750 °C | Valid reference thicknesses: R30 15 mm; R60 30 mm; R90 30 mm; R120 40 mm. |
| Ap/V 381, 400 and 401 | No valid thickness for any profile mode or supported fire duration, including where underlying tables contain a value. |
| R90 / 747 °C / Ap/V 379; R120 / 664 °C / Ap/V 17 | Unavailable reference cells remain unsupported despite Ap/V being within the maximum. |

These are fixtures from the reference data/tests, not permission to generalize thickness between inputs. Exhaustive four-field resolution and row-order independence complement these selected examples.

### 10.2 Integrated acceptance scenarios

| Scenario | Requirements covered | Pass condition |
| --- | --- | --- |
| Standard and custom workflow | UX-001; FR-001–FR-007; DR-001–DR-004 | Complete both direct and geometry custom modes and standard examples in each language. Missing/unsupported inputs do not produce valid-looking results. |
| Upward Ap/V rounding | FR-002–FR-003; DR-002–DR-004; UX-010 | Exercise all six decimal cases above through direct and geometry paths for R30/R60/R90/R120 in both languages. Exact integers remain unchanged; a rounded value above 380 is rejected before lookup. Missing cells at otherwise permitted rounded values remain unsupported. |
| Independent project editing | FR-009–FR-014; UX-008–UX-009 | Save standard and two differently named custom calculations, switch repeatedly, update only one, add another and cancel/confirm deletion and New Project. Counts, names and unaffected entries remain correct. |
| Identical profiles using total length | FR-009; FR-019; DR-006 | Document ten identical HEB100 members of 6 m as one calculation with 60 m total length and the same fire duration, design temperature, cladding and protected sides. At unchanged waste/build-up, quantities are ten times those for 6 m before display rounding. No profile-count field, extra count multiplier or duplicate calculations are needed. |
| Local historical-file round trip | FR-015–FR-017; EX-007; DR-011 | Open representative existing files and preserve stored results. Update one entry explicitly; save/reopen and verify the intended changed and unchanged values. |
| Length and waste validation | FR-019–FR-020; DR-006; UX-004; UX-010 | Verify defaults of 6.0 m and 10%. Accept length 0.5 m, waste 0%, decimal waste 12.5% and waste 150% with valid quantities. Reject length 0 or negative, negative waste, blank required input and nonnumeric text with clear localized messages; none silently becomes zero or a valid zero-quantity estimate. Test decimal input in both languages under the agreed separator convention. |
| Current versus saved material results | FR-018–FR-022; DR-005–DR-006 | Change length from 6 m to 12 m, waste and build-up. Current quantities refresh; saved project quantities change only after Update Calculation. |
| Repeated products and CO₂ | FR-023; FR-026; DR-007–DR-009 | Compare single/repeated board layers and identical/different clamps at 0% and 10% waste. No quantity or emissions are lost through aggregation. Repeat after switching languages. |
| Environmental basis | FR-025–FR-026; DR-008 | The relevant Knauf sustainability/data owner supplies the approved factor/module and exclusion mapping. Included calculations and explanatory scope match it; this does not assert independent regulatory verification. |
| First-download metadata | FR-008; EX-001–EX-002; EX-005; EX-010; UX-007 | Type, replace or clear metadata and immediately click the relevant download without a preliminary field commit. Inspect the first actual PDF or ZIP-contained PDF in both languages, with cold and existing caches. It contains the latest accepted metadata. |
| PDF date and description | EX-008–EX-009 | Exercise UTC midnight, both DST transitions, multiple report pages and later download of unchanged files. Verify two-line bounds/ellipsis for sentences, LF/CRLF, long words and literal special characters in both templates/report types. |
| Material Excel and ZIP consistency | EX-003–EX-006; FR-022; UX-005 | Standalone/project workbooks reconcile to their defined snapshots; the ZIP report matches the project basis. Simulated missing external documents are identified, and repeated links are deduplicated. |
| Approved export separation | EX-001–EX-005; EX-007 | Individual and combined PDFs contain dimensioning, with no material tables or CO₂ schedules. Individual, per-calculation and combined Excel material lists exclude CO₂/EPD/datasheet-link columns. ZIP contains documentation and available supporting files without automatically including editable `.fireboard` data, which remains a separate save/reopen output. Do not treat the prototype's summed per-metre rates as a project-wide rate or introduce an alternative aggregation formula or additional export type. |
| Complete localization | UX-002–UX-006; UX-010; DR-009 | Audit all application-controlled screens, errors, confirmations, notes, worksheet names and descriptive filenames in both languages. Catalogue descriptions match the designated fields, decimals use the selected convention, and identifiers/user names remain unchanged. |

Browser-level tests are necessary for immediate-download metadata, destructive-action confirmations and navigation. Tests must not accidentally pre-commit a field before exercising the download. Network/server delay and repeated edit/download sequences should be represented in acceptance execution; exact supported browser/device coverage is OQ-11.

The preceding implementation validation of the prototype version supplied in the ZIP reported **390 automated tests passed**, including 132 maximum-Ap/V cases and 89 PDF date/description cases. The suite was not rerun for this documentation-only revision. Existing tests do not establish compliance with the newly approved upward rounding and length/waste validation, or with the confirmation, complete localization and immediate-download target requirements.

## 11. Prototype Reference and Known Limitations

### 11.1 Baseline and traceability

Knauf Digital receives the prototype source code as a ZIP copy. References below identify individual source, data, test and documentation files within that copy; relative paths follow its folder structure. The existing `docs/functional-specification.md` is preserved unchanged. This draft is a separate requirements document, not a revision of that earlier as-built record. The prototype source ZIP is a handover artefact, distinct from the user-generated project documentation ZIP described in EX-005.

| Reference area | Relevant sources and tests |
| --- | --- |
| Workflow, profile/cladding selection, metadata and download orchestration | [app.py](../app.py): step navigation around 3314; final lookup around 4195–4370; sidebar downloads around 3107–3258; metadata/current PDF around 4495–4578. |
| Ap/V maximum and supported-result validation | [validation_helpers.py](../utils/validation_helpers.py), `validate_fireboard_lookup`; [test_apv_maximum.py](../test_apv_maximum.py). |
| Category-specific lookups | [app.py](../app.py), final Ap/V and material-rate filters; [test_profile_category_lookup.py](../test_profile_category_lookup.py). |
| Custom geometry and restoration | [geometry_helpers.py](../utils/geometry_helpers.py), [custom_profile_validation.py](../utils/custom_profile_validation.py); [test_geometry_helpers.py](../test_geometry_helpers.py), [test_custom_profile_state.py](../test_custom_profile_state.py). |
| Materials, actual identity and CO₂ | [material_helpers.py](../utils/material_helpers.py), `deduplicate_materials`, `build_material_row`, `generate_materials`; [test_material_co2.py](../test_material_co2.py), [test_screw_clamp_logic.py](../test_screw_clamp_logic.py). |
| Saved calculations, input settings and snapshots | [calculation_state.py](../utils/calculation_state.py); [test_calculation_state.py](../test_calculation_state.py). |
| Local project files | [project_io.py](../utils/project_io.py), `export_project_state`, `parse_project_file`, `import_project_state`; [test_project_io.py](../test_project_io.py). |
| PDF output and approved layout | [pdf_generator.py](../utils/pdf_generator.py), `draw_project_description`, `generate_single_pdf`, `generate_complete_pdf`; [Danish template](../PDF_template.pdf), [English template](../PDF_template_EN.pdf); [test_pdf_report_fields.py](../test_pdf_report_fields.py). |
| Excel, combined materials and ZIP | [export_helpers.py](../utils/export_helpers.py), [project_package.py](../utils/project_package.py); [test_excel_export_styling.py](../test_excel_export_styling.py), [test_project_package.py](../test_project_package.py). |
| Localization | [translations.py](../translations.py), catalogue description fields, material/export helpers and application-controlled text in [app.py](../app.py). |

### 11.2 Confirmed prototype gaps and boundaries

| Topic | Current evidence | Target interpretation |
| --- | --- | --- |
| Immediate-download metadata | The description is copied into project metadata after sidebar downloads are processed. Individual PDF bytes are prepared before the click; pending edits can arrive too late for the first download. | UX-007 and EX-010 are approved gaps to close. A framework-specific extra Apply step is not an approved target solution. |
| Destructive actions | Deletion and New Project execute without confirmation. | Confirmation is required by FR-012, FR-014 and UX-008. |
| Localization and catalogue wording | Several messages/notes, worksheet names and filenames remain Danish; current material display uses Danish text and substitutions. English catalogue fields themselves are not uniformly polished English. | Localize application-controlled content and use the supplied DK/EN fields unchanged. Catalogue editorial changes need separate approval. |
| Language-independent identity | Combined materials use displayed article numbers, falling back to descriptions; saved snapshots can retain earlier language text. | Stable product identity must govern aggregation. Ambiguous legacy rows require an agreed compatibility policy, not guessed identity. |
| Historical snapshots | Opening preserves old results; inputs and saved quantities may differ until Update Calculation. | Preservation and explicit updates are approved behavior. Clear explanation is required; automatic recalculation is not. |
| Custom quantities | No custom-profile material or CO₂ result is calculated. Some project notes have zero numeric placeholders. | Do not invent quantities or represent unavailable estimates as measured zero. Expansion of custom quantities is unapproved. |
| Numeric input handling | Direct Ap/V is truncated, geometry Ap/V rounded to nearest; unparseable length/waste can become zero and negative inputs are not comprehensively constrained. | Production must round positive Ap/V upward, reject rounded values above 380, accept decimal length > 0 and waste ≥ 0 without a separate upper waste limit, use defaults of 6.0 m/10%, and explain invalid input without silently substituting zero. These are approved gaps to close; only remaining material/CO₂ precision and input-separator details are OQ-09. |
| Identical profiles | The prototype supports total profile length and suppresses an exact repeat of the last saved calculation. | One calculation may cover multiple profiles with identical engineering conditions using their combined length. A profile-count field and duplicate-calculation feature are not required. |
| Environmental evidence | Stored factors/types and exclusions drive results; the code does not itself establish the lifecycle provenance or currency of each factor. | A1–A3/C3–C4 and the specified exclusions are approved functional scope. Supporting evidence and formal ownership require confirmation by the relevant Knauf sustainability/data owner. |
| Export boundaries | PDFs omit material/CO₂ schedules; Excel omits CO₂/document links; ZIP excludes editable project files. Combined per-metre rates are summed. | Preserve the approved separation and existing content, including both project material-list options. The summed per-metre-rate column is prototype behavior, not a meaningful project-wide rate; no replacement aggregation formula or new export type is approved. |
| Local persistence and external documents | No project database/accounts are implemented. Supporting documents depend on external URLs and can be omitted with a README when unavailable. | Local save/reopen remains required. Knauf Digital decides the production platform; external-document availability is not guaranteed by the application. |

The current baseline already includes the category-specific Ap/V/material lookup correction, full aggregated Fireboard-area CO₂ correction, distinct clamp articles, custom-profile restoration/reset correction, enforced integer Ap/V maximum, and Copenhagen generation dates/two-line PDF descriptions. Earlier as-built statements that these last two PDF behaviors or the 380 limit are missing are obsolete for this baseline.

## 12. Open Questions and Assumptions

The four decisions on upward Ap/V rounding, length/waste validation and defaults, identical profiles using combined length, and export separation are approved and no longer open questions. The remaining question IDs are retained to preserve references; gaps in numbering are intentional. None of the questions below reopens those decisions or the approved maximum, lifecycle scope, latest-metadata download outcome, confirmation requirements, language coverage or saved-result preservation policy.

The responsibility categories below identify where handover decisions belong. They do not assert that named owners, formal approval mandates or governance arrangements have already been assigned. No engineering, regulatory or environmental approval responsibility is assigned to the prototype developer personally.

| Responsibility area | Relevant organizational category |
| --- | --- |
| Functional requirements and product scope | Knauf Commercial / designated product owner |
| Engineering calculation data and fire-protection assumptions | Relevant Knauf technical/R&D owner |
| Environmental factors, lifecycle scope and exclusions | Relevant Knauf sustainability/data owner |
| Technical implementation, architecture, security, deployment and operations | Knauf Digital |
| Functional acceptance | Jointly agreed between Knauf Commercial and Knauf Digital |

### 12.1 A. Functional, engineering and environmental information requiring confirmation

| ID | Decision or evidence required | Responsibility and remaining uncertainty |
| --- | --- | --- |
| OQ-01 | Confirm the intended production audience and the user-facing statement of engineering responsibility. | Knauf Commercial / the designated product owner confirms audience and functional restrictions, with the relevant Knauf technical/R&D owner confirming engineering responsibility wording. Formal qualifications, role restrictions and wording remain undefined. |
| OQ-04 | Confirm the engineering reference release and geometry guidance, component rules, environmental factors and exclusion mappings; supply evidence connecting factors to A1–A3/C3–C4. | The relevant Knauf technical/R&D owner confirms engineering data and fire-protection assumptions; the relevant Knauf sustainability/data owner confirms environmental factors, lifecycle scope, exclusions and supporting evidence. Formal assignments and governance must be agreed with Knauf Digital under section 12.2. The repository alone cannot establish factor provenance or independent verification. No data-management UI is implied. |
| OQ-08 | Define fallback and review policy when the selected-language catalogue description is blank, ambiguous or contains Danish wording. | Knauf Commercial / the designated product owner confirms content policy with the relevant catalogue data owner; Knauf Digital implements the agreed fallback. Existing BESKRIVELSE_DK/BESKRIVELSE_EN contents must not be automatically rewritten. |
| OQ-09 | Confirm remaining material/CO₂ calculation and display precision, row-to-total reconciliation and accepted decimal-input separators. | Knauf Commercial / the designated product owner confirms presentation and input conventions with Knauf Digital. The relevant technical/R&D owner confirms material-calculation precision; the relevant sustainability/data owner confirms CO₂ precision and reconciliation. Ap/V upward rounding, decimal length/waste support, their ranges/defaults and localized decimal display are already approved; this question does not reopen them. The prototype's two-decimal formatting does not settle every material/CO₂ rounding boundary. |
| OQ-10 | Ratify the current-versus-saved export interpretation in section 1.2 and the user presentation of historical or changed-but-not-updated calculations. | Knauf Commercial / the designated product owner confirms functional semantics and wording; Knauf Digital implements the interaction. Latest entered metadata must be accepted automatically, while saved material snapshots require explicit updates. The approved export scope remains unchanged, with no per-field Apply workaround. |

### 12.2 B. Implementation, acceptance, governance and operational matters for handover

Formal data-maintenance and release responsibilities for OQ-04 must be agreed during handover among the relevant Knauf technical/R&D and sustainability/data owners, Knauf Commercial and Knauf Digital. This includes engineering tables, component rules, environmental factors, exclusions and linked documents. Knauf Digital owns the technical implementation and operational arrangements; this governance work does not transfer engineering or environmental approval to the functional product owner or authorize new functionality.

| ID | Decision or evidence required | Responsibility and remaining uncertainty |
| --- | --- | --- |
| OQ-05 | Agree the historical `.fireboard` compatibility set and treatment of missing material snapshots, unresolved product identities and incomplete legacy fields; decide whether data-revision identification is required. | Knauf Digital defines the compatibility approach with Knauf Commercial / the designated product owner agreeing supported files and user-visible handling, and the relevant technical/R&D or sustainability/data owner consulted on data interpretation. Existing files preserve results but lack a calculation-data revision identifier and may depend on rendered descriptions. Silent engineering recalculation remains prohibited. |
| OQ-11 | Agree production acceptance ownership, supported browsers/devices, review evidence and operational arrangements. | Functional acceptance is jointly agreed between Knauf Commercial and Knauf Digital. Knauf Digital is responsible for technical implementation, architecture, security, deployment and operations. Formal acceptance and operational arrangements remain to be agreed; no performance thresholds, accessibility standard, browser matrix or service level is invented here. |

The production technology and operational design remain with Knauf Digital. This document does not prescribe Streamlit, Python, CSV storage, a specific PDF library, session-state implementation, authentication technology or hosting platform. It also does not silently authorize new account, sharing, optimization or purchasing features.

Review of Version 1.0 should confirm the specification as the handover reference and resolve the remaining questions through the relevant responsibility categories. This review does not itself confer engineering, regulatory or environmental approval. Subsequent revisions can record those decisions without treating prototype defects as required production behavior.
