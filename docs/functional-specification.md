# Knauf Fireboard — Functional Specification

- **Document type:** As-built functional specification for handover to Knauf Digital
- **Repository:** `numanmorten-ctrl/Knauf-Fireboard`
- **Branch reviewed:** `development`
- **Approved baseline:** `861d8ea920c4a68b22ec7729c5f118d5416ac0d5`
- **Review date:** 3 November 2026

This specification describes the source code and repository data at the approved baseline. The branch and commit were verified; the only working-tree item before this revision was this untracked document. It includes the category-specific profile lookup, aggregated Fireboard CO₂, clamp catalogue, and custom-profile state corrections, including PR #150. Statements about functionality are based on repository inspection and, where identified, the product owner's reported manual verification in the deployed test app. This document revision does not constitute a new browser acceptance test or an engineering approval.

## 1. Introduction and Purpose

The Fireboard application supports selection of Knauf Fireboard cladding thickness for steel profiles. Users select a steel profile, cladding arrangement, fire resistance duration, and design steel temperature. The application determines the profile factor, Ap/V, and looks up the required Fireboard thickness in its supplied tables.

For standard profiles, the application also provides indicative material consumption, a material-level CO₂ display, and links to supporting product information. Users can collect multiple calculations in a project, export calculation reports and material lists, and save a project locally for later reopening.

The workflow supports people preparing fire protection specifications, material estimates, or associated project documentation. Product managers, technical advisers, designers, and estimating teams can use this specification to understand that workflow. The repository does not define formal user roles, required qualifications, or a definitive target-user policy; these require product-owner confirmation.

The functional scope is table-based cladding dimensioning and supporting documentation. It does not determine structural loading, member capacity, or critical steel temperature. A displayed thickness is the result of the selected inputs and supplied data, and does not represent an independent structural verification, certification, or regulatory compliance decision.

**Sources:** [app.py](../app.py), [Ap/V and consumption data](../data/apv.csv), and the four fire resistance tables described in section 4.

## 2. User Workflow

The main calculation workflow has four steps:

| Step | User activity | Result of the step |
| --- | --- | --- |
| 1. Profile | Select a standard profile category and size, or enter a custom profile and its Ap/V information. | Profile identity and the basis for Ap/V. |
| 2. Cladding | Select the clamp solution or beam/PHL profile solution and the protected sides. | Cladding arrangement; geometry-based custom Ap/V can now be calculated. |
| 3. Fire Requirements | Select 30, 60, 90, or 120 minutes and enter design steel temperature. | Inputs for the applicable thickness table. |
| 4. Result | Review Ap/V and total Fireboard thickness, enter project details, and, for standard profiles, review material consumption and build-up options. | A calculation that can be exported individually or explicitly added to/updated in the project. |

Users move through Previous/Next controls or select a step directly from the step bar. The step bar is not a locked sequence: users can open Result before completing earlier steps. In that case, the application requests the missing inputs instead of presenting a completed result.

Validation occurs while the page is rendered. Missing selections, invalid custom-profile inputs, invalid temperatures, unavailable profile configurations, or unavailable thickness values can stop further content from being rendered for that run. The interface does not disable every unsupported choice in advance; some combinations are rejected only at lookup time.

The project sidebar lists saved calculations with profile, fire duration, temperature, and thickness. Selecting a calculation returns to the Profile step for editing. New Calculation starts a separate draft without modifying existing saved project calculations; the accepted behavior concerning visible custom inputs is described in section 6.1. New Project clears the current session, including calculations and project information, and resets its inputs.

**Sources:** [app.py](../app.py), step navigation and result handling, approximately lines 3322–4652; [validation_helpers.py](../utils/validation_helpers.py).

## 3. Steel Profile Selection

### 3.1 Standard profiles

The application presents these categories and families:

| Category | Available family selection |
| --- | --- |
| H profiles | HEA, HEB, HEM |
| I profiles | IPE, INP |
| U profiles | UNP |
| Hot-rolled square hollow sections | Sizes from the selected category in the catalogue |
| Cold-rolled square hollow sections | Sizes from the selected category in the catalogue |
| Hot-rolled rectangular hollow sections | Sizes from the selected category in the catalogue |
| Cold-rolled rectangular hollow sections | Sizes from the selected category in the catalogue |
| Medium circular hollow sections | Sizes from the selected category in the catalogue |
| Heavy circular hollow sections | Sizes from the selected category in the catalogue |

