KG-IDG
================================================
Knowledge Graph for Illuminating the Druggable Genome

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=alert_status)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=coverage)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)

The IDG Project
------------------------------------------------

[Full details regarding the Illuminating the Druggable Genome (IDG) Program may be found here.](https://druggablegenome.net/)

The goal of IDG is to improve our understanding of the properties and functions of proteins that are currently unannotated within the three most commonly drug-targeted protein families: G-protein coupled receptors, ion channels, and protein kinases.

The knowledge graph assembled and updated by KG-IDG serves these goals by integrating disparate sources of drug vs. target information, including the biological context and phenotype impact of these interactions. The final product supports inference of novel relationships between drugs, proteins, and diseases.

KG-IDG Documentation
------------------------------------------------

[Please see the full documentation here.](https://knowledge-graph-hub.github.io/kg-idg/)

**Prebuilt KGs**

[Prebuilt versions of the KG-IDG graph may be found here](https://kg-hub.berkeleybop.io/kg-idg/), along with their raw and transformed data sources.

**Components**

- Download: The [download.yaml](download.yaml) contains all the URLs for the source data.
- Transform: The [transform_utils](project_name/transform_utils) contains the code relevant to trnsformations of the raw data into nodes and edges (tsv format).
- Merge: Implementation of the 'merge' function from [KGX](https://github.com/biolink/kgx) using [merge.yaml](merge.yaml) as a source file.

The [merge.yaml](merge.yaml) shows merging of the various source graphs.

