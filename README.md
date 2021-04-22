Download-Transform-Merge Template
================================================
KG hub template for tools to generate knowledge graphs for projects

Documentation
------------------------------------------------

This template could be used for data ingestion for varied sources.

**Components**

- Download: The [download.yaml](download.yaml) contains all the URLs for the source data.
- Transform: The [transform_utils](project_name/transform_utils) contains the code relevant to trnsformations of the raw data into nodes and edges (tsv format)
- Merge: Implementation of the 'merge' function from [KGX](https://github.com/biolink/kgx) using [merge.yaml](merge.yaml) as a source file.

**Utilities**

The code for these are found in the [utils](project_name/utils) folder.

- NLP using [OGER](https://github.com/OntoGene/OGER)
- [ROBOT](https://github.com/ontodev/robot) for transforming ontology.OWL to ontology.JSON

**Examples Included**

Thes examples have download links and transform codes from other projects.

- Drug Central: Sampled from [kg-covid-19](https://github.com/Knowledge-Graph-Hub/kg-covid-19). Code located [here](project_name/transform_utils/drug_central)
- Ontology: Sampled from [kg-covid-19](https://github.com/Knowledge-Graph-Hub/kg-covid-19). Code located [here](project_name/transform_utils/ontology)
- Traits: Sampled from [kg-microbe](https://github.com/Knowledge-Graph-Hub/kg-microbe). Code located [here](project_name/transform_utils/traits)
- Example Transform: Boilerplate code for transforms. Code located [here](project_name/example_transform).

The [merge.yaml](merge.yaml) shows merging of the various KGs. In this example we have ENVO, CHEBI, NCBITaxon and the Traits KGs merged.

**Implementation**

[Use this template](https://github.com/Knowledge-Graph-Hub/kg-dtm-template/generate) to generate a template in the desired repository and then refactor the string `project_name` in the project to the desired project name. 
