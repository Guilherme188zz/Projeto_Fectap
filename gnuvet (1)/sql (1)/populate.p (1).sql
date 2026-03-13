/*
 * sql/populate.psql: script to populate the gnuvet postgres db
 *
 * Copyright (c) 2015 Dipl.Tzt. Enno Deimel <ennodotvetatgmxdotnet>
 *
 * This file is part of gnuvet, published under the GNU General Public License
 * version 3 or later (GPLv3+ in short).  See the file LICENSE for information.
 *
 */

-- implement mustelid vaccination

---grant select on staff to gvuser;
-- add an entry in /path/to/pg_hba.conf on db host:
-- (debian:) /etc/postgresql/x.y/main/pg_hba.conf
-- local gnuvet gnuv md5
-- host gnuvet gvuser 192.168.0.0/16 md5 (IPv4 example)

insert into century values(20);
select setval('century_cent_seq',20);

insert into staffroles(staffrole_name) values
 ('master'),('vet'),('nurse'),('reception'),('helper'),('work experience');

insert into titles(t_title) values
 ('n/a'),('Mr'),('Mrs'),('Ms'),('Dr'),('Sir'),('Lady'),('Lord');

insert into staff(stf_func,stf_title,stf_surname,stf_mname,stf_forename,stf_short,stf_logname,stf_sex) values
  (1,1,'','','','gv','gnuvet','n');

-- 1 entry nec in addresses for referencing
insert into addresses(housen,street,village,city,region,postcode) values
('','','','','','');

-- 1 empty entry necessary in locations: -- change this?
insert into locations (l_id,l_name) values (1,'');

insert into species values
 ( 1, 'Canine',      FALSE),
 ( 2, 'Feline',      FALSE),
 ( 3, 'Rabbit',      TRUE),
 ( 4, 'Rodent',      FALSE),
 ( 5, 'Mustelid',    FALSE),
 ( 6, 'Equine',      TRUE),
 ( 7, 'Bovine',      TRUE),
 ( 8, 'Ovine',       TRUE),
 ( 9, 'Caprine',     TRUE),
 (10, 'Porcine',     TRUE),
 (11, 'Camelid',     TRUE),
 (12, 'Other mammal',TRUE),
 (13, 'Fowl',        TRUE),
 (14, 'Raptor',      FALSE),
 (15, 'Exotic avian',TRUE),
 (16, 'Fish',        TRUE),
 (17, 'Amphibian',   FALSE),
 (18, 'Reptile',     FALSE),
 (19, 'Insect',      FALSE), 
 (20, 'Spider',      FALSE);
-- other mammals: bear cetacea elephant other_ungulatae marsupial seal
-- other birds
-- other reptiles
-- ...

-- Colours:
insert into basecolours values
 (1,null,'0',0),(2,'according to breed','0',0),(3,'albino','0',0),
 (4,'bay','0',32),(5,'black','0',0),(6,'blue','0',1048543),
 (7,'bluebrindle','0',1),(8,'brindle','0',658531),(9,'brown','0',0),
 (10,'buckskin','0',32),(11,'chestnut','0',32),(12,'colourpoint','0',2),
 (13,'cream','0',1048543),(14,'dapple',null,32),
 (15,'darkbrindle','0',1),(16,'dun','0',32),(17,'fawn','0',1),
 (18,'fleabitten grey',null,32),(19,'ginger','0',2),(20,'golden','0',0),
 (21,'green','0',1032192),(22,'grey','0',0),(23,'overo',null,32),
 (24,'palomino',null,32),(25,'piebald',null,32),
 (26,'polecat',null,16),(27,'red','0',1040335),(28,'roan','0',32),
 (29,'rose','0',0),(30,'skewbald',null,32),(31,'spotted','1',0),
 (32,'tabby','0',2),(33,'tan','0',1),(34,'tobiano',null,32),
 (35,'tortoiseshell','0',2),(36,'white','0',0),(37,'dark','1',0),
 (38,'light','1',0),(39,'chocolate','0',11);

insert into colours(col1,col2,col3) values
 (2,1,1), (3,1,1), (4,1,1), (5,1,1),
 (6,1,1), (7,1,1),
 (8,1,1), (9,1,1), (10,1,1), (11,1,1),
 (12,1,1), (13,1,1),
 (14,1,1), (15,1,1), (16,1,1), (17,1,1),
 (18,1,1), (19,1,1), (20,1,1), (21,1,1),
 (22,1,1), (23,1,1), (24,1,1), (25,1,1),
 (26,1,1), (27,1,1),
 (28,1,1), (29,1,1), (30,1,1),
 (32,1,1), (33,1,1), (34,1,1), (35,1,1),
 (36,1,1), (39,1,1),
 (3,6,1), (3,13,1),
 (3,19,1), (3,31,1), (5,9,1), (5,9,35), (5,9,36),
 (5,32,1), (5,35,1), (5,35,9), (5,36,1), (5,36,9),
 (6,17,1), (6,13,1),
 (6,35,1), (7,5,1), (7,36,1),
 (8,36,1), (12,5,1), (12,6,1), (12,9,1),
 (13,3,1), (13,5,1),
 (13,6,1), (13,9,1),
 (13,35,1), (15,36,1), (17,36,1), (19,3,1),
 (19,6,1), (19,36,1), (22,3,1), (22,5,1),
 (22,6,1), (22,9,1),
 (22,13,1), (22,19,1),
 (22,36,1), (27,3,1),
 (27,17,1), (27,22,1),
 (27,31,1), (27,36,1),
 (32,3,1), (32,6,1), (32,19,1), (32,22,1),
 (32,27,1), (32,35,1), (32,36,1), (35,3,1),
 (36,5,1), (36,6,1), (36,6,17),
 (36,7,1), (36,8,1),
 (36,9,1), (36,13,1),
 (36,15,1), (36,17,1), (36,18,1), (36,32,1),
 (36,35,1);

-- Breeds
insert into breeds (breed_name, b_spec, breed_abbr) values
-- 1
 ('Abyssinian',2, 'Abyss'),
 ('Afghan',1, 'Afgh'),
 ('Ahal-Tekke',6, 'A-T'),
 ('Airedale Terrier',1, 'AirT'),
 ('Akita Inu',1, 'AInu'),
 ('Alaskan Malamute',1, 'AlMal'),
 ('Alpaca',11, 'Alpac'),
 ('American Cocker Spaniel',1, 'AmCSp'),
 ('American Pitbull Terrier',1, 'AmPT'),
 ('Andalusian',6, 'And'),
--11
 ('Angloarab',6, 'ox'),
 ('Aberdeen Angus',7, 'AA'),
 ('Appaloosa',6, 'Appy'),
 ('Arabian',6, 'oo'),
 ('Australian Cattle Dog',1, 'AuCD'),
 ('Australian Sheep Dog',1, 'AuSD'),
 ('Badger',5, 'Badge'),
 ('Balinese',2, 'Bal'),
 ('Barzoi',1, 'Barz'),
 ('Basset',1, 'Bass'),
--21
 ('Beagle',1, 'Beag'),
 ('Belgian Shepherd',1, 'BSD'),
 ('Bearded Collie',1, 'BearC'),
 ('Bernese Mountain Dog',1, 'BMD'),
 ('Bichon Frisé',1, 'BF'),
 ('Bloodhound',1, 'BH'),
 ('Bobtail',1, 'Bobt'),
 ('Boerboel',1, 'Boer'),
 ('Border Collie',1, 'BordC'),
 ('Border Terrier',1, 'BordT'),
