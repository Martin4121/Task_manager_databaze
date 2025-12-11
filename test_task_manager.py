
import unittest
import mysql.connector

from task_manager import pripojeni_db, pridat_ukol, aktualizovat_ukoly, odstranit_ukoly, vytvoreni_tabulky

TEST_DB_NAME = "test_mydb" 

class TestUkoly(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Metoda spuštěná jednou PŘED VŠEMI testy. Zajišťuje, že existuje testovací DB."""
        global db_connection
        
        cls.conn_no_db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="*********",        # DŮLEŽITÉ - ZMĚŇTE HESLO NA SVÉ VLASTNÍ - své jsem smazal.
            database=""
        )
        if not cls.conn_no_db.is_connected():
            raise Exception("Nelze se připojit k DB serveru pro testovací setup.")
        
        cursor = cls.conn_no_db.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_NAME}")
        cursor.close()
        cls.conn_no_db.close()
        
        db_connection = pripojeni_db(database_name=TEST_DB_NAME)
        
        if db_connection is None:
             raise Exception("Nepodařilo se připojit k nově vytvořené testovací DB.")

        vytvoreni_tabulky(db_connection)

    def setUp(self):
        cursor = db_connection.cursor()
        cursor.execute("DELETE FROM ukoly")
        db_connection.commit()
        cursor.close()
        
        self.test_id = 999
        self.test_nazev = "Testovaci Ukol"
        self.test_popis = "Popis pro mazani"
        self.stav_nezahajeno = "nezahájeno"
        
        cursor = db_connection.cursor()
        sql = "INSERT INTO ukoly (id, nazev, popis, stav) VALUES (%s, %s, %s, %s)"
        hodnoty = (self.test_id, self.test_nazev, self.test_popis, self.stav_nezahajeno)
        cursor.execute(sql, hodnoty)
        db_connection.commit()
        cursor.close()

    def test_01_pridani_ukolu_pozitivni(self):
        """Pozitivní test: Ověří, zda je nový úkol správně vložen do DB."""
        
        novy_nazev = "Novy pozitivni test"
        novy_popis = "Popis pozitivniho ukolu"
        
        cursor = db_connection.cursor()
        sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
        cursor.execute(sql, (novy_nazev, novy_popis))
        db_connection.commit()
        
        cursor.execute("SELECT nazev FROM ukoly WHERE nazev = %s", (novy_nazev,))
        vysledek = cursor.fetchone()
        cursor.close()
        
        self.assertIsNotNone(vysledek, "Úkol nebyl nalezen v databázi.")
        self.assertEqual(vysledek[0], novy_nazev, "Název úkolu se neshoduje.")

    def test_02_pridani_ukolu_negativni(self):
        """Negativní test: Ověří, že kód neumožní vložení úkolu bez názvu (porušení NOT NULL)."""
        
        nevalidni_hodnota = None 
        validni_popis = "Popis"
        
        cursor = db_connection.cursor()
        sql = "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)"
        
        with self.assertRaises(mysql.connector.IntegrityError):
             cursor.execute(sql, (nevalidni_hodnota, validni_popis))
             db_connection.commit()
             
        cursor.close()


    def test_03_aktualizace_ukolu_pozitivni(self):
        """Pozitivní test: Ověří, zda je stav úkolu správně aktualizován (z nezahájeno na hotovo)."""
        
        novy_stav = "hotovo"
        
        cursor = db_connection.cursor()
        sql = "UPDATE ukoly SET stav = %s WHERE id = %s"
        cursor.execute(sql, (novy_stav, self.test_id))
        db_connection.commit()
        
        cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (self.test_id,))
        skutecny_stav = cursor.fetchone()
        cursor.close()
        
        self.assertEqual(skutecny_stav[0], novy_stav, "Stav úkolu nebyl správně aktualizován.")

    def test_04_aktualizace_ukolu_negativni(self):
        """Negativní test: Ověří, že kód neumožní nastavit neexistující stav (porušení ENUM)."""
        
        nevalidni_stav = "vymysleny_stav"
        
        cursor = db_connection.cursor()
        sql = "UPDATE ukoly SET stav = %s WHERE id = %s"
        
        with self.assertRaises(mysql.connector.errors.DatabaseError):
             cursor.execute(sql, (nevalidni_stav, self.test_id))
             db_connection.commit()
             
        cursor.close()

    def test_05_odstraneni_ukolu_pozitivni(self):
        """Pozitivní test: Ověří, že existující úkol je úspěšně smazán."""
        
        cursor = db_connection.cursor()
        sql = "DELETE FROM ukoly WHERE id = %s"
        cursor.execute(sql, (self.test_id,))
        db_connection.commit()

        cursor.execute("SELECT * FROM ukoly WHERE id = %s", (self.test_id,))
        vysledek = cursor.fetchone()
        cursor.close()
        
        self.assertIsNone(vysledek, "Úkol nebyl po smazání odstraněn z databáze.")

    def test_06_odstraneni_ukolu_negativni(self):
        """Negativní test: Ověří, že mazání neexistujícího ID nezpůsobí chybu."""
        
        neexistujici_id = 999999
        
        cursor = db_connection.cursor()
        sql = "DELETE FROM ukoly WHERE id = %s"
        cursor.execute(sql, (neexistujici_id,))
        
        pocet_smazanych = cursor.rowcount
        db_connection.commit()
        cursor.close()

        self.assertEqual(pocet_smazanych, 0, "Byl smazán řádek, ačkoli ID neexistovalo.")


if __name__ == '__main__':
    unittest.main()