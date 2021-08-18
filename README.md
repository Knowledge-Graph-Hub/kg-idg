KG-IDG
================================================
Knowledge graph for Illuminating the Druggable Genome

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=alert_status)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-idg&metric=coverage)](https://sonarcloud.io/dashboard?id=Knowledge-Graph-Hub_kg-idg)

Documentation
------------------------------------------------

**Components**

- Download: The [download.yaml](download.yaml) contains all the URLs for the source data.
- Transform: The [transform_utils](project_name/transform_utils) contains the code relevant to trnsformations of the raw data into nodes and edges (tsv format)
- Merge: Implementation of the 'merge' function from [KGX](https://github.com/biolink/kgx) using [merge.yaml](merge.yaml) as a source file.

**Utilities**

The code for these are found in the [utils](project_name/utils) folder.

- NLP using [OGER](https://github.com/OntoGene/OGER)
- [ROBOT](https://github.com/ontodev/robot) for transforming ontology.OWL to ontology.JSON

The [merge.yaml](merge.yaml) shows merging of the various KGs.

.. |sonar_quality| image:: https://sonarcloud.io/api/project_badges/measure?project=Knowledge-Graph-Hub_kg-covid-19&metric=alert_status
    :target: https://sonarcloud.io/dashboard/index/Knowledge-Graph-Hub_kg-covid-19
        :alt: SonarCloud Quality
