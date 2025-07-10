# Abgabe Modellierung
## MOD.1
- Bitte CQs nummerieren ✅
- Zu den Verweisen auf Mekan: Mekan taucht vermutlich nicht im Datensatz auf, deswegen wäre es später sinnvoll, Beispiele aus dem gegebenen Datensatz zu nehmen → Warum? ✅
- Zu "Welche Maße hat die Pizza?" und "Welche Form hat die Pizza?": Frage gern konkreter, mit Beispiel stellen: "Welche Maße hat die Margherita bei Tony’s Pizza Place?" → Warum? ✅
- Zu "Kann ich Brokkoli auf eine Pizza Hawaii legen?" und "Ist eine Pizza Hawaii ohne Ananas immer noch eine Pizza Hawaii?": diese Fragen erscheinen mir eher religiöser Natur - ich weiß nicht wie man das anhand der Daten beanworten könnte, aber lassen Sie sie gern drin. Im Text danach schildern Sie, wie sie auf die Frage gekommen sind. Sie können natürlich als Domänenexperten alle Arten von Pizzen mit den erlaubten Belegen modelieren, vermutlich wird das aber beim Ausweiten auf den gesamten Datensatz sehr umständlich ✅
- Schauen Sie sich den Datensatz an und überlegen Sie, ob sie die vorgeschlagene Modellierung beibehalten anpassen könnten um die anderen verfügbaren Daten miteinzubeziehen: Geogr. Ort (Straße, Stadt) und Währung ✅

## MOD.2
- Bewertung auf Google: nicht in der Datenquelle gegeben und taucht nicht in den Kompetenzfragen auf → Entfernt ✅
- Es gibt in der Modellierung keine Möglichkeit Größe und Preis mit Einheiten zu versehen → 
- hier taucht die Adresse auf, jedoch als einfacher String. Das könnte man eventuell ausbauen (Modellierung von Straßen + Nummern, Städten und Ländern)
- Die Modellierung, die eine Pizza mit Pizzeria und Preis verknüpft (in der Modellierung werden Constraints genannt) erscheint unnatürlich. Denken Sie noch einmal über den Tip nach, der zum Subtask MOD.1 auf moodle steht. Eventuell wäre das Erstellen einer neuen Klasse angebracht (z.B. `menu item`)


## OWL
- die constraints, die für Pizzeria und Preis in der `terminology-hierarchy.pdf` beschrieben wurden, fehlen
- Die Klase `PizzaBeiMekan` hat kein Constraint dafür, dass die Pizza bei Mekan angeboten wird
- Subtask OWL.5: bewertungAufGoogle, groesse, preis hat keine Domain
- Subtask OWL.6: fehlt (zB `preis` ist functional)
- Subtask OWL.7: Label und Kommentare fehlen an den Properties