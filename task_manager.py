import  mysql.connector

def pripojeni_db(database_name="mydb"):
    #Funkce pro připojení k databázi MySQL

    try:
        databaze = mysql.connector.connect(
            host="localhost",
            user="root",
            password="********",      #DŮLEŽITÉ - ZMĚŇTE HESLO NA SVÉ VLASTNÍ - své jsem smazal.
            database=database_name
        )

        if databaze.is_connected():
            print("\nSuccess! (Úspěšně připojeno k databázi mydb)")
            return databaze

    except mysql.connector.Error as e:
        print(f"Chyba při připojování: {e}")
        return None

def vytvoreni_tabulky(db_connection):
    #Funkce pro vytvoření tabulky 'ukoly', pokud ještě neexistuje
    cursor = db_connection.cursor()
    cursor.execute("SHOW TABLES LIKE 'ukoly'")
    vysledek = cursor.fetchone()
    
    if vysledek:
        print("\nTabulka 'ukoly' už existuje. Přeskakuji vytváření.")
    else:
        print("\nTabulka neexistuje. Vytvořila se.\n")
        cursor.execute("""
            CREATE TABLE ukoly (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nazev VARCHAR(255) NOT NULL,
                popis TEXT,
                stav ENUM('nezahájeno', 'probíhá', 'hotovo') DEFAULT 'nezahájeno',
                datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Tabulka 'ukoly' byla úspěšně vytvořena.\n")

    cursor.close()

def pridat_ukol():
    #Funkce pro přidání nového úkolu do tabulky 'ukoly'
    while True:
        nazev_ukolu = str(input("Zadej nazev ukolu: ")).strip()
        popis_ukolu = str(input("Zadej popis ukolu: ")).strip()

        if popis_ukolu and nazev_ukolu:
                break
        print("\n Název a popis úkolu nemohou být prázdné. Zkuste to znovu.\n")

    try:
        cursor = db_connection.cursor()
        
        sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
        hodnoty = (nazev_ukolu, popis_ukolu)
        
        cursor.execute(sql, hodnoty)
        db_connection.commit()
        
        print(f"\n[OK] Úkol '{nazev_ukolu}' byl úspěšně uložen.")
        cursor.close()
        
    except Exception as e:
        print(f"\n[CHYBA] Nepodařilo se uložit úkol: {e}")

def zobrazit_ukoly(db_connection):
    #Funkce pro zobrazení všech úkolů v tabulce 'ukoly'
    nalezeno_ukolu = False

    print("\n--- SEZNAM VŠECH ÚKOLŮ ---")
    try:
        cursor = db_connection.cursor()
        
        cursor.execute("SELECT * FROM ukoly")
        vsechny_ukoly = cursor.fetchall()
        
        if not vsechny_ukoly:
            print("Seznam úkolů je prázdný.")
            cursor.close()
        else:
            for ukol in vsechny_ukoly:
                print(f"ID: {ukol[0]} | Stav: {ukol[3]} | Název: {ukol[1]}")
                print(f"Popis: {ukol[2]} | Datum: {ukol[4]}")
                print("-" * 30)

        print("\n--- ZDE JSOU POUZE ÚKOLY PROBÍHÁ / HOTOVO ---")
        
        if not vsechny_ukoly:
            print("Dle filtru PROBÍHÁ/HOTOVO nic nenazeleno.")
        else:
            for ukol in vsechny_ukoly:
                 if ukol[3] in ('probíhá', 'hotovo'):
                      nalezeno_ukolu = True

                      print(f"ID: {ukol[0]} | Stav: {ukol[3]} | Název: {ukol[1]}")
                      print(f"Popis: {ukol[2]} | Datum: {ukol[4]}")
                      print("-" * 30)
            if not nalezeno_ukolu:
                print("Dle filtru PROBÍHÁ/HOTOVO nic nenalezeno.")
        cursor.close()
        
    except Exception as e:
        print(f"\n[CHYBA] Nepodařilo se načíst úkoly: {e}")
        db_connection.rollback()


def aktualizovat_ukoly():
    #Funkce pro aktualizaci stavu úkolu v tabulce 'ukoly'
    print("\n--- SEZNAM VŠECH ÚKOLŮ ---")
    try:
        cursor = db_connection.cursor()
        
        cursor.execute("SELECT * FROM ukoly")
        vsechny_ukoly = cursor.fetchall()
        
        if not vsechny_ukoly:
            print("Seznam úkolů je prázdný.")
            cursor.close()
        else:
            for ukol in vsechny_ukoly:
                print(f"ID: {ukol[0]} | Stav: {ukol[1]} | Název: {ukol[3]}")
                print("-" * 30)

        zmena_id = int(input("\nZadejte ID úkolu, který chcete aktualizovat: "))
        novy_stav = input("\nZadejte nový stav úkolu (probíhá, hotovo): ").strip()

        sql = "UPDATE ukoly SET stav = %s WHERE id = %s"
        hodnoty = (novy_stav, zmena_id)
        cursor.execute(sql, hodnoty)
        db_connection.commit()
        print(f"\n[OK] Úkol s ID {zmena_id} byl úspěšně aktualizován na stav '{novy_stav}'.")
        cursor.close()
        
    except Exception as e:
        print(f"\n[CHYBA] Nepodařilo se načíst úkoly: {e}")
        db_connection.rollback()

def odstranit_ukoly():
    #Funkce pro odstranění úkolu z tabulky 'ukoly'
    print("\n--- SEZNAM VŠECH ÚKOLŮ ---")

    try:
        cursor = db_connection.cursor()
        cursor.execute("SELECT * FROM ukoly")
        vsechny_ukoly = cursor.fetchall()
        
        if not vsechny_ukoly:
            print("[INFO] Seznam úkolů je prázdný. Není co mazat.")
            cursor.close()
            return
            
        for ukol in vsechny_ukoly:
            print(f"ID: {ukol[0]} | Stav: {ukol[3]} | Název: {ukol[1]}")
            print(f"Popis: {ukol[2]} | Datum: {ukol[4]}")
            print("-" * 30)

        zmena_id = int(input("\nZadejte ID úkolu, který chcete odstranit: "))

        sql = ("DELETE FROM ukoly WHERE id = %s")
        
        hodnoty = (zmena_id,) 
        cursor.execute(sql, hodnoty)
        
        if cursor.rowcount == 0:
             print(f"\n[INFO] Úkol s ID {zmena_id} nebyl nalezen. Nic nebylo smazáno.")
        else:
             db_connection.commit()
             print(f"\n[OK] Úkol s ID {zmena_id} byl úspěšně smazán.")
             
        cursor.close()
            
    except ValueError:
        print("\n[CHYBA] Neplatný vstup. Zadejte prosím číslo ID.")
        db_connection.rollback()
        
    except Exception as e:
        print(f"\n[KRITICKÁ CHYBA] Při mazání došlo k chybě: {e}")
        db_connection.rollback()

def hlavni_menu():
    #Hlavní menu pro správu úkolů a výběr akcí
    while True:
    try:
        volba = int(input(
            "\n"
            "Správce úkolů - Hlavní menu\n"
            "1. Přidat úkol\n"
            "2. Zobrazit úkoly\n"
            "3. Aktualizovat úkol\n"
            "4. Odstranit úkol\n"
            "5. Ukončit program\n"
            "Vyberte možnost (1-5): "
        ))

        match volba:
            case 1:
                vytvoreni_tabulky(db_connection)
                pridat_ukol()
            case 2:
                zobrazit_ukoly(db_connection)
            case 3:
                aktualizovat_ukoly()
            case 4:
                odstranit_ukoly()
            case 5:
                print("Konec programu.\n")
                break
            case _:
                print("Neplatná volba.")

    except ValueError:
        print("Musíš zadat číslo.")
   
if __name__ == "__main__":
    db_connection = pripojeni_db() 
    
    if db_connection:
        hlavni_menu()