Profile sizes are loaded from `data/apv.csv`. Users select a catalogue entry; there is no standard-profile catalogue editor in the application.

Both the final Ap/V lookup and the material-consumption lookup match **category, profile name, cladding method, and protected sides**. A profile name alone is not sufficient. The application does not fall back to another category when a matching configuration is absent.

The baseline contains 3,050 distinct four-field configurations. The category distinction is significant: for the 100 mm circular profile with clamp cladding on four sides, the heavy category has Ap/V **130 m²/m³**, while the medium category has **154 m²/m³**. The regression coverage also checks cold-rolled square and rectangular profiles, unchanged HEB100/IPE120 selections, and lookup independence from CSV row order.

### 3.2 Custom profiles

Other Profiles accepts an optional profile name and offers two input modes:

- **Direct Ap/V:** enter a positive numeric profile factor in m²/m³. The implementation converts a positive numeric input to an integer by truncating its fractional part. It does not round a fractional direct input upward.
- **Geometry-based Ap/V:** enter dimensions `a` and `b` in millimetres and steel cross-sectional area `A` in mm². All three values must be positive. After the protected sides are selected, the application calculates an integer Ap/V from the prescribed geometry and rounds it to the nearest integer.

The geometry mode provides a Danish or English guidance image and an option to close it. The implemented perimeter rules are `a + 2b` for one or three sides, `a + b` for two sides, and `2a + 2b` for four sides. The ratio is perimeter × 1,000 / steel area. These are prescribed input conventions, not a general-purpose shape modeller or automatic geometry recognition.

Custom profiles can produce a thickness result, calculation PDF, and saved project calculation. They cannot produce an individual material list, including when the geometry mode has been used. The application displays a material-consumption-unavailable message for the entire Other Profiles category.

Selecting a saved custom-profile calculation restores its own saved name, Ap/V method, and relevant values: the direct Ap/V value or geometry inputs `a`, `b`, and `A`, together with the protected sides. The user can edit and update that selected calculation. PR #150 corrected name restoration, and the product owner has manually verified correct names and Ap/V values when switching between saved custom profiles in the deployed test app.

**Sources:** [app.py](../app.py), profile selection, sidebar restoration, and custom Ap/V helpers; [geometry_helpers.py](../utils/geometry_helpers.py); [custom_profile_validation.py](../utils/custom_profile_validation.py); [test_profile_category_lookup.py](../test_profile_category_lookup.py); [test_custom_profile_state.py](../test_custom_profile_state.py).

## 4. Fire Protection Dimensioning

### 4.1 Cladding and protected sides

Two cladding methods are presented: **clamp solution** and **beam profile or PHL profile**. For non-circular categories, the interface offers one, two, three, or four protected sides. For the two standard circular categories, one-, two-, and three-sided options are disabled; only four sides can be selected.

Availability ultimately depends on the category-specific catalogue record. At this baseline, standard circular profiles have records only for the clamp solution with four protected sides. The beam/PHL option remains visible but does not produce a supported circular-profile calculation.

### 4.2 Fire duration and design steel temperature

The supported fire resistance durations are **R30, R60, R90, and R120**. The initial duration selection is 30 minutes. Design steel temperature is a user-entered whole number between **350 °C and 750 °C**, inclusive; the displayed default is 450 °C when no prior value is available.

The application does not calculate or verify that the selected temperature is appropriate to the member, loading, or design situation. The critical/design steel temperature must be established outside this application.

### 4.3 Thickness result and unsupported cases

The selected duration chooses one of these data sources: [fireboard_30.csv](../data/fireboard_30.csv), [fireboard_60.csv](../data/fireboard_60.csv), [fireboard_90.csv](../data/fireboard_90.csv), and [fireboard_120.csv](../data/fireboard_120.csv). The application performs an exact lookup using the integer Ap/V and design temperature. It does not interpolate or extrapolate missing values at runtime.