--31
 ('Boston Terrier',1, 'BostT'),
 ('Bouvier des Flandres',1, 'BdF'),
 ('Bovine unknown',7,'bovin'),
 ('Boxer',1, 'Boxer'),
 ('British Short Hair',2, 'BSH'),
 ('Budgerigar',15, 'Budge'),
 ('Bullmastiff',1, 'BullM'),
 ('Bullterrier',1, 'BullT'),
 ('Bulldog - English',1, 'BulDE'),
 ('Bulldog - French',1, 'BulDF'),
--41
 ('Burmese',2, 'Burm'),
 ('Cairn Terrier',1, 'CT'),
 ('Canine Unknown Large',1,'CanL'),
 ('Canine Unknown Medium',1,'CanM'),
 ('Canine Unknown Small',1,'CanS'),
 ('Camel',11, 'Camel'),
 ('Carp',16, 'Carp'),
 ('Cat unknown',2,'cat'),
 ('Cavalier King Charles Spaniel',1, 'CKCSp'),
 ('Chameleon',18, 'Cham'),
--51
 ('Charolais',7, 'CHA'),
 ('Chicken',13, 'Chick'),
 ('Chihuahua',1, 'Chih'),
 ('Chinchilla',4, 'Chnch'),
 ('Chinese Crested',1, 'CCrst'),
 ('Chow Chow',1, 'ChCh'),
 ('Cockateel', 15, 'Ccktl'),
 ('Cockatoo',15, 'Cktoo'),
 ('Cocker Spaniel',1, 'CSp'),
 ('Collie',1, 'Colli'),
--61
 ('Colourpoint Persian (Himalayan)',2, 'CPers'),
 ('Corgi - Welsh',1, 'Corgi'),
 ('Cornish Rex',2, 'CRex'),
 ('Cow',7, 'Cow'),
 ('Dalmatian',1, 'Dalm'),
 ('Dachshund - Long Haired',1, 'DxL'),
 ('Dachshund - Miniature',1, 'DxM'),
 ('Dachshund - Standard',1, 'Dx'),
 ('Dachshund - Wire Haired',1, 'DxW'),
 ('Deerhound',1, 'DeerH'),
--71
 ('Degu',4, 'Degu'),
 ('Dexter',7, 'DXT'),
 ('Dingo',1, 'Dingo'),
 ('Doberman',1, 'Dober'),
 ('Dog unknown',1,'dog'),
 ('Dogo Argentino',1, 'Dogo'),
 ('Dolphin',12, 'Dolph'),
 ('Domestic Long Hair',2, 'DLH'),
 ('Domestic Short Hair',2, 'DSH'),
 ('Donkey',6,'donky'),
--81
 ('Duck',13, 'Duck'),
 ('Egyptian',6, 'ee'),
 ('Elkhound',1, 'ElkH'),
 ('English Mastiff',1, 'EMast'),
 ('English Setter',1, 'ESett'),
 ('Equine Unknown',6,'equid'),
 ('Exmoor Pony',6, 'ExmP'),
 ('Falcon',14, 'Falc'),
 ('Feline Unknown',2,'FU'),
 ('Fell And Dale Pony',6, 'FlDlP'),
--91
 ('Ferret',5, 'Frtt'),
 ('Fish',16,'fish'),
 ('Fox Terrier',1, 'FoxT'),
 ('Fox Terrier - Smooth Haired',1, 'FoxTS'),
 ('Frog',17,'Frog'),
 ('Game',12, 'Game'),
 ('German Shepherd Dog (Alsatian)',1, 'GSD'),
 ('Goat',9, 'goat'),
 ('Golden Retriever',1, 'GRet'),
 ('Goldfish',16, 'GFish'),
--101
 ('Goose',13, 'Goose'),
 ('Great Dane',1, 'GDane'),
 ('Greyhound',1, 'GH'),
 ('Guinea Pig',4, 'GPig'),
 ('Hamster',4, 'Hamst'),
 ('Hanoveranian',6, 'Hanov'),
 ('Highland',7, 'HL'),
 ('Holstein-Friesian',7, 'HF'),
 ('Horse',6, 'horse'),
 ('Hungarian (Magyar) Viszla',1, 'MVisz'),
--111
 ('Hunter',6, 'H'),
 ('Insect',19,'insct'),
 ('Siberian Husky',1, 'Husky'),
 ('Iguana',18, 'Iguan'),
 ('Irish Draught',6, 'IDr'),
 ('Irish Setter',1, 'ISett'),
 ('Irish Terrier',1, 'IT'),
 ('Irish Wolfhound',1, 'WH'),
 ('Jack Russell Terrier',1, 'JRT'),
 ('Keeshond',1, 'KeesH'),
--121
 ('Kerry Blue Terrier',1, 'KBluT'),
 ('Kestrel',14, 'Kestr'),
 ('King Charles Spaniel',1, 'KCS'),
 ('Koi',16, 'Koi'),
 ('Komondor',1, 'Komon'),
 ('Labrador Retriever',1, 'LRet'),
 ('Large White',10, 'LW'),
 ('Lhasa Apso',1, 'LApso'),
 ('Limousin',7, 'LIM'),
 ('Lionhead',3, 'LHead'),
--131
 ('Lippizaner',6, 'Lipiz'),
 ('Lizard',18, 'Lizrd'),
 ('Llama',11, 'Llama'),
 ('Lop Ear',3, 'LEar'),
 ('Lovebird',15, 'Lvbrd'),
 ('Lurcher',1, 'Lurch'),
 ('Malinois',1, 'Malin'),
 ('Maltese',2, 'Malt'),
 ('Manx',2, 'Manx'),
 ('Mastino Napolitano',1, 'MNapo'),
--141
 ('Mastiff',1, 'Mastf'),
 ('Monkey',12, 'Monky'),
 ('Mouse',4, 'Mouse'),
 ('Mustelid',5, 'mustl'),
 ('Newfoundlander',1, 'NewF'),
 ('Newt',17, 'Newt'),
 ('Old English Sheepdog',1, 'OESD'),
 ('Owl',14, 'Owl'),
 ('Paint Horse',6, 'Paint'),
 ('Papillon',1, 'Pap'),
--151
 ('Parrot',15, 'Parrt'),
 ('Peacock',15, 'Peack'),
 ('Pekingese',1, 'Pekin'),
 ('Persian',2, 'Pers'),
 ('Pig',10, 'pig'),
 ('Pike',16, 'Pike'),
 ('Pinscher - Miniature',1, 'PinM'),
 ('Pinzgauer',7,'PIN'),
 ('Pointer',1, 'Point'),
 ('Pomeranian (Spitz)',1, 'Pom'),
--161
 ('Pomeranian - Toy',1, 'PomT'),
 ('Poodle - Miniature',1, 'PoodM'),
 ('Poodle - Standard',1, 'PoodS'),
 ('Poodle - Toy',1, 'PoodT'),
 ('Potbelly',10,'PB'),
 ('Pug',1, 'Pug'),
 ('Puli',1, 'Puli'),
 ('Pyrenean',1, 'BdP'),
 ('Quarter Horse',6, 'QH'),
 ('Rabbit',3, 'rbbit'),
--171
 ('Raptor',14,'raptr'),
 ('Rat',4, 'Rat'),
 ('Rhodesian Ridgeback',1, 'RhodR'),
 ('Rodent',4, 'rodnt'),
 ('Rottweiler',1, 'Rottw'),
 ('Rough Collie',1, 'RColl'),
 ('Saddleback',10, 'SBk'),
 ('Saint Bernard',1, 'StBrn'),
 ('Saluki',1, 'Sluki'),
 ('Salamander',17,'Salam'),
