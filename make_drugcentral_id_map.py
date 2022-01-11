#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Produce a SSSOM CURIE map from various sources to DrugCentral IDs.
This requires the DrugCentral transform to be completed first.
"""

import click
import os

@click.command()
@click.option("--output_file",
               required=True,
               nargs=1,
               help="""Name of the map file to be created in the maps directory.""")
def run(output_file):

    dc_identifier_path = "data/transformed/drug_central/drugcentral-identifier_edges.tsv"
    out_path = os.path.join("maps",output_file)

    header = """#creator_id: "https://orcid.org/0000-0001-5705-7831"
#curie_map:
#  KEGG_DRUG: "http://www.kegg.jp/entry/"
#  UNII: "http://fdasis.nlm.nih.gov/srs/srsdirect.jsp?regno="
#  VUID: "https://academic.oup.com/jamia/article/17/4/432/866953"
#  NUI: "https://bioportal.bioontology.org/ontologies/NDFRT/"
#  CAS: "http://commonchemistry.org/ChemicalDetail.aspx?ref="
#  VANDF: "https://www.nlm.nih.gov/research/umls/sourcereleasedocs/current/VANDF"
#  UMLS: "http://linkedlifedata.com/resource/umls/id/"
#  CHEBI: "http://purl.obolibrary.org/obo/CHEBI_"
#  PDB: "http://www.rcsb.org/pdb/explore/explore.do?structureId="
#  CHEMBL_COMPOUND: "https://www.ebi.ac.uk/chembl/compound/inspect/"
#  PUBCHEM_COMPOUND: "http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi?cid="
#  DRUGBANK: "http://www.drugbank.ca/drugs/"
#  MESH: "http://id.nlm.nih.gov/mesh/"
#  INN: "https://mednet-communities.net/inn/db/ViewINN.aspx?i="
#  IUPHAR_LIGAND: "http://www.guidetopharmacology.org/GRAC/LigandDisplayForward?ligandId="
#  RXNORM: "https://mor.nlm.nih.gov/RxNav/search?searchBy=RXCUI&searchTerm="
#  MMSL: "https://www.nlm.nih.gov/research/umls/rxnorm/sourcereleasedocs/mmsl.html"
#  NDDF: "https://bioportal.bioontology.org/ontologies/NDDF/"
#  SNOMEDCT: "http://www.snomedbrowser.com/Codes/Details/"
#  DrugCentral: "https://drugcentral.org/drugcard/"
#  skos: "http://www.w3.org/2004/02/skos/core"
#license: "https://creativecommons.org/publicdomain/zero/1.0/"
#mapping_provider: "https://unmtid-shinyapps.net/download/drugcentral.dump.010_05_2021.sql.gz"
subject_id	predicate_id	object_id	match_type	subject_label	object_label	comment\n"""

    with open(out_path, "w") as map_file:
        map_file.write(header)
        with open(dc_identifier_path) as in_file:
            in_file.readline()
            for line in in_file:
                splitline = (line.rstrip()).split("\t")
                newline = f"{splitline[1]}\t{splitline[5]}\t{splitline[3]}\tLexical\t\t\n"
                map_file.write(newline)

    print(f"Complete. See {out_path}")

if __name__ == '__main__':
  run()