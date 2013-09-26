>>> mydb="c:/1most/perdict/p/qiys.dic"
>>> conn=sqlite3.connect(mydb)
>>> curson=conn.cursor()
>>> curson.execute("""create table pdict
(word text, sentence text, date text)""")
<sqlite3.Cursor object at 0x0269D320>
>>> curson.execute("""insert into pdict values
("example","Setting a good example for your kids takes all the fun out of your life  of middle age.", "2011-05-21")
""")