--181
 ('Salmon',16, 'Salmo'),
 ('Samoyed',1, 'Samoy'),
 ('Schipperke',1, 'Schpk'),
 ('Schnauzer - Standard',1, 'SchnS'),
 ('Schnauzer - Giant',1, 'SchnG'),
 ('Schnauzer - Miniature',1, 'SchnM'),
 ('Scotch Terrier',1, 'ScT'),
 ('Shagya',6, 'Shgya'),
 ('Shar-Pei',1, 'SharP'),
 ('Sheep',8, 'sheep'),
--191
 ('Shetland Pony',6, 'ShtP'),
 ('Shetland Sheep Dog',1, 'ShtSD'),
 ('Shih Tzu',1, 'STzu'),
 ('Shire',6, 'Shire'),
 ('Siamese',2, 'Siam'),
 ('Simmental',7, 'FV'),
 ('Skye Terrier',1, 'SkT'),
 ('Snake',18, 'Snake'),
 ('Somali',2, 'Somal'),
 ('Spider',20,'spidr'),
--201
 ('Springer Spaniel',1, 'SprSp'),
 ('Staffordshire Bullterrier',1, 'Staff'),
 ('Standardbred',6, 'SB'),
 ('Tervueren',1, 'Terv'),
 ('Thoroughbred',6, 'xx'),
 ('Tibetan Terrier',1, 'TibT'),
 ('Trout',16, 'Trt'),
 ('Turkish Van',2, 'TVan'),
 ('Turtle',18, 'Trtl'),
 ('Warmblood',6, 'WB'),
--211
 ('Weimaraner',1, 'Weim'),
 ('Welsh Cob',6, 'WCob'),
 ('Welsh Mountain Pony',6, 'WMP'),
 ('West Highland White Terrier',1, 'WHWT'),
 ('Whippet',1, 'Whip'),
 ('Wire Haired Terrier',1, 'WHT'),
 ('Yorkshire Terrier',1, 'YT');

insert into clients(c_title, c_sname, c_address, c_reg, c_last) values
 (1, 'unknown', 1, current_date, now());

insert into vats(vat_name, vat_rate) values
 ('Standard VAT', .2),
 ('Reduced VAT', .1),
 ('No VAT', 0);
-- Austria: insert vats(VatName, VatRate) values ('MWSt',.2), ('erm. MWSt',.1), ('USt',.2), ('erm. USt',.1), ('steuerfrei', 0);

insert into markups (m_name, m_rate) values -- markup usually unused in lang de
 ('None', 0), ('Standard', .8), ('Reduced', .6), ('Greyhound', .3);

insert into units values (1,'tablet','tablets','tab','t'),(2,'drop','drops','dr','d'),(3,'ml','','ml','m'),(4,'l','','l','l'),(5,'mg','','mg','M'),(6,'g','','g','g'),(7,'kg','','kg','k'),(8,'tube','tubes','tub','T'),(9,'bottle','bottles','bot','b'),(10,'pack','packs','pck','p'),(11,'sachet','sachets','sac','s'),(12,'piece','pieces','pc','P'),(13,'dose','doses','dos','D'),(14,'IU','','IU','i'),(15,'','','','X'),(16,'cm','','cm','c');
-- de: (1,'Tablette','Tabletten','Tab','t'),(2,'Tropfen','','Tr','T'),(3,'ml','','ml','m'),(4,'l','','l','l'),(5,'mg','','mg','M'),(6,'g','','g','g'),(7,'kg','','kg','k'),(8,'Tube','Tuben','Tub','T'),(9,'Flasche','Flaschen','Fl','f'),(10,'Packung','Packungen','Pck','P'),(11,'Beutel','','Btl','b'),(12,'Stück','','St','s'),(13,'Dosis','Dosen','Dos','d'),(14,'IU','','IU','i'),(15,'','','','X'),(16,'cm','','cm','c');

insert into validities (val_text, val_days) values
 ('3 - 5 weeks', 28),--1
 ('1 year', 365),    --2
 ('1 month', 28),    --3
 ('6 months', 180),  --4
 ('2 years', 730),   --5
 ('3 years', 1095),  --6
 ('None', 0);        --7

insert into categories /* as of NOAH 2007 */ (category) values ('ACE Inhibitor'), ('adsorbent'), ('amino acid'), ('anaesthetic, local'), ('anaesthetic, general'), ('anaesthetic, general, fish'), ('analgesic'), ('antacid'), ('antiarrhythmic'), ('antibiotic'), ('anticonvulsant'), ('antidepressant'), ('antidote'), ('antiemetic'), ('antiepileptic'), ('antifungal'), ('antihistamine'), ('antiinflammatory, nonsteroidal'), ('antiinflammatory, steroidal'), ('antiparasitic'), ('antiseptic'), ('antitussive'), ('astringens'), ('beta blocker'), ('bronchodilator'), ('bronchomucolytic'), ('calcium channel blocker'), ('cardiologic'), ('chemotherapeutic'), ('Cushing treatment'), ('diuretic'), ('electrolyte'), ('emetic'), ('enzyme'), ('euthanasia'), ('foam breaker'), ('h2 blocker'), ('herbal'), ('hormonal'), ('immunoglobuline'), ('immunosuppressant'), ('interferon'), ('laxans'), ('MAO inhibitor'), ('muscle relaxans'), ('nutritional'), ('obstetric adjuvant'), ('organic'), ('organic phosphorus'), ('parasympatholytic'), ('protein'), ('respiratory stimulant'), ('sedative'), ('spasmolytic'), ('styptic'), ('sympatholytic'), ('sympathomimetic'), ('synovial'), ('thyroid'), ('trace mineral'), ('vaccination'), ('vitamin'), ('ware'), ('water');

