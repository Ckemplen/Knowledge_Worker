Using the provided list of `raw_entities` and `existing_canonical_entities`, deduplicate and organize the raw entities into logical `canonical_entities` with the appropriate properties.


You should create or update canonical entities as needed, ensuring all raw entity IDs are linked to their respective canonical versions. Provide a unified entity description summarizing how the canonical entity is represented across various sources.


# Input Details

- **raw_entities**: A list of raw entities extracted from documents. Each has properties such as `id`, `name`, and a description. These may overlap or differ in wording.

- **existing_canonical_entities**: A list of existing canonical entities with the fields: `canonical_entity_id`, `name`, `description`, and associated `raw_entity_ids`.

- Your task is to consider overlaps and deduplicate these into meaningful canonical entities, ensuring proper linking of `raw_entity_ids`.


# Steps

1. **Identify Matches or Create New Canonical Entities**:
   - Review the `raw_entities` to identify duplicates or closely related entities based on name and description.

   - Compare these to the `existing_canonical_entities` to find matches or potential updates.

   - If a raw entity aligns with an existing canonical entity, update its `description` if new descriptive information is available and add the `raw_entity_id` to the canonical entity’s `raw_entity_ids` list.

   - If no match exists, create a new canonical entity using the `name` and summarizing the descriptions of the related raw entities. Link all relevant `raw_entity_ids`.


2. **Generate Descriptions**:
   - For new canonical entities, combine descriptive information from the associated raw entities to provide a summary that accurately reflects its representation across documents.


3. **Output Requirements**:
   - Ensure that each canonical entity in the output has:

     - A `name`: Must be consistent and representative of the raw entities it encompasses.

     - A `description`: An informative multi-sentence summary derived from the associated raw entities.

     - A `canonical_entity_id`: An integer for existing entities. For new canonical entities, this should be omitted.

     - A `raw_entity_ids`: A list of one or more integers representing the IDs of the raw entities contributing to this canonical entity.




# Output Format

Provide the output as a JSON array containing canonical entities, structured as follows:

```json
[
  {
    "name": "string (Canonical Entity Name)",
    "description": "string (Canonical Entity Description)",
    "canonical_entity_id": optional integer (if updating an existing entity),
    "raw_entity_ids": [integer, integer, ...] (list of one or more raw entity IDs)
  },
  ...
]
```


# Examples

## Input Example:

**raw_entities**:

```json
[
  { "id": 101, "name": "Apple Inc.", "description": "A technology company based in Cupertino." },
  { "id": 102, "name": "apple", "description": "Fruit tree producing apples, a popular fruit." },
  { "id": 103, "name": "Apple", "description": "Leading company in smartphones and personal computers." }
]
```


**existing_canonical_entities**:

```json
[
  { "canonical_entity_id": 1, "name": "Apple Inc.", "description": "A technology company in Cupertino, California.", "raw_entity_ids": [100] }
]
```


## Output Example:

```json
[
  {
    "name": "Apple Inc.",
    "description": "A leading technology company in Cupertino, California, specializing in smartphones and personal computers.",
    "canonical_entity_id": 1,
    "raw_entity_ids": [100, 101, 103]
  },
  {
    "name": "apple",
    "description": "Fruit tree producing apples, a popular fruit.",
    "raw_entity_ids": [102]
  }
]
```


# Notes

- Ensure that every raw_entity_id is represented in exactly one canonical entity.

- Prioritize concise but accurate and informative summaries for the canonical descriptions.

- Canonical entity names should be chosen to best represent the grouped entities and avoid ambiguity.

- **Remember**: canonical_entity_id is optional for new canonical entities. If a raw entity does not match any existing canonical entity, create a new one without a canonical_entity_id.

- **Encouragement**: Look for opportunities to create new canonical entities from the raw entities provided. If a raw entity does not fit well with any existing canonical entity, it is better to create a new one.



`raw_entities`



`existing_canonical_entities`



**Remember**: canonical_entity_id is optional for new canonical entities. If a raw entity does not match any existing canonical entity, create a new one without a canonical_entity_id.

**Encouragement**: Look for opportunities to create new canonical entities from the raw entities provided. If a raw entity does not fit well with any existing canonical entity, it is better to create a new one.