The supplied tables have temperature rows at 1 °C intervals from 350 to 750 °C and Ap/V columns from 1 to 400 m²/m³. A table coordinate does not guarantee a supported result: some cells are unavailable. Available total thicknesses across the tables are 15–50 mm in 5 mm increments. The Result page displays the calculated Ap/V and required total Fireboard thickness in millimetres.

An absent profile configuration, missing Ap/V column or temperature row, or empty thickness cell prevents a result. The missing-Ap/V-column message mentions a limit of 380 m²/m³, although the current tables extend to 400; this is an existing message/data inconsistency, not an additional enforced 380 limit.

The category correction is covered by these existing regression scenarios:

| Profile and arrangement | Fire requirement | Required total thickness |
| --- | --- | --- |
| Cold-rolled square 100 × 100 × 4 mm; beam/PHL; three sides | R60 / 750 °C | 20 mm |
| Cold-rolled rectangular 100 × 60 × 5 mm; beam/PHL; three sides | R90 / 550 °C | 35 mm |
| Cold-rolled rectangular 180 × 100 × 5 mm; beam/PHL; four sides | R120 / 750 °C | 40 mm |
| Heavy circular 100 mm; clamp; four sides | R60 / 350 °C | 25 mm |

**Sources:** [app.py](../app.py), cladding/fire steps and final lookup, approximately lines 3846–4370; [validation_helpers.py](../utils/validation_helpers.py); [test_profile_category_lookup.py](../test_profile_category_lookup.py).

## 5. Material Consumption

### 5.1 Material build-up variants

For a standard-profile result, the material list uses the layer combinations in [layer_logic.csv](../data/layer_logic.csv). Where more than one variant exists, the user selects a build-up labelled by its board layers. A previously selected variant is retained if valid for the current thickness; otherwise the first available variant is selected.

| Total thickness | Variant A | Variant B, where available |
| --- | --- | --- |
| 15 mm | 1 × 15 mm | — |
| 20 mm | 1 × 20 mm | — |
| 25 mm | 1 × 25 mm | — |
| 30 mm | 1 × 30 mm | 2 × 15 mm |
| 35 mm | 20 + 15 mm | — |
| 40 mm | 2 × 20 mm | — |
| 45 mm | 25 + 20 mm | 30 + 15 mm |
| 50 mm | 2 × 25 mm | 30 + 20 mm |

Selecting a variant changes the materials for the required total thickness. It does not change the calculated total thickness or enable arbitrary layer combinations.

### 5.2 Length, waste, and quantities

The material controls accept profile length in metres and a waste percentage. New-calculation defaults are **6.0 m** and **10%**. The material list shows consumption per linear metre, unit, and total quantity. Units include m² for boards, m for linear materials, kg for filler, and `stk` for pieces such as fasteners.

Total quantity is the material's aggregated per-metre rate × profile length × (1 + waste percentage / 100). The waste allowance applies to all generated material rows. Identical products used by repeated layers are combined before totals are displayed. Different products remain separate even if their displayed article numbers are blank.

The generated list can include Fireboard layers, layer-dependent screws and clamps, angle profiles, beam/PHL profiles, joint filler, and glass-fibre joint tape. The profile-specific rates come from `apv.csv`; product selection also uses the layer, fastener, angle, and beam-profile rule files. Filler and tape are based on the reference cladding area and are not multiplied by the number of board layers.

Quantities are estimates rather than purchase orders. The application formats quantities to two decimal places and does not convert them to whole boards, stock lengths, packs, or optimised cutting schedules. Pack sizes or stock lengths within a product description do not mean that the calculated quantity has been rounded to those purchasing units.

Length and waste use free-text numeric parsing. Unparseable values become zero for calculation; the implementation does not enforce positive length or a non-negative waste percentage. This limitation needs to be understood when reviewing an estimate.

### 5.3 Product identification and corrected clamps

The on-screen list includes article number, DB number where available, manufacturer, description, consumption rate, unit, total quantity, CO₂, EPD link, and datasheet link. Product information comes from [materials.csv](../data/materials.csv), which contains **23 unique article numbers** at this baseline.

The corrected catalogue distinguishes these foreign clamp materials:

| Internal catalogue article | Product |
| --- | --- |
| `90000005` | Steel clamp, minimum 50 × 9 × 1.5 mm |
| `90000006` | Steel clamp, minimum 64 × 9 × 1.5 mm |

The 50 mm clamp resolves for applicable 20 mm board layers. The layer rules select the 64 mm clamp for the relevant thicker layers. A 30 + 20 mm build-up can therefore contain both products, while two identical 20 mm layers aggregate their 50 mm clamp consumption into one row. The application intentionally leaves displayed article numbers blank for steel clamps; this does not make their actual material identities the same.

### 5.4 CO₂ and supporting documentation

The on-screen material list presents total product CO₂ impact in **kg CO₂e**, including the entered length and waste. The overall displayed total sums the numeric, already formatted material CO₂ values.

Fireboard products use their product-specific area factors. The corrected implementation applies each factor to the **full aggregated board area including waste**, so repeated identical layers contribute their full quantity. Linear products use their total linear quantities and corresponding factors. Filler retains its reference-area calculation; this correction did not change material quantities, factors, or other CO₂ calculation types.

Products marked `IGNORE` in the catalogue, including screws, clamps, and joint tape, display “Not included according to BR18” in English rather than a numeric contribution. This specification records the implemented exclusion and label; the repository alone does not establish the regulatory justification, lifecycle scope, or currency of the factors. The UI note states that generic datasets are used where a product-specific EPD is unavailable. The calculation itself uses the stored catalogue factors and does not obtain new factors from linked EPD documents.

EPD and datasheet icons appear where the catalogue provides a URL. Not every product has both links. These open external resources; their availability and document language are independent of the application's selected language.

**Sources:** [material_helpers.py](../utils/material_helpers.py), especially `generate_materials`, `deduplicate_materials`, and `build_material_row`; [screw_clamp_logic.csv](../data/screw_clamp_logic.csv); [angle_profile_logic.csv](../data/angle_profile_logic.csv); [beam_profile_logic.csv](../data/beam_profile_logic.csv); [test_material_co2.py](../test_material_co2.py).

## 6. Project Functionality

### 6.1 Add, select, edit, update, and delete

**Add Calculation** stores the current calculation and its matching rendered material snapshot in the project. The newly added calculation becomes the active calculation, and the action changes to **Update Calculation**. To create another calculation, the user starts New Calculation. The add helper also prevents an exact repeat of the most recently saved calculation data; this is not a project-wide uniqueness rule.

Selecting a sidebar calculation restores its profile, cladding, fire inputs, and material settings for editing. For a custom profile, this includes its saved name, selected Ap/V method, direct Ap/V or geometry inputs, and protected sides. Switching between saved custom profiles restores the selected calculation's own name and values. **Update Calculation** replaces the selected entry and its matching material snapshot rather than adding a second entry. Delete removes the selected list entry and rebuilds the combined material collection from the remaining saved calculations.

New Calculation starts an independent draft, exits editing of the selected calculation, and preserves existing saved project calculations and project metadata. Both New Calculation actions use the shared reset routine, which resets the principal selections, material settings, custom-profile state fields, and Ap/V method to their application defaults. The product owner's manual verification confirms that a separate calculation can be created without modifying existing saved calculations. Some custom input values may remain visible when starting New Calculation in the deployed test app. The product owner accepts this current visible-input behavior; it is not an unresolved defect or a guarantee that every visible input will be blank.

New Project clears the whole session immediately, removing the project calculations and metadata and resetting its inputs. The product owner has manually verified this behavior in the deployed test app. There is no confirmation dialogue or undo operation for New Project or calculation deletion in the reviewed code.

### 6.2 Project metadata

The Result page provides project name, prepared by, company, date, and description fields. Project name, prepared by, company, and description are shared across the project and used in calculation reports.

The visible date field is an exception: PDF generation uses the date at generation time, not the edited field value. The field is not included in `.fireboard` project metadata. Descriptions are drawn as a single line in the current PDF layout, so long or multiline descriptions do not have a corresponding automatic wrapping layout.

### 6.3 Local save and reopen

