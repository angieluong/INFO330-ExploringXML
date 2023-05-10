import sqlite3
import sys
import xml.etree.ElementTree as ET

# Incoming Pokemon MUST be in this format
#
# <pokemon pokedex="" classification="" generation="">
#     <name>...</name>
#     <hp>...</name>
#     <type>...</type>
#     <type>...</type>
#     <attack>...</attack>
#     <defense>...</defense>
#     <speed>...</speed>
#     <sp_attack>...</sp_attack>
#     <sp_defense>...</sp_defense>
#     <height><m>...</m></height>
#     <weight><kg>...</kg></weight>
#     <abilities>
#         <ability />
#     </abilities>
# </pokemon>

conn = sqlite3.connect('pokemontest.sqlite')
c = conn.cursor()

# Read pokemon XML file name from command-line
# (Currently this code does nothing; your job is to fix that!)
if len(sys.argv) < 2:
    print("You must pass at least one XML file name containing Pokemon to insert")

for i, arg in enumerate(sys.argv):
    # Skip if this is the Python filename (argv[0])
    if i == 0:
        continue

    elemtree = ET.parse(arg)
    elemtreeroot = elemtree.getroot()
    
    types = []
    abilities = []
    
    generation = int(elemtreeroot.attrib['generation'])
    pokedexNumber = int(elemtreeroot.attrib['pokedexNumber'])
    name = elemtreeroot.find('name').text
    classification = elemtreeroot.attrib['classification']
    for t in elemtreeroot.findall('type'):
        types.append(t.text)
    hp = int(elemtreeroot.find('hp').text)  
    attack = int(elemtreeroot.find('attack').text)
    defense = int(elemtreeroot.find('defense').text)
    speed = int(elemtreeroot.find('speed').text)
    sp_attack = int(elemtreeroot.find('sp_attack').text)
    sp_defense = int(elemtreeroot.find('sp_defense').text)
    height = float(elemtreeroot.find('height/m').text)
    weight = float(elemtreeroot.find('weight/kg').text)
    for a in elemtreeroot.findall('abilities/ability'):
        abilities.append(a.text)

    c.execute("SELECT * FROM pokemon WHERE pokedex_number = ?", (pokedexNumber,))
    if c.fetchone():
        print(name + " already exists in the database")
    else:
        # pokemon_abilities table
        for a in abilities:
            c.execute("SELECT id FROM ability WHERE name = (?)", (a,))
            ab_id = c.fetchone()
            c.execute("INSERT INTO pokemon_abilities VALUES (?, ?)",
                      (pokedexNumber, *ab_id))
        
        # classification table
        c.execute("SELECT id FROM classification WHERE text = (?)",
                  (classification,))
        class_id = c.fetchone()
        c.execute("INSERT INTO classification VALUES (?, ?)",
                  (pokedexNumber, *class_id))
        
        # #pokemon_types_view table
        t1 = types[0]
        t2 = types[1]
        c.execute("SELECT id FROM type WHERE name = (?)",
                  (t1,))
        t1_id = c.fetchone()
        c.execute("SELECT id FROM type WHERE name = (?)",
                  (t2,))
        t2_id = c.fetchone()
        c.execute("INSERT INTO pokemon_type VALUES (?, ?, ?)",
                  (pokedexNumber, *t1_id, '1'))
        c.execute("INSERT INTO pokemon_type VALUES (?, ?, ?)",
                  (pokedexNumber, *t2_id, '2'))
        
        # pokemon table
        c.execute("INSERT INTO pokemon VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                 (pokedexNumber, pokedexNumber, name, *class_id, generation, hp, attack, defense,
                  speed, sp_attack, sp_defense, None, None, None, None, None, None, None, None))
        
        
        print(name + " successfully added to the database")
c.close()