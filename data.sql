--Table pour l'etat des gens dans chaque ville
/*
CREATE TABLE data_utile AS
SELECT 'April_1'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_April_1 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'April_10'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_April_10 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'April_20'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_April_20 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'May_1'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_May_1 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'May_10'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_May_10 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'May_19'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_May_19 join citizens on id_patient = citizens.id) group by hometown,current_state
UNION ALL
SELECT 'June_1'  AS jour, hometown,current_state, count(*) as 'number'
from (patients_June_1 join citizens on id_patient = citizens.id) group by hometown,current_state
*/

--table regroupant toutes les données
/*
CREATE TABLE data_complete AS
SELECT 'April_1'  AS jour, * 
from (patients_April_1 join citizens on id_patient = citizens.id)
UNION ALL
SELECT 'April_10'  AS jour,*
from (patients_April_10 join citizens on id_patient = citizens.id)
UNION ALL
SELECT 'April_20'  AS jour, *
from (patients_April_20 join citizens on id_patient = citizens.id) 
UNION ALL
SELECT 'May_1'  AS jour, *
from (patients_May_1 join citizens on id_patient = citizens.id) 
UNION ALL
SELECT 'May_10'  AS jour, *
from (patients_May_10 join citizens on id_patient = citizens.id)
UNION ALL
SELECT 'May_19'  AS jour, *
from (patients_May_19 join citizens on id_patient = citizens.id)
*/



--Commande utiles sur "data_utile"

--SELECT * from data_utile where jour = 'April_20' and current_state like 'Dead %' and hometown = 'Noltrame'
--SELECT * from data_utile where jour = 'April_20' 
--SELECT * from data_utile where current_state like 'Dead %'
--SELECT * from data_utile where hometown = 'Noltrame'



--Les hommes semblent etre legerement plus sensibles que les femmes (plus de morts pour moins d'individus)

--SELECT sex, current_state, count(*) from data_complete  GROUP by sex, current_state



-- duree de moyenne depuis laquelle les gens sont malades (= duree maladie / 2)

--SELECT AVG(time_since) from data_complete where current_state = "Infected"


--Les morts et les recovered semblent avoir le meme temps d'infection donc gamma est le meme

--SELECT AVG(d1.time_since) from data_complete as d1 join data_complete as d2 on d1.id = d2.id and d1.jour = 'May_1' and d2.jour = 'May_19' AND d1.current_state = "Infected" and d2.current_state like 'Dead%'

--SELECT AVG(d1.time_since) from data_complete as d1 join data_complete as d2 on d1.id = d2.id and d1.jour = 'May_1' and d2.jour = 'May_19' AND d1.current_state = "Infected" and d2.current_state like 'Recovered%'



--Aucun recovered ne semble retomber malade

--SELECT * from data_complete as d1 join data_complete as d2 on d1.id = d2.id and d1.jour = 'April_20' and d2.jour = 'May_19' AND d1.current_state = "Recovered" and d2.current_state like 'Infec%'