Save Project downloads a timestamp-named `.fireboard` file. This is a versioned JSON project file containing project metadata, current workflow inputs, saved calculations, per-calculation material settings, and saved material-table snapshots. An empty project can also be saved. It is separate from the report/package downloads.

Open Project accepts a `.fireboard` upload. The loader checks JSON format, the Fireboard file marker, supported format version (currently 1), and the principal project/calculation/material payload structures. Invalid files display an error. Supported files replace the current project's saved calculations and metadata, rebuild combined materials from their snapshots, and return the workflow to Profile with no saved calculation selected for editing. The user must select a sidebar entry to update that entry.

This is local-file persistence, not an account-based project service. Projects are held in the active application session until downloaded; the repository implements no server-side project database, automatic durable project saving, or cross-user sharing workflow.

### 6.4 Material state versus saved quantities

Profile length, waste, and selected build-up are preserved while navigating between steps and calculations. Each saved calculation has its own material settings. The implementation keeps these values separately from temporary Streamlit widget state so that hiding a widget on another step does not discard them.

There is a deliberate distinction between **retained input settings** and **saved calculated quantities**. Material input settings can be retained on the active calculation during navigation, while combined project material lists continue to use the snapshot from the last explicit Add/Update action. Changing an input or viewing a newly calculated material table does not automatically replace the saved snapshot.

For example, changing a saved calculation from 6 m to 12 m updates the currently rendered material list. Until Update Calculation is used, a combined project export can still contain quantities calculated for 6 m, even though the retained length setting is 12 m. Saving a `.fireboard` file preserves this state; it is not equivalent to updating every calculation. Users should review the current Result and use Update Calculation before exporting project totals or saving the final project.

**Sources:** [app.py](../app.py), sidebar actions and Result; [calculation_state.py](../utils/calculation_state.py), `update_selected_calculation_material_settings`, `attach_pending_materials`, `replace_selected_calculation`, and `rebuild_combined_materials`; [validation_helpers.py](../utils/validation_helpers.py), `reset_calculation_state`; [project_io.py](../utils/project_io.py); [test_calculation_state.py](../test_calculation_state.py); [test_project_io.py](../test_project_io.py); [test_custom_profile_state.py](../test_custom_profile_state.py).

## 7. Reports and Exports

| Export | Source and actual contents | Boundaries |
| --- | --- | --- |
| Individual calculation PDF | Current valid Result; one calculation page with shared project metadata, profile category/name and representative image, cladding method, protected sides, duration, temperature, Ap/V, and total Fireboard thickness. Uses a Danish or English template. | Does not require adding the calculation to the project. Does not contain the material list, selected layer variant, profile length, waste, CO₂ totals, or custom geometry dimensions. |
| Individual material Excel | Current standard-profile material table: article number, DB number, manufacturer, description, consumption per linear metre, unit, and total quantity. | Excludes the on-screen CO₂, EPD, and datasheet columns. Not available for an individual custom profile. |
| Combined project PDF | One calculation page per saved project calculation, with page numbering and current shared project metadata. | Uses saved calculation results, not an unsaved draft. Does not append material lists or a project CO₂ total. |
| Combined material Excel | Aggregated quantities from saved material snapshots, grouped by displayed article number or description when the number is blank. | Includes the seven material fields above. Sums the per-metre rate column as well as total quantities; the summed rate is not a weighted project consumption rate. No CO₂/EPD/datasheet columns. |
| Material Excel per calculation | Saved material snapshots grouped under calculation identifiers, with separators and repeated headers in a single worksheet. | Preserves the calculation breakdown instead of merging it into one quantity per product. No CO₂/EPD/datasheet columns. |
| Project ZIP | Combined calculation PDF, both project material workbooks when available, Fireboard design and installation sections, and available product EPD/datasheet files resolved from saved project materials. | Does not contain a `.fireboard` file, separate individual-calculation PDFs, or an additional CO₂ report. External files are downloaded during package generation. |
| `.fireboard` project file | Editable project state, saved calculations and material snapshots, as described in section 6. | Not a PDF, Excel workbook, or archive of source tables/product documents. Does not save the language selection or a catalogue/calculation-engine revision identifier. |

Calculation PDFs also contain the template's installation-guidance statement and link to the Fireboard installation section. They do not embed that external document.

