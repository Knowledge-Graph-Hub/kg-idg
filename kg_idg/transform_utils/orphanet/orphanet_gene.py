import uuid

from biolink.model import Association, Disease, Protein
from koza.cli_runner import get_koza_app

# Options here include:
# Ensembl, Genatlas, HGNC,
# IUPHAR, OMIM, Reactome
# Swissprot
PREFERRED_GENE_SOURCES = ["SwissProt"]
# This is interpreted as UniProtKB ID,
# and we treat it as a Protein

RELATION_TYPE_MAP = {
    "Disease-causing germline mutation(s) in":
        "biolink:condition_associated_with_gene",
    "Disease-causing germline mutation(s) (loss of function) in":
        "biolink:condition_associated_with_gene",
    "Disease-causing germline mutation(s) (gain of function) in":
        "biolink:condition_associated_with_gene",
    "Role in the phenotype of":
        "biolink:condition_associated_with_gene",
    "Major susceptibility factor in":
        "biolink:condition_associated_with_gene",
    "Disease-causing somatic mutation(s) in":
        "biolink:condition_associated_with_gene",
    "Candidate gene tested in":
        "biolink:related_to",
    "Part of a fusion gene in":
        "biolink:condition_associated_with_gene",
    "Biomarker tested in":
        "biolink:has_biomarker",
}

koza_app = get_koza_app("orphanet_gene")

while (row := koza_app.get_row()) is not None:
    try:

        # Disease
        disease_id = "Orphanet:" + row["OrphaCode"]
        disease = Disease(id=disease_id,
                          name=row["Name"]["#text"],
                          category="biolink:Disease")

        koza_app.write(disease)

        # Gene
        # See if there's any overlap between the preferred sources
        # and the available sources first.
        all_assoc_genes = row["DisorderGeneAssociationList"]["DisorderGeneAssociation"]
        all_assoc_genes = (
            [all_assoc_genes] if isinstance(all_assoc_genes, dict) else all_assoc_genes
        )
        for gene in all_assoc_genes:
            is_preferred_gene = False

            all_ex_refs = gene["Gene"]["ExternalReferenceList"]["ExternalReference"]
            all_ex_refs = [all_ex_refs] if isinstance(all_ex_refs, dict) else all_ex_refs
            for ref in all_ex_refs:
                if ref["Source"] in PREFERRED_GENE_SOURCES:
                    source = ref["Source"]
                    ref = ref["Reference"]
                    is_preferred_gene = True
                    break

            if is_preferred_gene:
                gene_id = "UniProtKB:" + ref
                gene_obj = Protein(id=gene_id, category="biolink:Protein")

                # Association
                orphanet_association_type = gene["DisorderGeneAssociationType"]["Name"]["#text"]
                if orphanet_association_type in RELATION_TYPE_MAP:
                    predicate = RELATION_TYPE_MAP[orphanet_association_type]
                else:
                    predicate = "biolink:related_to"
                association = Association(
                    id="uuid:" + str(uuid.uuid1()),
                    subject=disease.id,
                    predicate=predicate,
                    category="biolink:Association",
                    object=gene_obj.id,
                )

                koza_app.write(association, gene_obj)

    except (TypeError, ValueError) as e:
        row_id = row["@id"]
        count = row["DisorderGeneAssociationList"]["@count"]
        print(f"Invalid entry: {e}. See entry {row_id}, with {count} gene(s)")