insert into ingredients /* as of NOAH 2007 + a few additions */ (ingredient, ingr_catid) values ('Acepromazine',53), ('Acetylisovaleryltylosil Tartrate',10), ('Adrenaline',39), ('Aeromonus salmonicida',61), ('Aglepristone',39), ('Albendazole',20), ('Aloe vera',38), ('Altrenogest',39), ('Amethocaine-HCl',4), ('Amitraz',20), ('Amoxicillin',10), ('Amoxicillin/Clavulanic Acid',10), ('Ampicillin',10), ('Apramycin',10), ('Atipamezol',13), ('Atropine',50), ('Azamethiphos',20), ('Azaperone',53), ('Benazepril',1), ('Benzocaine',4), ('Benzoyl Peroxide',20), ('Benzylpenicillin',20), ('Betamethason',19), ('Bismuth Carbonate',23), ('Bismuth Subnitrate',2), ('Bovine Concentrated Lactoserum',40), ('Bromhexine',26), ('Bronopol',16), ('Buprenorphine',7), ('Busereline',39), ('Butorphanol',7), ('Butylscopolamine',54), ('Cabergoline',39), ('Ca - Calcium',32), ('(Sodium-)Calciumedetate',13), ('Carbetocine',39), ('Carprofen',18), ('Cascara',38)/*?*/, ('Catechu',38)/*?*/, ('Cefalexin',10), ('Cefoperazone',10), ('Cefquinome',10), ('Ceftiofur',10), ('Celery',38)/*?*/, ('Cephalexin',10), ('Cefalonium',10), ('Cephapirin',10), ('Cetrimide',10), ('Charcoal',2), ('Chlorhexidine',21), ('Chlortetracycline',10), ('Cinchocaine',35), ('Cinchophen',19), ('Clenbuterol',57), ('Clindamycin',10), ('Clomipramine',12), ('Cloprostenol',39), ('Closantel',20), ('Clotrimazole',16), ('Cloxacillin',10), ('Co - Cobalt',60), ('Codeine',22), ('Colistin',10), ('Copper',60), ('Cyclosporin',41), ('Cypermethrin',20), ('Cyromazine',20), ('Damiana',38) /*?*/, ('Dandelion',38) /*?*/, ('Danofloxacin',10), ('Decoquinate',20), ('Delmadinone',39), ('Deltamethrin',20), ('Dembrexine',26), ('Deslorelin',39), ('Detomidine',5), ('Dexamethasone',19), ('Diazinon',20), ('Diclazuril',20), ('Dicyclanil',20), ('Difloxacin',10),  ('Digitoxin',9), ('Diltiazem',27), ('Dinoprost',39), ('Diprenorphine',13), ('Doramectin',20), ('Doxapram',52), ('Doxycycline',10), ('Electrolytes',32), ('Eltenac',18), ('Emamectin Benzoate',20), ('Emodepside',20), ('Enalapril Maleate',28), ('Enilconazole',16), ('Enrofloxacin',10), ('Epinephrine',39), ('Eprinomectin',20), ('IgG, equine',40), ('Erythromycin',10), ('Estriol',39), ('Etamiphylline Camsylate',28), ('Etorphine',7), ('Fe - Iron',60), ('Febantel',20), ('Fenbendazole',20), ('Fentanyl',7), ('Fenugreek',38) /*?*/, ('Fipronil',20), ('Firocoxib',18), ('Florfenicol',10), ('Fluanisone',7), ('Flubendazole',20), ('Flugestone',39), ('Flumethrin',20), ('Flunixine Meglumine',18), ('Food',46), ('Framycetin',10), ('Fucus',38) /*?*/, ('Furosemide',31), ('Fusidic Acid',10), ('Garlic',38) /*?*/, ('Gentamicin',10), ('Gentiana vulg.',38), ('Glacial Ac',48), ('Gleptoferron',60), ('Glc',46), ('Glycerine',48), ('Glycine',3), ('Glycosaminoglycan',58), ('Gonadorelin',39), ('(Serum-)Gonadotrophin',39), ('Griseofulvin',10), ('Guaifenesin',45), ('Haemoglobin',51), ('Halofuginone',20), ('Halothane',5), ('Hexamine',21), ('Horseradish',38) /*?*/, ('Hyaluronic Acid',58), ('Ibafloxacin',10), ('Imidacloprid',20), ('Imidapril',1), ('Imidocarb',20), ('Insulin',39), ('Interferon',42), ('I - Iodine',60), ('Isoflurane',5), ('Isoxsuprine',18), ('Isphagula',38) /*?*/, ('Itraconazole',16), ('Ivermectin',20), ('K - Potassium',32), ('Kaolin',2), ('Ketamine',5), ('Ketoconazole',16), ('Ketoprofen',18), ('Kola',38) /*?*/, ('Lasalocid',20), ('Levamisole',20), ('Lidocaine',4), ('Lincomycin',10), ('Lufenuron',20), ('Luprostiol',39), ('Lysine',3), ('Maduramicin',20), ('Marbofloxacin',10), ('Mebendazole',20), ('Meclofenamic Acid',18), ('Medetomidine',5), ('Medroxyprogesterone',39), ('Megestrol',39), ('Melatonin',39), ('Meloxicam',18), ('Mepivacaine',4), ('Metamizole',18), ('Methimazole (Thiamazole)',59), ('Methionine',3), ('Methylprednisolone',19), ('Metoclopramide',14), ('Metronidazole',10), ('Mg - Magnesium',32), ('Miconazole',16), ('Milbemycin',20), ('Mistletoe',38) /*?*/, ('Monensin',20), ('Morantel',20), ('Moxidectin',20), ('Na - Sodium',32), ('Nafcillin',10), ('Nandrolone',39), ('Narasin',20), ('Natamycin',16), ('Neomycin',10), ('Nicarbazin',20), ('Nicergoline',56), ('Nimesulide',18), ('Nitenpyram',20), ('Nitroscanate',20), ('Nitroxynil',20), ('Novobiocin',10), ('Nystatin',16), ('Oestradiol',39), ('Omeprazol',8), ('Orbifloxacin',10), ('Oxfendazol',20), ('Oxyclozanide',20), ('Oxytetracycline',20), ('Oxytocin',39), ('P - Phosphate',32), ('Pancreatin',34), ('Paracetamol',7), ('Parsley',38), ('Penethamate hydriodide',10), ('Penicillin',10), ('Pentobarbital',35), ('Pentosan Polysulphate',18), ('Permethrin',20), ('Pethidine',7), ('Phenobarbital',15), ('Phenoxymethylpenicillin',10),  ('Phenylbutazone',18), ('Phenylpropanolamine',57), ('Pimobendan',28), ('Piperazine',20), ('Piperonyl Butoxide',20), ('Pirlimycin',10), ('Poloxalene',36), ('Polymyxin B',10), ('Praziquantel',20), ('Prednisolone',19), ('Primidone',11), ('Procaine Benzylpenicillin',10), ('Procaine',4), ('Procaine Penicillin',10), ('Progesterone',39), ('Proligestone',39), ('Propentofylline',28), ('Propofol',5), ('Propoxur',20), ('Propylene Glycol',48), ('Pyrantel Embonate',20), ('Pyrethrum',20), ('Quinalbarbitone',35), ('Ramipril',1), ('Raspberry',38), ('Rhubarb',38), ('Ricobendazole',20), ('Robenidine',20), ('Romifidine',53), ('(S)-methoprene',20), ('Salicylic Acid',18), ('Salinomycin',20), ('Scullcap',38), ('Se - Selenium',60), ('Selamectin',20), ('Selegiline',44), ('Senna',38), ('Sevoflurane',5), ('Simethicone',36), ('Spectinomycin',10), ('Spiramycin',10), ('Spironolactone',31), ('Sterculia',43), ('Streptomycin',10), ('Sulfadimethoxine',20), ('Suxibuzone',18), ('Tepoxaline',18), ('Testosterone',39), ('Tetracycline',10), ('Theophylline',25), ('Thiabendazole',20), ('Thiopentone',5), ('Thiostrepton',10), ('Tiamulin',10), ('Thyroxine L-',39), ('Tilmicosin',10), ('Toldimphos',49), ('Tolfenamic Acid',18), ('Toltrazuril',20), ('Triamcinolone',18), ('Tricaine Methane Sulphonate',6), ('Triclabendazole',20), ('Trilostane',30), ('Trimethoprim/Sulfadiazine',10), ('Tulathromycin',10), ('Tylosin',10), ('Valerian',38), ('Valnemulin',10), ('Vedaprofen',18), ('Vetrabutine',47), ('Vitamin',62), ('Ware',63), ('Water',64), ('Watercress',38), ('Xylazine',5), ('Yersinia ruckeri',61);

insert into instructions (inst_abbr, inst_txt, inst_pos) values
 ('g',  'Give', 1), -- this looks quite different in German
 ('a',  'Apply', 1),
 ('i',  'Inject', 1),
 ('1',  'once', 2),
 ('2',  'twice', 2),
 ('3',  'three times', 2),
 ('3-5','3 to 5 times', 2),
 ('o',  'every other day', 3),
 ('d',  'daily', 3),
 ('d2', 'daily (every 12 hrs)', 3),
 ('d3', 'daily (every 8 hrs)', 3),
 ('m',  'per month', 3),
 ('w',  'per week', 3),
 ('ar','to affected region', 4),
 ('lr', 'to left ear', 4), -- a3-5dlrg
 ('rr', 'to right ear', 4),
 ('er', 'to each ear', 4),
 ('ly', 'to left eye', 4),
 ('ry', 'to right eye', 4),
 ('ey', 'to each eye', 4),
 ('d',  'days', 5),
 ('w',  'weeks', 5),
 ('g',  'Wear rubber gloves or wash hands well after use', 6),
 ('l',  'Wear rubber gloves when handling litter of cats treated with this medication', 6);

