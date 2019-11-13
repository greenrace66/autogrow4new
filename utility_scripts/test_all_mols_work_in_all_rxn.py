import glob
import os
import sys
import rdkit
import rdkit.Chem as Chem
import rdkit.Chem.AllChem as AllChem
import support_scripts.Multiprocess as mp
import pickle
import copy

num_processors = -1

#Robust Reactions
Robust_reactions ={
    "1_Pictet_Spengler": {
        "reaction_name": "1_Pictet_Spengler", 
        "example_rxn_product": "CC1NCCc2ccccc21", 
        "example_rxn_reactants": ["c1cc(CCN)ccc1", "CC(=O)"],
        "functional_groups": ["beta_arylethylamine", "aldehyde"],
        "group_smarts": ["[c&H1]1:c(-[C&H2]-[C&H2]-[N&H2]):c:c:c:c:1", "[#6]-[C&H1&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[cH1:1]1:[c:2](-[CH2:7]-[CH2:8]-[NH2:9]):[c:3]:[c:4]:[c:5]:[c:6]:1.[#6:11]-[CH1;R0:10]=[OD1]>>[c:1]12:[c:2](-[CH2:7]-[CH2:8]-[NH1:9]-[C:10]-2(-[#6:11])):[c:3]:[c:4]:[c:5]:[c:6]:1", 
        "RXN_NUM": 1
        },
    "2_benzimidazole_derivatives_carboxylic_acid_ester": {
        "reaction_name": "2_benzimidazole_derivatives_carboxylic_acid_ester", 
        "example_rxn_product": "Cc1n~c2ccccc2n1C", 
        "example_rxn_reactants": ["c1c(NC)c(N)ccc1", "OC(=O)C"],
        "functional_groups": ["ortho_phenylenediamine", "carboxylic_acid_or_ester"],
        "group_smarts": ["[c&r6](-[N&H1&$(N-[#6])]):[c&r6]-[N&H2]", "[#6]-[C&R0](=[O&D1])-[#8;H1,$(O-[C&H3])]"],
        "num_reactants": 2, 
        "reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[#8;H1,$(O-[CH3])]>>[c:3]2:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]@2", 
        "RXN_NUM": 2
        },
    "3_benzimidazole_derivatives_aldehyde": {
        "reaction_name": "3_benzimidazole_derivatives_aldehyde", 
        "example_rxn_product": "Cc1n~c2ccccc2n1C", 
        "example_rxn_reactants": ["c1c(NC)c(N)ccc1", "CC(=O)"],
        "functional_groups": ["ortho_phenylenediamine", "aldehyde"],
        "group_smarts": ["[c&r6](-[N&H1&$(N-[#6])]):[c&r6]-[N&H2]", "[#6]-[C&H1&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]@2", 
        "RXN_NUM": 3
        },
    "4_benzothiazole": {
        "reaction_name": "4_benzothiazole", 
        "example_rxn_product": "Cc1n~c2ccccc2s1", 
        "example_rxn_reactants": ["c1c(S)c(N)ccc1", "CC(=O)"],
        "functional_groups": ["ortho_aminothiophenol", "aldehyde"],
        "group_smarts": ["[c&r6](-[S&H1]):[c&r6]-[N&H2]", "[#6]-[C&H1&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[c;r6:1](-[SH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[s:2]:[c:5](-[#6:6]):[n:4]@2", 
        "RXN_NUM": 4
        },
    "5_benzoxazole_arom_aldehyde": {
        "reaction_name": "5_benzoxazole_arom_aldehyde", 
        "example_rxn_product": "c1ccc(-c2n~c3ccccc3o2)cc1", 
        "example_rxn_reactants": ["c1cc(O)c(N)cc1", "c1ccccc1C(=O)"],
        "functional_groups": ["ortho_aminophenol", "aryl_aldehyde"],
        "group_smarts": ["c(-[O&H1&$(Oc1ccccc1)]):[c&r6]-[N&H2]", "c-[C&H1&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[c:1](-[OH1;$(Oc1ccccc1):2]):[c;r6:3](-[NH2:4]).[c:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[o:2]:[c:5](-[c:6]):[n:4]@2", 
        "RXN_NUM": 5
        },
    "6_benzoxazole_carboxylic_acid": {
        "reaction_name": "6_benzoxazole_carboxylic_acid", 
        "example_rxn_product": "Cc1n~c2ccccc2o1", 
        "example_rxn_reactants": ["c1cc(O)c(N)cc1", "CC(=O)O"],
        "functional_groups": ["ortho_1amine_2alcohol_arylcyclic", "carboxylic_acid"],
        "group_smarts": ["[c&r6](-[O&H1]):[c&r6]-[N&H2]", "[#6]-[C&R0](=[O&D1])-[O&H1]"],
        "num_reactants": 2, 
        "reaction_string": "[c;r6:1](-[OH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[OH1]>>[c:3]2:[c:1]:[o:2]:[c:5](-[#6:6]):[n:4]@2", 
        "RXN_NUM": 6
        },
    "7_thiazole": {
        "reaction_name": "7_thiazole", 
        "example_rxn_product": "Cc1nc(C)c(C)s1", 
        "example_rxn_reactants": ["CC(=O)C(I)C", "NC(=S)C"],
        "functional_groups": ["haloketone", "thioamide"],
        "group_smarts": ["[#6]-[C&R0](=[O&D1])-[C&H1&R0](-[#6])-[*;#17,#35,#53]", "[$([N&H2]-[C]=[S&D1,O&D1]),$([N&H1]=[C]-[SH1,OH1])]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:6]-[C;R0:1](=[OD1])-[CH1;R0:5](-[#6:7])-[*;#17,#35,#53].[$([N&H2:2]-[C:3]([*:6])=[S&D1,O&D1:4]),$([N&H1:2]=[C:3]([*:6])-[SH1,OH1:4])]>>[c:1]2(-[#6:6]):[n:2]:[c:3]([*:6]):[s:4][c:5]([#6:7]):2", 
        "RXN_NUM": 7
        },
    "8_Niementowski_quinazoline": {
        "reaction_name": "8_Niementowski_quinazoline", 
        "example_rxn_product": "O=C1NC=Nc2ccccc21", 
        "example_rxn_reactants": ["c1c(C(=O)O)c(N)ccc1", "C(=O)N"],
        "functional_groups": ["anthranilic_acid", "amide"],
        "group_smarts": ["c(-[C&$(C-c1ccccc1)](=[O&D1])-[O&H1]):c-[N&H2]", "[N&!H0&!$(N-N)&!$(N-C=N)&!$(N(-C=O)-C=O)]-[C;H1,$(C-[#6])]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[OH1]):[c:4](-[NH2:5]).[N;!H0;!$(N-N);!$(N-C=N);!$(N(-C=O)-C=O):6]-[C;H1,$(C-[#6]):7]=[OD1]>>[c:4]2:[c:1]-[C:2](=[O:3])-[N:6]-[C:7]=[N:5]-2", 
        "RXN_NUM": 8
        },
    "9_tetrazole_terminal": {
        "reaction_name": "9_tetrazole_terminal", 
        "example_rxn_product": "CC1=NNN=N1", 
        "example_rxn_reactants": ["CC#N"],
        "functional_groups": ["nitrile"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]"],
        "num_reactants": 1, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2]>>[C:1]1=[N:2]-N-N=N-1", 
        "RXN_NUM": 9
        },
    "10_tetrazole_connect_regioisomere_1": {
        "reaction_name": "10_tetrazole_connect_regioisomere_1", 
        "example_rxn_product": "CC1=NN(C)N=N1", 
        "example_rxn_reactants": ["CC#N", "CBr"],
        "functional_groups": ["nitrile", "alkyl_halogen"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&A&!$(C=O)]-[*;#17,#35,#53]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N(-[C:3])-N=N-1", 
        "RXN_NUM": 10
        },
    "11_tetrazole_connect_regioisomere_2": {
        "reaction_name": "11_tetrazole_connect_regioisomere_2", 
        "example_rxn_product": "CC1=NN=NN1C", 
        "example_rxn_reactants": ["CC#N", "CBr"],
        "functional_groups": ["nitrile", "alkyl_halogen"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&A&!$(C=O)]-[*;#17,#35,#53]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N=N-N-1(-[C:3])", 
        "RXN_NUM": 11
        },
    "12_Huisgen_Cu_catalyzed_1_4_subst": {
        "reaction_name": "12_Huisgen_Cu_catalyzed_1_4_subst", 
        "example_rxn_product": "CCN1C=C(C)N=N1", 
        "example_rxn_reactants": ["CC#C", "CCBr"],
        "functional_groups": ["aliphatic_alkyne", "alkyl_halogen_or_alcohol"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[C&H1]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[CH1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N(-[C:3])-N=N-1", 
        "RXN_NUM": 12
        },
    "13_Huisgen_Ru_catalyzed_1_5_subst": {
        "reaction_name": "13_Huisgen_Ru_catalyzed_1_5_subst", 
        "example_rxn_product": "CCN1N=NC=C1C", 
        "example_rxn_reactants": ["CC#C", "CCBr"],
        "functional_groups": ["aliphatic_alkyne", "alkyl_halogen_or_alcohol"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[C&H1]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[CH1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1", 
        "RXN_NUM": 13
        },
    "14_Huisgen_disubst_alkyne": {
        "reaction_name": "14_Huisgen_disubst_alkyne", 
        "example_rxn_product": "CCN1N=NC(C)=C1C", 
        "example_rxn_reactants": ["CC#CC", "CCBr"],
        "functional_groups": ["aliphatic_alkyne_w_aro_alkyl_group", "alkyl_halogen_or_alcohol"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[C&H0&$(C-[#6])]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[CH0;$(C-[#6]):2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1", 
        "RXN_NUM": 14
        },
    "15_1_2_4_triazole_acetohydrazide": {
        "reaction_name": "15_1_2_4_triazole_acetohydrazide", 
        "example_rxn_product": "CC1=NNC(C)=N1", 
        "example_rxn_reactants": ["CC#N", "NNC(=O)C"],
        "functional_groups": ["nitrile", "acetohydrazide"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[N&H2]-[N&H1]-[C&H0&$(C-[#6])&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[NH2:3]-[NH1:4]-[CH0;$(C-[#6]);R0:5]=[OD1]>>[N:2]1-[C:1]=[N:3]-[N:4]-[C:5]=1", 
        "RXN_NUM": 15
        },
    "16_1_2_4_triazole_carboxylic_acid_ester": {
        "reaction_name": "16_1_2_4_triazole_carboxylic_acid_ester", 
        "example_rxn_product": "CC1=NNC(C)=N1", 
        "example_rxn_reactants": ["CC#N", "OC(=O)C"],
        "functional_groups": ["nitrile", "carboxylic_acid_or_extended_esters"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&H0&$(C-[#6])&R0](=[O&D1])-[#8;H1,$(O-[C&H3]),$(O-[C&H2]-[C&H3])]"],
        "num_reactants": 2, 
        "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[CH0;$(C-[#6]);R0:5](=[OD1])-[#8;H1,$(O-[CH3]),$(O-[CH2]-[CH3])]>>[N:2]1-[C:1]=N-N-[C:5]=1", 
        "RXN_NUM": 16
        },
    "17_3_nitrile_pyridine": {
        "reaction_name": "17_3_nitrile_pyridine", 
        "example_rxn_product": "Cc1cc(C)c(C#N)c(O)n1", 
        "example_rxn_reactants": ["CC(=O)CC(=O)C"],
        "functional_groups": ["beta_dicarbonyl"],
        "group_smarts": ["[#6&!$([#6](-C=O)-C=O)]-[C&H0](=[O&D1])-[C;H1&!$(C-[*&!#6])&!$(C-C(=O)O),H2]-[C&H0&R0](=[O&D1])-[#6&!$([#6](-C=O)-C=O)]"],
        "num_reactants": 1, 
        "reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5]>>[c:1]1(-[#6:4]):[c:2]:[c:3](-[#6:5]):n:c(-O):c(-C#N):1", 
        "RXN_NUM": 17
        },
    "18_spiro_chromanone": {
        "reaction_name": "18_spiro_chromanone", 
        "example_rxn_product": "O=C1CC2(CCNCC2)Oc2ccccc21", 
        "example_rxn_reactants": ["c1cc(C(=O)C)c(O)cc1", "C1(=O)CCNCC1"],
        "functional_groups": ["2_acetylphenol", "cyclohexanone"],
        "group_smarts": ["c(-[C&$(C-c1ccccc1)](=[O&D1])-[C&H3]):c-[O&H1]", "[C&$(C1-[C&H2]-[C&H2]-[N,C]-[C&H2]-[C&H2]-1)]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[CH3:4]):[c:5](-[OH1:6]).[C;$(C1-[CH2]-[CH2]-[N,C]-[CH2]-[CH2]-1):7](=[OD1])>>[O:6]1-[c:5]:[c:1]-[C:2](=[OD1:3])-[C:4]-[C:7]-1", 
        "RXN_NUM": 18
        },
    "19_pyrazole": {
        "reaction_name": "19_pyrazole", 
        "example_rxn_product": "CC1=CC(C)=NN1C", 
        "example_rxn_reactants": ["CC(=O)CC(=O)C", "NNC"],
        "functional_groups": ["beta_dicarbonyl", "hydrazine"],
        "group_smarts": ["[#6&!$([#6](-C=O)-C=O)]-[C&H0](=[O&D1])-[C;H1&!$(C-[*&!#6])&!$(C-C(=O)O),H2]-[C&H0&R0](=[O&D1])-[#6&!$([#6](-C=O)-C=O)]", "[N&H2]-[N&!H0;$(N-[#6]),H2]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5].[NH2:6]-[N;!H0;$(N-[#6]),H2:7]>>[C:1]1(-[#6:4])-[C:2]=[C:3](-[#6:5])-[N:7]-[N:6]=1", 
        "RXN_NUM": 19
        },
    "20_phthalazinone": {
        "reaction_name": "20_phthalazinone", 
        "example_rxn_product": "CC1=NN(C)C(=O)c2ccccc21", 
        "example_rxn_reactants": ["c1cc(C(=O)O)c(C(=O)C)cc1", "NNC"],
        "functional_groups": ["phthalazinone_precursor", "restricted_hydrazine"],
        "group_smarts": ["[c&r6](-[C&$(C=O)]-[O&H1]):[c&r6]-[C;H1,$(C-C)]=[O&D1]", "[N&H2]-[N&H1&$(N-[#6])&!$(NC=[O,S,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[c;r6:1](-[C;$(C=O):6]-[OH1]):[c;r6:2]-[C;H1,$(C-C):3]=[OD1].[NH2:4]-[NH1;$(N-[#6]);!$(NC=[O,S,N]):5]>>[c:1]1:[c:2]-[C:3]=[N:4]-[N:5]-[C:6]-1", 
        "RXN_NUM": 20
        },
    "21_Paal_Knorr_pyrrole": {
        "reaction_name": "21_Paal_Knorr_pyrrole", 
        "example_rxn_product": "CC1=CC=C(C)N1C", 
        "example_rxn_reactants": ["CC(=O)CCC(=O)C", "NC"],
        "functional_groups": ["1_4_dione", "primary_amine"],
        "group_smarts": ["[#6]-[C&R0](=[O&D1])-[C;H1,H2]-[C;H1,H2]-C(=[O&D1])-[#6]", "[N&H2&$(N-[C,N])&!$(NC=[O,S,N])&!$(N(-,:[#6])[#6])&!$(N~N~N)]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:5]-[C;R0:1](=[OD1])-[C;H1,H2:2]-[C;H1,H2:3]-[C:4](=[OD1])-[#6:6].[NH2;$(N-[C,N]);!$(NC=[O,S,N]);!$(N([#6])[#6]);!$(N~N~N):7]>>[C:1]1(-[#6:5])=[C:2]-[C:3]=[C:4](-[#6:6])-[N:7]-1", 
        "RXN_NUM": 21
        },
    "22_triaryl_imidazole": {
        "reaction_name": "22_triaryl_imidazole", 
        "example_rxn_product": "c1ccc(C2=NC(c3ccccc3)=C(c3ccccc3)N2)cc1", 
        "example_rxn_reactants": ["c1ccccc1C(=O)C(=O)c1ccccc1", "c1ccccc1C(=O)"],
        "functional_groups": ["benzil_or_benzoin", "aryl_aldehyde"],
        "group_smarts": ["[C&$(C-c1ccccc1)](=[O&D1])-[C&D3&$(C-c1ccccc1)]~[O;D1,H1]", "c-[C&H1&R0]=[O&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[C;$(C-c1ccccc1):1](=[OD1])-[C;D3;$(C-c1ccccc1):2]~[O;D1,H1].[CH1;$(C-c):3]=[OD1]>>[C:1]1-N=[C:3]-[NH1]-[C:2]=1", 
        "RXN_NUM": 22
        },
    "23_Fischer_indole": {
        "reaction_name": "23_Fischer_indole", 
        "example_rxn_product": "CC1=C(C)c2ccccc2N1", 
        "example_rxn_reactants": ["c1ccccc1NN", "CCC(=O)C"],
        "functional_groups": ["phenylhydrazine", "ketone"],
        "group_smarts": ["[N&H1&$(N-c1ccccc1)](-[N&H2])-c:[c&H1]", "[C&$(C(-,:[#6])[#6])](=[O&D1])-[C&H2&$(C(-,:[#6])[#6])&!$(C(-,:C=O)C=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[NH1;$(N-c1ccccc1):1](-[NH2])-[c:5]:[cH1:4].[C;$(C([#6])[#6]):2](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O):3]>>[C:5]1-[N:1]-[C:2]=[C:3]-[C:4]:1", 
        "RXN_NUM": 23
        },
    "24_Friedlaender_chinoline": {
        "reaction_name": "24_Friedlaender_chinoline", 
        "example_rxn_product": "CC1=Cc2ccccc2-nc1C", 
        "example_rxn_reactants": ["c1cccc(C=O)c1N", "CCC(=O)C"],
        "functional_groups": ["ortho_aminobenzaldehyde", "ketone"],
        "group_smarts": ["[N&H2&$(N-c1ccccc1)]-c:c-[C&H1]=[O&D1]", "[C&$(C(-,:[#6])[#6])](=[O&D1])-[C&H2&$(C(-,:[#6])[#6])&!$(C(-,:C=O)C=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[NH2;$(N-c1ccccc1):1]-[c:2]:[c:3]-[CH1:4]=[OD1].[C;$(C([#6])[#6]):6](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O):5]>>[N:1]1-[c:2]:[c:3]-[C:4]=[C:5]-[C:6]:1", 
        "RXN_NUM": 24
        },
    "25_benzofuran": {
        "reaction_name": "25_benzofuran", 
        "example_rxn_product": "CC1=Cc2ccccc2O1", 
        "example_rxn_reactants": ["c1cc(I)c(O)cc1", "CC#C"],
        "functional_groups": ["ortho_halo_phenol", "alkyne"],
        "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[O&H1]", "[C&H1]#[C&$(C-[#6])]"],
        "num_reactants": 2, 
        "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[OH1:3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[O:3]-[C:4]=[C:5]-1", 
        "RXN_NUM": 25
        },
    "26_benzothiophene": {
        "reaction_name": "26_benzothiophene", 
        "example_rxn_product": "CC1=Cc2ccccc2S1", 
        "example_rxn_reactants": ["c1cc(I)c(SC)cc1", "CC#C"],
        "functional_groups": ["aminobenzenethiol", "alkyne"],
        "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[S&D2]-[C&H3]", "[C&H1]#[C&$(C-[#6])]"],
        "num_reactants": 2, 
        "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[SD2:3]-[CH3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[S:3]-[C:4]=[C:5]-1", 
        "RXN_NUM": 26
        },
    "27_indole": {
        "reaction_name": "27_indole", 
        "example_rxn_product": "CC1=Cc2ccccc2N1", 
        "example_rxn_reactants": ["c1cc(I)c(N)cc1", "CC#C"],
        "functional_groups": ["ortho_halo_thioanizole", "alkyne"],
        "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[N&H2]", "[C&H1]#[C&$(C-[#6])]"],
        "num_reactants": 2, 
        "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[NH2:3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[N:3]-[C:4]=[C:5]-1", 
        "RXN_NUM": 27
        },
    "28_oxadiazole": {
        "reaction_name": "28_oxadiazole", 
        "example_rxn_product": "Cc1noc(C)n1", 
        "example_rxn_reactants": ["CC#N", "CC(=O)O"],
        "functional_groups": ["nitrile", "carboxylic_acid"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[#6]-[C&R0](=[O&D1])-[O&H1]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:6][C:5]#[#7;D1:4].[#6:1][C:2](=[OD1:3])[OH1]>>[#6:6][c:5]1[n:4][o:3][c:2]([#6:1])n1", 
        "RXN_NUM": 28
        },
    "29_Williamson_ether": {
        "reaction_name": "29_Williamson_ether", 
        "example_rxn_product": "CCOCC", 
        "example_rxn_reactants": ["CCO", "CCBr"],
        "functional_groups": ["alcohol", "alkyl_halide"],
        "group_smarts": ["[#6&$([#6]~[#6])&!$([#6]=O)][#8&H1]", "[Cl,Br,I][#6&H2&$([#6]~[#6])]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;$([#6]~[#6]);!$([#6]=O):2][#8;H1:3].[Cl,Br,I][#6;H2;$([#6]~[#6]):4]>>[CH2:4][O:3][#6:2]", 
        "RXN_NUM": 29
        },
    "30_reductive_amination": {
        "reaction_name": "30_reductive_amination", 
        "example_rxn_product": "CCNC", 
        "example_rxn_reactants": ["CC(=O)", "NC"],
        "functional_groups": ["aldehyde_or_ketone", "primary_or_secondary_amine"],
        "group_smarts": ["[#6]-[C;H1,$([C&H0](-[#6])[#6])]=[O&D1]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:4]-[C;H1,$([CH0](-[#6])[#6]):1]=[OD1].[N;H2,$([NH1;D2](C)C);!$(N-[#6]=[*]):3]-[C:5]>>[#6:4][C:1]-[N:3]-[C:5]", 
        "RXN_NUM": 30
        },
    "31_Suzuki": {
        "reaction_name": "31_Suzuki", 
        "example_rxn_product": "c1ccc(-c2ccccc2)cc1", 
        "example_rxn_reactants": ["c1ccccc1B(O)O", "c1ccccc1Br"],
        "functional_groups": ["boronic_acid", "aryl_halide"],
        "group_smarts": ["[#6&H0&D3&$([#6](~[#6])~[#6])]B(-,:O)O", "[#6&H0&D3&$([#6](~[#6])~[#6])][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;H0;D3;$([#6](~[#6])~[#6]):1]B(O)O.[#6;H0;D3;$([#6](~[#6])~[#6]):2][Cl,Br,I]>>[#6:2][#6:1]", 
        "RXN_NUM": 31
        },
    "32_piperidine_indole": {
        "reaction_name": "32_piperidine_indole", 
        "example_rxn_product": "C1=C(c2c[nH]c3ccccc23)CCNC1", 
        "example_rxn_reactants": ["c1cccc2c1C=CN2", "C1CC(=O)CCN1"],
        "functional_groups": ["indole", "4_piperidone"],
        "group_smarts": ["[c&H1]1:c:c:[c&H1]:c2:[n&H1]:c:[c&H1]:c:1:2", "O=C1[#6&H2][#6&H2][N][#6&H2][#6&H2]1"],
        "num_reactants": 2, 
        "reaction_string": "[c;H1:3]1:[c:4]:[c:5]:[c;H1:6]:[c:7]2:[nH:8]:[c:9]:[c;H1:1]:[c:2]:1:2.O=[C:10]1[#6;H2:11][#6;H2:12][N][#6;H2][#6;H2]1>>[#6;H2:12]3[#6;H1:11]=[C:10]([c:1]1:[c:9]:[n:8]:[c:7]2:[c:6]:[c:5]:[c:4]:[c:3]:[c:2]:1:2)[#6;H2:15][#6;H2:14][N:13]3", 
        "RXN_NUM": 32
        },
    "33_Negishi": {
        "reaction_name": "33_Negishi", 
        "example_rxn_product": "CCCC", 
        "example_rxn_reactants": ["CCBr", "CCBr"],
        "functional_groups": ["halide_type_3", "halide_type_3"],
        "group_smarts": ["[#6&$([#6]~[#6])&!$([#6]~[S,N,O,P])][Cl,Br,I]", "[#6&$([#6]~[#6])&!$([#6]~[S,N,O,P])][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):1][Cl,Br,I].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):2]>>[#6:2][#6:1]", 
        "RXN_NUM": 33
        },
    "34_Mitsunobu_imide": {
        "reaction_name": "34_Mitsunobu_imide", 
        "example_rxn_product": "CC(=O)N(C(C)=O)C(C)C", 
        "example_rxn_reactants": ["CC(O)C", "CC(=O)NC(=O)C"],
        "functional_groups": ["primary_or_secondary_alcohol", "imide"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[N&H1&$(N(-,:C=O)C=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[NH1;$(N(C=O)C=O):2]>>[C:1][N:2]", 
        "RXN_NUM": 34
        },
    "35_Mitsunobu_phenole": {
        "reaction_name": "35_Mitsunobu_phenole", 
        "example_rxn_product": "CC(C)Oc1ccccc1", 
        "example_rxn_reactants": ["CC(O)C", "c1ccccc1O"],
        "functional_groups": ["primary_or_secondary_alcohol", "phenole"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[O&H1&$(Oc1ccccc1)]"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[OH1;$(Oc1ccccc1):2]>>[C:1][O:2]", 
        "RXN_NUM": 35
        },
    "36_Mitsunobu_sulfonamide": {
        "reaction_name": "36_Mitsunobu_sulfonamide", 
        "example_rxn_product": "CC(C)N(C)S(C)(=O)=O", 
        "example_rxn_reactants": ["CC(O)C", "CNS(=O)(=O)C"],
        "functional_groups": ["primary_or_secondary_alcohol", "sulfonamide"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[N&H1&$(N(-,:[#6])S(=O)=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[NH1;$(N([#6])S(=O)=O):2]>>[C:1][N:2]", 
        "RXN_NUM": 36
        },
    "37_Mitsunobu_tetrazole_1": {
        "reaction_name": "37_Mitsunobu_tetrazole_1", 
        "example_rxn_product": "CC(C)n1cnnn1", 
        "example_rxn_reactants": ["CC(O)C", "N1=NNC=N1"],
        "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_1"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7&H1]1~[#7]~[#7]~[#7]~[#6]~1"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[C:1][#7:2]1:[#7:3]:[#7:4]:[#7:5]:[#6:6]:1", 
        "RXN_NUM": 37
        },
    "38_Mitsunobu_tetrazole_2": {
        "reaction_name": "38_Mitsunobu_tetrazole_2", 
        "example_rxn_product": "CC(C)n1ncnn1", 
        "example_rxn_reactants": ["CC(O)C", "N1=NNC=N1"],
        "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_1"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7&H1]1~[#7]~[#7]~[#7]~[#6]~1"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[#7H0:2]1:[#7:3]:[#7H0:4]([C:1]):[#7:5]:[#6:6]:1", 
        "RXN_NUM": 38
        },
    "39_Mitsunobu_tetrazole_3": {
        "reaction_name": "39_Mitsunobu_tetrazole_3", 
        "example_rxn_product": "CC(C)n1cnnn1", 
        "example_rxn_reactants": ["CC(O)C", "N1N=NC=N1"],
        "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_2"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7]1~[#7]~[#7&H1]~[#7]~[#6]~1"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[C:1][#7H0:2]1:[#7:3]:[#7H0:4]:[#7:5]:[#6:6]:1", 
        "RXN_NUM": 39
        },
    "40_Mitsunobu_tetrazole_4": {
        "reaction_name": "40_Mitsunobu_tetrazole_4", 
        "example_rxn_product": "CC(C)n1ncnn1", 
        "example_rxn_reactants": ["CC(O)C", "N1N=NC=N1"],
        "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_2"],
        "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7]1~[#7]~[#7&H1]~[#7]~[#6]~1"],
        "num_reactants": 2, 
        "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[#7:2]1:[#7:3]:[#7:4]([C:1]):[#7:5]:[#6:6]:1", 
        "RXN_NUM": 40
        },
    "41_Heck_terminal_vinyl": {
        "reaction_name": "41_Heck_terminal_vinyl", 
        "example_rxn_product": "C(=C/c1ccccc1)\\c1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1C=C", "c1ccccc1Br"],
        "functional_groups": ["alkene", "halide_type_2"],
        "group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6&H1]=[#6&H2]", "[#6;$([#6]=[#6]),$(c:c)][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6;H1:2]=[#6;H2:1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4]/[#6:1]=[#6:2]/[#6:3]", 
        "RXN_NUM": 41
        },
    "42_Heck_non_terminal_vinyl": {
        "reaction_name": "42_Heck_non_terminal_vinyl", 
        "example_rxn_product": "CC(=C(C)c1ccccc1)c1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1C(C)=CC", "c1ccccc1Br"],
        "functional_groups": ["terminal_alkene", "halide_type_2"],
        "group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6](-,:[#6])=[#6&H1&$([#6][#6])]", "[#6;$([#6]=[#6]),$(c:c)][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6:2]([#6:5])=[#6;H1;$([#6][#6]):1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4][#6;H0:1]=[#6:2]([#6:5])[#6:3]", 
        "RXN_NUM": 42
        },
    "43_Stille": {
        "reaction_name": "43_Stille", 
        "example_rxn_product": "c1ccc(-c2ccccc2)cc1", 
        "example_rxn_reactants": ["c1ccccc1Br", "c1ccccc1Br"],
        "functional_groups": ["aryl_or_vinyl_halide", "aryl_halide"],
        "group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[#6&H0&D3&$([#6](~[#6])~[#6])][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[Cl,Br,I][c:2]>>[c:2][#6:1]", 
        "RXN_NUM": 43
        },
    "44_Grignard_carbonyl": {
        "reaction_name": "44_Grignard_carbonyl", 
        "example_rxn_product": "CCC(C)=O", 
        "example_rxn_reactants": ["CC#N", "CCBr"],
        "functional_groups": ["nitrile", "halide_type_1"],
        "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[Cl,Br,I][#6&$([#6]~[#6])&!$([#6](-,:[Cl,Br,I])[Cl,Br,I])&!$([#6]=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:1][C:2]#[#7;D1].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):3]>>[#6:1][C:2](=O)[#6:3]", 
        "RXN_NUM": 44
        },
    "45_Grignard_alcohol": {
        "reaction_name": "45_Grignard_alcohol", 
        "example_rxn_product": "CCC(C)(C)O", 
        "example_rxn_reactants": ["CC(=O)C", "CCBr"],
        "functional_groups": ["aldehyde_or_ketone_restricted", "halide_type_1"],
        "group_smarts": ["[#6][C;H1,$(C(-,:[#6])[#6])]=[O&D1]", "[Cl,Br,I][#6&$([#6]~[#6])&!$([#6](-,:[Cl,Br,I])[Cl,Br,I])&!$([#6]=O)]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:1][C;H1,$([C]([#6])[#6]):2]=[OD1:3].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):4]>>[C:1][#6:2]([OH1:3])[#6:4]", 
        "RXN_NUM": 45
        },
    "46_Sonogashira": {
        "reaction_name": "46_Sonogashira", 
        "example_rxn_product": "CC#Cc1ccccc1", 
        "example_rxn_reactants": ["c1cc(Br)ccc1", "CC#C"],
        "functional_groups": ["aryl_or_vinyl_halide", "terminal_alkyne"],
        "group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[C&H1&$(C#CC)]"],
        "num_reactants": 2, 
        "reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[CH1;$(C#CC):2]>>[#6:1][C:2]", 
        "RXN_NUM": 46
        },
    "47_Schotten_Baumann_amide": {
        "reaction_name": "47_Schotten_Baumann_amide", 
        "example_rxn_product": "CCNC(C)=O", 
        "example_rxn_reactants": ["CC(=O)O", "NCC"],
        "functional_groups": ["carboxylic_acid", "primary_or_secondary_amine_C_aryl_alkyl"],
        "group_smarts": ["[#6]-[C&R0](=[O&D1])-[O&H1]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[C;$(C=O):1][OH1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[C:1][N+0:2]", 
        "RXN_NUM": 47
        },
    "48_sulfon_amide": {
        "reaction_name": "48_sulfon_amide", 
        "example_rxn_product": "CCNS(C)(=O)=O", 
        "example_rxn_reactants": ["CS(=O)(=O)O", "NCC"],
        "functional_groups": ["sulfonic_acid", "primary_or_secondary_amine"],
        "group_smarts": ["[S&$(S(=O)(=O)[C,N])]O", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[S;$(S(=O)(=O)[C,N]):1][O].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[S:1][N+0:2]", 
        "RXN_NUM": 48
        },
    "49_N_arylation_heterocycles": {
        "reaction_name": "49_N_arylation_heterocycles", 
        "example_rxn_product": "c1ccc(n2ccnc2)cc1", 
        "example_rxn_reactants": ["c1ccccc1B(O)O", "N1C=NC=C1"],
        "functional_groups": ["aryl_boronic_acid", "5_mem_aryl_w_NH_max2N"],
        "group_smarts": ["cB(-,:O)O", "[n&H1&+0&r5&!$(n[#6]=[O,S,N])&!$(n~n~n)&!$(n~n~c~n)&!$(n~c~n~n)]"],
        "num_reactants": 2, 
        "reaction_string": "[c:1]B(O)O.[nH1;+0;r5;!$(n[#6]=[O,S,N]);!$(n~n~n);!$(n~n~c~n);!$(n~c~n~n):2]>>[c:1][n:2]", 
        "RXN_NUM": 49
        },
    "50_Wittig": {
        "reaction_name": "50_Wittig", 
        "example_rxn_product": "CC=C(C)C", 
        "example_rxn_reactants": ["CC(=O)C", "BrCC"],
        "functional_groups": ["aldehyde_or_ketone_flexible", "primary_or_secondary_halide"],
        "group_smarts": ["[#6]-[C;H1,$([C&H0](-[#6])[#6]);!$(CC=O)]=[O&D1]", "[Cl,Br,I][C&H2&$(C-[#6])&!$(CC[I,Br])&!$(CCO[C&H3])]"],
        "num_reactants": 2, 
        "reaction_string": "[#6:3]-[C;H1,$([CH0](-[#6])[#6]);!$(CC=O):1]=[OD1].[Cl,Br,I][C;H2;$(C-[#6]);!$(CC[I,Br]);!$(CCO[CH3]):2]>>[C:3][C:1]=[C:2]", 
        "RXN_NUM": 50
        },
    "51_Buchwald_Hartwig": {
        "reaction_name": "51_Buchwald_Hartwig", 
        "example_rxn_product": "CN(C)c1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1Br", "CNC"],
        "functional_groups": ["aryl_halide_nitrogen_optional", "primary_or_secondary_amine_aro_optional"],
        "group_smarts": ["[Cl,Br,I][c&$(c1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1)]", "[N;$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N]),H2&$(Nc1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1)]"],
        "num_reactants": 2, 
        "reaction_string": "[Cl,Br,I][c;$(c1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1):1].[N;$(NC)&!$(N=*)&!$([N-])&!$(N#*)&!$([ND3])&!$([ND4])&!$(N[c,O])&!$(N[C,S]=[S,O,N]),H2&$(Nc1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1):2]>>[c:1][N:2]", 
        "RXN_NUM": 51
        },
    "52_imidazole": {
        "reaction_name": "52_imidazole", 
        "example_rxn_product": "CNC1=NC(C)=C(C)N1", 
        "example_rxn_reactants": ["CC(=O)C(Br)C", "N=C(N)NC"],
        "functional_groups": ["alpha_halo_ketone", "amidine"],
        "group_smarts": ["[C&$(C(-,:[#6])[#6&!$([#6]Br)])](=[O&D1])[C&H1&$(C(-,:[#6])[#6])]Br", "[#7&H2][C&$(C(=N)(-,:N)[c,#7])]=[#7&H1&D1]"],
        "num_reactants": 2, 
        "reaction_string": "[C;$(C([#6])[#6;!$([#6]Br)]):4](=[OD1])[CH;$(C([#6])[#6]):5]Br.[#7;H2:3][C;$(C(=N)(N)[c,#7]):2]=[#7;H1;D1:1]>>[C:4]1=[CH0:5][NH:3][C:2]=[N:1]1", 
        "RXN_NUM": 52
        },
    "53_decarboxylative_coupling": {
        "reaction_name": "53_decarboxylative_coupling", 
        "example_rxn_product": "O=[N+]([O-])c1ccccc1c1ccccc1", 
        "example_rxn_reactants": ["c1c(C(=O)O)c([N+](=O)[O-])ccc1", "c1ccccc1Br"],
        "functional_groups": ["aryl_carboxylic_acid", "aryl_halide_flexible"],
        "group_smarts": ["[c&$(c1[c&$(c[C,S,N](=[O&D1])[*&R0])]cccc1)][C&$(C(=O)[O&H1])]", "[c&$(c1aaccc1)][Cl,Br,I]"],
        "num_reactants": 2, 
        "reaction_string": "[c;$(c1[c;$(c[C,S,N](=[OD1])[*;R0])]cccc1):1][C;$(C(=O)[O;H1])].[c;$(c1aaccc1):2][Cl,Br,I]>>[c:1][c:2]", 
        "RXN_NUM": 53
        },
    "54_heteroaromatic_nuc_sub": {
        "reaction_name": "54_heteroaromatic_nuc_sub", 
        "example_rxn_product": "CNc1ccccn1", 
        "example_rxn_reactants": ["c1cnc(F)cc1", "CN"],
        "functional_groups": ["pyridine_pyrimidine_triazine", "primary_or_secondary_amine"],
        "group_smarts": ["[c&!$(c1ccccc1)&$(c1[n,c]c[n,c]c[n,c]1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[c;!$(c1ccccc1);$(c1[n,c]c[n,c]c[n,c]1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
        "RXN_NUM": 54
        },
    "55_nucl_sub_aromatic_ortho_nitro": {
        "reaction_name": "55_nucl_sub_aromatic_ortho_nitro", 
        "example_rxn_product": "CNc1ccccc1[N+](=O)[O-]", 
        "example_rxn_reactants": ["c1c([N+](=O)[O-])c(F)ccc1", "CN"],
        "functional_groups": ["ortho_halo_nitrobenzene", "primary_or_secondary_amine"],
        "group_smarts": ["[c&$(c1c(-,:N(~O)~O)cccc1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[c;$(c1c(N(~O)~O)cccc1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
        "RXN_NUM": 55
        },
    "56_nucl_sub_aromatic_para_nitro": {
        "reaction_name": "56_nucl_sub_aromatic_para_nitro", 
        "example_rxn_product": "CNc1ccc([N+](=O)[O-])cc1", 
        "example_rxn_reactants": ["c1c(F)ccc([N+](=O)[O-])c1", "CN"],
        "functional_groups": ["para_halo_nitrobenzene", "primary_or_secondary_amine"],
        "group_smarts": ["[c&$(c1ccc(-,:N(~O)~O)cc1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[c;$(c1ccc(N(~O)~O)cc1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
        "RXN_NUM": 56
        },
    "57_urea": {
        "reaction_name": "57_urea", 
        "example_rxn_product": "CNC(=O)NC", 
        "example_rxn_reactants": ["CN=C=O", "CN"],
        "functional_groups": ["isocyanate", "primary_or_secondary_amine_C_aryl_alkyl"],
        "group_smarts": ["[N&$(N-[#6])]=[C&$(C=O)]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[N;$(N-[#6]):3]=[C;$(C=O):1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[N:3]-[C:1]-[N+0:2]", 
        "RXN_NUM": 57
        },
    "58_thiourea": {
        "reaction_name": "58_thiourea", 
        "example_rxn_product": "CNC(=S)NC", 
        "example_rxn_reactants": ["CN=C=S", "CN"],
        "functional_groups": ["isothiocyanate", "primary_or_secondary_amine_C_aryl_alkyl"],
        "group_smarts": ["[N&$(N-[#6])]=[C&$(C=S)]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
        "num_reactants": 2, 
        "reaction_string": "[N;$(N-[#6]):3]=[C;$(C=S):1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[N:3]-[C:1]-[N+0:2]", 
        "RXN_NUM": 58
        }
    }
# AUTOCLICKCHEM Reactions
AUTOCLICKCHEM_reactions = {
    "1_Epoxide_and_Alcohol":     {
        "reaction_name": "1_Epoxide_and_Alcohol",
        "example_rxn_product": "CC(C)(C)C(O)(OCCCF)C(C)(C)O", 
        "example_rxn_reactants": ["CC(C)(C)C1(O)OC1(C)C", "FCCC(O)"], 
        "functional_groups": ["Epoxide", "Alcohol"], 
        "group_smarts": ["[CR1;H2,H1X4,H0X4]1O[CR1;H2,H1X4,H0X4]1", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[CR1;H2,H1X4,H0X4:1]1O[CR1;H2,H1X4,H0X4:2]1.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):3]-[OR0&H1]>>O[C:1][C:2]O-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):3]", 
        "RXN_NUM": 1
        },
    "2_Epoxide_and_Thiol":     {
        "reaction_name": "2_Epoxide_and_Thiol",
        "example_rxn_product": "CC(C)(C)C(O)(SCCC(=O)OC(=O)[O-])C(C)(C)O", 
        "example_rxn_reactants": ["CC(C)(C)C1(O)OC1(C)C", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Epoxide", "Thiol_1R"], 
        "group_smarts": ["[CR1;H2,H1X4,H0X4]1O[CR1;H2,H1X4,H0X4]1", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[CR1;H2,H1X4,H0X4:1]1O[CR1;H2,H1X4,H0X4:2]1.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):3]-[SR0&H1]>>O[C:1][C:2]S-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):3]", 
        "RXN_NUM": 2
        },
    "3_Alkene_Oxidized_To_Epoxide":     {
        "reaction_name": "3_Alkene_Oxidized_To_Epoxide",
        "example_rxn_product": "CNC1(C)OC1(O)Br", 
        "example_rxn_reactants": ["BrC(O)=C(C)NC"], 
        "functional_groups": ["Alkene"], 
        "group_smarts": ["[CR0;X3,X2H1,X1H2]=[CR0;X3,X2H1,X1H2]"],
        "num_reactants": 1, 
        "reaction_string": "[CR0;X3,X2H1,X1H2:1]=[CR0;X3,X2H1,X1H2:2]>>[C:1]1O[C:2]1", 
        "RXN_NUM": 3
        },
    "4_Sulfonyl_Azide_and_Thio_Acid":     {
        "reaction_name": "4_Sulfonyl_Azide_and_Thio_Acid",
        "example_rxn_product": "C=CCS(=O)(=O)NC(=O)C(O)CC1CNNN1", 
        "example_rxn_reactants": ["C=CCS(=O)(=O)N=[N+]=[N-]", "O=C(S)C(O)CC1CNNN1"], 
        "functional_groups": ["Sulfonyl_Azide", "Thio_Acid"], 
        "group_smarts": ["[*]S(=O)(=O)-[$(N=[N+]=[N-]),$([N-][N+]#N)]", "[C]-[$([CX3R0]([S;H1,X1])=[OX1]),$([CX3R0]([O;H1,X1])=[SX1])]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]S(=O)(=O)-[$(N=[N+]=[N-]),$([N-][N+]#N)].[C:2]-[$([CX3R0]([S;H1,X1])=[OX1]),$([CX3R0]([O;H1,X1])=[SX1])]>>[*:1]S(=O)(=O)N-C([C:2])=O", 
        "RXN_NUM": 4
        },
    "5_Alkyne_and_Azide":     {
        "reaction_name": "5_Alkyne_and_Azide",
        "example_rxn_product": "O=C(Cl)OCC1=C(CBr)N=NN1CC1CCCCO1", 
        "example_rxn_reactants": ["BrCC#CCOC(=O)Cl", "[N-]=[N+]=NCC1CCCCO1"], 
        "functional_groups": ["Alkyne", "Azide_1R"], 
        "group_smarts": ["[*][CR0]#[CR0;X2,X1H1]", "[*;#6]-[$(N=[N+]=[N-]),$([N-][N+]#N)]"], 
        "num_reactants": 2,
        "reaction_string": "[*:2][CR0]#[CR0;X2,X1H1:3].[*;#6:1]-[$(N=[N+]=[N-]),$([N-][N+]#N)]>>[*;#6:1]N-1-N=N-C([*:2])=[*:3]1", 
        "RXN_NUM": 5
        },
    "6_Halide_To_Azide":     {
        "reaction_name": "6_Halide_To_Azide",
        "example_rxn_product": "CC(C(=O)F)C(F)(F)N=[N+]=[N-]", 
        "example_rxn_reactants": ["CC(C(=O)F)C(F)(F)Br"], 
        "functional_groups": ["Halide"], 
        "group_smarts": ["[Cl,Br,I][#6;H0X4,H0X3,H1X4,H1X3,H2X4,H3X1]"], 
        "num_reactants": 1,
        "reaction_string": "[Cl,Br,I:2][#6;H0X4,H0X3,H1X4,H1X3,H2X4,H3X1:1]>>[#6:1]-N=[N+]=[N-]", 
        "RXN_NUM": 6
        },
    "7_Halide_To_Cyanide":     {
        "reaction_name": "7_Halide_To_Cyanide",
        "example_rxn_product": "CC(C(=O)F)C(F)(F)C#N", 
        "example_rxn_reactants": ["CC(C(=O)F)C(F)(F)Br"], 
        "functional_groups": ["Halide"], 
        "group_smarts": ["[Cl,Br,I][#6;H0X4,H0X3,H1X4,H1X3,H2X4,H3X1]"], 
        "num_reactants": 1, 
        "reaction_string": "[Cl,Br,I:2][#6;H0X4,H0X3,H1X4,H1X3,H2X4,H3X1:1]>>[#6:1]C#N", 
        "RXN_NUM": 7
        },
    "8_Alcohol_To_Azide":     {
        "reaction_name": "8_Alcohol_To_Azide",
        "example_rxn_product": "[N-]=[N+]=NCCCF", 
        "example_rxn_reactants": ["FCCC(O)"], 
        "functional_groups": ["Alcohol"], 
        "group_smarts": ["[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 1, 
        "reaction_string": "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]-[OR0&H1]>>[N-]=[N+]=N-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]", 
        "RXN_NUM": 8
        },
    "9_Alcohol_To_Cyanide":     {
        "reaction_name": "9_Alcohol_To_Cyanide",
        "example_rxn_product": "N#CCCCF", 
        "example_rxn_reactants": ["FCCC(O)"], 
        "functional_groups": ["Alcohol"], 
        "group_smarts": ["[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 1,
        "reaction_string": "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]-[OR0&H1]>>N#C-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]", 
        "RXN_NUM": 9
        },
    "10_Primary_Amine_Oxidized_To_an_Azide":     {
        "reaction_name": "10_Primary_Amine_Oxidized_To_an_Azide",
        "example_rxn_product": "[N-]=[N+]=NC(=O)O", 
        "example_rxn_reactants": ["NC(=O)O"], 
        "functional_groups": ["Primary_Amine_1R"], 
        "group_smarts": ["[#7&!H3;H2R0]-[#6]"], 
        "num_reactants": 1, 
        "reaction_string": "[#7&!H3;H2R0]-[#6:1]>>[#6:1]N=[N+]=[N-]", 
        "RXN_NUM": 10
        },
    "11_Primary_Amine_Oxidized_To_an_Isocyanate":     {
        "reaction_name": "11_Primary_Amine_Oxidized_To_an_Isocyanate",
        "example_rxn_product": "O=C=NC(=O)O", 
        "example_rxn_reactants": ["NC(=O)O"], 
        "functional_groups": ["Primary_Amine_1R"], 
        "group_smarts": ["[#7&!H3;H2R0]-[#6]"], 
        "num_reactants": 1, 
        "reaction_string": "[#7&!H3;H2R0]-[#6:1]>>[#6:1]N=C=O", 
        "RXN_NUM": 11
        },
    "12_Primary_Amine_Oxidized_To_an_Isothiocyanate":     {
        "reaction_name": "12_Primary_Amine_Oxidized_To_an_Isothiocyanate",
        "example_rxn_product": "O=C(O)N=C=S", 
        "example_rxn_reactants": ["NC(=O)O"], 
        "functional_groups": ["Primary_Amine_1R"], 
        "group_smarts": ["[#7&!H3;H2R0]-[#6]"], 
        "num_reactants": 1, 
        "reaction_string": "[#7&!H3;H2R0]-[#6:1]>>[#6:1]N=C=S", 
        "RXN_NUM": 12
        },
    "13_Azide_Reduced_To_Amine":     {
        "reaction_name": "13_Azide_Reduced_To_Amine",
        "example_rxn_product": "NCC1CCCCO1", 
        "example_rxn_reactants": ["[N-]=[N+]=NCC1CCCCO1"], 
        "functional_groups": ["Azide_1R"], 
        "group_smarts": ["[*;#6]-[$(N=[N+]=[N-]),$([N-][N+]#N)]"], 
        "num_reactants": 1, 
        "reaction_string": "[*;#6:1]-[$(N=[N+]=[N-]),$([N-][N+]#N)]>>[NH2][*;#6:1]", 
        "RXN_NUM": 13
        },
    "14_Carbonochloridate_and_Amine":     {
        "reaction_name": "14_Carbonochloridate_and_Amine",
        "example_rxn_product": "O=C(Cl)OC(=O)N1CC(=O)OC1=O", 
        "example_rxn_reactants": ["O=C(Cl)OC(=O)Cl", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Carbonochloridate", "Amine_2R"], 
        "group_smarts": ["Cl[C;X3](=O)-O[*]", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "Cl[C;X3](=O)-O[*:1].[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*:1]O-C(=O)-[#7:2]", 
        "RXN_NUM": 14
        },
    "15_Carboxylate_and_Amine":     {
        "reaction_name": "15_Carboxylate_and_Amine",
        "example_rxn_product": "O=C1CN(C(=O)Cc2ccccc2)C(=O)O1", 
        "example_rxn_reactants": ["c1ccccc1CC(=O)O", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Carboxylate", "Amine_2R"], 
        "group_smarts": ["[*]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*:1]C(=O)-[#7:2]", 
        "RXN_NUM": 15
        },
    "16_Carboxylate_and_Alcohol":     {
        "reaction_name": "16_Carboxylate_and_Alcohol",
        "example_rxn_product": "O=C(Cc1ccccc1)OCCCF", 
        "example_rxn_reactants": ["c1ccccc1CC(=O)O", "FCCC(O)"], 
        "functional_groups": ["Carboxylate", "Alcohol"], 
        "group_smarts": ["[*]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[*:1]C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 16
        },
    "17_Carboxylate_and_Thiol":     {
        "reaction_name": "17_Carboxylate_and_Thiol",
        "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)Cc1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1CC(=O)O", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Carboxylate", "Thiol_1R"], 
        "group_smarts": ["[*]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[*:1]C(=O)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
        "RXN_NUM": 17
        },
    "18_Carboxylate_To_Cyanide":     {
        "reaction_name": "18_Carboxylate_To_Cyanide",
        "example_rxn_product": "N#CC(=O)Cc1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1CC(=O)O"], 
        "functional_groups": ["Carboxylate"], 
        "group_smarts": ["[*]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]"], 
        "num_reactants": 1, 
        "reaction_string": "[*:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]>>[*:1]C(=O)C#N", 
        "RXN_NUM": 18
        },
    "19_Carboxylate_To_Azide":     {
        "reaction_name": "19_Carboxylate_To_Azide",
        "example_rxn_product": "[N-]=[N+]=NC(=O)Cc1ccccc1", 
        "example_rxn_reactants": ["c1ccccc1CC(=O)O"], 
        "functional_groups": ["Carboxylate"], 
        "group_smarts": ["[*]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]"], 
        "num_reactants": 1, 
        "reaction_string": "[*:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]>>[*:1]C(=O)-N=[N+]=[N-]", 
        "RXN_NUM": 19
        },
    "20_Acyl_Halide_and_Amine":     {
        "reaction_name": "20_Acyl_Halide_and_Amine",
        "example_rxn_product": "CC(=O)CC(=O)N1CC(=O)OC1=O", 
        "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Acyl_Halide", "Amine_2R"], 
        "group_smarts": ["[*;#6][C](-[Cl,Br,I])=O", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[*;#6:1][C](-[Cl,Br,I])=O.[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*;#6:1][C](=O)-[#7:2]", 
        "RXN_NUM": 20
        },
    "21_Acyl_Halide_and_Alcohol":     {
        "reaction_name": "21_Acyl_Halide_and_Alcohol",
        "example_rxn_product": "CC(=O)CC(=O)OCCCF", 
        "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "FCCC(O)"], 
        "functional_groups": ["Acyl_Halide", "Alcohol"], 
        "group_smarts": ["[*;#6][C](-[Cl,Br,I])=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*;#6:1][C](-[Cl,Br,I])=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[*;#6:1][C](=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 21
        },
    "22_Acyl_Halide_and_Thiol":     {
        "reaction_name": "22_Acyl_Halide_and_Thiol",
        "example_rxn_product": "CC(=O)CC(=O)SCCC(=O)OC(=O)[O-]", 
        "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Acyl_Halide", "Thiol_1R"], 
        "group_smarts": ["[*;#6][C](-[Cl,Br,I])=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*;#6:1][C](-[Cl,Br,I])=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[*;#6:1][C](=O)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
        "RXN_NUM": 22
        },
    "23_Acyl_Halide_To_Cyanide":     {
        "reaction_name": "23_Acyl_Halide_To_Cyanide",
        "example_rxn_product": "CC(=O)CC(=O)C#N", 
        "example_rxn_reactants": ["O=C(C)CC(=O)Cl"], 
        "functional_groups": ["Acyl_Halide"], 
        "group_smarts": ["[*;#6][C](-[Cl,Br,I])=O"], 
        "num_reactants": 1, 
        "reaction_string": "[*;#6:1][C](-[Cl,Br,I])=O>>[*;#6:1][C](=O)C#N", 
        "RXN_NUM": 23
        },
    "24_Acyl_Halide_To_Azide":     {
        "reaction_name": "24_Acyl_Halide_To_Azide",
        "example_rxn_product": "CC(=O)CC(=O)N=[N+]=[N-]", 
        "example_rxn_reactants": ["O=C(C)CC(=O)Cl"], 
        "functional_groups": ["Acyl_Halide"], 
        "group_smarts": ["[*;#6][C](-[Cl,Br,I])=O"], 
        "num_reactants": 1, 
        "reaction_string": "[*;#6:1][C](-[Cl,Br,I])=O>>[*;#6:1][C](=O)-N=[N+]=[N-]", 
        "RXN_NUM": 24
        },
    "25_Ester_and_Amine":     {
        "reaction_name": "25_Ester_and_Amine",
        "example_rxn_product": "O=C1CN(C(=O)C2CCCN2)C(=O)O1", 
        "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Ester", "Amine_2R"], 
        "group_smarts": ["[*;#6]C(=O)-O[*]", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[*;#6:1]C(=O)-O[*:4].[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*;#6:1]C(=O)-[#7:2]", 
        "RXN_NUM": 25
        },
    "26_Ester_and_Alcohol":     {
        "reaction_name": "26_Ester_and_Alcohol",
        "example_rxn_product": "O=C(OCCCF)C1CCCN1", 
        "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "FCCC(O)"], 
        "functional_groups": ["Ester", "Alcohol"], 
        "group_smarts": ["[*;#6]C(=O)-O[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2,
        "reaction_string": "[*;#6:1]C(=O)-O[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[*;#6:1]C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 26
        },
    "27_Ester_and_Thiol":     {
        "reaction_name": "27_Ester_and_Thiol",
        "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)C1CCCN1", 
        "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Ester", "Thiol_1R"], 
        "group_smarts": ["[*;#6]C(=O)-O[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*;#6:1]C(=O)-O[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[*;#6:1]C(=O)-S[CR0&$([#6])&!$([#6]=O):2]", 
        "RXN_NUM": 27
        },
    "28_Acid_Anhydride_Noncyclic_and_Amine":     {
        "reaction_name": "28_Acid_Anhydride_Noncyclic_and_Amine",
        "example_rxn_product": "O=C1CN(C(=O)C2CCCCC2)C(=O)O1", 
        "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Acid_Anhydride_Noncyclic", "Amine_2R"], 
        "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:4].[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*:1]C(=O)-[#7:2]", 
        "RXN_NUM": 28
        },
    "29_Acid_Anhydride_Noncyclic_and_Alcohol":     {
        "reaction_name": "29_Acid_Anhydride_Noncyclic_and_Alcohol",
        "example_rxn_product": "O=C(OCCCF)C1CCCCC1", 
        "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "FCCC(O)"], 
        "functional_groups": ["Acid_Anhydride_Noncyclic", "Alcohol"], 
        "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[*:1]C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 29
        },
    "30_Acid_Anhydride_Noncyclic_and_Thiol":     {
        "reaction_name": "30_Acid_Anhydride_Noncyclic_and_Thiol",
        "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)C1CCCCC1", 
        "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Acid_Anhydride_Noncyclic", "Thiol_1R"], 
        "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[*:1]C(=O)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
        "RXN_NUM": 30
        },
    "31_Acid_Anhydride_Noncyclic_To_Cyanide":     {
        "reaction_name": "31_Acid_Anhydride_Noncyclic_To_Cyanide",
        "example_rxn_product": "N#CC(=O)C1CCCCC1", 
        "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2"], 
        "functional_groups": ["Acid_Anhydride_Noncyclic"], 
        "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]"], 
        "num_reactants": 1, 
        "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:2]>>[*:1]C(=O)C#N", 
        "RXN_NUM": 31
        },
    "32_Acid_Anhydride_Noncyclic_To_Azide":     {
        "reaction_name": "32_Acid_Anhydride_Noncyclic_To_Azide",
        "example_rxn_product": "[N-]=[N+]=NC(=O)C1CCCCC1", 
        "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2"], 
        "functional_groups": ["Acid_Anhydride_Noncyclic"], 
        "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]"], 
        "num_reactants": 1, 
        "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:2]>>[*:1]C(=O)-N=[N+]=[N-]", 
        "RXN_NUM": 32
        },
    "33_Isocyanate_and_Amine":     {
        "reaction_name": "33_Isocyanate_and_Amine",
        "example_rxn_product": "O=C(Cl)NC(=O)N1CC(=O)OC1=O", 
        "example_rxn_reactants": ["O=C=NC(=O)Cl", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Isocyanate", "Amine_2R"], 
        "group_smarts": ["[#6]N=C=O", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=O.[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[#6:1]N-C(=O)-[#7:2]", 
        "RXN_NUM": 33
        },
    "34_Isothiocyanate_and_Amine":     {
        "reaction_name": "34_Isothiocyanate_and_Amine",
        "example_rxn_product": "O=C(Cl)CCNC(=S)N1CC(=O)OC1=O", 
        "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "O=C1CNC(=O)O1"], 
        "functional_groups": ["Isothiocyanate", "Amine_2R"], 
        "group_smarts": ["[#6]N=C=S", "[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=S.[#7;$([#7&!H3;H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[#6:1]N-C(=S)-[#7:2]", 
        "RXN_NUM": 34
        },
    "35_Isocyanate_and_Thiol":     {
        "reaction_name": "35_Isocyanate_and_Thiol",
        "example_rxn_product": "O=C(Cl)NC(=O)SCCC(=O)OC(=O)[O-]", 
        "example_rxn_reactants": ["O=C=NC(=O)Cl", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Isocyanate", "Thiol_1R"], 
        "group_smarts": ["[#6]N=C=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[#6:1]N-C(=O)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
        "RXN_NUM": 35
        },
    "36_Isothiocyanate_and_Thiol":     {
        "reaction_name": "36_Isothiocyanate_and_Thiol",
        "example_rxn_product": "O=C(Cl)CCNC(=S)SCCC(=O)OC(=O)[O-]", 
        "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "O=C([O-])OC(=O)CCS"], 
        "functional_groups": ["Isothiocyanate", "Thiol_1R"], 
        "group_smarts": ["[#6]N=C=S", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=S.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0&H1]>>[#6:1]N-C(=S)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
        "RXN_NUM": 36
        },
    "37_Isocyanate_and_Alcohol":     {
        "reaction_name": "37_Isocyanate_and_Alcohol",
        "example_rxn_product": "O=C(Cl)NC(=O)OCCCF", 
        "example_rxn_reactants": ["O=C=NC(=O)Cl", "FCCC(O)"], 
        "functional_groups": ["Isocyanate", "Alcohol"], 
        "group_smarts": ["[#6]N=C=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[#6:1]N-C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 37
        },
    "38_Isothiocyanate_and_Alcohol":     {
        "reaction_name": "38_Isothiocyanate_and_Alcohol",
        "example_rxn_product": "O=C(Cl)CCNC(=S)OCCCF", 
        "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "FCCC(O)"], 
        "functional_groups": ["Isothiocyanate", "Alcohol"], 
        "group_smarts": ["[#6]N=C=S", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0&H1]"], 
        "num_reactants": 2, 
        "reaction_string": "[#6:1]N=C=S.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0&H1]>>[#6:1]N-C(=S)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
        "RXN_NUM": 38
    }
    }
# all_rxns Reactions
All_Rxns_reactions =     {
        "1_Epoxide_and_Alcohol":     {
            "reaction_name": "1_Epoxide_and_Alcohol",
            "example_rxn_product": "CC(C)(C)C(O)(OCCCF)C(C)(C)O", 
            "example_rxn_reactants": ["CC(C)(C)C1(O)OC1(C)C", "FCCC(O)"], 
            "functional_groups": ["Epoxide", "Alcohol"], 
            "group_smarts": ["[CR1;H2,H1X4,H0X4]1O[CR1;H2,H1X4,H0X4]1", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[CR1;H2,H1X4,H0X4:1]1O[CR1;H2,H1X4,H0X4:2]1.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):3]-[OR0;H1,-]>>O[C:1][C:2]O-[#6:3]", 
            "RXN_NUM": 1
            },
        "2_Epoxide_and_Thiol":     {
            "reaction_name": "2_Epoxide_and_Thiol",
            "example_rxn_product": "CC(C)(C)C(O)(SCCC(=O)OC(=O)[O-])C(C)(C)O", 
            "example_rxn_reactants": ["CC(C)(C)C1(O)OC1(C)C", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Epoxide", "Thiol_1R"], 
            "group_smarts": ["[CR1;H2,H1X4,H0X4]1O[CR1;H2,H1X4,H0X4]1", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[CR1;H2,H1X4,H0X4:1]1O[CR1;H2,H1X4,H0X4:2]1.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):3]-[SR0;H1,-]>>O[C:1][C:2]S-[#6:3]", 
            "RXN_NUM": 2
            },
        "3_Alkene_Oxidized_To_Epoxide":     {
            "reaction_name": "3_Alkene_Oxidized_To_Epoxide",
            "example_rxn_product": "CNC1(C)OC1(O)Br", 
            "example_rxn_reactants": ["BrC(O)=C(C)NC"], 
            "functional_groups": ["Alkene"], 
            "group_smarts": ["[CR0;X3,X2H1,X1H2]=[CR0;X3,X2H1,X1H2]"],
            "num_reactants": 1, 
            "reaction_string": "[CR0;X3,X2H1,X1H2:1]=[CR0;X3,X2H1,X1H2:2]>>[C:1]1O[C:2]1", 
            "RXN_NUM": 3
            },
        "4_Sulfonyl_Azide_and_Thio_Acid":     {
            "reaction_name": "4_Sulfonyl_Azide_and_Thio_Acid",
            "example_rxn_product": "C=CCS(=O)(=O)NC(=O)C(O)CC1CNNN1", 
            "example_rxn_reactants": ["C=CCS(=O)(=O)N=[N+]=[N-]", "O=C(S)C(O)CC1CNNN1"], 
            "functional_groups": ["Sulfonyl_Azide", "Thio_Acid"], 
            "group_smarts": ["[*]S(=O)(=O)-[$(N=[N+]=[N-]),$([N-][N+]#N)]", "[C]-[$([CX3R0]([S;H1,X1])=[OX1]),$([CX3R0]([O;H1,X1])=[SX1])]"], 
            "num_reactants": 2, 
            "reaction_string": "[*:1]S(=O)(=O)-[$(N=[N+]=[N-]),$([N-][N+]#N)].[C:2]-[$([CX3R0]([S;H1,X1])=[OX1]),$([CX3R0]([O;H1,X1])=[SX1])]>>[*:1]S(=O)(=O)N-C([C:2])=O", 
            "RXN_NUM": 4
            },
        "5_Alkyne_and_Azide":     {
            "reaction_name": "5_Alkyne_and_Azide",
            "example_rxn_product": "O=C(Cl)OCC1=C(CBr)N=NN1CC1CCCCO1", 
            "example_rxn_reactants": ["BrC#CCOC(=O)Cl", "[N-]=[N+]=NCC1CCCCO1"], 
            "functional_groups": ["Alkyne", "Azide_1R"], 
            "group_smarts": ["[CR0;X2,X1H1]#[CR0;X2,X1H1]", "[*;#6]-[$(N=[N+]=[N-]),$([N-][N+]#N)]"], 
            "num_reactants": 2,
            "reaction_string": "[CR0;X2,X1H1:2]#[CR0;X2,X1H1:3].[*;#6:1]-[$(N=[N+]=[N-]),$([N-][N+]#N)]>>[*;#6:1]N-1-N=N-C([*:2])=[*:3]1", 
            "RXN_NUM": 5
            },
        "6_Alcohol_To_Azide":     {
            "reaction_name": "6_Alcohol_To_Azide",
            "example_rxn_product": "[N-]=[N+]=NCCCF", 
            "example_rxn_reactants": ["FCCC(O)"], 
            "functional_groups": ["Alcohol"], 
            "group_smarts": ["[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 1, 
            "reaction_string": "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]-[OR0;H1,-]>>[N-]=[N+]=N-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]", 
            "RXN_NUM": 6
            },
        "7_Alcohol_To_Cyanide":     {
            "reaction_name": "7_Alcohol_To_Cyanide",
            "example_rxn_product": "N#CCCCF", 
            "example_rxn_reactants": ["FCCC(O)"], 
            "functional_groups": ["Alcohol"], 
            "group_smarts": ["[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 1,
            "reaction_string": "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]-[OR0;H1,-]>>N#C-[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):1]", 
            "RXN_NUM": 7
            },
        "8_Primary_Amine_Oxidized_To_an_Azide":     {
            "reaction_name": "8_Primary_Amine_Oxidized_To_an_Azide",
            "example_rxn_product": "[N-]=[N+]=NC(=O)O", 
            "example_rxn_reactants": ["NC(=O)O"], 
            "functional_groups": ["Primary_Amine_1R"], 
            "group_smarts": ["[#7;$([H3+]),$([H2R0;!+])]-[#6]"], 
            "num_reactants": 1, 
            "reaction_string": "[#7;$([H3+]),$([H2R0;!+])]-[#6:1]>>[#6:1]N=[N+]=[N-]", 
            "RXN_NUM": 8
            },
        "9_Primary_Amine_Oxidized_To_an_Isocyanate":     {
            "reaction_name": "9_Primary_Amine_Oxidized_To_an_Isocyanate",
            "example_rxn_product": "O=C=NC(=O)O", 
            "example_rxn_reactants": ["NC(=O)O"], 
            "functional_groups": ["Primary_Amine_1R"], 
            "group_smarts": ["[#7;$([H3+]),$([H2R0;!+])]-[#6]"], 
            "num_reactants": 1, 
            "reaction_string": "[#7;$([H3+]),$([H2R0;!+])]-[#6:1]>>[#6:1]N=C=O", 
            "RXN_NUM": 9
            },
        "10_Primary_Amine_Oxidized_To_an_Isothiocyanate":     {
            "reaction_name": "10_Primary_Amine_Oxidized_To_an_Isothiocyanate",
            "example_rxn_product": "O=C(O)N=C=S", 
            "example_rxn_reactants": ["NC(=O)O"], 
            "functional_groups": ["Primary_Amine_1R"], 
            "group_smarts": ["[#7;$([H3+]),$([H2R0;!+])]-[#6]"], 
            "num_reactants": 1, 
            "reaction_string": "[#7;$([H3+]),$([H2R0;!+])]-[#6:1]>>[#6:1]N=C=S", 
            "RXN_NUM": 10
            },
        "11_Azide_Reduced_To_Amine":     {
            "reaction_name": "11_Azide_Reduced_To_Amine",
            "example_rxn_product": "NCC1CCCCO1", 
            "example_rxn_reactants": ["[N-]=[N+]=NCC1CCCCO1"], 
            "functional_groups": ["Azide_1R"], 
            "group_smarts": ["[*;#6]-[$(N=[N+]=[N-]),$([N-][N+]#N)]"], 
            "num_reactants": 1, 
            "reaction_string": "[*;#6:1]-[$(N=[N+]=[N-]),$([N-][N+]#N)]>>[NH2][*;#6:1]", 
            "RXN_NUM": 11
            },
        "12_Carbonochloridate_and_Amine":     {
            "reaction_name": "12_Carbonochloridate_and_Amine",
            "example_rxn_product": "O=C(Cl)OC(=O)N1CC(=O)OC1=O", 
            "example_rxn_reactants": ["O=C(Cl)OC(=O)Cl", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Carbonochloridate", "Amine_2R"], 
            "group_smarts": ["Cl[C;X3](=O)-O[*]", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "Cl[C;X3](=O)-O[*:1].[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*:1]O-C(=O)-[#7+0:2]", 
            "RXN_NUM": 12
            },
        "13_Carboxylate_and_Amine":     {
            "reaction_name": "13_Carboxylate_and_Amine",
            "example_rxn_product": "O=C1CN(C(=O)Cc2ccccc2)C(=O)O1", 
            "example_rxn_reactants": ["c1ccccc1CC(=O)O", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Carboxylate", "Amine_2R"], 
            "group_smarts": ["[*;!O]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[*;!O:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*;!O:1]C(=O)-[#7+0:2]", 
            "RXN_NUM": 13
            },
        "14_Carboxylate_and_Alcohol":     {
            "reaction_name": "14_Carboxylate_and_Alcohol",
            "example_rxn_product": "O=C(Cc1ccccc1)OCCCF", 
            "example_rxn_reactants": ["c1ccccc1CC(=O)O", "FCCC(O)"], 
            "functional_groups": ["Carboxylate", "Alcohol"], 
            "group_smarts": ["[*;!O]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[*;!O:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[*;!O:1]C(=O)-O[#6:2]", 
            "RXN_NUM": 14
            },
        "15_Carboxylate_and_Thiol":     {
            "reaction_name": "15_Carboxylate_and_Thiol",
            "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)Cc1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1CC(=O)O", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Carboxylate", "Thiol_1R"], 
            "group_smarts": ["[*;!O]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[*;!O:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[*;!O:1]C(=O)-S[#6:2]", 
            "RXN_NUM": 15
            },
        "16_Carboxylate_To_Cyanide":     {
            "reaction_name": "16_Carboxylate_To_Cyanide",
            "example_rxn_product": "N#CC(=O)Cc1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1CC(=O)O"], 
            "functional_groups": ["Carboxylate"], 
            "group_smarts": ["[*;!O]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]"], 
            "num_reactants": 1, 
            "reaction_string": "[*;!O:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]>>[*;!O:1]C(=O)C#N", 
            "RXN_NUM": 16
            },
        "17_Carboxylate_To_Azide":     {
            "reaction_name": "17_Carboxylate_To_Azide",
            "example_rxn_product": "[N-]=[N+]=NC(=O)Cc1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1CC(=O)O"], 
            "functional_groups": ["Carboxylate"], 
            "group_smarts": ["[*;!O]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]"], 
            "num_reactants": 1, 
            "reaction_string": "[*;!O:1]-[$([CR0;X3](=[OR0&D1])[OR0&H1]),$([CR0;X3](=[OR0&D1])[OR0-])]>>[*;!O:1]C(=O)-N=[N+]=[N-]", 
            "RXN_NUM": 17
            },
        "18_Halide_and_Amine":     {
            "reaction_name": "18_Halide_and_Amine",
            "example_rxn_product": "CC(=O)CC(=O)N1CC(=O)OC1=O", 
            "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Halide", "Amine_2R"], 
            "group_smarts": ["[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S])]", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S]):1].[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[#6:1]-[#7+0:2]", 
            "RXN_NUM": 18
            },
        "19_Halide_and_Alcohol":     {
            "reaction_name": "19_Halide_and_Alcohol",
            "example_rxn_product": "CC(=O)CC(=O)OCCCF", 
            "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "FCCC(O)"], 
            "functional_groups": ["Halide", "Alcohol"], 
            "group_smarts": ["[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S]):1].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[#6:1]-O-[#6:2]", 
            "RXN_NUM": 19
            },
        "20_Halide_and_Thiol":     {
            "reaction_name": "20_Halide_and_Thiol",
            "example_rxn_product": "CC(=O)CC(=O)SCCC(=O)OC(=O)[O-]", 
            "example_rxn_reactants": ["O=C(C)CC(=O)Cl", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Halide", "Thiol_1R"], 
            "group_smarts": ["[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S])]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S]):1].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[#6:1]-S-[#6:2]", 
            "RXN_NUM": 20
            },
        "21_Halide_To_Cyanide":     {
            "reaction_name": "21_Halide_To_Cyanide",
            "example_rxn_product": "CC(=O)CC(=O)C#N", 
            "example_rxn_reactants": ["O=C(C)CC(=O)Cl"], 
            "functional_groups": ["Halide"], 
            "group_smarts": ["[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S])]"], 
            "num_reactants": 1, 
            "reaction_string": "[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S]):1]>>[#6:1]C#N", 
            "RXN_NUM": 21
            },
        "22_Halide_To_Azide":     {
            "reaction_name": "22_Halide_To_Azide",
            "example_rxn_product": "CC(=O)CC(=O)N=[N+]=[N-]", 
            "example_rxn_reactants": ["O=C(C)CC(=O)Cl"], 
            "functional_groups": ["Halide"], 
            "group_smarts": ["[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S])]"], 
            "num_reactants": 1, 
            "reaction_string": "[Cl,Br,I][$([CX4,c]),$([#6X3]=[O,S]):1]>>[#6:1]-N=[N+]=[N-]", 
            "RXN_NUM": 22
            },
        "23_Ester_and_Amine":     {
            "reaction_name": "23_Ester_and_Amine",
            "example_rxn_product": "O=C1CN(C(=O)C2CCCN2)C(=O)O1", 
            "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Ester", "Amine_2R"], 
            "group_smarts": ["[*;#6]C(=O)-O[*]", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[*;#6:1]C(=O)-O[*:4].[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*;#6:1]C(=O)-[#7+0:2]", 
            "RXN_NUM": 23
            },
        "24_Ester_and_Alcohol":     {
            "reaction_name": "24_Ester_and_Alcohol",
            "example_rxn_product": "O=C(OCCCF)C1CCCN1", 
            "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "FCCC(O)"], 
            "functional_groups": ["Ester", "Alcohol"], 
            "group_smarts": ["[*;#6]C(=O)-O[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2,
            "reaction_string": "[*;#6:1]C(=O)-O[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[*;#6:1]C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
            "RXN_NUM": 24
            },
        "25_Ester_and_Thiol":     {
            "reaction_name": "25_Ester_and_Thiol",
            "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)C1CCCN1", 
            "example_rxn_reactants": ["C1CCNC(C(=O)-OCC)1", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Ester", "Thiol_1R"], 
            "group_smarts": ["[*;#6]C(=O)-O[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[*;#6:1]C(=O)-O[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[*;#6:1]C(=O)-S[CR0&$([#6])&!$([#6]=O):2]", 
            "RXN_NUM": 25
            },
        "26_Acid_Anhydride_Noncyclic_and_Amine":     {
            "reaction_name": "26_Acid_Anhydride_Noncyclic_and_Amine",
            "example_rxn_product": "O=C1CN(C(=O)C2CCCCC2)C(=O)O1", 
            "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Acid_Anhydride_Noncyclic", "Amine_2R"], 
            "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:4].[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[*:1]C(=O)-[#7+0:2]", 
            "RXN_NUM": 26
            },
        "27_Acid_Anhydride_Noncyclic_and_Alcohol":     {
            "reaction_name": "27_Acid_Anhydride_Noncyclic_and_Alcohol",
            "example_rxn_product": "O=C(OCCCF)C1CCCCC1", 
            "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "FCCC(O)"], 
            "functional_groups": ["Acid_Anhydride_Noncyclic", "Alcohol"], 
            "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[*:1]C(=O)-O[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]", 
            "RXN_NUM": 27
            },
        "28_Acid_Anhydride_Noncyclic_and_Thiol":     {
            "reaction_name": "28_Acid_Anhydride_Noncyclic_and_Thiol",
            "example_rxn_product": "O=C([O-])OC(=O)CCSC(=O)C1CCCCC1", 
            "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Acid_Anhydride_Noncyclic", "Thiol_1R"], 
            "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:3].[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[*:1]C(=O)-S[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]", 
            "RXN_NUM": 28
            },
        "29_Acid_Anhydride_Noncyclic_To_Cyanide":     {
            "reaction_name": "29_Acid_Anhydride_Noncyclic_To_Cyanide",
            "example_rxn_product": "N#CC(=O)C1CCCCC1", 
            "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2"], 
            "functional_groups": ["Acid_Anhydride_Noncyclic"], 
            "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]"], 
            "num_reactants": 1, 
            "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:2]>>[*:1]C(=O)C#N", 
            "RXN_NUM": 29
            },
        "30_Acid_Anhydride_Noncyclic_To_Azide":     {
            "reaction_name": "30_Acid_Anhydride_Noncyclic_To_Azide",
            "example_rxn_product": "[N-]=[N+]=NC(=O)C1CCCCC1", 
            "example_rxn_reactants": ["C1CCC(CC1)C(=O)OC(=O)C2CCCCC2"], 
            "functional_groups": ["Acid_Anhydride_Noncyclic"], 
            "group_smarts": ["[*]C(=O)-[O;R0]-C(=O)[*]"], 
            "num_reactants": 1, 
            "reaction_string": "[*:1]C(=O)-[O;R0]-C(=O)[*:2]>>[*:1]C(=O)-N=[N+]=[N-]", 
            "RXN_NUM": 30
            },
        "31_Isocyanate_and_Amine":     {
            "reaction_name": "31_Isocyanate_and_Amine",
            "example_rxn_product": "O=C(Cl)NC(=O)N1CC(=O)OC1=O", 
            "example_rxn_reactants": ["O=C=NC(=O)Cl", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Isocyanate", "Amine_2R"], 
            "group_smarts": ["[#6]N=C=O", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=O.[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[#6:1]N-C(=O)-[#7+0:2]", 
            "RXN_NUM": 31
            },
        "32_Isothiocyanate_and_Amine":     {
            "reaction_name": "32_Isothiocyanate_and_Amine",
            "example_rxn_product": "O=C(Cl)CCNC(=S)N1CC(=O)OC1=O", 
            "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "O=C1CNC(=O)O1"], 
            "functional_groups": ["Isothiocyanate", "Amine_2R"], 
            "group_smarts": ["[#6]N=C=S", "[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0])]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=S.[#7;$([#7;H3+,H2R0X1]-[#6]),$([#7&!H3;H1R1X3](:,-[#6R1]):,-[#6R1,#7R1]),$([#7&!H3;H2]-[#6]),$([#7&!H3;H0R1X2](:,-[#6R1;X3H1]):,-[#6R1X3H1]),$([#7&!H3;H0R1X2](:,-[#6R1;X3]):,-[#7R1X3]),$([#7&!H3;H1R0X3](-[#6])-[#6R0]):2]>>[#6:1]N-C(=S)-[#7+0:2]", 
            "RXN_NUM": 32
            },
        "33_Isocyanate_and_Thiol":     {
            "reaction_name": "33_Isocyanate_and_Thiol",
            "example_rxn_product": "O=C(Cl)NC(=O)SCCC(=O)OC(=O)[O-]", 
            "example_rxn_reactants": ["O=C=NC(=O)Cl", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Isocyanate", "Thiol_1R"], 
            "group_smarts": ["[#6]N=C=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[#6:1]N-C(=O)-S[#6:2]", 
            "RXN_NUM": 33
            },
        "34_Isothiocyanate_and_Thiol":     {
            "reaction_name": "34_Isothiocyanate_and_Thiol",
            "example_rxn_product": "O=C(Cl)CCNC(=S)SCCC(=O)OC(=O)[O-]", 
            "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "O=C([O-])OC(=O)CCS"], 
            "functional_groups": ["Isothiocyanate", "Thiol_1R"], 
            "group_smarts": ["[#6]N=C=S", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0])]-[SR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=S.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[SR0]):2]-[SR0;H1,-]>>[#6:1]N-C(=S)-S[#6:2]", 
            "RXN_NUM": 34
            },
        "35_Isocyanate_and_Alcohol":     {
            "reaction_name": "35_Isocyanate_and_Alcohol",
            "example_rxn_product": "O=C(Cl)NC(=O)OCCCF", 
            "example_rxn_reactants": ["O=C=NC(=O)Cl", "FCCC(O)"], 
            "functional_groups": ["Isocyanate", "Alcohol"], 
            "group_smarts": ["[#6]N=C=O", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=O.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[#6:1]N-C(=O)-O[#6:2]", 
            "RXN_NUM": 35
            },
        "36_Isothiocyanate_and_Alcohol":     {
            "reaction_name": "36_Isothiocyanate_and_Alcohol",
            "example_rxn_product": "O=C(Cl)CCNC(=S)OCCCF", 
            "example_rxn_reactants": ["O=C(Cl)CCN=C=S", "FCCC(O)"], 
            "functional_groups": ["Isothiocyanate", "Alcohol"], 
            "group_smarts": ["[#6]N=C=S", "[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0])]-[OR0;H1,-]"], 
            "num_reactants": 2, 
            "reaction_string": "[#6:1]N=C=S.[#6&$([CR0,R1X3,R1X4])&!$([#6](=,-[OR0,SR0])[OR0]):2]-[OR0;H1,-]>>[#6:1]N-C(=S)-O[#6:2]", 
            "RXN_NUM": 36
            },
        "37_Pictet_Spengler": {
            "reaction_name": "37_Pictet_Spengler", 
            "example_rxn_product": "CC1NCCc2ccccc21", 
            "example_rxn_reactants": ["c1cc(CCN)ccc1", "CC(=O)"],
            "functional_groups": ["beta_arylethylamine", "aldehyde"],
            "group_smarts": ["[c&H1]1:c(-[C&H2]-[C&H2]-[N&H2]):c:c:c:c:1", "[#6]-[C&H1&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[cH1:1]1:[c:2](-[CH2:7]-[CH2:8]-[NH2:9]):[c:3]:[c:4]:[c:5]:[c:6]:1.[#6:11]-[CH1;R0:10]=[OD1]>>[c:1]12:[c:2](-[CH2:7]-[CH2:8]-[NH1:9]-[C:10]-2(-[#6:11])):[c:3]:[c:4]:[c:5]:[c:6]:1", 
            "RXN_NUM": 37
            },
        "38_benzimidazole_derivatives_carboxylic_acid_ester": {
            "reaction_name": "38_benzimidazole_derivatives_carboxylic_acid_ester", 
            "example_rxn_product": "Cc1n~c2ccccc2n1C", 
            "example_rxn_reactants": ["c1c(NC)c(N)ccc1", "OC(=O)C"],
            "functional_groups": ["ortho_phenylenediamine", "carboxylic_acid_or_ester"],
            "group_smarts": ["[c&r6](-[N&H1&$(N-[#6])]):[c&r6]-[N&H2]", "[#6]-[C&R0](=[O&D1])-[#8;H1,$(O-[C&H3])]"],
            "num_reactants": 2, 
            "reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[#8;H1,$(O-[CH3])]>>[c:3]2:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]@2", 
            "RXN_NUM": 38
            },
        "39_benzimidazole_derivatives_aldehyde": {
            "reaction_name": "39_benzimidazole_derivatives_aldehyde", 
            "example_rxn_product": "Cc1n~c2ccccc2n1C", 
            "example_rxn_reactants": ["c1c(NC)c(N)ccc1", "CC(=O)"],
            "functional_groups": ["ortho_phenylenediamine", "aldehyde"],
            "group_smarts": ["[c&r6](-[N&H1&$(N-[#6])]):[c&r6]-[N&H2]", "[#6]-[C&H1&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[c;r6:1](-[NH1;$(N-[#6]):2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[n:2]:[c:5](-[#6:6]):[n:4]@2", 
            "RXN_NUM": 39
            },
        "40_benzothiazole": {
            "reaction_name": "40_benzothiazole", 
            "example_rxn_product": "Cc1n~c2ccccc2s1", 
            "example_rxn_reactants": ["c1c(S)c(N)ccc1", "CC(=O)"],
            "functional_groups": ["ortho_aminothiophenol", "aldehyde"],
            "group_smarts": ["[c&r6](-[S&H1]):[c&r6]-[N&H2]", "[#6]-[C&H1&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[c;r6:1](-[SH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[s:2]:[c:5](-[#6:6]):[n:4]@2", 
            "RXN_NUM": 40
            },
        "41_benzoxazole_arom_aldehyde": {
            "reaction_name": "41_benzoxazole_arom_aldehyde", 
            "example_rxn_product": "c1ccc(-c2n~c3ccccc3o2)cc1", 
            "example_rxn_reactants": ["c1cc(O)c(N)cc1", "c1ccccc1C(=O)"],
            "functional_groups": ["ortho_aminophenol", "aryl_aldehyde"],
            "group_smarts": ["c(-[O&H1&$(Oc1ccccc1)]):[c&r6]-[N&H2]", "c-[C&H1&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[c:1](-[OH1;$(Oc1ccccc1):2]):[c;r6:3](-[NH2:4]).[c:6]-[CH1;R0:5](=[OD1])>>[c:3]2:[c:1]:[o:2]:[c:5](-[c:6]):[n:4]@2", 
            "RXN_NUM": 41
            },
        "42_benzoxazole_carboxylic_acid": {
            "reaction_name": "42_benzoxazole_carboxylic_acid", 
            "example_rxn_product": "Cc1n~c2ccccc2o1", 
            "example_rxn_reactants": ["c1cc(O)c(N)cc1", "CC(=O)O"],
            "functional_groups": ["ortho_1amine_2alcohol_arylcyclic", "carboxylic_acid"],
            "group_smarts": ["[c&r6](-[O&H1]):[c&r6]-[N&H2]", "[#6]-[C&R0](=[O&D1])-[O&H1]"],
            "num_reactants": 2, 
            "reaction_string": "[c;r6:1](-[OH1:2]):[c;r6:3](-[NH2:4]).[#6:6]-[C;R0:5](=[OD1])-[OH1]>>[c:3]2:[c:1]:[o:2]:[c:5](-[#6:6]):[n:4]@2", 
            "RXN_NUM": 42
            },
        "43_thiazole": {
            "reaction_name": "43_thiazole", 
            "example_rxn_product": "Cc1nc(C)c(C)s1", 
            "example_rxn_reactants": ["CC(=O)C(I)C", "NC(=S)C"],
            "functional_groups": ["haloketone", "thioamide"],
            "group_smarts": ["[#6]-[C&R0](=[O&D1])-[C&H1&R0](-[#6])-[*;#17,#35,#53]", "[$([N&H2]-[C]=[S&D1,O&D1]),$([N&H1]=[C]-[SH1,OH1])]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:6]-[C;R0:1](=[OD1])-[CH1;R0:5](-[#6:7])-[*;#17,#35,#53].[$([N&H2:2]-[C:3]([*:6])=[S&D1,O&D1:4]),$([N&H1:2]=[C:3]([*:6])-[SH1,OH1:4])]>>[c:1]2(-[#6:6]):[n:2]:[c:3]([*:6]):[s:4][c:5]([#6:7]):2", 
            "RXN_NUM": 43
            },
        "44_Niementowski_quinazoline": {
            "reaction_name": "44_Niementowski_quinazoline", 
            "example_rxn_product": "O=C1NC=Nc2ccccc21", 
            "example_rxn_reactants": ["c1c(C(=O)O)c(N)ccc1", "C(=O)N"],
            "functional_groups": ["anthranilic_acid", "amide"],
            "group_smarts": ["c(-[C&$(C-c1ccccc1)](=[O&D1])-[O&H1]):c-[N&H2]", "[N&!H0&!$(N-N)&!$(N-C=N)&!$(N(-C=O)-C=O)]-[C;H1,$(C-[#6])]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[OH1]):[c:4](-[NH2:5]).[N;!H0;!$(N-N);!$(N-C=N);!$(N(-C=O)-C=O):6]-[C;H1,$(C-[#6]):7]=[OD1]>>[c:4]2:[c:1]-[C:2](=[O:3])-[N:6]-[C:7]=[N:5]-2", 
            "RXN_NUM": 44
            },
        "45_tetrazole_terminal": {
            "reaction_name": "45_tetrazole_terminal", 
            "example_rxn_product": "CC1=NNN=N1", 
            "example_rxn_reactants": ["CC#N"],
            "functional_groups": ["nitrile"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]"],
            "num_reactants": 1, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2]>>[C:1]1=[N:2]-N-N=N-1", 
            "RXN_NUM": 45
            },
        "46_tetrazole_connect_regioisomere_1": {
            "reaction_name": "46_tetrazole_connect_regioisomere_1", 
            "example_rxn_product": "CC1=NN(C)N=N1", 
            "example_rxn_reactants": ["CC#N", "CBr"],
            "functional_groups": ["nitrile", "alkyl_halogen"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&A&!$(C=O)]-[*;#17,#35,#53]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N(-[C:3])-N=N-1", 
            "RXN_NUM": 46
            },
        "47_tetrazole_connect_regioisomere_2": {
            "reaction_name": "47_tetrazole_connect_regioisomere_2", 
            "example_rxn_product": "CC1=NN=NN1C", 
            "example_rxn_reactants": ["CC#N", "CBr"],
            "functional_groups": ["nitrile", "alkyl_halogen"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&A&!$(C=O)]-[*;#17,#35,#53]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[C;A;!$(C=O):3]-[*;#17,#35,#53]>>[C:1]1=[N:2]-N=N-N-1(-[C:3])", 
            "RXN_NUM": 47
            },
        "48_Huisgen_Cu_catalyzed_1_4_subst": {
            "reaction_name": "48_Huisgen_Cu_catalyzed_1_4_subst", 
            "example_rxn_product": "CCN1C=C(C)N=N1", 
            "example_rxn_reactants": ["CC#C", "CCBr"],
            "functional_groups": ["aliphatic_alkyne", "alkyl_halogen_or_alcohol"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[C&H1]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[CH1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N(-[C:3])-N=N-1", 
            "RXN_NUM": 48
            },
        "49_Huisgen_Ru_catalyzed_1_5_subst": {
            "reaction_name": "49_Huisgen_Ru_catalyzed_1_5_subst", 
            "example_rxn_product": "CCN1N=NC=C1C", 
            "example_rxn_reactants": ["CC#C", "CCBr"],
            "functional_groups": ["aliphatic_alkyne", "alkyl_halogen_or_alcohol"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[C&H1]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[CH1:2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1", 
            "RXN_NUM": 49
            },
        "50_Huisgen_disubst_alkyne": {
            "reaction_name": "50_Huisgen_disubst_alkyne", 
            "example_rxn_product": "CCN1N=NC(C)=C1C", 
            "example_rxn_reactants": ["CC#CC", "CCBr"],
            "functional_groups": ["aliphatic_alkyne_w_aro_alkyl_group", "alkyl_halogen_or_alcohol"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[C&H0&$(C-[#6])]", "[C;H1,H2;A;!$(C=O)]-[*;#17,#35,#53,O&H1]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[CH0;$(C-[#6]):2].[C;H1,H2;A;!$(C=O):3]-[*;#17,#35,#53,OH1]>>[C:1]1=[C:2]-N=NN(-[C:3])-1", 
            "RXN_NUM": 50
            },
        "51_1_2_4_triazole_acetohydrazide": {
            "reaction_name": "51_1_2_4_triazole_acetohydrazide", 
            "example_rxn_product": "CC1=NNC(C)=N1", 
            "example_rxn_reactants": ["CC#N", "NNC(=O)C"],
            "functional_groups": ["nitrile", "acetohydrazide"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[N&H2]-[N&H1]-[C&H0&$(C-[#6])&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[NH2:3]-[NH1:4]-[CH0;$(C-[#6]);R0:5]=[OD1]>>[N:2]1-[C:1]=[N:3]-[N:4]-[C:5]=1", 
            "RXN_NUM": 51
            },
        "52_1_2_4_triazole_carboxylic_acid_ester": {
            "reaction_name": "52_1_2_4_triazole_carboxylic_acid_ester", 
            "example_rxn_product": "CC1=NNC(C)=N1", 
            "example_rxn_reactants": ["CC#N", "OC(=O)C"],
            "functional_groups": ["nitrile", "carboxylic_acid_or_extended_esters"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[C&H0&$(C-[#6])&R0](=[O&D1])-[#8;H1,$(O-[C&H3]),$(O-[C&H2]-[C&H3])]"],
            "num_reactants": 2, 
            "reaction_string": "[CH0;$(C-[#6]):1]#[NH0:2].[CH0;$(C-[#6]);R0:5](=[OD1])-[#8;H1,$(O-[CH3]),$(O-[CH2]-[CH3])]>>[N:2]1-[C:1]=N-N-[C:5]=1", 
            "RXN_NUM": 52
            },
        "53_3_nitrile_pyridine": {
            "reaction_name": "53_3_nitrile_pyridine", 
            "example_rxn_product": "Cc1cc(C)c(C#N)c(O)n1", 
            "example_rxn_reactants": ["CC(=O)CC(=O)C"],
            "functional_groups": ["beta_dicarbonyl"],
            "group_smarts": ["[#6&!$([#6](-C=O)-C=O)]-[C&H0](=[O&D1])-[C;H1&!$(C-[*&!#6])&!$(C-C(=O)O),H2]-[C&H0&R0](=[O&D1])-[#6&!$([#6](-C=O)-C=O)]"],
            "num_reactants": 1, 
            "reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5]>>[c:1]1(-[#6:4]):[c:2]:[c:3](-[#6:5]):n:c(-O):c(-C#N):1", 
            "RXN_NUM": 53
            },
        "54_spiro_chromanone": {
            "reaction_name": "54_spiro_chromanone", 
            "example_rxn_product": "O=C1CC2(CCNCC2)Oc2ccccc21", 
            "example_rxn_reactants": ["c1cc(C(=O)C)c(O)cc1", "C1(=O)CCNCC1"],
            "functional_groups": ["2_acetylphenol", "cyclohexanone"],
            "group_smarts": ["c(-[C&$(C-c1ccccc1)](=[O&D1])-[C&H3]):c-[O&H1]", "[C&$(C1-[C&H2]-[C&H2]-[N,C]-[C&H2]-[C&H2]-1)]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[c:1](-[C;$(C-c1ccccc1):2](=[OD1:3])-[CH3:4]):[c:5](-[OH1:6]).[C;$(C1-[CH2]-[CH2]-[N,C]-[CH2]-[CH2]-1):7](=[OD1])>>[O:6]1-[c:5]:[c:1]-[C:2](=[OD1:3])-[C:4]-[C:7]-1", 
            "RXN_NUM": 54
            },
        "55_pyrazole": {
            "reaction_name": "55_pyrazole", 
            "example_rxn_product": "CC1=CC(C)=NN1C", 
            "example_rxn_reactants": ["CC(=O)CC(=O)C", "NNC"],
            "functional_groups": ["beta_dicarbonyl", "hydrazine"],
            "group_smarts": ["[#6&!$([#6](-C=O)-C=O)]-[C&H0](=[O&D1])-[C;H1&!$(C-[*&!#6])&!$(C-C(=O)O),H2]-[C&H0&R0](=[O&D1])-[#6&!$([#6](-C=O)-C=O)]", "[N&H2]-[N&!H0;$(N-[#6]),H2]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;!$([#6](-C=O)-C=O):4]-[CH0:1](=[OD1])-[C;H1&!$(C-[*;!#6])&!$(C-C(=O)O),H2:2]-[CH0;R0:3](=[OD1])-[#6;!$([#6](-C=O)-C=O):5].[NH2:6]-[N;!H0;$(N-[#6]),H2:7]>>[C:1]1(-[#6:4])-[C:2]=[C:3](-[#6:5])-[N:7]-[N:6]=1", 
            "RXN_NUM": 55
            },
        "56_phthalazinone": {
            "reaction_name": "56_phthalazinone", 
            "example_rxn_product": "CC1=NN(C)C(=O)c2ccccc21", 
            "example_rxn_reactants": ["c1cc(C(=O)O)c(C(=O)C)cc1", "NNC"],
            "functional_groups": ["phthalazinone_precursor", "restricted_hydrazine"],
            "group_smarts": ["[c&r6](-[C&$(C=O)]-[O&H1]):[c&r6]-[C;H1,$(C-C)]=[O&D1]", "[N&H2]-[N&H1&$(N-[#6])&!$(NC=[O,S,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[c;r6:1](-[C;$(C=O):6]-[OH1]):[c;r6:2]-[C;H1,$(C-C):3]=[OD1].[NH2:4]-[NH1;$(N-[#6]);!$(NC=[O,S,N]):5]>>[c:1]1:[c:2]-[C:3]=[N:4]-[N:5]-[C:6]-1", 
            "RXN_NUM": 56
            },
        "57_Paal_Knorr_pyrrole": {
            "reaction_name": "57_Paal_Knorr_pyrrole", 
            "example_rxn_product": "CC1=CC=C(C)N1C", 
            "example_rxn_reactants": ["CC(=O)CCC(=O)C", "NC"],
            "functional_groups": ["1_4_dione", "primary_amine"],
            "group_smarts": ["[#6]-[C&R0](=[O&D1])-[C;H1,H2]-[C;H1,H2]-C(=[O&D1])-[#6]", "[N&H2&$(N-[C,N])&!$(NC=[O,S,N])&!$(N(-,:[#6])[#6])&!$(N~N~N)]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:5]-[C;R0:1](=[OD1])-[C;H1,H2:2]-[C;H1,H2:3]-[C:4](=[OD1])-[#6:6].[NH2;$(N-[C,N]);!$(NC=[O,S,N]);!$(N([#6])[#6]);!$(N~N~N):7]>>[C:1]1(-[#6:5])=[C:2]-[C:3]=[C:4](-[#6:6])-[N:7]-1", 
            "RXN_NUM": 57
            },
        "58_triaryl_imidazole": {
            "reaction_name": "58_triaryl_imidazole", 
            "example_rxn_product": "c1ccc(C2=NC(c3ccccc3)=C(c3ccccc3)N2)cc1", 
            "example_rxn_reactants": ["c1ccccc1C(=O)C(=O)c1ccccc1", "c1ccccc1C(=O)"],
            "functional_groups": ["benzil_or_benzoin", "aryl_aldehyde"],
            "group_smarts": ["[C&$(C-c1ccccc1)](=[O&D1])-[C&D3&$(C-c1ccccc1)]~[O;D1,H1]", "c-[C&H1&R0]=[O&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[C;$(C-c1ccccc1):1](=[OD1])-[C;D3;$(C-c1ccccc1):2]~[O;D1,H1].[CH1;$(C-c):3]=[OD1]>>[C:1]1-N=[C:3]-[NH1]-[C:2]=1", 
            "RXN_NUM": 58
            },
        "59_Fischer_indole": {
            "reaction_name": "59_Fischer_indole", 
            "example_rxn_product": "CC1=C(C)c2ccccc2N1", 
            "example_rxn_reactants": ["c1ccccc1NN", "CCC(=O)C"],
            "functional_groups": ["phenylhydrazine", "ketone"],
            "group_smarts": ["[N&H1&$(N-c1ccccc1)](-[N&H2])-c:[c&H1]", "[C&$(C(-,:[#6])[#6])](=[O&D1])-[C&H2&$(C(-,:[#6])[#6])&!$(C(-,:C=O)C=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[NH1;$(N-c1ccccc1):1](-[NH2])-[c:5]:[cH1:4].[C;$(C([#6])[#6]):2](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O):3]>>[C:5]1-[N:1]-[C:2]=[C:3]-[C:4]:1", 
            "RXN_NUM": 59
            },
        "60_Friedlaender_chinoline": {
            "reaction_name": "60_Friedlaender_chinoline", 
            "example_rxn_product": "CC1=Cc2ccccc2-nc1C", 
            "example_rxn_reactants": ["c1cccc(C=O)c1N", "CCC(=O)C"],
            "functional_groups": ["ortho_aminobenzaldehyde", "ketone"],
            "group_smarts": ["[N&H2&$(N-c1ccccc1)]-c:c-[C&H1]=[O&D1]", "[C&$(C(-,:[#6])[#6])](=[O&D1])-[C&H2&$(C(-,:[#6])[#6])&!$(C(-,:C=O)C=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[NH2;$(N-c1ccccc1):1]-[c:2]:[c:3]-[CH1:4]=[OD1].[C;$(C([#6])[#6]):6](=[OD1])-[CH2;$(C([#6])[#6]);!$(C(C=O)C=O):5]>>[N:1]1-[c:2]:[c:3]-[C:4]=[C:5]-[C:6]:1", 
            "RXN_NUM": 60
            },
        "61_benzofuran": {
            "reaction_name": "61_benzofuran", 
            "example_rxn_product": "CC1=Cc2ccccc2O1", 
            "example_rxn_reactants": ["c1cc(I)c(O)cc1", "CC#C"],
            "functional_groups": ["ortho_halo_phenol", "alkyne"],
            "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[O&H1]", "[C&H1]#[C&$(C-[#6])]"],
            "num_reactants": 2, 
            "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[OH1:3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[O:3]-[C:4]=[C:5]-1", 
            "RXN_NUM": 61
            },
        "62_benzothiophene": {
            "reaction_name": "62_benzothiophene", 
            "example_rxn_product": "CC1=Cc2ccccc2S1", 
            "example_rxn_reactants": ["c1cc(I)c(SC)cc1", "CC#C"],
            "functional_groups": ["aminobenzenethiol", "alkyne"],
            "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[S&D2]-[C&H3]", "[C&H1]#[C&$(C-[#6])]"],
            "num_reactants": 2, 
            "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[SD2:3]-[CH3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[S:3]-[C:4]=[C:5]-1", 
            "RXN_NUM": 62
            },
        "63_indole": {
            "reaction_name": "63_indole", 
            "example_rxn_product": "CC1=Cc2ccccc2N1", 
            "example_rxn_reactants": ["c1cc(I)c(N)cc1", "CC#C"],
            "functional_groups": ["ortho_halo_thioanizole", "alkyne"],
            "group_smarts": ["[*;Br,I;$(*c1ccccc1)]-c:c-[N&H2]", "[C&H1]#[C&$(C-[#6])]"],
            "num_reactants": 2, 
            "reaction_string": "[*;Br,I;$(*c1ccccc1)]-[c:1]:[c:2]-[NH2:3].[CH1:5]#[C;$(C-[#6]):4]>>[c:1]1:[c:2]-[N:3]-[C:4]=[C:5]-1", 
            "RXN_NUM": 63
            },
        "64_oxadiazole": {
            "reaction_name": "64_oxadiazole", 
            "example_rxn_product": "Cc1noc(C)n1", 
            "example_rxn_reactants": ["CC#N", "CC(=O)O"],
            "functional_groups": ["nitrile", "carboxylic_acid"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[#6]-[C&R0](=[O&D1])-[O&H1]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:6][C:5]#[#7;D1:4].[#6:1][C:2](=[OD1:3])[OH1]>>[#6:6][c:5]1[n:4][o:3][c:2]([#6:1])n1", 
            "RXN_NUM": 64
            },
        "65_Williamson_ether": {
            "reaction_name": "65_Williamson_ether", 
            "example_rxn_product": "CCOCC", 
            "example_rxn_reactants": ["CCO", "CCBr"],
            "functional_groups": ["alcohol", "alkyl_halide"],
            "group_smarts": ["[#6&$([#6]~[#6])&!$([#6]=O)][#8&H1]", "[Cl,Br,I][#6&H2&$([#6]~[#6])]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;$([#6]~[#6]);!$([#6]=O):2][#8;H1:3].[Cl,Br,I][#6;H2;$([#6]~[#6]):4]>>[CH2:4][O:3][#6:2]", 
            "RXN_NUM": 65
            },
        "66_reductive_amination": {
            "reaction_name": "66_reductive_amination", 
            "example_rxn_product": "CCNC", 
            "example_rxn_reactants": ["CC(=O)", "NC"],
            "functional_groups": ["aldehyde_or_ketone", "primary_or_secondary_amine"],
            "group_smarts": ["[#6]-[C;H1,$([C&H0](-[#6])[#6])]=[O&D1]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:4]-[C;H1,$([CH0](-[#6])[#6]):1]=[OD1].[N;H2,$([NH1;D2](C)C);!$(N-[#6]=[*]):3]-[C:5]>>[#6:4][C:1]-[N:3]-[C:5]", 
            "RXN_NUM": 66
            },
        "67_Suzuki": {
            "reaction_name": "67_Suzuki", 
            "example_rxn_product": "c1ccc(-c2ccccc2)cc1", 
            "example_rxn_reactants": ["c1ccccc1B(O)O", "c1ccccc1Br"],
            "functional_groups": ["boronic_acid", "aryl_halide"],
            "group_smarts": ["[#6&H0&D3&$([#6](~[#6])~[#6])]B(-,:O)O", "[#6&H0&D3&$([#6](~[#6])~[#6])][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;H0;D3;$([#6](~[#6])~[#6]):1]B(O)O.[#6;H0;D3;$([#6](~[#6])~[#6]):2][Cl,Br,I]>>[#6:2][#6:1]", 
            "RXN_NUM": 67
            },
        "68_piperidine_indole": {
            "reaction_name": "68_piperidine_indole", 
            "example_rxn_product": "C1=C(c2c[nH]c3ccccc23)CCNC1", 
            "example_rxn_reactants": ["c1cccc2c1C=CN2", "C1CC(=O)CCN1"],
            "functional_groups": ["indole", "4_piperidone"],
            "group_smarts": ["[c&H1]1:c:c:[c&H1]:c2:[n&H1]:c:[c&H1]:c:1:2", "O=C1[#6&H2][#6&H2][N][#6&H2][#6&H2]1"],
            "num_reactants": 2, 
            "reaction_string": "[c;H1:3]1:[c:4]:[c:5]:[c;H1:6]:[c:7]2:[nH:8]:[c:9]:[c;H1:1]:[c:2]:1:2.O=[C:10]1[#6;H2:11][#6;H2:12][N][#6;H2][#6;H2]1>>[#6;H2:12]3[#6;H1:11]=[C:10]([c:1]1:[c:9]:[n:8]:[c:7]2:[c:6]:[c:5]:[c:4]:[c:3]:[c:2]:1:2)[#6;H2:15][#6;H2:14][N:13]3", 
            "RXN_NUM": 68
            },
        "69_Negishi": {
            "reaction_name": "69_Negishi", 
            "example_rxn_product": "CCCC", 
            "example_rxn_reactants": ["CCBr", "CCBr"],
            "functional_groups": ["halide_type_3", "halide_type_3"],
            "group_smarts": ["[#6&$([#6]~[#6])&!$([#6]~[S,N,O,P])][Cl,Br,I]", "[#6&$([#6]~[#6])&!$([#6]~[S,N,O,P])][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):1][Cl,Br,I].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]~[S,N,O,P]):2]>>[#6:2][#6:1]", 
            "RXN_NUM": 69
            },
        "70_Mitsunobu_imide": {
            "reaction_name": "70_Mitsunobu_imide", 
            "example_rxn_product": "CC(=O)N(C(C)=O)C(C)C", 
            "example_rxn_reactants": ["CC(O)C", "CC(=O)NC(=O)C"],
            "functional_groups": ["primary_or_secondary_alcohol", "imide"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[N&H1&$(N(-,:C=O)C=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[NH1;$(N(C=O)C=O):2]>>[C:1][N:2]", 
            "RXN_NUM": 70
            },
        "71_Mitsunobu_phenole": {
            "reaction_name": "71_Mitsunobu_phenole", 
            "example_rxn_product": "CC(C)Oc1ccccc1", 
            "example_rxn_reactants": ["CC(O)C", "c1ccccc1O"],
            "functional_groups": ["primary_or_secondary_alcohol", "phenole"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[O&H1&$(Oc1ccccc1)]"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[OH1;$(Oc1ccccc1):2]>>[C:1][O:2]", 
            "RXN_NUM": 71
            },
        "72_Mitsunobu_sulfonamide": {
            "reaction_name": "72_Mitsunobu_sulfonamide", 
            "example_rxn_product": "CC(C)N(C)S(C)(=O)=O", 
            "example_rxn_reactants": ["CC(O)C", "CNS(=O)(=O)C"],
            "functional_groups": ["primary_or_secondary_alcohol", "sulfonamide"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[N&H1&$(N(-,:[#6])S(=O)=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[NH1;$(N([#6])S(=O)=O):2]>>[C:1][N:2]", 
            "RXN_NUM": 72
            },
        "73_Mitsunobu_tetrazole_1": {
            "reaction_name": "73_Mitsunobu_tetrazole_1", 
            "example_rxn_product": "CC(C)n1cnnn1", 
            "example_rxn_reactants": ["CC(O)C", "N1=NNC=N1"],
            "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_1"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7&H1]1~[#7]~[#7]~[#7]~[#6]~1"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[C:1][#7:2]1:[#7:3]:[#7:4]:[#7:5]:[#6:6]:1", 
            "RXN_NUM": 73
            },
        "74_Mitsunobu_tetrazole_2": {
            "reaction_name": "74_Mitsunobu_tetrazole_2", 
            "example_rxn_product": "CC(C)n1ncnn1", 
            "example_rxn_reactants": ["CC(O)C", "N1=NNC=N1"],
            "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_1"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7&H1]1~[#7]~[#7]~[#7]~[#6]~1"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7H1:2]1~[#7:3]~[#7:4]~[#7:5]~[#6:6]~1>>[#7H0:2]1:[#7:3]:[#7H0:4]([C:1]):[#7:5]:[#6:6]:1", 
            "RXN_NUM": 74
            },
        "75_Mitsunobu_tetrazole_3": {
            "reaction_name": "75_Mitsunobu_tetrazole_3", 
            "example_rxn_product": "CC(C)n1cnnn1", 
            "example_rxn_reactants": ["CC(O)C", "N1N=NC=N1"],
            "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_2"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7]1~[#7]~[#7&H1]~[#7]~[#6]~1"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[C:1][#7H0:2]1:[#7:3]:[#7H0:4]:[#7:5]:[#6:6]:1", 
            "RXN_NUM": 75
            },
        "76_Mitsunobu_tetrazole_4": {
            "reaction_name": "76_Mitsunobu_tetrazole_4", 
            "example_rxn_product": "CC(C)n1ncnn1", 
            "example_rxn_reactants": ["CC(O)C", "N1N=NC=N1"],
            "functional_groups": ["primary_or_secondary_alcohol", "tetrazole_2"],
            "group_smarts": ["[C;H1&$(C(-,:[#6])[#6]),H2&$(C[#6])][O&H1]", "[#7]1~[#7]~[#7&H1]~[#7]~[#6]~1"],
            "num_reactants": 2, 
            "reaction_string": "[C;H1&$(C([#6])[#6]),H2&$(C[#6]):1][OH1].[#7:2]1~[#7:3]~[#7H1:4]~[#7:5]~[#6:6]~1>>[#7:2]1:[#7:3]:[#7:4]([C:1]):[#7:5]:[#6:6]:1", 
            "RXN_NUM": 76
            },
        "77_Heck_terminal_vinyl": {
            "reaction_name": "77_Heck_terminal_vinyl", 
            "example_rxn_product": "C(=C/c1ccccc1)\\c1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1C=C", "c1ccccc1Br"],
            "functional_groups": ["alkene", "halide_type_2"],
            "group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6&H1]=[#6&H2]", "[#6;$([#6]=[#6]),$(c:c)][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6;H1:2]=[#6;H2:1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4]/[#6:1]=[#6:2]/[#6:3]", 
            "RXN_NUM": 77
            },
        "78_Heck_non_terminal_vinyl": {
            "reaction_name": "78_Heck_non_terminal_vinyl", 
            "example_rxn_product": "CC(=C(C)c1ccccc1)c1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1C(C)=CC", "c1ccccc1Br"],
            "functional_groups": ["terminal_alkene", "halide_type_2"],
            "group_smarts": ["[#6;c,$(C(=O)O),$(C#N)][#6](-,:[#6])=[#6&H1&$([#6][#6])]", "[#6;$([#6]=[#6]),$(c:c)][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;c,$(C(=O)O),$(C#N):3][#6:2]([#6:5])=[#6;H1;$([#6][#6]):1].[#6;$([#6]=[#6]),$(c:c):4][Cl,Br,I]>>[#6:4][#6;H0:1]=[#6:2]([#6:5])[#6:3]", 
            "RXN_NUM": 78
            },
        "79_Stille": {
            "reaction_name": "79_Stille", 
            "example_rxn_product": "c1ccc(-c2ccccc2)cc1", 
            "example_rxn_reactants": ["c1ccccc1Br", "c1ccccc1Br"],
            "functional_groups": ["aryl_or_vinyl_halide", "aryl_halide"],
            "group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[#6&H0&D3&$([#6](~[#6])~[#6])][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[Cl,Br,I][c:2]>>[c:2][#6:1]", 
            "RXN_NUM": 79
            },
        "80_Grignard_carbonyl": {
            "reaction_name": "80_Grignard_carbonyl", 
            "example_rxn_product": "CCC(C)=O", 
            "example_rxn_reactants": ["CC#N", "CCBr"],
            "functional_groups": ["nitrile", "halide_type_1"],
            "group_smarts": ["[C&H0&$(C-[#6])]#[N&H0]", "[Cl,Br,I][#6&$([#6]~[#6])&!$([#6](-,:[Cl,Br,I])[Cl,Br,I])&!$([#6]=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:1][C:2]#[#7;D1].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):3]>>[#6:1][C:2](=O)[#6:3]", 
            "RXN_NUM": 80
            },
        "81_Grignard_alcohol": {
            "reaction_name": "81_Grignard_alcohol", 
            "example_rxn_product": "CCC(C)(C)O", 
            "example_rxn_reactants": ["CC(=O)C", "CCBr"],
            "functional_groups": ["aldehyde_or_ketone_restricted", "halide_type_1"],
            "group_smarts": ["[#6][C;H1,$(C(-,:[#6])[#6])]=[O&D1]", "[Cl,Br,I][#6&$([#6]~[#6])&!$([#6](-,:[Cl,Br,I])[Cl,Br,I])&!$([#6]=O)]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:1][C;H1,$([C]([#6])[#6]):2]=[OD1:3].[Cl,Br,I][#6;$([#6]~[#6]);!$([#6]([Cl,Br,I])[Cl,Br,I]);!$([#6]=O):4]>>[C:1][#6:2]([OH1:3])[#6:4]", 
            "RXN_NUM": 81
            },
        "82_Sonogashira": {
            "reaction_name": "82_Sonogashira", 
            "example_rxn_product": "CC#Cc1ccccc1", 
            "example_rxn_reactants": ["c1cc(Br)ccc1", "CC#C"],
            "functional_groups": ["aryl_or_vinyl_halide", "terminal_alkyne"],
            "group_smarts": ["[#6;$(C=C-[#6]),$(c:c)][Br,I]", "[C&H1&$(C#CC)]"],
            "num_reactants": 2, 
            "reaction_string": "[#6;$(C=C-[#6]),$(c:c):1][Br,I].[CH1;$(C#CC):2]>>[#6:1][C:2]", 
            "RXN_NUM": 82
            },
        "83_Schotten_Baumann_amide": {
            "reaction_name": "83_Schotten_Baumann_amide", 
            "example_rxn_product": "CCNC(C)=O", 
            "example_rxn_reactants": ["CC(=O)O", "NCC"],
            "functional_groups": ["carboxylic_acid", "primary_or_secondary_amine_C_aryl_alkyl"],
            "group_smarts": ["[#6]-[C&R0](=[O&D1])-[O&H1]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[C;$(C=O):1][OH1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[C:1][N+0:2]", 
            "RXN_NUM": 83
            },
        "84_sulfon_amide": {
            "reaction_name": "84_sulfon_amide", 
            "example_rxn_product": "CCNS(C)(=O)=O", 
            "example_rxn_reactants": ["CS(=O)(=O)O", "NCC"],
            "functional_groups": ["sulfonic_acid", "primary_or_secondary_amine"],
            "group_smarts": ["[S&$(S(=O)(=O)[C,N])]O", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[S;$(S(=O)(=O)[C,N]):1][O].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[S:1][N+0:2]", 
            "RXN_NUM": 84
            },
        "85_N_arylation_heterocycles": {
            "reaction_name": "85_N_arylation_heterocycles", 
            "example_rxn_product": "c1ccc(n2ccnc2)cc1", 
            "example_rxn_reactants": ["c1ccccc1B(O)O", "N1C=NC=C1"],
            "functional_groups": ["aryl_boronic_acid", "5_mem_aryl_w_NH_max2N"],
            "group_smarts": ["cB(-,:O)O", "[n&H1&+0&r5&!$(n[#6]=[O,S,N])&!$(n~n~n)&!$(n~n~c~n)&!$(n~c~n~n)]"],
            "num_reactants": 2, 
            "reaction_string": "[c:1]B(O)O.[nH1;+0;r5;!$(n[#6]=[O,S,N]);!$(n~n~n);!$(n~n~c~n);!$(n~c~n~n):2]>>[c:1][n:2]", 
            "RXN_NUM": 85
            },
        "86_Wittig": {
            "reaction_name": "86_Wittig", 
            "example_rxn_product": "CC=C(C)C", 
            "example_rxn_reactants": ["CC(=O)C", "BrCC"],
            "functional_groups": ["aldehyde_or_ketone_flexible", "primary_or_secondary_halide"],
            "group_smarts": ["[#6]-[C;H1,$([C&H0](-[#6])[#6]);!$(CC=O)]=[O&D1]", "[Cl,Br,I][C&H2&$(C-[#6])&!$(CC[I,Br])&!$(CCO[C&H3])]"],
            "num_reactants": 2, 
            "reaction_string": "[#6:3]-[C;H1,$([CH0](-[#6])[#6]);!$(CC=O):1]=[OD1].[Cl,Br,I][C;H2;$(C-[#6]);!$(CC[I,Br]);!$(CCO[CH3]):2]>>[C:3][C:1]=[C:2]", 
            "RXN_NUM": 86
            },
        "87_Buchwald_Hartwig": {
            "reaction_name": "87_Buchwald_Hartwig", 
            "example_rxn_product": "CN(C)c1ccccc1", 
            "example_rxn_reactants": ["c1ccccc1Br", "CNC"],
            "functional_groups": ["aryl_halide_nitrogen_optional", "primary_or_secondary_amine_aro_optional"],
            "group_smarts": ["[Cl,Br,I][c&$(c1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1)]", "[N;$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N]),H2&$(Nc1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1)]"],
            "num_reactants": 2, 
            "reaction_string": "[Cl,Br,I][c;$(c1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1):1].[N;$(NC)&!$(N=*)&!$([N-])&!$(N#*)&!$([ND3])&!$([ND4])&!$(N[c,O])&!$(N[C,S]=[S,O,N]),H2&$(Nc1:[c,n]:[c,n]:[c,n]:[c,n]:[c,n]:1):2]>>[c:1][N:2]", 
            "RXN_NUM": 87
            },
        "88_imidazole": {
            "reaction_name": "88_imidazole", 
            "example_rxn_product": "CNC1=NC(C)=C(C)N1", 
            "example_rxn_reactants": ["CC(=O)C(Br)C", "N=C(N)NC"],
            "functional_groups": ["alpha_halo_ketone", "amidine"],
            "group_smarts": ["[C&$(C(-,:[#6])[#6&!$([#6]Br)])](=[O&D1])[C&H1&$(C(-,:[#6])[#6])]Br", "[#7&H2][C&$(C(=N)(-,:N)[c,#7])]=[#7&H1&D1]"],
            "num_reactants": 2, 
            "reaction_string": "[C;$(C([#6])[#6;!$([#6]Br)]):4](=[OD1])[CH;$(C([#6])[#6]):5]Br.[#7;H2:3][C;$(C(=N)(N)[c,#7]):2]=[#7;H1;D1:1]>>[C:4]1=[CH0:5][NH:3][C:2]=[N:1]1", 
            "RXN_NUM": 88
            },
        "89_decarboxylative_coupling": {
            "reaction_name": "89_decarboxylative_coupling", 
            "example_rxn_product": "O=[N+]([O-])c1ccccc1c1ccccc1", 
            "example_rxn_reactants": ["c1c(C(=O)O)c([N+](=O)[O-])ccc1", "c1ccccc1Br"],
            "functional_groups": ["aryl_carboxylic_acid", "aryl_halide_flexible"],
            "group_smarts": ["[c&$(c1[c&$(c[C,S,N](=[O&D1])[*&R0])]cccc1)][C&$(C(=O)[O&H1])]", "[c&$(c1aaccc1)][Cl,Br,I]"],
            "num_reactants": 2, 
            "reaction_string": "[c;$(c1[c;$(c[C,S,N](=[OD1])[*;R0])]cccc1):1][C;$(C(=O)[O;H1])].[c;$(c1aaccc1):2][Cl,Br,I]>>[c:1][c:2]", 
            "RXN_NUM": 89
            },
        "90_heteroaromatic_nuc_sub": {
            "reaction_name": "90_heteroaromatic_nuc_sub", 
            "example_rxn_product": "CNc1ccccn1", 
            "example_rxn_reactants": ["c1cnc(F)cc1", "CN"],
            "functional_groups": ["pyridine_pyrimidine_triazine", "primary_or_secondary_amine"],
            "group_smarts": ["[c&!$(c1ccccc1)&$(c1[n,c]c[n,c]c[n,c]1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[c;!$(c1ccccc1);$(c1[n,c]c[n,c]c[n,c]1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
            "RXN_NUM": 90
            },
        "91_nucl_sub_aromatic_ortho_nitro": {
            "reaction_name": "91_nucl_sub_aromatic_ortho_nitro", 
            "example_rxn_product": "CNc1ccccc1[N+](=O)[O-]", 
            "example_rxn_reactants": ["c1c([N+](=O)[O-])c(F)ccc1", "CN"],
            "functional_groups": ["ortho_halo_nitrobenzene", "primary_or_secondary_amine"],
            "group_smarts": ["[c&$(c1c(-,:N(~O)~O)cccc1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[c;$(c1c(N(~O)~O)cccc1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
            "RXN_NUM": 91
            },
        "92_nucl_sub_aromatic_para_nitro": {
            "reaction_name": "92_nucl_sub_aromatic_para_nitro", 
            "example_rxn_product": "CNc1ccc([N+](=O)[O-])cc1", 
            "example_rxn_reactants": ["c1c(F)ccc([N+](=O)[O-])c1", "CN"],
            "functional_groups": ["para_halo_nitrobenzene", "primary_or_secondary_amine"],
            "group_smarts": ["[c&$(c1ccc(-,:N(~O)~O)cc1)][Cl,F]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[c,O])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[c;$(c1ccc(N(~O)~O)cc1):1][Cl,F].[N;$(NC);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[c,O]);!$(N[C,S]=[S,O,N]):2]>>[c:1][N:2]", 
            "RXN_NUM": 92
            },
        "93_urea": {
            "reaction_name": "93_urea", 
            "example_rxn_product": "CNC(=O)NC", 
            "example_rxn_reactants": ["CN=C=O", "CN"],
            "functional_groups": ["isocyanate", "primary_or_secondary_amine_C_aryl_alkyl"],
            "group_smarts": ["[N&$(N-[#6])]=[C&$(C=O)]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[N;$(N-[#6]):3]=[C;$(C=O):1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[N:3]-[C:1]-[N+0:2]", 
            "RXN_NUM": 93
            },
        "94_thiourea": {
            "reaction_name": "94_thiourea", 
            "example_rxn_product": "CNC(=S)NC", 
            "example_rxn_reactants": ["CN=C=S", "CN"],
            "functional_groups": ["isothiocyanate", "primary_or_secondary_amine_C_aryl_alkyl"],
            "group_smarts": ["[N&$(N-[#6])]=[C&$(C=S)]", "[N&$(NC)&!$(N=*)&!$([N&-])&!$(N#*)&!$([N&D3])&!$([N&D4])&!$(N[O,N])&!$(N[C,S]=[S,O,N])]"],
            "num_reactants": 2, 
            "reaction_string": "[N;$(N-[#6]):3]=[C;$(C=S):1].[N;$(N[#6]);!$(N=*);!$([N-]);!$(N#*);!$([ND3]);!$([ND4]);!$(N[O,N]);!$(N[C,S]=[S,O,N]):2]>>[N:3]-[C:1]-[N+0:2]", 
            "RXN_NUM": 94
            }
    }
def dothing(file):
    zinc_list = []
    smile_list = []


    with open(file, "r") as f:
        for line in f.readlines():
        

            line = line.replace("\n","")
            parts = line.split("\t")
            if len(parts) != 2:
                parts = line.split("    ")
                if len(parts) != 2:
                    parts = line.split(" ")
                    if len(parts) != 2:
                        print("Fail because line could split in {}".format(file))
                        print(line)
                        print("")
                        raise Exception("Fail because line could split in {}".format(file))
            smile = parts[0]
            zinc_id = parts[1]

            zinc_list.append(zinc_id)
            smile_list.append(smile)
       

    if len(smile_list)<50 or len(zinc_list)<50:
        print("FAIL NO LIGANDS!!!!!!!")
        raise Exception("FAIL NO LIGANDS!!!!!!!")
    job_input = [[smile_list[i], zinc_list[i]]  for i in range(0, len(smile_list))]
        
    output = mp.multi_threading(job_input, num_processors,  dothing_to_mol)

    output = [x for x in output if x is not None]
    if len(output)==0:
        return None

    else:
        for i in output:
            if i is None:
                continue
            else:
                print(i)

    return file
    #
     
def dothing_to_mol(smile,zinc_id):       
    mol = Chem.MolFromSmiles(smile)
    mol = Chem.AddHs(mol) 
    Chem.SanitizeMol(mol)
    
    return [zinc_id, [smile,zinc_id, mol]]


def get_mols(file_name):

    job_input = [] 
    # counter = 0
    with open(file_name, "r") as f:

        for line in f.readlines():
            
            # # FOR DEBUGGING
            # counter= counter + 1
            # if counter >100:
            #     break

            line = line.replace("\n","")
            parts = line.split("\t")
            if len(parts) != 2:
                parts = line.split("    ")
                if len(parts) != 2:
                    parts = line.split(" ")
                if len(parts) != 2:
                    print("Fail because line could split in {}".format(file_name))
                    print(line)
                    print("")
                    raise Exception("Fail because line could split in {}".format(file))

            # counter = counter +1
            job_input.append((parts[0], parts[1]))
            continue
    print("Multithread testing: ", file_name)
    print("      len multithread:", len(job_input))
    # job_input = [[smile_list[i], zinc_list[i]] for i in range(0, len(smile_list))]
    output = mp.multi_threading(job_input, num_processors,  dothing_to_mol)

    mol_dic = {}
    for x in output:
        mol_dic[x[0]] = x[1]

    return mol_dic

##############################
def conduct_reaction_one(mol_set, rxn, sub, substructure_from_rxn):
    mol = mol_set[2]

    if mol.HasSubstructMatch(sub) is False:
        mol = Chem.RemoveHs(mol)   
        if mol.HasSubstructMatch(sub) is False: 
            return ["Missing", mol_set]
    if mol.HasSubstructMatch(substructure_from_rxn) is False:
        mol = Chem.RemoveHs(mol)   
        if mol.HasSubstructMatch(substructure_from_rxn) is False: 
            return ["Missing", mol_set]

    try:
        rxn.RunReactants((mol,))[0][0]
        return  [True, mol_set]
    except:
        return [False, mol_set]

def conduct_reaction_two_mol2control(mol_set, mol_2, rxn, sub_1, substructure_from_rxn):

    mol_1 = mol_set[2]
    if mol_1.HasSubstructMatch(sub_1) is False:
        mol_1 = Chem.RemoveHs(mol_1)   
        if mol_1.HasSubstructMatch(sub_1) is False: 
            mol_1 = Chem.AddHs(mol_1)   
            if mol_1.HasSubstructMatch(sub_1) is False: 
                return ["Missing", mol_set]
    if mol_1.HasSubstructMatch(substructure_from_rxn) is False:
        mol_1 = Chem.RemoveHs(mol_1)   
        if mol_1.HasSubstructMatch(substructure_from_rxn) is False: 
            mol_1 = Chem.AddHs(mol_1)   
            if mol_1.HasSubstructMatch(substructure_from_rxn) is False: 
                return ["Missing", mol_set]
    try:
        rxn.RunReactants((mol_1, mol_2))[0][0]
        return [True, mol_set]
    except:
        try:
            mol_2 = Chem.AddHs(mol_2)
            rxn.RunReactants((mol_1,mol_2))[0][0]
            return [True, mol_set]
        except:
            return [False, mol_set]
       
def conduct_reaction_two_mol1control(mol_set, mol_1, rxn, sub_2, substructure_from_rxn):
    mol_2 = mol_set[2]

    if mol_2.HasSubstructMatch(sub_2) is False:
        mol_2 = Chem.RemoveHs(mol_2)   
        if mol_2.HasSubstructMatch(sub_2) is False: 
            return ["Missing", mol_set]
    if mol_2.HasSubstructMatch(substructure_from_rxn) is False:
        mol_2 = Chem.RemoveHs(mol_2)   
        if mol_2.HasSubstructMatch(substructure_from_rxn) is False: 
            return ["Missing", mol_set]
            
    try:
        rxn.RunReactants((mol_1, mol_2))[0][0]
        return [True, mol_set]
    except:
        try:
            mol_2 = Chem.AddHs(mol_2)
            rxn.RunReactants((mol_1,mol_2))[0][0]
            return [True, mol_set]
        except:
            return [False, mol_set]

def write_to_badmol_library(missing_substructure,failed_reaction, output_folder, functional_group_name):
 

    # missing_substructure
    missing_sub_folder = output_folder + "missing_sub/"
    if os.path.isdir(missing_sub_folder) is False:
        os.makedirs(missing_sub_folder)
    missing_sub_file = missing_sub_folder + functional_group_name + ".smi"
    printout = ""
    for missing_mol in missing_substructure:
        temp_list = [missing_mol[1][0],missing_mol[1][1]]
        mol_info = "\t".join(temp_list)
        printout = printout + mol_info + "\n"
    if os.path.exists(missing_sub_file) is True:
        with open(missing_sub_file, "a") as f:
            f.write(printout) 
    else:
        with open(missing_sub_file, "w") as f:
            f.write(printout) 

    # failed_reaction
    printout = ""
    failed_reaction_folder = output_folder + "failed_reaction/"
    if os.path.isdir(failed_reaction_folder) is False:
        os.makedirs(failed_reaction_folder)
    failed_reaction_file = failed_reaction_folder + functional_group_name + ".smi"

    for failed_mol in failed_reaction:
        temp_list = [failed_mol[1][0],failed_mol[1][1]]
        mol_info = "\t".join(temp_list)
        printout = printout + mol_info + "\n"
        
    if os.path.exists(failed_reaction_file) is True:
        with open(failed_reaction_file, "a") as f:
            f.write(printout) 
    else:
        with open(failed_reaction_file, "w") as f:
            f.write(printout) 


def write_to_goodmol_library(mols_dict, final_output_folder, functional_group_name):
 

    # missing_substructure
    final_name = final_output_folder +functional_group_name + ".smi"

    printout = ""
    for key in list(mols_dict.keys()):
        temp = [mols_dict[key][0],mols_dict[key][1]]
        printout = printout + "\t".join(temp) + "\n"

    with open(missing_sub_file, "w") as f:
        f.write(printout) 

def get_mols_dict_from_pickle(file_path):

    with open(file_path, 'rb') as handle:
        mols_dict = pickle.load(handle)
    return mols_dict

def write_pickle_to_file(file_path, obj):
    with open(file_path, 'wb') as handle:
        pickle.dump(obj, handle, protocol=pickle.HIGHEST_PROTOCOL)
        

def write_final_outputs(out_file, pickle_file):
    mols_dict = get_mols_dict_from_pickle(pickle_file)
    
    printout = ""
    with open(out_file, "w") as f:
        f.write(printout)

    with open(out_file, "a") as f:
        for zinc_id in mols_dict:
            printout = ""
            temp = [mols_dict[zinc_id][0], mols_dict[zinc_id][0]]
            printout = printout + "\t".join(temp) + "\n"
            f.write(printout)
            printout = ""
    mols_dict = None

def check_id_in_list(zinc_id, list_to_remove):
    """
    if in list return None (will be excluded)
    if NOT IN LIST RETURN zinc_id
    """
    if zinc_id in list_to_remove:
        return None
    else:
        return zinc_id

def run_post_multithread(output, functional_group, output_folder, modified_pickle_folder):
    """
    if in list return None (will be excluded)
    if NOT IN LIST RETURN zinc_id
    """
    missing_substructure = [x for x in output if x[0]=="Missing"]
    failed_reaction = [x for x in output if x[0] is False]
    passed_reaction = [x[1] for x in output if x[0] is True]
    output = []
    print("            {} ligands are missing_substructure.".format(len(missing_substructure)))
    print("            {} ligands failed reaction.".format(len(failed_reaction)))
    print("            {} ligands which PASSED Everything!.".format(len(passed_reaction)))

    print("     Writing bad mols to file")

    # write the failures to a bad mol library
    write_to_badmol_library(missing_substructure,failed_reaction, output_folder, functional_group)
    missing_substructure = []
    failed_reaction = []
    
    
    print("     Making new mol_dict without bad mols")
    if len(passed_reaction)!=0:
        print("example of passed_reaction:  ", passed_reaction[0])
    mols_dict = {}
    for x in passed_reaction:
        mols_dict[x[1]] = x
    
    print("     Finished making modified mols_dict")
    # Repickle the mols_dict folder to modified.
    temp_pickle_name = modified_pickle_folder + functional_group + "_pickle"
    print("     Pickle modified mols_dict")
    write_pickle_to_file(temp_pickle_name, mols_dict)
    # Modify the pickled_file_dictionary to use the modified pickle dictionary
    mols_dict = None

    print("     Finished with run_post_multithread")
    return temp_pickle_name




if __name__ == "__main__":

    rxn_set = "Robust"
    rxn_set = "all_rxns"
    if rxn_set=="Robust": reactions=Robust_reactions
    elif rxn_set=="AUTOCLICKCHEM": reactions=AUTOCLICKCHEM_reactions
    elif rxn_set=="all_rxns": reactions=All_Rxns_reactions
    else:
        raise Exception("WHICH REACTION SET?")


    folder = "/home/jacob/Desktop/test_all_rxns/complimentary_mol_dir/"
    
    output_folder = "/home/jacob/Desktop/test_all_rxns/Robust_reactions_FILTERED/"
    source_pickle_folder = "/home/jacob/Desktop/test_all_rxns/Robust_reactions_FILTERED/source_pickled_lib/"
    modified_pickle_folder = "/home/jacob/Desktop/test_all_rxns/Robust_reactions_FILTERED/modified_pickled_lib/"
    good_mols_folder = "/home/jacob/Desktop/test_all_rxns/Robust_reactions_FILTERED/Final/"

    if os.path.exists(folder) is False:
        raise Exception("folder HERE!!")

    if os.path.exists(output_folder) is False:
        os.mkdir(output_folder)

    if os.path.exists(source_pickle_folder) is False:
        os.mkdir(source_pickle_folder)
    if os.path.exists(modified_pickle_folder) is False:
        os.mkdir(modified_pickle_folder)
    if os.path.exists(good_mols_folder) is False:
        os.mkdir(good_mols_folder)

    
    list_file_basename = [os.path.basename(x).replace(".smi","") for x in glob.glob(folder+"*.smi")]
    

    print("Geting molecules from library")
    pickled_file_dictionary = {}

    # Make a dictionary of pickle file locations

    for name in list_file_basename:
        # 1st see if we've made a modified pickle file before
        # This would be a file which has already been filtered down.
        # # If so lets use this

        modified_pickle_file = modified_pickle_folder + name+"_pickle"
        if os.path.exists(modified_pickle_file) is True:
            pickled_file_dictionary[name] = modified_pickle_file
            modified_pickle_file = None
        # If no pre-modified pickle file exists lets check if there is a pickled version of the source file.
        # Presumably this is bigger than the modified would've been
        else:     
            temp_pickle_name = source_pickle_folder + name+"_pickle"
            # print(temp_pickle_name)
            pickled_file_dictionary[name] = temp_pickle_name
            
            if os.path.exists(temp_pickle_name) is True:
                # print("pickled version Already Exists use this")
                temp_pickle_name = None
                continue

            else:
                # Import all molecules from a large list. This often takes a while.
                file_name = folder + name + ".smi"
                temp_mol = get_mols(file_name)
                write_pickle_to_file(temp_pickle_name, temp_mol)
                temp_mol = None
                temp_pickle_name = None

    #Close out excess variables
    list_file_basename = None

    for top_level_key in list(reactions.keys()):
        sub = reactions[top_level_key]

        reaction_string =sub["reaction_string"]
        functional_groups = sub["functional_groups"] 
        group_smarts = sub["group_smarts"]
        example_rxn_reactants = sub["example_rxn_reactants"] 
        num_reactants = sub["num_reactants"] 
        reaction_string_split = reaction_string.split(">>")[0]

        rxn_num = sub["RXN_NUM"] 


        print("")
        print("")
        print("Running Reaction: ", top_level_key)
        print("")

        rxn = AllChem.ReactionFromSmarts(reaction_string)
        rxn.Initialize()  


        list_mols_to_react_1 = []
        mol_standardized = []
        mols = []
        

        if num_reactants == 1:
            print("     Running onestep Reactions for: ", top_level_key)

            # Get mols_dict from pickled file 
            mols_dict = get_mols_dict_from_pickle(pickled_file_dictionary[functional_groups[0]])
            for key in list(mols_dict.keys()):
                mols.append(mols_dict[key])
            mols_dict = {}

            substructure = Chem.MolFromSmarts(group_smarts[0])
            substructure_from_rxn = Chem.MolFromSmarts(reaction_string_split)
            job_input = tuple([tuple([mols[i], rxn, substructure, substructure_from_rxn]) for i in range(0, len(mols))])
            mols = []
            substructure = None
            rxn = None
            print("     multi_threading onestep")
            print("          {} Number of reactions to perform.".format(len(job_input)))
            output = mp.multi_threading(job_input, num_processors,  conduct_reaction_one)
            job_input = None
            output = [x for x in output if x is not None]

            pickled_file_dictionary[functional_groups[0]] = run_post_multithread(output, functional_groups[0], output_folder, modified_pickle_folder)
            
            output = None
            

        if num_reactants == 2:

            print("     Running Two Step Reactions for: ", top_level_key)

            reaction_string_split = reaction_string_split.split(".")

            
            # Handle mol_1 as variable and mol_2 as a control.
            # Get mols_dict from pickled file 
            mols_dict = get_mols_dict_from_pickle(pickled_file_dictionary[functional_groups[0]])

            control_mol = Chem.MolFromSmiles(example_rxn_reactants[1])
            sub_control = Chem.MolFromSmarts(group_smarts[1])
            if control_mol.HasSubstructMatch(sub_control) is False:
                control_mol = Chem.AddHs(control_mol)
                if control_mol is None:
                    print("THIS SHOULDNT HAPPEN {}".format(reaction_string))
                    
                    raise Exception("THIS SHOULDNT HAPPEN")
                if control_mol.HasSubstructMatch(sub_control) is False:
                    print("THIS SHOULDNT HAPPEN 2 {}".format(reaction_string))
                    raise Exception("THIS SHOULDNT HAPPEN 2")
                else:
                    control_mol = Chem.AddHs(control_mol)
            sub_control = None


            for key in list(mols_dict.keys()):
                mols.append(mols_dict[key])
            
            substructure = Chem.MolFromSmarts(group_smarts[0])
            substructure_from_rxn = Chem.MolFromSmarts(reaction_string_split[0])
            job_input = tuple([tuple([mols[i], control_mol, rxn, substructure,substructure_from_rxn]) for i in range(0, len(mols))])
            mols_dict = {}
            mols = []
            substructure = None
            print("     multi_threading mol_1 as variable, mol_2 as control")
            print("          {} Number of reactions to perform.".format(len(job_input)))
            
            output = mp.multi_threading(job_input, num_processors,  conduct_reaction_two_mol2control)
            job_input = None
            print("     Removing bad mols")

            output = [x for x in output if x is not None]

            pickled_file_dictionary[functional_groups[0]] = run_post_multithread(output, functional_groups[0], output_folder, modified_pickle_folder)
            output = None
            ###################################################################
            ###################################################################
            ###################################################################
            ###################################################################

            # Handle mol_2 as variable and mol_1 as a control.
            # Get mols_dict from pickled file 
            mols_dict = get_mols_dict_from_pickle(pickled_file_dictionary[functional_groups[1]])

            control_mol = Chem.MolFromSmiles(example_rxn_reactants[0])
            sub_control = Chem.MolFromSmarts(group_smarts[0])
            if control_mol.HasSubstructMatch(sub_control) is False:
                control_mol = Chem.AddHs(control_mol)
                if control_mol is None:
                    print("THIS SHOULDNT HAPPEN {}".format(reaction_string))
                    raise Exception("THIS SHOULDNT HAPPEN")
                if control_mol.HasSubstructMatch(sub_control) is False:
                    print("THIS SHOULDNT HAPPEN 2 {}".format(reaction_string))
                    raise Exception("THIS SHOULDNT HAPPEN 2")
                else:
                    control_mol = Chem.AddHs(control_mol)
            sub_control = None

            mols = []
            for key in list(mols_dict.keys()):
                mols.append(mols_dict[key])
            mols_dict = {}
            
            substructure = Chem.MolFromSmarts(group_smarts[1])
            substructure_from_rxn = Chem.MolFromSmarts(reaction_string_split[1])

            # mol_set, mol_1, rxn, sub_2, substructure_from_rxn
            job_input = tuple([tuple([mols[i], control_mol, rxn, substructure, substructure_from_rxn]) for i in range(0, len(mols))])
            mols = None
            substructure = None
            rxn = None
            print("     multi_threading mol_2 as variable, mol_1 as control")
            print("          {} Number of reactions to perform.".format(len(job_input)))
            output = mp.multi_threading(job_input, num_processors,  conduct_reaction_two_mol1control)
            job_input = None
            print("     Removing bad mols")

            pickled_file_dictionary[functional_groups[1]] = run_post_multithread(output, functional_groups[1], output_folder, modified_pickle_folder)

            output = None



    print("")
    print("")
    print("")
    print("#################")

    print("Finished Testing Reactions!!!")

    # Save Final sets
    if os.path.isdir(good_mols_folder) is False:
        os.makedirs(good_mols_folder)


    job_input = []
    for groups in list(pickled_file_dictionary.keys()):
        out_file = good_mols_folder + groups + ".smi"
        pickle_file = pickled_file_dictionary[groups]
        temp = (out_file, pickle_file)
        job_input.append(temp)


    output = mp.multi_threading(job_input, -1,  write_final_outputs)


    print("finished!")