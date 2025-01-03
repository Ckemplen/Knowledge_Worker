Analyze the provided text and return structured information in a hierarchical JSON format based on the specified schema.

You will identify hierarchical topics (ranging from broader overarching ones to more specific subtopics) and entities within the text, summarize the document in three sentences, and provide their respective details in the updated hierarchical JSON structure.

# Steps

1. **Hierarchical Topic Extraction**
   - Identify the overarching **broad topics** discussed in the document.
     - These represent high-level themes, ideas, or classifications.
   - For each broad topic, identify **subtopics** that refine, specify, or relate to detailed aspects of the broader topics.
     - For each subtopic:
       - Assign a `name` summarizing the subtopic.
       - Write a brief `description` explaining its context or significance within the document.
       - Assign a `prevalence` value (an integer between 1 and 10) to indicate its prominence and frequency relative to the other topics or subtopics.

2. **Entity Identification**
   - Extract notable entities such as people, organizations, locations, events, or specialized terms. (Aim for at least 10)
   - For each entity:
     - Provide its `name`.
     - Write a brief `description` explaining its significance or role in the document.
     - Assign a `prevalence` value (an integer between 1 and 10) to indicate how prominently the entity features in the document.

3. **Document Summarization**
   - Create a concise summary of the document in **three sentences.**
   - Capture the main themes, arguments, or narratives conveyed in the document without altering its original intent.

4. **Hierarchy Logic**
   - Topics are represented in a nested format with broader topics containing more specific subtopics.
   - If no hierarchy is detected (e.g., when the document has only broad or flat subject matter), focus on broad topics and omit subtopics.

# Output Format

Provide all results in the following hierarchical JSON format:

```json
{
  "document_analysis": {
    "topics": [
      {
        "name": "<broad_topic_name>",
        "description": "<brief_broad_topic_description>",
        "prevalence": <int_from_1_to_10>,
        "subtopics": [
          {
            "name": "<subtopic_name>",
            "description": "<brief_subtopic_description>",
            "prevalence": <int_from_1_to_10>
          },
          ...
        ]
      },
      ...
    ],
    "entities": [
      {
        "name": "<entity_name>",
        "description": "<brief_description>",
        "prevalence": <int_from_1_to_10>
      },
      ...
    ],
    "summary": "<3_sentence_summary>"
  }
}
```

# Notes

1. **Hierarchy of Topics:**
   - Begin with broad themes and progressively add detailed subtopics as necessary.
   - A broad topic may have zero subtopics if no further hierarchical layers are inherent in the document.

2. **Prevalence Values:**
   - The `prevalence` field should reflect the frequency and significance of topics or entities in the specific document.
   - Subtopics' prevalence values are independent of broader topics and should reflect their prominence within the entire document's scope.

3. **Summary:**
   - Ensure the three-sentence summary provides a concise but comprehensive snapshot of the document’s main ideas, balancing breadth and depth.

4. **Omission Handling:**
   - If the document lacks clear subtopics or entities, focus on crafting detailed broad topics or summarizing the overarching core ideas.

# Example

**Input Text:**  
"Climate change continues to impact ecosystems globally. Rising temperatures and melting ice caps have accelerated sea level rise, while extreme weather events such as hurricanes and droughts are becoming more frequent. Renewable energy alternatives and international agreements like the Paris Accord aim to mitigate these impacts."

**Output JSON:**

```json
{
  "document_analysis": {
    "topics": [
      {
        "name": "Climate Change",
        "description": "The overarching issue of global temperature rise and environmental impacts.",
        "prevalence": 10,
        "subtopics": [
          {
            "name": "Rising Temperatures",
            "description": "Increase in average global temperatures due to greenhouse gas emissions.",
            "prevalence": 8
          },
          {
            "name": "Sea Level Rise",
            "description": "Melting ice caps causing an increase in global sea levels.",
            "prevalence": 7
          },
          {
            "name": "Extreme Weather Events",
            "description": "An increase in the frequency and intensity of hurricanes, droughts, and other severe weather.",
            "prevalence": 7
          },
          {
            "name": "Climate Mitigation Efforts",
            "description": "Global initiatives like renewable energy and international agreements to combat climate change.",
            "prevalence": 6
          }
        ]
      }
    ],
    "entities": [
      {
        "name": "Paris Accord",
        "description": "An international agreement aiming to limit global temperature rise and mitigate climate change.",
        "prevalence": 6
      },
      {
        "name": "Renewable Energy",
        "description": "Sources of energy such as wind or solar that aim to reduce dependency on fossil fuels.",
        "prevalence": 5
      }
    ],
    "summary": "Climate change is impacting ecosystems globally, with rising temperatures leading to drastic effects such as sea level rise and frequent extreme weather events. Efforts to combat these issues include renewable energy initiatives and international collaboration through agreements like the Paris Accord. These measures aim to address both the causes and effects of climate change over the coming decades."
  }
}
```

This structure allows for a hierarchical understanding of topics while maintaining clarity in entities and summaries.

# Text

`insert text here`
