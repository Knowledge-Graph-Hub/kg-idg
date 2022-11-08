import uuid

from biolink.model import AnatomicalEntity, Association, Protein  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "hpa-data"
full_source_name = "Human Protein Atlas"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()
go_lookup = koza_app.get_map("go_term_lookup_map")

CLEAN_SUBCELL_LOCS = {
    "actin filaments": "actin filament",
    "cell junctions": "cell junction",
    "cytokinetic bridge": "intercellular bridge",
    "cytoplasmic bodies": "cytoplasm",
    "endosomes": "endosome",
    "focal adhesion sites": "focal adhesion",  # For replacing some names w/o GO terms
    "intermediate filaments": "intermediate filament",
    "lipid droplets": "lipid droplet",
    "lysosomes": "lysosome",
    "microtubule ends": "microtubule",
    "microtubules": "microtubule",
    "midbody ring": "flemming body",
    "mitochondria": "mitochondrion",
    "mitotic chromosome": "chromosome",
    "nuclear bodies": "nuclear body",
    "nuclear speckles": "nuclear speck",
    "nucleoli fibrillar center": "fibrillar center",
    "nucleoli": "nucleolus",
    "nucleoli rim": "nucleolus",
    "peroxisomes": "peroxisome",
    "rods & rings": "cytosol",
    "vesicles": "vesicle",
}

# Entities
protein_list = []  # Some entries have multiple protein IDs
xref_list = []
subcell_locations = []  # Some entries have multiple subcell locations, or none

xref_types = {"ENSEMBL:": "Ensembl"}
for xref_type in xref_types:
    value = row[xref_types[xref_type]]
    value = value.replace("/", "_")  # Gotta handle illegal slashes
    if str(value) == "None":
        continue
    else:
        xref_list.append(xref_type + str(value))

have_location = False
if str(row["Subcellular location"]) != "":
    locations = str(row["Subcellular location"]).split(",")
    for location in locations:
        location = location.lower()
        if location in CLEAN_SUBCELL_LOCS:
            location = CLEAN_SUBCELL_LOCS[location]
        anatomy = AnatomicalEntity(
            id=go_lookup[location]["id"],  # GO term lookup
            description=location,
            provided_by=full_source_name,
            category="biolink:AnatomicalEntity",
        )
        subcell_locations.append(anatomy)
    have_location = True

for entry in row["Uniprot"].split(", "):
    if entry != "":
        protein = Protein(
            id="UniProtKB:" + entry,
            provided_by=full_source_name,
            xref=xref_list,
            category="biolink:Protein",
        )
        protein_list.append(protein)

# Association
for _ in protein_list:
    if have_location:
        association = Association(  # This works for Gene OR GeneProduct
            id="uuid:" + str(uuid.uuid1()),
            subject=protein.id,
            predicate="biolink:expressed_in",
            object=anatomy.id,
            aggregator_knowledge_source=full_source_name,
        )
        for _ in subcell_locations:
            koza_app.write(protein, association, anatomy)
    else:
        koza_app.write(protein)