Project report and package actions are available when the project contains saved calculations. A project containing custom profiles can still produce its calculation report and package. Project material exports include an explanatory note for custom profiles without generating quantities; a project containing only custom profiles can produce note-based material workbooks. Numeric normalization can display zero in their numeric fields, which should not be interpreted as a calculated zero material requirement.

Project ZIP generation deduplicates repeated product-document URLs within each document type. If an external download fails or returns no content, the package is still created and a `README.txt` identifies skipped files. A successful ZIP download therefore does not guarantee that every supporting document was included. The sidebar also provides direct links to the Fireboard design and installation sections.

Generated project downloads are cached for the current saved project state and language. They are regenerated when the relevant state changes; they are not an automatic live refresh of external product documents or all saved calculations.

**Sources:** [pdf_generator.py](../utils/pdf_generator.py), `generate_single_pdf` and `generate_complete_pdf`; [export_helpers.py](../utils/export_helpers.py); [project_package.py](../utils/project_package.py), `build_project_material_exports` and `create_project_package_zip`; [documentation.py](../utils/documentation.py); [app.py](../app.py), download controls and the removal of the last three material columns before export.

## 8. Language Support

The language selector offers **Dansk** and **English**, with Danish as the initial session language. The application translates the main workflow, category and cladding labels, project actions, material column headings, and much of the material description text. Calculation PDFs use separate Danish and English templates. Workbook titles and download/package names are also localized, and custom Ap/V guidance has language-specific images.

Localization is incomplete in the following confirmed areas:

- Some validation errors, including unsupported lookup messages, are hardcoded in Danish. The unsupported-profile path also displays diagnostic information.
- The custom-profile material note in project workbooks is hardcoded in Danish, including for English exports.
- Excel worksheets retain the name `Materialeliste`, and piece units remain `stk`. Formatted material numbers use decimal commas in both languages.
- Some friendly ZIP product-document filenames remain Danish. External PDF contents are not translated by changing the UI language.
- Material descriptions use the Danish catalogue description with application substitutions; the existence of an English CSV description does not mean every displayed description is sourced from it or fully translated.
- Saved material snapshots retain the descriptions and manufacturer text rendered when saved. Project export code normalizes Danish/English column names, but it does not retranslate all saved row contents. Switching languages can therefore leave mixed-language project material content, particularly description-based rows with blank article numbers.

User-entered project descriptions and names are not automatically translated. Language selection is not stored in the `.fireboard` file.

**Sources:** [translations.py](../translations.py); [app.py](../app.py), material translations; [material_helpers.py](../utils/material_helpers.py), formatting; [project_package.py](../utils/project_package.py); [export_helpers.py](../utils/export_helpers.py).

## 9. Functional Limitations

The following are confirmed boundaries of the reviewed implementation:

- **Custom-profile quantities:** no material quantities or material-level CO₂ results are generated for Other Profiles, including geometry-based inputs.
- **External design inputs:** the user supplies design steel temperature and fire duration. There is no structural capacity, load utilisation, or critical-temperature calculation.
- **Catalogue and table scope:** standard-profile results require a matching four-field record and an available table cell. There is no arbitrary profile catalogue editing, general geometry modelling, interpolation of missing results, or automatic selection of a different profile when a configuration is unsupported.
- **Estimation scope:** no package rounding, cutting optimisation, purchasing workflow, pricing, inventory, or supplier ordering is implemented.
- **Project persistence:** no user accounts or server-side project storage are implemented in this repository. Local downloads are the supported durable project mechanism. Deployment-level access controls cannot be established from this application alone.
- **Saved results:** project totals and reports can remain based on older saved calculations until explicitly updated. Opening a project does not migrate its engineering results or material snapshots to the current catalogue.
- **Validation:** file validation checks compatibility and structure, not the engineering correctness of every imported calculation. Length and waste lack range validation. The Ap/V limit message is inconsistent with table column coverage.
- **Reporting scope:** PDF reports contain dimensioning results, not material schedules or CO₂ results. Excel material exports omit CO₂ and document links. The displayed date field does not control report dates, and long descriptions are not wrapped by the PDF generator.
- **Documentation dependencies:** PDFs depend on repository templates/images; EPDs, datasheets, and packaged design/installation sections depend on external resources. Their current availability or formal applicability has not been established by this source review.
- **CO₂ scope:** the display is based on stored factors and exclusions, not a complete building lifecycle assessment or a regulatory verification service.

