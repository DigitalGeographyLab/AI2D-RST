# AI2D-RST
This repository contains code for the conference article "Enhancing the AI2 Diagrams dataset using Rhetorical Structure Theory" by Tuomo Hiippala and Serafina Orekhova, published in the Proceedings of the 11th Language Resources and Evaluation Conference.

## Caveat

Note that this repository is very much a work in progress, as the scripts in the [utils](utils/) directory relate to unpublished and ongoing work.

If you came here for the LREC paper, see the section below.

## LREC paper

Please find the conference paper [here](http://www.helsinki.fi/~thiippal/publications/2018-lrec.pdf).

## Application of Rhetorical Structure Theory to the AI2D dataset

This section documents common RST relations encountered during the annotation and presents examples of their application to the AI2D dataset. These examples are intended to illustrate how we applied RST to the AI2D diagrams, particularly during the experiments measuring agreement between annotators, as reported in the conference paper.

| Relation              | Description   | Example  |
| :-------------------- |:------------- | :--------|
| *restatement*         | A relationship in which two diagram elements could stand in for each other in the context of the entire diagram. Due to their independent status, both elements are annotated as *nucleus*. | The food web in [318.png](docs/restatement-318.png) would remain understandable even if either illustrations or their labels removed, because they restate each other. |
| *identification*      | A relationship in which an element identifies another diagram element or its part. The identifying element is marked as a *satellite* while the identified element is annotated as *nucleus*. | The labels in [2891.png](docs/identification-2891.png) identify specific parts of the cell. |
| *effect*              | A relationship in which one element affects another. The source of the effect is marked as *satellite*, while the affected element is marked as *nucleus*. | Effect is a common relation in graph-like diagrams, such as the food web in [519.png](docs/effect-519.png), indicating that gulls sustain foxes. |
| *sequence*            | A temporal or spatial sequence between diagram elements. Both elements are marked as *nucleus*. | The life cycle of a mosquito illustrated in [108.png](docs/sequence-108.png) shows a sequence of its various stages of development. | 
| *property-ascription* | A relationship in which one element describes the properties of another element. The element providing the properties is marked *satellite*, whereas the one being described annotated as *nucleus*. | [1031.png](docs/property-1031.png) shows groups of different types of plant leaves. Their properties (shape) are described using written labels. |
| *title*               | A relationship in which one element acts as a title for the entire diagram or its part. The element providing the title is marked as *satellite*, while the entire diagram is annotated as *nucleus*. | The upper part of [555.png](docs/title-555.png) features a title, which describes the entire diagram. [108.png](docs/sequence-108.png), in turn, features a title right in the middle of the diagram. |
| *none*                | A relationship used during to flag problematic relations during the annotation process: also used if one of the bounding boxes marking the elements is missing. This relation is not included in the final AI2D-RST corpus. | The copyright information in [564.png](docs/none-564.png) is not a part of the rhetorical structure of the diagram. |

The confusion matrix below shows how we used the categories above to describe the discourse relations extracted from the dataset.

<img src="docs/conf_matrix.png" alt="drawing" width="700"/>
