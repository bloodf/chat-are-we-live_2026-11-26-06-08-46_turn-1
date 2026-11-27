BLK=[.055,.045,.045]; DBR=[.13,.08,.055]; BRN=[.24,.15,.09]; AUB=[.36,.12,.05]; GNG=[.62,.27,.10]; BLD=[.72,.54,.30]; GRY=[.52,.50,.48]; PNK=[.85,.25,.45]; TEAL=[.12,.48,.52]; PLT=[.82,.76,.66]
CM='young_caucasian_male/textures/young_lightskinned_male_diffuse'; CF='young_caucasian_female/textures/young_lightskinned_female_diffuse'
AM='young_african_male/textures/young_darkskinned_male_diffuse.png'; AF='young_african_female/textures/young_darkskinned_female_diffuse.png'
SM='young_asian_male/textures/young_lightskinned_male_diffuse3.png'; SF='young_asian_female/textures/young_lightskinned_female_diffuse3.png'
DARK=dict(tone=[1.42,1.38,1.34],lip=[.42,.20,.18],lipA=.30,blush=.15,lidA=.2,eyebag=.25)
def t(a,b='#fff',**k): return dict(text=a,col=b,**k)
S4='male_casualsuit04'; S2='male_casualsuit02'; S6='male_casualsuit06'; F1='female_casualsuit01'; F2='female_casualsuit02'
CAST = {
 # ---------- playable
 'p_max': dict(race='caucasian', gender=1, age=.05, muscle=.36, weight=.42, height=.55, prop=.45, seed=3, skin=CM+'.png',
   hair=['short02'], hairRGB=BRN, eye='green', brow='eyebrow009', stubble=.25, clothes=[S4,'shoes05'],
   outfit={S4:dict(shirt='#2b2d33', trim='#f6c419', pants='#34465e', print=t('404\nSLEEP','#f6c419'))},
   details=[('head/head-oval',.4),('chin/chin-width-decr',.2),('eyes/l-eye-scale-incr',.3)]),
 'p_zoe': dict(race='african', gender=0, age=.04, muscle=.45, weight=.42, height=.5, prop=.6, seed=7, skin=AF, **DARK,
   hair=['afro01'], hairRGB=BLK, eye='brown', brow='eyebrow006', lash='eyelashes03', clothes=[F1,'shoes05'],
   outfit={F1:dict(shirt='#e9e3d2', trim='#f2331b', pants='#2b3140', print=t('MAIN\nCHARACTER','#f2331b'))},
   details=[('mouth/mouth-lowerlip-volume-incr',.3),('eyes/l-eye-scale-incr',.5)]),
 'p_mei': dict(race='asian', gender=0, age=.04, muscle=.4, weight=.38, height=.42, prop=.6, seed=11, skin=SF, lipA=.45,
   hair=['long01'], hairRGB=[.10,.07,.07], eye='brown', brow='eyebrow007', lash='eyelashes03', clothes=[F2,'shoes06'],
   outfit={F2:dict(shirt='#d9a5b4', trim='#ffffff', pants='#39527a', print=t('AFK','#ffffff'))},
   details=[('eyes/l-eye-scale-incr',.6),('head/head-round',.2)]),
 'p_dre': dict(race='african', gender=1, age=.06, muscle=.5, weight=.45, height=.62, prop=.6, seed=13, skin=AM, **DARK,
   hair=['afro01'], hairRGB=BLK, eye='brown', brow='eyebrow001', stubble=.35, clothes=[S2,'shoes02'],
   outfit={S2:dict(shirt='#b5452c', trim='#efe7d6', pants='#22262d', print=t('NPC','#efe7d6'))},
   details=[('head/head-square',.2)]),
 'p_ivy': dict(race='caucasian', gender=0, age=.05, muscle=.42, weight=.42, height=.52, prop=.6, seed=17, skin=CF+'2.png', freckles=.8,
   hair=['ponytail01'], hairRGB=GNG, eye='bluegreen', brow='eyebrow002', lash='eyelashes03', clothes=[F1,'shoes02'],
   outfit={F1:dict(shirt='#2f6b55', trim='#efe7d6', pants='#3d5578', print=t('TOUCH\nGRASS','#efe7d6'))},
   details=[('eyes/l-eye-scale-incr',.5),('nose/nose-scale-horiz-decr',.3)]),
 'p_ken': dict(race='asian', gender=1, age=.05, muscle=.38, weight=.5, height=.48, prop=.5, seed=19, skin=SM,
   hair=['short03'], hairRGB=[.09,.07,.07], eye='brown', brow='eyebrow001', clothes=[S2,'shoes06'],
   outfit={S2:dict(shirt='#3a4a66', trim='#f6c419', pants='#4a4640', print=t('GG\nEZ','#f6c419'))},
   details=[('head/head-round',.3)]),
 # ---------- family & story
 'mom_c': dict(race='caucasian', gender=0, age=.42, muscle=.42, weight=.62, height=.45, prop=.45, seed=23, skin='middleage_caucasian_female/textures/middleage_lightskinned_female_diffuse.png', eyebag=.6,
   hair=['long01'], hairRGB=[.40,.24,.13], eye='green', brow='eyebrow002', clothes=['female_elegantsuit01','shoes01'], outfit={'female_elegantsuit01':dict(tint=None)}, bg=(.62,.70,.60)),
 'mom_a': dict(race='african', gender=0, age=.40, muscle=.42, weight=.62, height=.45, prop=.45, seed=29, skin='middleage_african_female/textures/middleage_darkskinned_female_diffuse.png', **DARK,
   hair=['Braid01'], hairRGB=BLK, eye='brown', brow='eyebrow003', clothes=['female_elegantsuit01','shoes01'], bg=(.62,.70,.60)),
 'mom_s': dict(race='asian', gender=0, age=.40, muscle=.42, weight=.55, height=.4, prop=.45, seed=31, skin='middleage_asian_female/textures/middleage_lightskinned_female_diffuse2.png', eyebag=.5,
   hair=['ponytail01'], hairRGB=[.12,.09,.08], eye='brown', brow='eyebrow002', clothes=['female_elegantsuit01','shoes01'], bg=(.62,.70,.60)),
 'feast': dict(race='caucasian', gender=1, age=.1, muscle=.5, weight=.5, height=.72, prop=.6, seed=37, skin=CM+'2.png',
   hair=['short01','Full_beard'], hairRGB=DBR, eye='blue', brow='eyebrow010', clothes=['male_casualsuit05','shoes04'], face=dict(smile=1,open=.15,wide=.3), bg=(.32,.62,.82)),
 'landlord': dict(race='caucasian', gender=1, age=.62, muscle=.4, weight=.7, height=.5, prop=.4, seed=41, skin='old_caucasian_male/textures/old_lightskinned_male_diffuse.png', eyebag=.8,
   hair=['short04','Moustache'], hairRGB=GRY, eye='grey', brow='eyebrow012', clothes=['male_casualsuit03','shoes01'], outfit={'male_casualsuit03':dict(shirt='#66735a',pants='#4a4238',contrast=1.2)}, face=dict(frown=.4,brow_down=.6), bg=(.55,.55,.52)),
 'kyle': dict(race='caucasian', gender=1, age=.08, muscle=.45, weight=.6, height=.6, prop=.5, seed=43, skin=CM+'.png',
   hair=['short01','Full_beard'], hairRGB=AUB, eye='blue', brow='eyebrow011', clothes=['male_worksuit01','shoes02'], bg=(.78,.60,.45)),
 # ---------- staff / guests pool
 's01': dict(race='caucasian', gender=0, age=.1, muscle=.42, weight=.45, height=.55, seed=51, skin=CF+'.png', hair=['long01'], hairRGB=BLD, eye='blue', brow='eyebrow004', lash='eyelashes03',
   clothes=[F1,'shoes05'], outfit={F1:dict(shirt='#1f2430', trim='#17b5c4', pants='#55606e', print=t('CTRL+Z','#17b5c4'))}, details=[('eyes/l-eye-scale-incr',.3)], bg=(.45,.55,.62)),
 's02': dict(race='african', gender=1, age=.12, muscle=.62, weight=.5, height=.66, seed=53, skin=AM, **DARK, hair=['short04'], hairRGB=BLK, eye='brown', brow='eyebrow012', stubble=.5,
   clothes=[S6,'shoes03'], outfit={S6:dict(shirt='#d8d2c4', pants='#2a2d33', contrast=1.2)}, bg=(.70,.50,.36)),
 's03': dict(race='asian', gender=0, age=.08, muscle=.4, weight=.4, height=.4, seed=59, skin=SF, lipA=.5, hair=['long01'], hairRGB=PNK, browRGB=[.25,.12,.12], eye='brownlight', brow='eyebrow005', lash='eyelashes03',
   clothes=[F2,'shoes05'], outfit={F2:dict(shirt='#f0c53a', trim='#1a1a1a', pants='#6b7890', print=t('TL;DR','#1a1a1a'))}, details=[('eyes/l-eye-scale-incr',.7)], bg=(.80,.58,.62)),
 's04': dict(race='caucasian', gender=1, age=.3, muscle=.45, weight=.72, height=.55, seed=61, skin='middleage_caucasian_male/textures/middleage_lightskinned_male_diffuse.png', hair=['short04','Full_beard'], hairRGB=[.30,.26,.23], eye='brown', brow='eyebrow010',
   clothes=['male_casualsuit05','shoes02'], bg=(.42,.48,.40)),
 's05': dict(race='african', gender=0, age=.15, muscle=.42, weight=.55, height=.5, seed=67, skin=AF, **DARK, hair=['Braid01'], hairRGB=[.10,.06,.05], eye='brown', brow='eyebrow008', lash='eyelashes03',
   clothes=['female_elegantsuit01','shoes01'], bg=(.72,.62,.36)),
 's06': dict(race='asian', gender=1, age=.1, muscle=.4, weight=.42, height=.52, seed=71, skin=SM, hair=['short01'], hairRGB=TEAL, browRGB=[.1,.1,.1], eye='brown', brow='eyebrow009',
   clothes=[S2,'shoes06'], outfit={S2:dict(shirt='#e6e0d0', trim='#2b2d33', pants='#30343c', print=t('RENDER\nING...','#2b2d33'))}, bg=(.45,.58,.58)),
 's07': dict(race='caucasian', gender=0, age=.22, muscle=.5, weight=.5, height=.6, seed=73, skin='middleage_caucasian_female/textures/middleage_lightskinned_female_diffuse.png', hair=['ponytail01'], hairRGB=DBR, eye='grey', brow='eyebrow003',
   clothes=[F1,'shoes04'], outfit={F1:dict(shirt='#4a5a4f', trim='#d9b36a', pants='#2f3644', print=t('ACTION','#d9b36a'))}, bg=(.60,.52,.48)),
 's08': dict(race={'caucasian':.5,'african':.5}, gender=1, age=.1, muscle=.45, weight=.48, height=.6, seed=79, skin=AM, tone=[1.7,1.62,1.55], hair=['curly2'] and ['afro01'], hairRGB=[.20,.12,.07], eye='brownlight', brow='eyebrow011', stubble=.2, lip=[.55,.28,.25],
   clothes=[S4,'shoes05'], outfit={S4:dict(shirt='#6a4c93', trim='#f6c419', pants='#3a3f48', print=t('L + RATIO','#f6c419'))}, bg=(.55,.45,.62)),
 's09': dict(race='caucasian', gender=1, age=.18, muscle=.75, weight=.6, height=.75, seed=83, skin=CM+'2.png', hair=['short04'], hairRGB=BLD, eye='lightblue', brow='eyebrow010', stubble=.3,
   clothes=['male_elegantsuit01','shoes03'], face=dict(press=.4,brow_down=.3), bg=(.34,.36,.40)),
 's10': dict(race='asian', gender=0, age=.3, muscle=.42, weight=.5, height=.42, seed=89, skin='middleage_asian_female/textures/middleage_lightskinned_female_diffuse2.png', hair=['ponytail01'], hairRGB=[.16,.10,.09], eye='brown', brow='eyebrow004',
   clothes=['Asymmetric_Tunic_and_Sash','Tightjeans','shoes01'], bg=(.66,.56,.40)),
 's11': dict(race='african', gender=1, age=.35, muscle=.5, weight=.65, height=.58, seed=97, skin='middleage_african_male/textures/middleage_darkskinned_male_diffuse.png', **DARK, hair=['short04','Full_beard'], hairRGB=[.16,.15,.15], eye='brown', brow='eyebrow012',
   clothes=['male_casualsuit03','shoes01'], outfit={'male_casualsuit03':dict(shirt='#44618a',pants='#2c2c30',contrast=1.2)}, bg=(.50,.40,.34)),
 's12': dict(race='caucasian', gender=0, age=.06, muscle=.4, weight=.4, height=.48, seed=101, skin=CF+'2.png', freckles=.6, hair=['bob02'], hairRGB=PLT, hairContrast=.6, browRGB=[.38,.28,.2], eye='ice', brow='eyebrow005', lash='eyelashes03',
   clothes=[F1,'shoes06'], outfit={F1:dict(shirt='#7a2b3a', trim='#efe7d6', pants='#23262c', print=t('NO\nTHOUGHTS','#efe7d6'))}, details=[('eyes/l-eye-scale-incr',.6)], bg=(.62,.46,.50)),
 's13': dict(race={'asian':.5,'caucasian':.5}, gender=1, age=.08, muscle=.4, weight=.38, height=.55, seed=103, skin=SM, hair=['short02'], hairRGB=[.16,.11,.09], eye='brown', brow='eyebrow001',
   clothes=[S4,'shoes02'], outfit={S4:dict(shirt='#2f6d86', trim='#efe7d6', pants='#4c4038', print=t('RTFM','#efe7d6'))}, bg=(.40,.54,.62)),
 's14': dict(race='caucasian', gender=1, age=.5, muscle=.42, weight=.55, height=.5, seed=107, skin='old_caucasian_male/textures/old_lightskinned_male_diffuse.png', hair=['short03'], hairRGB=GRY, hairContrast=.6, eye='blue', brow='eyebrow012',
   clothes=['male_casualsuit01','shoes01'], bg=(.48,.50,.55)),
}
GLASSES = {'p_ken','s06'}
for k in GLASSES: CAST[k]['clothes'] = CAST[k]['clothes'] + ['glasses']
CAST['s08']['hair']=['afro01']