insert into labels (lb_abbr, lb_txt) values -- not sure yet if i'll use this
 ('g.5ud', 'Give 1/2 a % per day'),
 ('g.5u2', 'Give 1/2 a % twice daily'),
 ('g1ud', 'Give one % per day'),
 ('g1u2', 'Give one % twice daily'),
 ('g1u3', 'Give one % three times daily (every 8 hrs)'),
 ('g1uo', 'Give one % every other day'),
 ('g2u1', 'Give two % once daily'),
 ('g2u2', 'Give two % twice daily'),
 ('g2u3', 'Give two % three times daily (every 8 hrs)'),
 ('g3u1', 'Give three % once daily'),
 ('g3u2', 'Give three % twice daily'),
 ('g3u3', 'Give three % three times daily (every 8 hrs)'),
 ('a3-5dtar', 'Apply three to five times per day to affected region');

insert into paymodes values(1,'Cash',FALSE),(2,'Debit Card',FALSE),(3,'Cheque',TRUE),(4,'Credit Card',TRUE),(5,'Transfer',TRUE),(6,'Direct Debit',TRUE);

insert into ptypes(pt_name,pt_col)values('cons','darkCyan'),('hist','black'),('med','darkBlue'),('serv','darkGreen'),('good','darkMagenta'),('food','darkYellow'),('other','darkRed'),('vac','darkBlue'); -- vac is a serv -- no vac has 2b a type of its own

-- examples, might be imported from diff source if code available
-- worst case print, scan, OCR, edit -> table
insert into products
 (pr_id,pr_name,pr_short,pr_type,pr_perm,
  pr_nprice,pr_u,pr_instr,pr_vat) values
