import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Protein,
    AnatomicalEntity,
    GeneToExpressionSiteAssociation,
    Predicate
)

from koza.cli_runner import koza_app #type: ignore

source_name="hpa-data"

row = koza_app.get_row(source_name)
go_lookup = koza_app.get_map('go_term_lookup_map')

CLEAN_SUBCELL_LOCS = {"actin filaments":"actin filament",
                        "cell junctions":"cell junction",
                        "cytokinetic bridge":"intercellular bridge",
                        "cytoplasmic bodies":"cytoplasm",
                        "endosomes":"endosome",
                        "focal adhesion sites":"focal adhesion", #For replacing some names w/o GO terms
                        "intermediate filaments":"intermediate filament",
                        "lipid droplets":"lipid droplet",
                        "lysosomes":"lysosome",
                        "microtubule ends":"microtubule",
                        "microtubules":"microtubule",
                        "midbody ring":"flemming body",
                        "mitochondria":"mitochondrion",
                        "mitotic chromosome":"chromosome",
                        "nuclear bodies":"nuclear body",
                        "nuclear speckles":"nuclear speck",
                        "nucleoli fibrillar center":"fibrillar center",
                        "nucleoli":"nucleolus",
                        "nucleoli rim":"nucleolus",
                        "peroxisomes":"peroxisome",
                        "rods & rings":"cytosol",
                        "vesicles":"vesicle"} 

# Entities
protein_list = [] # Some entries have multiple protein IDs
xref_list = []
subcell_locations = [] # Some entries have multiple subcell locations, or none

xref_types = {"ENSEMBL:":'Ensembl'}
for xref_type in xref_types:
    value = row[xref_types[xref_type]]
    value = value.replace("/","_") #Gotta handle illegal slashes
    if str(value) == 'None':
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
        anatomy = AnatomicalEntity(id=go_lookup[location]['id'], # GO term lookup
                            description=location,
                            source="Human Protein Atlas")
        subcell_locations.append(anatomy)
    have_location = True

for entry in row["Uniprot"].split(", "):
    if entry != "":
        protein = Protein(id='UniProtKB:' + entry,
                    source="Human Protein Atlas",
                    xref=xref_list)
        protein_list.append(protein)

# Association
for entry in protein_list:
    if have_location:
        association = GeneToExpressionSiteAssociation( #This works for Gene OR GeneProduct
            id="uuid:" + str(uuid.uuid1()),
            subject=protein.id,
            predicate=Predicate.expressed_in,
            object=anatomy.id,
            relation="RO:0002206", #"expressed in",
            source = "Human Protein Atlas"
        )
        for location in subcell_locations:
            koza_app.write(protein, association, anatomy)
    else:
        koza_app.write(protein)
