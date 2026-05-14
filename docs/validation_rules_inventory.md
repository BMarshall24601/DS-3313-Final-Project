** Validation Rules Inventory

Rule 1: Required Fields Present

This rule matters because it records missing critical fields that are crucial for analysis and reflects data entry failures

This rule is checked by testing columns for NaN or missing values. If critical fields are missing, the row is flagged and sent to a csv file for review.

For example: required_fields: ["Unique Key", "Created Date", "Borough"]


Rule 2: Valid Categories

This rule matters because categorical fields used for grouping or filtering should be have known values and unknown values could have various meanings.

This rule is checked by comparing values against a given allowed list and the row is flagged as an invalid category.

For example: - column: "Borough" / values: ["BRONX", "BROOKLYN", ...]


Rule 3: Regex Format Checks

This rule matters because some fields (such as zip codes or phone numbers) should conform to a certain format for future analysis.

This rule is checked by applying a regular expression pattern to each non null value and flagging as a format errorif inconsistent.

Example: - column: "Incident Zip" / pattern: '^\d{5}$'


Rule 4: Numeric Range Checks

This rule matters because values outside of the logical boundaries of numeric fields should be checked and can indicate data entry errors or unit mismatches.

This rule is checked by making selected columns of values numeric and testing against max/min bounds. If there is an inconsistency, the row is flagged as out of range.

Example: - column: "EXT1" / min: 1 / max: 5 (for a 1–5 Likert scale)


Rule 5: Duplicate ID Check

This rule matters because each record should appear once and duplicates cause inaccuracies.

This rule is checked by pandas.duplicated() on the specified unique ID column. Duplicate rows are removed during cleaning.


Rule 6: Date Format Check

This rule matters because incorrectly formatted dates can limit data analysis.

This rule is checked by testing each date column with pd.to_datetime() and values that will not allow this are flagged.


To validate a completely different dataset:

1. Update validation.required_fields with the new required column names
2. Set validation.unique_id_column to the ID column name (or remove if none)
3. Add entries to validation.valid_categories for any categorical columns
4. Add entries to validation.regex_checks for any format-constrained columns
5. Add entries to validation.range_checks for numeric columns with known bounds
6. Update validation.date_format and cleaning.date_columns if dates are present

No changes to validator.py are necessary.