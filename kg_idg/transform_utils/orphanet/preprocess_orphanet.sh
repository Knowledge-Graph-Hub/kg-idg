#!/bin/sh

iconv -f ISO-8859-1 -t utf-8 data/raw/orphanet_gene.xml | xq '.JDBOR.DisorderList.Disorder' > data/raw/orphanet_gene.json
iconv -f ISO-8859-1 -t utf-8 data/raw/orphanet_pheno.xml | xq '.JDBOR.HPODisorderSetStatusList.HPODisorderSetStatus' > data/raw/orphanet_pheno.json