These boundaries describe the current application. They do not imply that additional functions have been approved or scheduled for development.

## 10. Known Functional Behaviors and Open Questions

### 10.1 Existing saved project files

Version 1 project files restore stored calculation results and material snapshots. They do not carry a data-baseline identifier and are not automatically recalculated on import. A file saved before the category or clamp corrections can therefore retain an old Ap/V, thickness, or material list until its calculation is selected, reviewed, and explicitly updated. Opening the file or downloading a new combined PDF alone does not apply the corrections to its saved values.

Older calculations without material settings use defaults when selected: 6.0 m, 10% waste, and an available build-up selected for the current result. Calculations without a material snapshot are omitted from the combined material collection; the loader does not reconstruct the missing quantities automatically. Custom-profile explanatory notes are handled separately in project material exports.

The custom profile's displayed name is stored in the calculation's `profile` field. After PR #150, sidebar selection restores that value to the custom-name input along with the saved Ap/V method and relevant values. This restoration uses the existing saved fields and requires no project-file format change. The product owner has verified switching between saved custom profiles, creating an independent calculation with New Calculation, and clearing the project and inputs with New Project. The possibility of some custom inputs remaining visible after New Calculation is accepted behavior, as described in section 6.1.

### 10.2 Clarifications required from the product owner

The questions below concern product intent or acceptance of confirmed behavior. They are not proposed features presented as implemented.

| Topic | Current evidence | Confirmation required |
| --- | --- | --- |
| Intended audience and responsibility | Workflow supports dimensioning and estimating, but no formal user-role or qualification policy is defined. | Who is the intended production audience, and what responsibility/use guidance should accompany the application? |
| Explicit project updates | Retained length/waste/build-up settings can differ from saved material quantities until Update Calculation. | Is this distinction accepted, and what user guidance should define when a calculation/project is ready for export? |
| Historical projects | Old results and material snapshots are restored without automatic recalculation or baseline migration. | How should users handle files created before the Ap/V and clamp corrections, and who decides which projects require review? |
| Custom-profile conventions | Geometry mode uses prescribed one-/two-/three-/four-sided perimeter rules; fractional direct Ap/V is truncated. | Are these input conventions and the custom-profile scope the approved functional interpretation to communicate to users? |
| Input validation and messages | Length/waste lack range validation; the error text mentions 380 while tables extend to 400. | What input boundaries and limit wording are intended? |
| CO₂ and BR18 wording | Fixed catalogue factors, generic-dataset UI wording, and `IGNORE` exclusions are implemented. | Who owns the factor/exclusion basis, lifecycle scope, and review of the displayed regulatory wording? |
| Export scope and quantities | PDFs omit materials/CO₂; Excel omits CO₂/links; combined exports sum per-metre rates; ZIP is separate from `.fireboard`. | Is this reporting scope accepted, and how should combined rate columns and indicative purchasing quantities be explained? |
| Localization | Some errors, worksheet names, descriptions, custom notes, and document filenames remain Danish; saved snapshots can retain another language. | What localization boundaries are acceptable for the English handover and production use? |
| Date and description fields | PDFs use generation date and a single description line. | What is the intended meaning of the editable date, and what description-length guidance is required? |
| Destructive session actions | New Project and deletion act immediately without confirmation or undo. | Is this interaction accepted, and what local-save guidance is required? |

**Sources:** [project_io.py](../utils/project_io.py), import/export and supported version; [calculation_state.py](../utils/calculation_state.py), restore/default/snapshot behavior; [app.py](../app.py), sidebar selection, resets, and project controls; [test_custom_profile_state.py](../test_custom_profile_state.py), custom-profile restoration, switching, updates, resets, and project-file round trips. Existing regression tests also provide evidence for the corrected profile lookups, CO₂/clamp identity, material-state persistence, and package contents. The full suite at baseline `861d8ea` passed **169 tests** in the preceding repository validation; tests were not rerun solely to revise this document.
