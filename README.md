# AI2D-RST
Repository for the conference article "Enhancing the AI2 Diagrams dataset using Rhetorical Structure Theory", published in the Proceedings of the 11th Language Resources and Evaluation Conference.

## Guide to Annotation

| Relation              | Usage         | Example  |
| :-------------------- |:------------- | :--------|
| *restatement*         | Describes a relationship in which two diagram elements could stand in for each other in the context of the entire diagram. Due to their independent status, both elements are annotated as *nucleus*. | The food web in [318.png](docs/restatement-318.png) would remain understandable even if either illustrations or their labels removed, because they restate each other. |
| *identification*      | This relationship is used to describe a label that identifies another diagram element or its part. The label is marked as a *satellite* while the identified entity is annotated as *nucleus*. | The labels in [2891.png](docs/identification-2891.png) identify specific parts of the cell. |
| *effect*              |               |          |
| *sequence*            |               |          | 
| *property-ascription* |               |          |
| *title*               |               |          |
| *none*                |               |          |


