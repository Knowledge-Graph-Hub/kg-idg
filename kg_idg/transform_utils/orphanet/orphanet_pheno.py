import uuid

from biolink.model import Association, Disease, PhenotypicFeature
from koza.cli_runner import get_koza_app

# Orphanet phenotype to disease associations
# HPO entry annotations come from the ontology itself
# so this just ingests the IDs

koza_app = get_koza_app("orphanet_pheno")

while (row := koza_app.get_row()) is not None:
    try:

        # Disease
        disease_id = "Orphanet:" + row["Disorder"]["OrphaCode"]
        disease = Disease(
            id=disease_id, name=row["Disorder"]["Name"]["#text"], category="biolink:Disease"
        )

        koza_app.write(disease)

        # Phenotype
        # Some disorders don't have any HPO phenotype associations,
        # so check the count first
        if row["Disorder"]["HPODisorderAssociationList"]["@count"] == "0":
            break
        all_assoc_phenos = row["Disorder"]["HPODisorderAssociationList"]["HPODisorderAssociation"]
        for pheno in all_assoc_phenos:
            hpo_id = pheno["HPO"]["HPOId"]
            pheno_obj = PhenotypicFeature(id=hpo_id, category="biolink:PhenotypicFeature")

            # Association
            predicate = "biolink:has_phenotype"
            association = Association(
                id="uuid:" + str(uuid.uuid1()),
                subject=disease.id,
                predicate=predicate,
                category="biolink:Association",
                object=pheno_obj.id,
            )

            koza_app.write(association, pheno_obj)

    except (TypeError, ValueError) as e:
        row_id = row["Disorder"]["@id"]
        print(f"Invalid entry: {e}. See entry {row_id}")