(1,'Amoxicillin Injectable','amoxi1',(select pt_id from ptypes where pt_name='med'),TRUE,0.12,3,FALSE,1),
(2,'Amoxicillin Injectable 50 ml','amoxib',(select pt_id from ptypes where pt_name='med'),TRUE,5.96,9,TRUE,2),
(3,'Amoxicillin Tablets 50 mg','amoxit50',(select pt_id from ptypes where pt_name='med'),TRUE,0.12,1,TRUE,2),
(4,'Amoxicillin Tablets 100 mg','amoxit100',(select pt_id from ptypes where pt_name='med'),TRUE,0.22,1,TRUE,2),
(5,'Amoxicillin Tablets 250 mg','amoxit250',(select pt_id from ptypes where pt_name='med'),TRUE,0.43,1,TRUE,2),
(6,'Antirobe Capsules 25 mg','antir25',(select pt_id from ptypes where pt_name='med'),TRUE,0.60,1,TRUE,2),
(7,'Antirobe Capsules 75 mg','antir75',(select pt_id from ptypes where pt_name='med'),TRUE,1.70,1,TRUE,2),
(8,'Antirobe Capsules 150 mg','antir150',(select pt_id from ptypes where pt_name='med'),TRUE,3.23,1,TRUE,2),
(9,'Antirobe Capsules 300 mg','antir300',(select pt_id from ptypes where pt_name='med'),TRUE,6.30,1,TRUE,2),
(10,'Baytril Injectable 2.5 %','baytri2.5',(select pt_id from ptypes where pt_name='med'),TRUE,0.49,3,FALSE,1),
(11,'Baytril Injectable 5 %','baytri5',(select pt_id from ptypes where pt_name='med'),TRUE,0.95,3,FALSE,1),
(12,'Baytril Injectable 10 %','baytri10',(select pt_id from ptypes where pt_name='med'),TRUE,1.67,3,FALSE,1),
(13,'Betamox Injectable','betamoxi',(select pt_id from ptypes where pt_name='med'),TRUE,0.20,3,FALSE,1),
(14,'Betamox Injectable 50 ml','betamoxib',(select pt_id from ptypes where pt_name='med'),TRUE,9.70,9,TRUE,2),
(15,'Buster Collar 25 cm','collar25',(select pt_id from ptypes where pt_name='good'),FALSE,10.21,12,FALSE,1),
(16,'Choo-Bone XL','choobonexl',(select pt_id from ptypes where pt_name='food'),FALSE,1.28,12,FALSE,2),
(17,'Dexafort Injection','dexaf',(select pt_id from ptypes where pt_name='med'),TRUE,0.41,3,FALSE,1),
(18,'Drontal Plus Palatable Canine','drontppc',(select pt_id from ptypes where pt_name='med'),FALSE,1.19,1,TRUE,2),
(19,'Duramune DAPPi+L','ddappil',(select pt_id from ptypes where pt_name='med'),TRUE,6.81,13,FALSE,2),
(20,'Duramune DAPPi+LC','ddappilc',(select pt_id from ptypes where pt_name='med'),TRUE,8.17,13,FALSE,2),
(21,'Eurican DHPPi+LC','edhppilc',(select pt_id from ptypes where pt_name='med'),TRUE,8.51,13,FALSE,2),
(22,'Felimazole 2.5 mg','felimaz2.5',(select pt_id from ptypes where pt_name='med'),TRUE,1.50,1,TRUE,2),
(23,'Fevaxyn Pentofel','fpento',(select pt_id from ptypes where pt_name='med'),TRUE,8.51,13,FALSE,2),
(24,'Fevaxyn iCHPChlam','fichpch',(select pt_id from ptypes where pt_name='med'),TRUE,6.81,13,FALSE,2),
(25,'Frontline Spray 100 ml','frontl100',(select pt_id from ptypes where pt_name='med'),FALSE,7.23,9,TRUE,2),
(26,'Frontline Spray 250 ml','frontl250',(select pt_id from ptypes where pt_name='med'),FALSE,13.62,9,TRUE,2),
(27,'Hills Feline Growth 1.8 kg','hfgr1.8',(select pt_id from ptypes where pt_name='food'),FALSE,5.96,10,TRUE,2),
(28,'Marbocyl Injectable 2.5 %','marboi2.5',(select pt_id from ptypes where pt_name='med'),TRUE,0.27,3,FALSE,1),
(29,'Nobivac KC','nkc',(select pt_id from ptypes where pt_name='med'),TRUE,13.62,13,FALSE,2),
(30,'Nobivac Myxo','nmyxo',(select pt_id from ptypes where pt_name='med'),TRUE,4.26,13,FALSE,2),
(31,'Nobivac Rabies','nrab',(select pt_id from ptypes where pt_name='med'),TRUE,12.77,13,FALSE,2),
(32,'Oral Hygiene Rinse','oralhy',(select pt_id from ptypes where pt_name='med'),FALSE,4.26,9,TRUE,1),
(33,'ProteqFlu','proteqf',(select pt_id from ptypes where pt_name='med'),TRUE,7.66,13,FALSE,2),
(34,'ProteqFlu Te','proteqft',(select pt_id from ptypes where pt_name='med'),TRUE,10.21,13,FALSE,2),
(35,'Vicryl 5-0 mounted','vicryl50m',(select pt_id from ptypes where pt_name='med'),TRUE,2.98,12,FALSE,1),
(36,'VitBee 1000 Injectable','vitbee1k',(select pt_id from ptypes where pt_name='med'),TRUE,0.48,3,FALSE,1),
(37,'Consultation','constd',(select pt_id from ptypes where pt_name='cons'),FALSE,20.00,15,FALSE,1),
(38,'Consultation Follow-Up','con2',(select pt_id from ptypes where pt_name='cons'),FALSE,14.89,15,FALSE,1),
(39,'Consultation Further Follow-Up','conff',(select pt_id from ptypes where pt_name='cons'),FALSE,9.79,15,FALSE,1),
(40,'Consultation Free','confree',(select pt_id from ptypes where pt_name='cons'),FALSE,0.00,15,FALSE,1),
(41,'Consultation Child Pet','conchpet',(select pt_id from ptypes where pt_name='cons'),FALSE,6.38,15,FALSE,1),
(42,'Consultation Exotic','conexot',(select pt_id from ptypes where pt_name='cons'),FALSE,23.40,15,FALSE,1),
(43,'Consultation Out of Hours 1 ( 7 pm to 10 pm)','conooh1',(select pt_id from ptypes where pt_name='cons'),FALSE,28.51,15,FALSE,1),
(44,'Consultation Out of Hours 2 (10 pm to  0 am)','conooh2',(select pt_id from ptypes where pt_name='cons'),FALSE,37.87,15,FALSE,1),
(45,'Consultation Out of Hours 3 ( 0 am to  7 am)','conooh3',(select pt_id from ptypes where pt_name='cons'),FALSE,47.23,15,FALSE,1),
(46,'Consultation Out of Hours 4 (Sat 5 pm to Mon 7 am)','conooh4',(select pt_id from ptypes where pt_name='cons'),FALSE,56.68,15,FALSE,1),
(47,'Castr. Canine S (< 10 kg)','castc1',(select pt_id from ptypes where pt_name='serv'),FALSE,34.04,15,FALSE,1),
(48,'Castr. Canine M (< 20 kg)','castc2',(select pt_id from ptypes where pt_name='serv'),FALSE,51.06,15,FALSE,1),
(49,'Castr. Canine L (< 50 kg)','castc3',(select pt_id from ptypes where pt_name='serv'),FALSE,68.09,15,FALSE,1),
(50,'Castr. Canine XL (<100 kg)','castc4',(select pt_id from ptypes where pt_name='serv'),FALSE,85.11,15,FALSE,1),
(51,'Castr. Canine XXL (>100 kg)','castc5',(select pt_id from ptypes where pt_name='serv'),FALSE,119.15,15,FALSE,1),
(52,'Castr. Feline','castf',(select pt_id from ptypes where pt_name='serv'),FALSE,25.53,15,FALSE,1),
(53,'Castr. Lagomorph/Rodent','castr',(select pt_id from ptypes where pt_name='serv'),FALSE,35.74,15,FALSE,1),
(54,'Spay Canine S   (< 10 kg)','spaycs',(select pt_id from ptypes where pt_name='serv'),FALSE,51.06,15,FALSE,1),
(55,'Spay Canine M   (< 20 kg)','spaycm',(select pt_id from ptypes where pt_name='serv'),FALSE,68.09,15,FALSE,1),
(56,'Spay Canine L   (< 50 kg)','spaycl',(select pt_id from ptypes where pt_name='serv'),FALSE,85.11,15,FALSE,1),
(57,'Spay Canine XL  (<100 kg)','spaycxl',(select pt_id from ptypes where pt_name='serv'),FALSE,119.15,15,FALSE,1),
(58,'Spay Canine XXL (>100 kg)','spaycxxl',(select pt_id from ptypes where pt_name='serv'),FALSE,153.19,15,FALSE,1),
(59,'Spay Feline','spayf1',(select pt_id from ptypes where pt_name='serv'),FALSE,42.55,15,FALSE,1),
(60,'Spay Feline Pregnant','spayf2',(select pt_id from ptypes where pt_name='serv'),FALSE,51.06,15,FALSE,1),
(61,'Spay Feline Season','spayf3',(select pt_id from ptypes where pt_name='serv'),FALSE,68.09,15,FALSE,1),
(62,'Spay Rabbit/Rodent','spayr',(select pt_id from ptypes where pt_name='serv'),FALSE,25.53,15,FALSE,1),
(63,'Euthanasia Canine S   (< 10 kg)','euthcs',(select pt_id from ptypes where pt_name='serv'),FALSE,29.79,15,FALSE,1),
(64,'Euthanasia Canine M   (< 20 kg)','euthcm',(select pt_id from ptypes where pt_name='serv'),FALSE,38.30,15,FALSE,1),
(65,'Euthanasia Canine L   (< 50 kg)','euthcl',(select pt_id from ptypes where pt_name='serv'),FALSE,55.32,15,FALSE,1),
(66,'Euthanasia Canine XL  (<100 kg)','euthcxl',(select pt_id from ptypes where pt_name='serv'),FALSE,72.34,15,FALSE,1),
(67,'Euthanasia Canine XXL (>100 kg)','euthcxxl',(select pt_id from ptypes where pt_name='serv'),FALSE,89.36,15,FALSE,1),
(68,'Euthanasia Feline','euthf',(select pt_id from ptypes where pt_name='serv'),FALSE,25.53,15,FALSE,1),
(69,'Euth./Body Disposal Canine S   (< 10 kg)','euthcsb',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(70,'Euth./Body Disposal Canine M   (< 20 kg)','euthcmb',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(71,'Euth./Body Disposal Canine L   (< 50 kg)','euthclb',(select pt_id from ptypes where pt_name='serv'),FALSE,12.78,15,FALSE,1),
(72,'Euth./Body Disposal Canine XL  (<100 kg)','euthcxlb',(select pt_id from ptypes where pt_name='serv'),FALSE,17.04,15,FALSE,1),
(73,'Euth./Body Disposal Canine XXL (>100 kg)','euthcxxlb',(select pt_id from ptypes where pt_name='serv'),FALSE,25.60,15,FALSE,1),
(74,'Euth./Body Disposal Feline','euthfb',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(75,'Euth./Individual Cremation','euthind',(select pt_id from ptypes where pt_name='serv'),FALSE,0.00,15,FALSE,1),
(76,'Injection s.c.','injsc',(select pt_id from ptypes where pt_name='serv'),FALSE,1.91,15,FALSE,1),
(77,'Injection i.m.','injim',(select pt_id from ptypes where pt_name='serv'),FALSE,2.77,15,FALSE,1),
(78,'Injection i.v.','injiv',(select pt_id from ptypes where pt_name='serv'),FALSE,6.17,15,FALSE,1),
(79,'Injection i.a.','injia',(select pt_id from ptypes where pt_name='serv'),FALSE,13.40,15,FALSE,1),
(80,'Injection i.v. Catheter','injivc',(select pt_id from ptypes where pt_name='serv'),FALSE,8.51,15,FALSE,1),
(81,'Anal Gland Emptying during Consultation','ag1',(select pt_id from ptypes where pt_name='serv'),FALSE,6.81,15,FALSE,1),
(82,'Anal Gland Emptying (only)','ag2',(select pt_id from ptypes where pt_name='serv'),FALSE,10.64,15,FALSE,1),
(83,'Tablet Administration','tab1',(select pt_id from ptypes where pt_name='serv'),FALSE,0.85,15,FALSE,1),
(84,'Tablet Administration difficult','tab2',(select pt_id from ptypes where pt_name='serv'),FALSE,2.55,15,FALSE,1),
(85,'Dispense Fee','disp',(select pt_id from ptypes where pt_name='serv'),FALSE,0.85,15,FALSE,1),
(86,'Dispense Fee Out of Hours 1 ( 7 pm to 10 pm)','dispo1',(select pt_id from ptypes where pt_name='serv'),FALSE,2.13,15,FALSE,1),
(87,'Dispense Fee Out of Hours 2 (10 pm to  0 am)','dispo2',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(88,'Dispense Fee Out of Hours 3 ( 0 am to  7 am)','dispo3',(select pt_id from ptypes where pt_name='serv'),FALSE,6.38,15,FALSE,1),
(89,'Dispense Fee Out of Hours 4 (Sat 5 pm to Non 7 am)','dispo4',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(90,'Dressing S','dress',(select pt_id from ptypes where pt_name='serv'),FALSE,2.13,15,FALSE,1),
(91,'Dressing M','dresm',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(92,'Dressing L','dresl',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(93,'Clip nails','clipn',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(94,'Clip nails (only)','clipno',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(95,'Clip beak and nails','clipbn',(select pt_id from ptypes where pt_name='serv'),FALSE,11.91,15,FALSE,1),
(96,'Ear cleaning','ears',(select pt_id from ptypes where pt_name='serv'),FALSE,8.26,15,FALSE,1),
(97,'Dental Scaling and Polishing Feline incl. Anaesth.','dentf',(select pt_id from ptypes where pt_name='serv'),FALSE,68.09,15,FALSE,1),
(98,'Dental Scaling and Polishing Canine S   (< 10 kg)','dentcs',(select pt_id from ptypes where pt_name='serv'),FALSE,68.09,15,FALSE,1),
(99,'Dental Scaling and Polishing Canine M   (< 20 kg)','dentcm',(select pt_id from ptypes where pt_name='serv'),FALSE,85.11,15,FALSE,1),
(100,'Dental Scaling and Polishing Canine L   (< 50 kg)','dentcl',(select pt_id from ptypes where pt_name='serv'),FALSE,102.13,15,FALSE,1),
(101,'Dental Scaling and Polishing Canine XL  (<100 kg)','dentcxl',(select pt_id from ptypes where pt_name='serv'),FALSE,119.15,15,FALSE,1),
(102,'Dental Scaling and Polishing Canine XXL (>100 kg)','dentcxxl',(select pt_id from ptypes where pt_name='serv'),FALSE,136.17,15,FALSE,1),
(103,'Dental Extraction','dentx',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(104,'Dental Extraction Complicated','dentxc',(select pt_id from ptypes where pt_name='serv'),FALSE,11.91,15,FALSE,1),
(105,'Grooming per 10 min','groom',(select pt_id from ptypes where pt_name='serv'),FALSE,4.68,15,FALSE,1),
(106,'General Anaesthesia Feline per 10 min','anesf',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(107,'General Anaesthesia Canine < 10 kg per 10 min','anesc1',(select pt_id from ptypes where pt_name='serv'),FALSE,8.52,15,FALSE,1),
(108,'Surgical Time per 10 min','surgt1',(select pt_id from ptypes where pt_name='serv'),FALSE,25.53,15,FALSE,1),
(109,'Professional Time per 10 min','proft1',(select pt_id from ptypes where pt_name='serv'),FALSE,17.02,15,FALSE,1),
(110,'Ultrasound Scan Time per 10 min','uss1',(select pt_id from ptypes where pt_name='serv'),FALSE,34.04,15,FALSE,1),
(111,'Urinalysis Dip-Stick','ur1',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(112,'Urinalysis microscopic crystals','ur2',(select pt_id from ptypes where pt_name='serv'),FALSE,6.81,15,FALSE,1),
(113,'Urinalysis microscopic cytology','ur3',(select pt_id from ptypes where pt_name='serv'),FALSE,12.77,15,FALSE,1),
(114,'Visit within 20 miles','visit1',(select pt_id from ptypes where pt_name='serv'),FALSE,34.04,15,FALSE,1),
(115,'Visit per extra mile','visit2',(select pt_id from ptypes where pt_name='serv'),FALSE,0.68,15,FALSE,1),
(116,'Xray 1st Plate','xray1',(select pt_id from ptypes where pt_name='serv'),FALSE,29.79,15,FALSE,1),
(117,'Xray 2nd Plate','xray2',(select pt_id from ptypes where pt_name='serv'),FALSE,21.28,15,FALSE,1),
(118,'Xray 3rd Plate','xray3',(select pt_id from ptypes where pt_name='serv'),FALSE,12.77,15,FALSE,1),
(119,'Xray Same Plate 1 more Exposure','xray4',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(120,'Tel. advice per 10 min','tel1',(select pt_id from ptypes where pt_name='serv'),FALSE,12.77,15,FALSE,1),
(121,'Hospitalisation Feline per night','hosf',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(122,'Hospitalisation Canine S   (< 10 kg) per night','hoscs',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(123,'Hospitalisation Canine M   (< 20 kg) per night','hoscm',(select pt_id from ptypes where pt_name='serv'),FALSE,6.81,15,FALSE,1),
(124,'Hospitalisation Canine L   (< 50 kg) per night','hoscl',(select pt_id from ptypes where pt_name='serv'),FALSE,10.21,15,FALSE,1),
(125,'Hospitalisation Canine XL  (<100 kg) per night','hoscxl',(select pt_id from ptypes where pt_name='serv'),FALSE,12.77,15,FALSE,1),
(126,'Hospitalisation Canine XXL (>100 kg) per night','hoscxxl',(select pt_id from ptypes where pt_name='serv'),FALSE,17.02,15,FALSE,1),
(127,'Repeat Prescription','reppre',(select pt_id from ptypes where pt_name='serv'),FALSE,4.26,15,FALSE,1),
(128,'Died naturally','diednat',(select pt_id from ptypes where pt_name='other'),FALSE,0.00,15,FALSE,null),
(129,'Dead On Arrival','doa',(select pt_id from ptypes where pt_name='other'),FALSE,0.00,15,FALSE,null),
(130,'Vacc. Canine DHPPi+L2 1st incl. 2nd','vacc61',(select pt_id from ptypes where pt_name='vac'),TRUE,34.04,13,FALSE,1),
(131,'Vacc. Canine DHPPi+L2 2nd','vacc62',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(132,'Vacc. Canine DHPPi+L2 2nd only','vacc621',(select pt_id from ptypes where pt_name='vac'),TRUE,20.43,13,FALSE,1),
(133,'Vacc. Canine DHPPi+L2 Booster','vacc6b',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(134,'Vacc. Canine DHPPi 1st incl. 2nd','vacc41',(select pt_id from ptypes where pt_name='vac'),TRUE,29.79,13,FALSE,1),
(135,'Vacc. Canine DHPPi 2nd','vacc42',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(136,'Vacc. Canine DHPPi 2nd only','vacc421',(select pt_id from ptypes where pt_name='vac'),TRUE,15.32,13,FALSE,1),
(137,'Vacc. Canine DHPPi Booster','vacc4b',(select pt_id from ptypes where pt_name='vac'),TRUE,23.83,13,FALSE,1),
(138,'Vacc. Canine Kennel Cough','vacckc',(select pt_id from ptypes where pt_name='vac'),TRUE,17.02,13,FALSE,1),
(139,'Vacc. Canine Kennel Cough + other','vacckc2',(select pt_id from ptypes where pt_name='vac'),TRUE,12.77,13,FALSE,1),
(140,'Vacc. Rabies','vacrab',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(141,'Vacc. Feline4 + FeLV 1st incl. 2nd','vacf51',(select pt_id from ptypes where pt_name='vac'),TRUE,34.04,13,FALSE,1),
(142,'Vacc. Feline4 + FeLV 2nd','vacf52',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(143,'Vacc. Feline4 + FeLV 2nd only','vacf521',(select pt_id from ptypes where pt_name='vac'),TRUE,21.28,13,FALSE,1),
(144,'Vacc. Feline4 + FeLV Booster','vacf5b',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(145,'Vacc. Feline4 2nd','vacf42',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(146,'Vacc. Feline4 2nd only','vacf421',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(147,'Vacc. Feline4 Booster','vacf4b',(select pt_id from ptypes where pt_name='vac'),TRUE,21.28,13,FALSE,1),
(148,'Vacc. Equine Flu 1st incl. 2nd','vacef1',(select pt_id from ptypes where pt_name='vac'),TRUE,46.81,13,FALSE,1),
(149,'Vacc. Equine Flu 1st only','vacef11',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(150,'Vacc. Equine Flu 2nd','vacef2',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(151,'Vacc. Equine Flu 2nd only','vacef21',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(152,'Vacc. Equine Flu Booster','vacefb',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(153,'Vacc. Equine Tet 1st','vacet1',(select pt_id from ptypes where pt_name='vac'),TRUE,21.28,13,FALSE,1),
(154,'Vacc. Equine Tet Booster','vacetb',(select pt_id from ptypes where pt_name='vac'),TRUE,21.28,13,FALSE,1),
(155,'Vacc. Equine FT 1st incl. 2nd','vaceft1',(select pt_id from ptypes where pt_name='vac'),TRUE,59.57,13,FALSE,1),
(156,'Vacc. Equine FT 1st only','vaceft11',(select pt_id from ptypes where pt_name='vac'),TRUE,34.04,13,FALSE,1),
(157,'Vacc. Equine FT 2nd','vaceft2',(select pt_id from ptypes where pt_name='vac'),TRUE,0.00,13,FALSE,1),
(158,'Vacc. Equine FT Booster','vaceftb',(select pt_id from ptypes where pt_name='vac'),TRUE,21.28,13,FALSE,1),
(159,'Vacc. Equine EHV 1st','vaceh1',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(160,'Vacc. Equine EHV Booster','vacehb',(select pt_id from ptypes where pt_name='vac'),TRUE,25.53,13,FALSE,1),
(161,'Vacc. Rabbit Myxo','vaclmyxo',(select pt_id from ptypes where pt_name='vac'),TRUE,12.77,13,FALSE,1),
(162,'Vacc. Rabbit VHD','vaclvhd',(select pt_id from ptypes where pt_name='vac'),TRUE,12.77,13,FALSE,1),
(163,'Vacc. Canine Parvo','vaccp1',(select pt_id from ptypes where pt_name='vac'),TRUE,10.21,13,FALSE,1),
(164,'Tetanol','tet',(select pt_id from ptypes where pt_name='med'),TRUE,10.21,13,FALSE,1),
(165,'Prevacun FT','prevacft',(select pt_id from ptypes where pt_name='med'),TRUE,10.21,13,FALSE,1),
(166,'EHV1','ehv',(select pt_id from ptypes where pt_name='med'),TRUE,17.02,13,FALSE,1),
(167,'Cylap','cylap',(select pt_id from ptypes where pt_name='med'),TRUE,8.52,13,FALSE,1),
(168,'Nobivac Puppy P','nobipupp',(select pt_id from ptypes where pt_name='med'),TRUE,10.21,13,FALSE,1),
(169,'Onsior Tablets 80 mg','onsior80',(select pt_id from ptypes where pt_name='med'),TRUE,1.19,1,TRUE,2),
(170,'Vacc. Feline4 1st incl 2nd','vacf41',(select pt_id from ptypes where pt_name='vac'),TRUE,25,13,FALSE,1),
(171,'Drop Administration','drop',(select pt_id from ptypes where pt_name='serv'),FALSE,0.85,15,FALSE,1);

/*('Artificial Insemination Cow excl. semen price', 'aib', 10, 1, 15),
 *('Künstliche Besamung Kuh excl. Samen', 'kbb', 15, 2, 15) for Austria;*/

insert into vtypes(vt_id,vt_type) values
 (1,  'DHPPi'),
 (2,  'DHPPi+L'),
 (3,  'Parvo'),
 (4,  'Kennel Cough'),
 (5,  'Rabies'),
 (6,  'RCP'),
 (7,  'FeLV'),
 (8,  'RCP+FeLV'),
 (9,  'Chlam'),
 (10, 'RCP+Chlam'),
 (11, 'RCP+Chlam+FeLV'),
 (12, 'EqFlu'),
 (13, 'EqFlu+Tet'),
 (14, 'Tetanus'),
 (15, 'EHV'),
 (16, 'Myxo'),
 (17, 'RHD');

insert into vaccinations -- hierwei
 (vac_id, vac_type, vac_prid, vac_sid, vac_validity, vac_spec)
 values
( 1, 2, 20, 130, 1, 1),
( 2, 2, 20, 131, 2, 1),
( 3, 2, 20, 132, 2, 1),
( 4, 2, 20, 133, 2, 1),
( 5, 1, 20, 134, 1, 1),
( 6, 1, 20, 135, 2, 1),
( 7, 1, 20, 136, 2, 1),
( 8, 1, 20, 137, 2, 1),
( 9, 4, 29, 138, 2, 1),
(10, 4, 29, 139, 2, 1),
(11, 5, 31, 140, 6, 4095),
(12, 8, 23, 141, 1, 2),
(13, 8, 23, 142, 2, 2),
(14, 8, 23, 143, 2, 2),
(15, 8, 23, 144, 2, 2),
(16, 7, 24, 145, 1, 2),
(17, 7, 24, 146, 2, 2),
(18, 7, 24, 147, 2, 2),
(19, 12, 24, 148, 2, 2),
(20, 12, 33, 149, 1, 32),
(21, 12, 33, 150, 1, 32),
(22, 12, 33, 151, 4, 32), -- check mfs here
(23, 12, 33, 152, 4, 32),
(24, 14, 33, 153, 4, 32),
(25, 14, 164, 154, 2, 32),
(26, 13, 165, 155, 6, 32),
(27, 13, 34, 156, 1, 32),
(28, 13, 34, 157, 1, 32),
(29, 13, 34, 158, 4, 32),
(30, 15, 34, 159, 4, 32),
(31, 15, 34, 160, 2, 32),
(32, 16, 166, 161, 1, 32),
(33, 17, 166, 162, 2, 32),
(34, 3, 168, 163, 1, 1);

insert into symptoms(symptom, sy_short) values ('',''),('anal glands','ag'),('arthrologic','arth'),('cardiac','card'),('central nervous','cns'),('dental','dent'),('dermatologic','derm'),('ears','ears'),('gastrologic','gast'),('genital','genit'),('hepatic','hepat'),('intestinal','int'),('muscular','musc'),('nasal','nasal'),('neoplastic','np'),('obstetric','obst'),('ophthalmologic','ophth'),('oropharyngeal','oroph'),('pancreatic','panc'),('pulmonary','pulm'),('renal','renal'),('reproductive','repr'),('respiratory','resp'),('skeletal','skel'),('spinal','spin'),('standard surgery','stsrg'),('unwell','unwel'),('urinary','urin'),('vaccination','vacc'),('vascular','vasc'),('ektoparasites','ekp'),('endoparasites','enp');

insert into chronics (chr_name) values
 ('allergic'),
 ('arthrologic'),
 ('bronchial'),
 ('cardiac'),
 ('dermatologic'),
 ('ears'),
 ('eyes'),
 ('hepatic'),
 ('intestinal'),
 ('neoplastic'),
 ('pancreatic'),
 ('renal'),
 ('urinary');

insert into applications (app_keyword) values
 ('injection'), ('%dministr%|%ispense%');

insert into app2prod (a2p_prid,a2p_prod) values
 (1,1), (10,1), (11,1), (12,1), (13,1), (17,1), (28,1), (36,1);

--insert into wd_apps(wda_app) values ('i.m.'), ('i.v.'), ('s.c.'), ('p.o.'),
--       ('i.m. 2'), ('i.v. 2'), ('s.c. 2'), ('p.o. 2');
