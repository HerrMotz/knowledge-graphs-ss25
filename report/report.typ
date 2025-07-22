#import "dvd.typ": *
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *

#show: dvdtyp.with(
  main_title: [Bericht zum Modul\ \"Knowledge Graphs\"],
  title: [Bericht zum Modul \"Knowledge Graphs\"],
  subtitle: [Im Sommersemester 2025 von König-Ries, Bachinger, Enderling],
  author: "Daniel Motz",

)

#show: codly-init.with()
#codly(languages: codly-languages)

#set text(lang: "de")
#set par(justify: true)

#set underline(stroke: 1.5pt+lime, offset: 2pt)

#let check = [✅]

#let theorem-style = builder-thmbox(color: colors.at(3), shadow: (offset: (x: 3pt, y: 3pt), color: luma(70%)))
#let theorem = theorem-style("theorem", "Theorem")
#let beispiel = theorem-style("Beispiel", "Beispiel")

#let definition-style = builder-thmline(color: colors.at(8))
#let definition = definition-style("definition", "Definition")
#let diskussion = definition-style("diskussion", "Diskussionsanregung")

#outline(depth: 2)

#show heading.where(depth: 1): it => {
  if not state("in-outline", false).get() {
    pagebreak(weak: true)
  }
  it
}

= Modellierung

Die Aufgaben in diesem Abschnitt waren das systematische Herangehen an das Modellieren von Wissensgraphen kennenzulernen, eigene Competency Questions zu einem gegebenen Thema (hier die Domäne Pizza) zu erstellen, den Begriff der Concept Hierarchy zu erfassen sowie die wesentlichen Konzepte des OntoClean-Ansatzes zu verstehen und auf die erstellte Ontologie anzuwenden.

#grid(columns: (2fr, 2fr), column-gutter: 2em, [
== Competency Questions

+ Welche #underline("Toppings") hat eine #underline[Pizza] Hawaii?
+ Welche #underline[Teigsorten] gibt es?
+ Welche #underline[Saucen] können auf einer Pizza sein?
+ Kann ich #underline[Brokkoli] auf eine #underline[Pizza Hawaii] legen?
+ Ist eine Pizza Hawaii ohne #underline[Ananas] immer noch eine Pizza Hawaii?
+ Was gehört zu einer Pizza #underline[Margherita]?
+ Welche Zutaten hat eine #underline[Calzone]?
+ Welche #underline[Sorten von Pizza] gibt es?
+ Welche Pizzen sind #underline[vegetarisch]?
+ Welche Pizzen sind #underline[vegan]?
+ Gibt es #underline[glutenfreie] Pizzen?
+ Welche Pizzen enthalten Mozzarella?
+ Welche Pizzen gibt es bei #underline[Mekan]?
+ Wie wird die "Pizza FCC" bei Mekan gemacht?
+ Wie viel kostet eine Pizza Frutti di Mare bei Giovannis Pizzeria?
+ Welche #underline[Maße] hat die Pizza?
+ Welche #underline[Form] hat die Pizza?
+ Welche Pizza bei Mekan ist am #underline[billigsten]?
+ Welche Pizzen enthalten #underline[Schinken]?

+ Welche #underline[laktosefreien] Pizzen gibt es?
+ Welche Pizzen sind mit #underline[Tomaten] belegt?

], [
  == Important and Derived Terms
  *Dickgedruckte* Terme sind für die Termhierarchie relevant.
  #v(2mm)
  - Topping #sym.arrow *Zutat*

  - *Pizza*

  - *Teigsorte*

  - *Sauce*

  - Brokkoli #sym.arrow *konkrete Zutat* die zu einer Kind von Pizza gehört

  - *Pizza Hawaii* #sym.arrow Eine *Kind/Art* einer Pizza mit Einschränkungen im Wertebereich der möglichen Zutaten

  - Ananas #sym.arrow *konkrete Zutat*

  - *Pizza Margherita* #sym.arrow Eine *Kind*, wie Pizza Hawaii

  - *Calzone* #sym.arrow Ebenfalls eine *Kind* von Pizza, allerdings ohne strikte Einschränkungen im Wertebereich der Zutaten

  - *Sorte* #sym.arrow *Kinds* von Pizza
  - *vegetarisch* #sym.arrow Ein direktes Prädikat für *Zutat* und ein Inferiertes für Pizza, sofern alle Zutaten der Pizza das Prädikat tragen.
  - *vegan* #sym.arrow Ebenfalls Prädikat für *Zutat* und ein Inferiertes für Pizza
  - *glutenfrei* #sym.arrow Analog zu vegetarisch, ...
  - *Mekan* #sym.arrow Eine *Pizzeria*
  - *Form* / *Maße*
  - billigsten #sym.arrow *Preis*
  - *Schinken*

  - *laktosefrei*
])


#pagebreak()

== Terms and Classes

Unsere Ontologie modelliert nicht konkrete, real existierende Pizzen, sondern Einträge einer Speisekarte. Anfangs modellierten wir eine am Prozess der Fastfoodkette "Dominos" orientierte Kategorisierung. Wir stellten jedoch fest, dass dies aufwändig und zur Beantwortung der Competency Questions nicht notwendig ist. Wir stellten jedoch die Anforderung, dass die Ontologie sowohl Pizzen die in einer Pizzeria, als auch für solche, die in den "eigenen vier Wänden", produziert werden, abbilden kann. Die Klasse Pizza umfasst daher die für eine Pizza wesentlichen Eigenschaften, wie etwa eine Zutatenliste.

Wir entschieden außerdem, dass weit verbreitete Rezepturen, wie etwa "Pizza Hawaii", als Unterklasse von *Pizza* mit Einschränkungen im Wertebereich der Zutaten modelliert werden. Dafür ist es notwendig, dass wir entweder Klassen für Zutaten anlegen, wie etwa "Schinken" oder aber wir liefern zu unserer TBox eine ABox. Wir haben uns für letzteres entschieden. Dies entstand aus der CQ "Kann man eine Pizza Hawaii ohne Ananas herstellen".

Wir haben uns außerdem dazu entschieden, dass gewisse Zutaten eine eigene Klasse erhalten, nämlich Teig, Sauce und Käse, um erzwingen zu können, dass eine Pizza mindestens aus einem Teig und einer Sauce bestehen muss.

Zu Pizzerien haben wir folgende Gedanken: Eine Pizza kann bei einer Pizzeria hergestellt werden. Dann wird sie zu einem konkreten Preis verkauft und der Preis variiert zudem mit der Größe. In unserer Feldstudie im Raum Jena stellten wir fest, dass es Pizzerien gibt, die an ihrer Speisenkartentafel eigens Klassifizierungen vornehmen. So fanden wir beispielsweise die Aufschrift "Alle Pizzen mit Tomatensauce und Käse#super[g]". Dies lieferte die Idee, dass eine Pizza gewisse Mindestanforderungen in ihren Zutaten erfüllen muss. In unserer Ontologie wurde daher ursprünglich gefordert, dass eine Pizza aus den Zutaten "mindestens eine Sauce" und "genau einen Teig" bestehen muss. Es gibt allerdings Ausnahmen, wie etwa die "Pizza Bianca", die möglciherweise keine Sauce enthalten -- das Bestreichen mit Crème Fraîche ist zwar möglich, aber nicht notwendig. In der Abwägung zwischen einer *konzeptionell sauberen* und nicht *übermäßig restriktiven* Definition wurde entschieden zu definieren, dass eine Pizza mindestens eine Sauce oder einen Käse enthalten muss, um als solche zu gelten. Es gibt andere Gerichte, wie etwa Focaccia, die diese Zutatenkombinationen abdecken und damit nicht in die zu modellierende Domäne "Pizza" fallen.

Anfangs modellierten wir "Toppings" bzw. Beläge (bspw. Schinken, Brokkolli, Blumenkohl und Zwiebeln, aber auch Saucen) in der Klasse *Zutat* und fügten data properties für wie `istGlutenfrei` ein. Dies ersetzten wir durch Typen wie etwa `Glutenfreie`, `Vegetarische` und `Vegane`.

Wir haben Teig nicht als vegan modelliert, damit wir ggf. auch Teige mit Ei erlauben können. Die Einschränkung in vegetarisch erscheint sinnvoll, jedoch wird die Zubereitung des Teigs in unserer Ontologie nicht näher spezifiziert. 

Die Ontologie enthält ein Beispiel für eine unerfüllbare Klasse: `VegetarischePizza_Hawaii`, modelliert als Schnitt zwischen `Vegetarische_Pizza` und `Pizza_Hawaii`. Die Bedingungen sind also, dass jedes Individuum dieses Typs ausschließlich vegetarische Zutaten enthält, sowie die für eine Pizza Hawaii notwendigen (Ananas, Tomatensauce, Teig/Boden und Schinken). Da Schinken nicht den Typ `Vegetarische` besitzt, kann es die Anforderungen der Klasse `Vegetarische_Pizza` nicht erfüllen.

#bemerkung("Änderungen an der Ontologie basierend auf dem Feedback")[
  Obwohl die Aufgabenstellung zum Projekt folgendes erlaubte: #quote[The ontology should abstract knowledge about the domain, valid for the data at hand but potentially valid for other datasets (e.g., tables)], gab es Feedback, dass die Eigenschaft `bewertungAufGoogle` von Pizzerien nicht in den Daten begründet liegt und auch in keiner Competency Question erwähnt wird -- sie wurde daher entfernt.
]


== Informelle Hierarchisierung

#show link: it => underline(stroke: (paint: blue, thickness: 1pt, dash: "dashed"), offset: 2.5pt, it)

Die Datei befindet sich im Repositorium unter #link("week1/terminology-hierarchy.pdf")[`terminology-hierarchy.pdf`].

// TODO: fix, dass das nicht überdeckt wird
#place(bottom+left)[#v(1cm)\ #text(1.2em, super[g])"Milch"]


== OntoClean: Rigidity, Unity, Identity

Wir haben festellen müssen, dass die Validierung von Rigidity, Identity und Unity für die Klassen unserer Ontologie weder trivial, noch (zumindest in einigen Fällen) eindeutig ist. Die folgenden Modellierungen haben wir nach bestem Wissen und Gewissen derart vorgenommen, sodass diese einerseits widerspruchsfrei sind und andererseits (aus unserer Sicht) dem Zweck der Ontlogie entsprechen.

=== Rigidity

//Hiermit habe ich mich noch einmal ausführlich auseinandergesetzt -  unsere Modellierung ist schlüssig und widerspruchsfrei.

Von den Competency Questions ausgehend war es sinnvoll für Klassen wie *Pizza\_Hawaii* oder bspw. *Pizza\_bei\_Mekan* anti-rigidity $(~R)$ zu modellieren, denn man kann bspw. bei der Bestellung einer Pizza bestimmte Zutaten weglassen oder dazuwählen. Da jedoch eine Pizza Hawaii insbesondere durch die Zutat "Ananas" charakterisiert wird, sollte mindestens diese Zutat wesentlich für die Klassenzugehörigkeit sein. Eine Pizza ist allerdings noch dieselbe, wenn jemand die Ananas von ihr herunterisst, jedoch dann keine Pizza Hawaii mehr.

Die Klasse *Zutat* kann ebenso kritisch bewertet werden. Brokkolli muss nicht notwendigerweise Zutat einer Pizza sein. Im Rahmen der Competency Questions ist diese Unterscheidung irrelevant. Für eine kurze Zeit überlegten wir "Zutat" als Rolle zu definieren, sodass ein Produkt, bspw. Brokkoli, seine Eigenschaft als Zutat verlieren kann, sofern er keine Zutat bei einer Pizza ist. *Zutat* erhält daher $+R$, wie auch alle Unterklassen. Etwa als wir die property `enthaeltZutat` modellierten, war für die Beschreibung der range restriction notwendig die Vereinigung aller möglichen Zutatenklassen zu finden. Mit unserer Zutatenklassifizierung gab es jedoch Zutaten, die in keine Klasse fielen. Ein Beispiel hierfür ist Hinterkochschinken -- er enthält Gluten, ist nicht vegetarisch, kein Teig und so weiter. Es ergab daher Sinn die Klasse Zutaten einzufügen.

Für die restlichen Klassen entschieden wir, dass sie die Property $+R$ erhalten. Eine Pizza könnte zwar auch gegessen werden und eine Pizzeria kann auch auf indisches Essen umstellen, jedoch ist dies von unseren Competency Questions ausgehend keine potentielle Anfrage.

=== Identity

//Identity noch mal überdenken. Aus dem Zeitintervall vs. Dauer Beispiel werde ich nicht schlauer. Hieraus wird nur deutlich, dass diese beiden Klassen keine Subklassen voneinander sein dürfen. (s. Sack Video "5.7 EXTRA: More Ontology Evaluation")
// weitere Quelle: https://pubs.dbs.uni-leipzig.de/dc/files/GuarinoWeltyOntoCleanv3.pdf

Wir haben uns nachträglich dazu entschieden, ausschließlich die Klasse *Pizzeria* mit $+I$ zu modellieren und haben dafür die Eigenschaft "Adresse" hinzugefügt. In allen anderen Klassen lässt sich aus unserer Sicht nicht eindeutig sagen, ob zwei Instanzen gleich (oder unterschiedlich) sind. Diese enthalten dementsprechend $-I$.

=== Unity

//Quelle: Sack Video "5.7 EXTRA: More Ontology Evaluation" ab 19:45)

Instanzen der Klasse *Pizza*, so genannte Pizzen, bilden ein zusammenhängendes Ganzes und werden daher mit $+U$ markiert. Diese Eigenschaft wird logischerweise an alle Subklassen wie *Pizza_Hawaii* oder *Pizza_bei_Mekan* vererbt. Gleiches gilt für die Klasse *Pizzeria*.

Für die meisten anderen Klassen kann aus unserer Sicht keine eindeutige Aussage über deren Unity getroffen werden. Wenn wir die Klasse *Zutat* betrachten, enthält diese sowohl Instanzen, die als ein Ganzes angesehen werden _können_ (eine Tomate, ein Brokkolirösschen etc.), es gibt aber auch Zutaten, die eindeutig kein Unity-Kriterium erfüllen (Käseraspeln, Tomatensauce etc.). Dennoch haben wir uns dazu entschlossen, die Klasse *Zutat* sowie all ihre Subklassen als anti-unity ($~U$) zu modellieren und dementsprechend _alle_ in unserer Ontologie potentiell vorkommenden Zutaten nicht als ein physisches Ganzes zu betrachten. Beispielsweise betrachten wir anstatt einer Tomate eine Tomatenscheibe als Zutat, welche auch nach Teilen dieser immer noch eine Tomatenscheibe ist.

== Verbesserungsmöglichkeiten

Die Benennung der Klasse *Pizza* ist unklar, denn sie lässt weit offen, was mit einer Pizza gemeint ist; erst der Kommentar schafft Klarheit.

== Ontologie
Die Datei befindet sich ebenfalls im Repositorium unter #link("week1/ontology.xml")[`ontology.xml`].

=== Anreichung der Properties <abs:anreichung_properites>

Im Zuge der Weiterentwicklung der Ontologie habe ich mich mit der semantischen Anreicherung von Properites befasst. Ziel war es, die Korrektheit und Leistung der Ontologie zu erhöhen und fehlerhafte Assertions durch logische Inkonsistenzen erkennbar zu machen. Dabei orientierte ich mich an den in OWL verfügbaren Property-Charakteristiken wie `functional`, `asymmetric`, `irreflexive` und `inverseOf`.

Zu Beginn fiel mir auf, dass sich bestimmte Eigenschaften -- beispielsweise `enthaeltZutat` -- besonders gut für eine Anreicherung eignen. Diese Relation ist sowohl asymmetrisch als auch irreflexiv, da es nicht möglich ist, dass eine Pizza eine Zutat enthält, die wiederum die Pizza enthält oder mit ihr identisch ist. Zur verbesserten Navigierbarkeit (mit bspw. SPARQL) innerhalb der Ontologie ergänzte ich zudem eine inverse Eigenschaft `istZutatVon`, sodass sowohl von der Pizza auf die Zutat als auch umgekehrt geschlossen werden kann. Sie sind allerdings beide nicht `functional`.

Auch für die Relation `gehoertZuPizzeria` entschied ich mich dazu, die inverse Beziehung `hatPizza` zu modellieren. Diese Relation ist asymmetrisch, da zwar eine Pizza einer Pizzeria zugeordnet, jedoch das Gegenteil semantisch unsinnig ($"Pizza" stretch(->)^" hatPizza " "Pizzeria"$). Die Funktionalität von `gehoertZuPizzeria` -- im Sinne der Annahme, dass jede Pizza (ein Eintrag einer Speisekarte) genau einer Pizzeria zugeordnet ist -- wurde beibehalten. Dabei ist zu bedenken, dass OWL2 die Eigenschaften nicht autoatisch der T-Box hinzufügt. Grundsätzlich sollte eine Inkonsistenz festgestellt, da für eine Assertion in der inversen Relation immer eine Assertion in der ursprünglichen existiert, die die entsprechenden Prädikate trägt. Es ist daher möglich, aber überflüssig, sie in der TBox zu explizieren. Für meine Version von Protegé die HermiT 1.4.3 ausgestattet ist und auch das Paket `owlready2` (das ebenfalls eine Variante von HermiT verwendet) hat sich dies allerdings nicht bewahrheitet.

Ein Beispiel in meiner Ontologie für eine `functional data property` ist `groesse`: Eine Pizza kann genau eine Größe haben und die Aussage ist ungültig, sofern es zwei Assertions gibt die sich auf die gleiche Pizza beziehen.

Beim Prüfen der Datatype Property `waehrung` stellte sich die Frage, ob eine Standardwährung (beispielsweise „USD“) angenommen werden kann, wenn keine Angabe erfolgt. Da OWL keine direkte Möglichkeit bietet, einen Standardwert zu hinterlegen, ohne die Option zur expliziten Abweichung (etwa „EUR“) zu verlieren, entschied ich mich gegen eine globale Einschränkung des Wertebereichs mittels allValuesFrom. Stattdessen 

Durch diese Erweiterungen ist es mir möglich, die Modellierungsschärfe der Ontologie zu erhöhen und gezielter zu überprüfen, ob konkrete Assertions valide sind. Ein Beispiel: Sollte die Eigenschaft `enthaeltZutat` irrtümlich zyklisch verwendet werden, kann ein Reasoner dies aufgrund der definierten Irreflexivität erkennen. Ebenso erleichtern inverse Beziehungen die Ableitung zusätzlicher Informationen aus wenigen ABox-Einträgen -- etwa darüber, welche Zutaten in mehreren Pizzen verwendet werden.

Diese formale Präzisierung stellt einen weiteren Schritt in Richtung einer robusten und qualitativ hochwertigen Ontologie dar, die nicht nur zur Wissensmodellierung, sondern auch zur automatisierten Konsistenzprüfung eingesetzt werden kann.

/*

== Aktueller Bearbeitungsstand der Teilaufgaben / To-Dos

=== Modellierung

+ Mindestens 20 Kompetenzfragen formulieren. #check
  - Wir haben genau 20 und könnten noch ein paar mehr hinzufügen oder austauschen.
+ Begriffe und Eigenschaften aus den Kompetenzfragen ableiten und hierarchisch darstellen. #check
  - Die Liste der Begriffe sollte aktuell vollständig sein (also die aus den Kompetenzfragen ableitbaren Begriffe umfassen), kann aber natürlich noch erweitert werden.
  - Die Hierarchie (s. Abb.) muss noch erweitert werden. #check
    - Beispielsweise fehlt momentan noch eine (Beispiel-)Instanz der Klasse "Pizza Hawaii". Hier könnte man die Pizza Hawaii von Mekan hinzufügen (und im gleichen Zug die Eigenschaft "Preis"). #check
    - Die Eigenschaften "glutenfrei" und "laktosefrei" zur Zutatenklasse hinzufügen. #check
      - Momentan kann nur Teig glutenfrei sein. Können auch Toppings Gluten enthalten? #check
    - "Mekan" als Instanz der Klasse "Pizzeria" hinzufügen. #check
    - Form / Maße als Eigenschaft einer konkreten Pizza (beispielsweise der Pizza Hawaii von Mekan) hinzufügen. #check
    
+ Rigidität, Identität und "Unity" der Klassen verifizieren. $arrow$ Identity fehlt noch.

=== OWL

Hier sind nur die fünf Teilaufgaben aufgeführt, die auch bewertet werden.

+ Klassen entsprechend unseres Modells erstellen. #check
+ Daten- und Objekteigenschaften entsprechend unseres Modells erstellen. #check
+ Je nach Bedarf lokale oder globale restrictions erstellen. #check
+ Passende "property characteristics" erstellen. #check
+ Für jede erstellte Entität eine Bezeichnung (Name oder Synonym) und einen Kommentar (z.B. für die Bedeutung) erstellen. #check

=== TODOs
- Die Pflichtaufgaben noch mal durchgehen. #check
- Die restlichen Aufgaben (die nicht bewertet werden) eventuell auch bearbeiten. #sym.crossmark.heavy
- Unseren inoffiziellen Gruppennamen nicht in unsere Abgabe schreiben. #sym.crossmark.heavy
- Das aktuelle LucidChart in dieses Dokument einfügen.
- Noch mal die Daten von der Mekan-Speisekarte überprüfen. #check

- Wir haben Teig nicht als Vegan modelliert, damit wir ggf. auch Teige mit Ei erlauben können. Je nach Zubereitung könnte man sich auch vorstellen, dass ein Pizzateig Schweineschmalz enthält. #check

- Begründen, warum die Klasse VegetarischePizza_Hawaii existiert, wie man es hätte modellieren können, wenn man gewollt hätte, dass es eine veg. Hawaii gibt und beschreiben, warum die Klasse nicht erfüllbar ist.

- Begründen, warum wir den Constraint, dass Pizza eine Pizzeria haben muss wenn Preis gesetzt ist nicht modelliert haben. (Closed World vs. Open World Sicht, Subklasse war doof zu modellieren, ist nicht notwendig basierend auf den CQs)

*/


/*
=== Was fehlt noch in der ontology.xml

- Klassen:
  - *Pizza_bei_Mekan* als Unterklasse von *Pizza* #check
    - *Pizza_FCC* als Unterklasse von *Pizza_bei_Mekan* #check
- Instanzen:
  - Brokkoli: vegan #check
  - Eigenschaften von Instanzen hinzufügen (bzw. Klassenzugehörigkeiten). Diese fehlen z. T. auch noch im LucidChart.
    - Glutenfrei quasi überall hinzufügen? #check
  - Die Pizzen von Mekan als Instanzen der entsprechenden Klasse hinzufügen. #check
- Annotation Properties für alle Entitäten hinzufügen (kurzer Kommentar). #check
- Constraints der Klasse *Pizza_FCC* hinzufügen. #check

=== Eventuelle Änderungen am LucidChart

- Klassenname *Teig* ändern oder die ABox entsprechend anpassen. #check
- Weitere Eigenschaften von Zutaten hinzufügen (z.B. ist Brokkoli auch glutenfrei). #check
- Identity und Unity überarbeiten. #check
*/


= Integration tabellarischer Daten in die Ontologie

Die Integration von fehlerbehafteten Daten in semi-strukturierter Form erfordern eine Vielzahl von Abwägungen und ingenieurstechnischen Methoden um die Informationen präzise und semantisch fundiert abzubilden. Im Folgenden werden die getroffenen Entscheidungen hinsichtlich _Entity Identification_ und Datenbereinigung diskutiert.

== Struktur des Datensatzes

Der gegebene Datensatz ist eine Tabelle mit 11 Spalten. Je Zeile können o.B.d.A. zwei Entitäten bzw. Individuen _identifiziert_ werden: Die Spalten `name`, `address`, `city`, `country`, `postcode`, `state` und `categories` beschreiben ein _*Restaurant*_ (`ontology:Pizzeria`), das über einen Namen verfügt, sich an einem bestimmten Ort (beschrieben durch Straße, Stadt, Land, Postleitzahl und Staat) befindet und zudem unter bestimmte Kategorien fällt. Die Spalten `menu item`, `item value`, `currency` und `item description` beschreiben einen _*Eintrag in der Speisekarte*_ (`ontology:Pizza`) des genannten Restaurants. Die Spalten sind in der Datei wie oben beschrieben aufgeführt und suggerieren damit in ihrer Struktur einen Zusammenhang. Nimmt man diese Abbildung an, existiert eine "1:n"-Zuordnung zwischen _Restaurant_ und _Speisekarteneintrag_. Dies erscheint schlüssig.

#bemerkung("Categories")[
  Bei der ursprünglichen Aufstellung der Competency Questions wurden keine aufgeführt, die nach der Kategorie einer Pizzeria fragen. Daher findet sich in der Ontologie diese Object Property auch nicht wieder und wird in diesem Schritt nicht berücksichtigt.
]

Sofern die Pizzeria gleiche Ausprägungen in den Merkmalen Name, Addresse und Stadt besitzt, wird angenommen, dass es sich um dieselbe Pizzeria handelt. Dies ist das Ergebnis der Abwägung zwischen Exaktheit der Reidentifikation und Übergenauigkeit -- sollte bspw. die Postleitzahl in einer Zeile fehlen, jedoch sind Name, Stadt und Addresse gleich, so würde der Vergleich fehlschlagen und eine neue Pizzeria instanziiert werden. Eine nachträgliche Verbesserung war das Aufnehmen von Bundesstaat und Land in die 

#text(.8em)[
```python
  pizz_key = (row['name'], row['address'], row['city'], row['state'], row['country'])
```]

Die Wahl des Merkmals Stadt ist erstmal arbiträr. Ebenso gut hätte die Postleitzahl anstelle der Stadt zur Unterscheidung der groben Region dienen können. Die Daten haben allerdings einige Einträge, bei denen die Postleitzahl nicht gesetzt ist, der Name der Stadt allerdings sehr wohl. Daher field die Wahl (datensatzspezifisch) auf das Merkmal Stadt, statt Postleitzahl.

== Anomalien im Datensatz

Es gibt einige Beispiele für Namen und Kategorien die suggerieren, dass die aufgeführten Einträge keine Pizzerien sind (und bspw. die Erfassung der Daten fehlerhaft war).

#let data= ("24 Hour Express Locksmith Inc", "Locksmiths", "7 Day 24 Hours Emergency Locks", "Locks & Locksmiths")

#figure(
  table(columns: 2,
  [*Name*], [*Categories*],
  ..data
  ),
  caption: [Namen, die suggerieren, dass es sich nicht um eine Pizzeria handelt]
)

Jedoch werden in einem Fall 7 und im anderen 17 Speisekarteneinträge aufgeführt.

Einige Einträge erwecken den Eindruck eines Formatierungsfehlers, etwa: gibt es einen Eintrag in dem das erste Feld (`name`) folgenden Wert enthält:
`'l Bistro,100 S 42nd St,Grand Forks,US,58201,ND,"Italian Restaurant,Seafood Restaurant,Pizza Place,Italian Restaurant, Seafood Restaurant, and Pizza Place",Roasted Vegetable and Goat Cheese Pizza,,,Oven roasted vegetables and kalamata olives with marinara sauce topped with goat cheese and mozzarella`. Diese Einträge wurden _manuell_ durch das entfernen des führenden einfachen Anführungszeichen korrigiert.

Auch das Feld für `item description` wurde verschiedentlich verwendet. Am häufigsten führt es Zutaten an, wie etwa "tomatoes, garlic, mozzarella, basil". Daher wurde von mir die Annahme getroffen, dass ein typisches `item description`-Feld eine Zutatenliste darstellt. Jedoch finden sich auch Beschreibungen wie

- 1 each (324.00 g)

- Create your own pizza

Die erste Ausprägung suggeriert, dass die Pizza mit dieser Beschreibung 324g wiegt. Dies ist in der Ontologie nicht modelliert und im Sinne der Competency Questions nicht relevant; weiters ist die Information im Datensatz nur selten verfügbar. Eine Erweiterung der Ontologie um diese Data Property wurde daher nicht vorgenommen. Außerdem finden sich mitunter sehr spezifische Angaben für Zutaten:

- Seven layer bean dip
- Sun dried tomatoes

- sliced chicken breast

Relevant im Sinne der Competency Questions ist lediglich die grobe Kategorie der jeweiligen Zutat: "beans", "tomato" und "chicken". Eine später separat besprochene Erweiterung ist die Einführung einer tieferen Zutatenhierarchie, die dies ermöglicht. Ebenfalls werden Singular- und Pluralformen einer Zutat verwendet, bspw. "tomato" und "tomatoes". In meiner persönlichen Erfahrung ist dies in der realen Welt keine Angabe der Menge an Tomaten auf einer Pizza, sondern eine Präferenz des Erstellers der Speisekarte. Daher wurde hier festgelegt, dass das Ziel der Extraktion der Zutat immer der Singular sein soll, bspw. "beans" #sym.arrow "bean". (Dies ist später für die Integration von bestehenden Knowledge Graphs relevant.)

== Die Pipeline

// TODO: Wie habe ich das ingenieursmäßig realisiert?

Ich habe diesen Abschnitt zur Vertiefung gewählt, weil viele Möglichkeiten zur Verbesserung in jedem Teilschritt existieren. Die Pipeline ist in etwa wie folgt aufgebaut:

$
  "data.csv" stretch(->)^"Bereinigen & Extrahieren" "Pizza- und Zutatenliste" stretch(->)^"Matching" "TBox oder ABox anpassen"
$

Aus den tabellarischen Daten werden natürlich auch andere Informationen (bspw. über Restaurants) extrahiert. Diese Schritte erforderten jedoch nur wenig Bereinigung und sind daher nur in der technischen Dokumentation erwähnt.

Alle Schritte sind fehleranfällig; Bei der Bereinigung der Daten können wertvolle Informationen verworfen und unsinnige als wichtig angesehen werden. Die Auflösung mit den bestehenden Zutaten in der Ontologie kann verwechselt werden, aber auch eine falsche Entsprechung gefunden werden. Selbst ein manuelles Mapping ist nicht fehlerfrei, aufgrund der teilweise fehlenden Informationen über die Pizzatypen, bspw. "Choose Your Own Pizza". Auch das Matching mit der Ontologie kann semantisch falsch sein und letztlich muss der Interpretant unter einem Bezeichner der Ontologie nicht dasselbe wie der Entwickler verstehen.

=== Vorüberlegungen
Dieser Abschnitt soll grob zusammenfassen, wie die Pipeline funktioniert und warum ich welche Entscheidungen getroffen habe. Die technischen Details sind im Repositorium dokumentiert.

Im Datensatz finden sich einige typische Pizzasorten/-typen/-klassen, wie etwa _Pizza Margherita_. Hier ist recht klar welche Zutaten zu ihr gehören und gehören sollten. Die Wahrscheinlichkeit, dass populäre Sorten in der Ontologie modelliert sind ist hoch und die Variationen halten sich in geringem Maße. Jedoch gibt es ebenfalls Sorten am anderen Ende des Spektrums oder solche, die je nach Region (und Land) sehr unterschiedlich zubereitet werden. Grundsätzlich sind alle Macharten valide und sollten daher vom Extraksionsschritt berücksichtigt und dem Nutzer in der letzendlichen Abfrage transparent gemacht werden. Dies muss allerdings aus Gründen der Praktikabilität und Überschaubarkeit nur bis zu einem bestimmten Detailgrad möglich sein; diese Schwelle gilt es zur Umsetzung dieses Pipeline-Schritts zu setzen.

Folgende zwei grundlegenden Ansätze sind denkbar: 1) Man geht vom Namen des Menüeintrags aus oder 2) man geht von der Beschreibung aus. Es ist natürlich sinnvoll beide Merkmale zu nutzen, um den Informationsgehalt maximal auszuschöpfen. Eine Möglichkeit, zur Nutzung beider Merkmale, wäre, basierend auf dem Bezeichner des Menüeintrags (bspw. `menu item` = _Pizza Margherita_) die Zutatenliste durch die Ontologie bei einer Übereinstimmung zu übernehen (bspw. Tomate, Mozzarella, Basilikum) und in der ABox festzuschreiben. Falls keine Entsprechung existiert, wird kein solcher Pizzatyp bzw. -klasse und die Zutatenliste festgelegt, sondern ein Pizzaeintrag mit der Zutatenliste wird angelegt. Dieser Ansatz hat kein Problem, wenn die Zutatenliste leer ist, solange es einen Pizzatypen zum Bezeichnes aus dem Datensatz gibt, jedoch ignoriert er gänzlich die individuelle Rezeptur einer Pizzeria, die ggf. dem in der Ontologie definierten Typen und seiner Einschränkungen widersprechen. Wenn man beide Informationen einbeziehen möchte, muss man sich über Schritte zur Konfliktresolution  einigen. Für meinen Ansatz habe ich eine übersichtliche Menge an Sorten definiert, hier sind die "Pizza Bianca" und "Pizza Frutti Di Mare" zu nennen. Für dieses Projekt habe ich mich wegen der Zeitbegrenzung für _Ansatz 1)_ entschieden: Die extrahierten Zutaten spielen nur eine Rolle, wenn keine Übereinstimmung über das Feld `menu item` gefunden werden kann.

=== Ingredient Extraction Step

Unabhängig von der Wahl des "Merging"-Verfahrens ist es sinnvoll die Zutaten zu extrahieren und kategorisieren. Dies wäre für einen Datensatz dieser Größe ein hoher Aufwand, insbesondere, wenn man allein agiert. Das Feld `item description` wird verschiedentlich genutzt und ist nicht in jedem Fall eine Zutatenliste (sondern gelegentlich leer oder mit irreführenden Angaben gefüllt). Die überwältigende Mehrheit macht jedoch indikative Einträge über die Gestalt der Pizza. Dies mit klassischen Werkzeugen des Natural Language Processing zu verarbeiten wäre in der Konzeption aufwändig, daher habe ich mich eines Large Language Models bedient.

+ Ein Large Language Model bereinigt die Rohdaten (Größenangaben und sonstige unpassende Beschreibungen werden entfernt). Je Zeile in der ursprünglichen CSV-Datei gibt es nun einen strukturierten Datensatz.

+ Diese Liste wird einem Clusteringverfahren übergeben und führt ein
  + Clustering der `menu item`-Namen in Pizzasorten, und ein
  + Zuordnen der Zutaten in Expertenkategorien durch.

+ Das Clustering wird für die Integration der Daten in die Ontologie abgelegt.

==== LLM Prompt
Der Prompt verlangt, basierend auf den Merkmalen `menu item` und `item description`, zu klassifizieren ob es sich um eine Pizza handelt, welche Zutaten sie enthält und den Namen des Menüeitnrags zu kanonisieren. Explizit wird das LLM aufgefordert die Zutaten zu "vereinfachen" (Beispiel _green pepper_ soll zu _pepper_ werden). _Dies ist selbstverständlich fehleranfällig_, jedoch gab es keine bedeutenden Auffälligkeiten in einer stichprobenartigen Kontrolle. Der Schritt kann durch eine weitere Anpassung des Prompts und Einstellen der Temperatur (Zufälligkeit), sowie das Auslassen der Aufforderung des Konfabulierens vermutlich verbessert werden. Erstaunlich gut funktioniert die Klassifizierung, ob etwas eine Pizza ist. Der Prompt fordert bspw. "Pizza Bagel" nicht als Pizza anzuerkennen#footnote[Grundsätzlich wäre ein Pizza Bagel im Sinne meiner Ontologie eine Pizza. Jedoch zeigt dieses Beispiel, dass man unerwünschte Einträge mit einem LLM leicht filtern kann.].

==== Clustering
Das Ziel dieses Clustering-Schritts ist die Verbesserung der Zusammenfassung von gleich oder ähnlich bedeutenden Zutaten. Beispielsweise ist es für die meisten Abfragen irrelevant, ob man _sun dried tomatoes_ oder _spiced tomatoes_ auf der Pizza vorfinden kann. Der LLM-Step hat jedoch einiges auf deer Strecke gelassen (unter anderem das gerade genannte Beispiel). Die Hoffnung ist, dass nach einem Embedding der Zutaten ein Clustering-Verfahren ähnliche Zutaten zusammenfassen kann. Hier soll die Besonderheit von der Domäne Pizza ausgenutzt werden: Bestimmte Pizzasorten enthalten oft die gleichen (oder ähnliche Zutaten) die mit kleinen Variationen oder auch Euphemismen ausgestattet sind. Beispielsweise wird oft _Pecorino_ und _Parmesan_ auf Pizzen in ähnlicher Art verwendet (weil es beides würzige italienische Hartkäse sind). Im Datensatz finden sich auch solche Sorten gelegentlich, jedoch sind sie etwas unspezifischer, beispielsweise "Italian Pizza"  oder "Junior Pizza".

Das Clustering setzt ein Sentence Embedding ein. Die Zutat wird nicht einfach nur als Wort mit einem vortrainierten Embedding vektorisiert, sondern in einem Satz der die Zutat benennt und aufzählt, auf welchen `menu items` sie vorkommt. "\<Zutat\> in Margherita, Caprese, Quattro Formaggi". Das Clustering wird mit einem _agglomerativem Clustering_-Verfahren berechnet. Dies würde es prinzipiell ermöglichen einen beliebigen Schnitt im Dendrogramm zu setzen, jedoch habe ich mich dafür entschieden das Ergebnis dieses Schritts in eine semiautomatisch angelegte Sammlung von Buckets (das oben erwähnte "Expertenwissen") mit Stichworten einordnen zu lassen:

- Jeder Blatt-Cluster enthält eine Liste Zutaten.
- Die Zutaten werden nach den Stichworten der Buckets durchsucht.
- Enthält ein Blatt-Cluster ein Stichwort so wird es diesem Bucket untergeordnet.

Dies ist vorteilhaft, weil das automatische Clustering (mit Labeling mithilfe des Zentroiden) einer Kategorie zugordnet werden kann. Die Stichwortsuche ohne vorheriges Clustering war weniger erfolgreich. Der große Vorteil von der Einordnung in manuelle Kategorien ist die Übersichtlichkeit für eine spätere Abfrage mit SPARQL. In einer echten (Produktions-)Anwendung könnte diese Kategorieliste ausziseliert werden um potente Abfragen zu ermöglichen, da das automatische Clustering teilweise zu wünschen übrig lässt.

==== Qualität des Clustering
Für Pizzasorten hat das Clustering schlecht funktioniert. Etwa gehört zur Kategorie "Bianca" die "Tuna Pizza", die "Whole Breakfast Pizza", allerdings auch die "White Pizza" und ihre Varianten. Aufgrund dieses Ergebnisses habe ich mich dazu entschieden es nicht weiterzuverfolgen. Das Clustering der Zutaten weist ebenfalls Mängel auf.

#bemerkung()[Das Clustering findet sich in der Datei #link("https://git.uni-jena.de/fusion/teaching/project/2025sose/KnowledgeGraphs/group-05/-/blob/main/week2/cluster_labels.json")[week2/cluster_labels.json] und enthält zwei Abschnitte: Pizza-Sorten Clustering (oben) und darunter das Zutatenclustering.]

#figure(
```json
    ... "Other": {
      "pizza crust": [
        "",
        "bbq",
        "beef",
        "buffalo",
        "cheddar",
        "ground beef",
        "hot",
        "lettuce",
        "pizza crust",
        "pork",
        "pulled pork",
        "ranch",
        "steak"
      ], ... }
    ```, caption: [Beispiel für ein semantisch wenig wertvolles Clustering.])

Der Bucket "Other" enthält den Cluster "pizza crust", der sich zu einem "Catch-All" entwickelt hat.

Leider konnte auch mit keinem (angemessenen) Schwellwert die Kategorie _Basilikumpesto_ gefunden werden (selbst für $0.5$ im Agglomerative Clustering wurden sie nicht zusammegefasst). Hier reicht vermutlich die Menge der Trainingsdaten nicht aus um mit diesem Verfahren zu einem angemessenen Ergebnis zu kommen.

#figure(
```json
      ... "basil pesto sauce": [
        "basil aioli",
        "basil pesto sauce",
        "chipotle pesto",
        "garlic pesto",
        "hempseed pesto",
        "lemon aioli"
      ],
      "basil pesto": [
        "basil pesto",
        "marinara sauce",
        "pesto",
        "pesto sauce",
        "ranch dressing"
      ], ...
  ```,
  caption: [Basilikumpesto wird aufgrund des Worts "Sauce" nicht in eine Kategorie zusammegefasst.]
  )

Das Clustering ist jedoch in Summe sehr gut und fasst Zutaten ähnlicher Bedeutung gut zusammen.

#figure(
```json
    "Hard Cheeses": {
      "white parmesan sauce": [
        "brazil nut parmesan",
        "white parmesan sauce"
      ],
      "pecorino": [
        "grana padano",
        "parmesan",
        "parmesan cheese",
        "pecorino",
        "pecorino cheese",
        "pecorino romano",
        "romano",
        "romano cheese"
      ]
    },
    ```, caption: [Beispiel für ein gelungenes Clustering: _Hartkäse_])

=== Integration der Daten in die Ontologie

Es ist nicht offensichtlich, wie die Ergebnisse des Clusterings in die Ontologie integriert werden sollen. Denkbar sind etwa folgende Ansätze: 1) Man fügt die Fragmente (Expertenkategorie und dem Cluster als Subklasse) der TBox hinzu, erstellt in der ABox die Zutaten als benannte Individuen und gibt ihr den Typ der Clusteringkategorie, 2) man verwendet Vokabulare wie das SKOS um einen Thesaurus bzw. kleines WordNet anzulegen oder 3) man verwendet die generierten Labels der automatischen Kategorisierung und betrachtet sie als Zutat. 

Für das Beispiel _Tomate_ würde Ansatz 3) fast funktionieren: Die Expertenkategorie Tomate enthält einen Cluster mit dem Label _sundried tomato_, welche zumindest einige Tomaten zusammenfasst, jedoch enthält sie auch _tomato sauce_. Würde man diese Ebene zusammenstauchen würde es die Qualität wesentlich verschlechtern. Es gibt jedoch auch noch schlechetere Beispiele, etwa _Mushrooms_ oder die bereits genannte _Pizza Crust_-Cluster. Ansatz 2) mit SKOS ist insofern eine Herausforderung, als dass SKOS selbst ein ausgereiftes RDFS-Vokabular ist und eine formale Sprache sein soll. Das Projekt hat jedoch den Fokus OWL als Modallogik; es wäre dahher etwas überflüssig (auch wenn SKOS genau für Thesauri und einfache Taxonomien gedacht ist) quasi eine zweite Logik mit eigenen Regeln anzulegen. Ansatz 1) ist daher für den Scope dieses Projekt meiner Auffassung am Besten geeignet.

Dabei ist besonders darauf zu achten, dass ein potenziell schlechtes Clustering keine Qualitätsminderung der Ontologie und des Knowledge Graphen im Vergleich zum Ausgangszustand bewirkt (wie bspw. bei Ansatz 3). Daher ist hier ein Vergleich zum vorherigen Zustand sinnvoll: Die Daten wurden nach dem LLM-Step zu bestehenden Zutaten in der Ontologie und sonst zu Items in Wikidata gemappt und anschließend als Zutat in die ABox übernommen. Durch diese Erweiterung der TBox bleibt diese Information erhalten und der Nutzer kann in der SPARQL Abfrage wählen, ob er die Expertenkategorie "Tomatoes", den labelled Cluster "Sundried Tomato" abfragen möchte oder gar direkt die Zutat "tomato". Die Cluster werden in der TBox mit einem Vermerk "automatisch generiert" abgelegt, damit Nutzer informiert ihren Umgang wählen können.

= Abfrage des RDF-basierten Knowledge Graphs

Zur Abfrage von RDF-basierten Knowledge Graphs wird in aller Regel der ebenfalls von der W3C spezifizierte SPARQL-Formalismus verwendet. Einige Systeme, wie etwa Wikibase/Wikidata, bilden lediglich in das Resource Description Framework ab und verwenden andere interne Repräsentation. 

== SPARLQ.1 -- Reasoning über der Ontologie und den integrierten Daten

Wie in @abs:anreichung_properites angeschnitten können Reasoner verwendet werden um bestimmte Schlussfolgerungen in der TBox zu machen. Es ist grundsätzlich nicht sinnvoll die deduktive Hülle zu explizieren, u.a. weil sich dadurch Speicherplatz sparen und Übersichtlichkeit schaffen lässt. Wird in Protégé (mit Reasoner HermiT 1.4.3) ein Ding als Typ verwendet, so wird gefolgert und expliziert, dass es als Klasse aufzufassen ist. Zum Reasoning verwende ich _OWL RL_ (statt OWL DL und Lite), weil es ausreichend und Stand der Technik ist. Leider hat die Python-Implementation von OWL RL den entscheidenden (eigentlich Fehler), dass Tripel inferiert und asserted werden, die nicht dem RDF-Standard entsprechen. Daher enthält das Script für das Reasoning `reasoning.py` eine Funktion `remove_invalid_owl_triples` die Tripel entfernt, bei denen das Subjekt ein Literal ist. Die Python-Implementation nimmt bspw. Statements wie `"0.25"^^xsd:decimal owl:SameAs "0.25"^^xsd:decimal` auf (was GraphDB strikt ablehnt). Die Ursache konnte ich bisher nicht abschließend klären.

== SPARQL.2 -- Pizzerien, die Pizza ohne Tomaten servieren

Die Abfrage sucht lediglich nach Dingen vom Typ Pizzeria und filtert anschließend mit `FILTER NOT EXISTS` Dinge aus der Ergebnismenge, die eine Pizza servieren die Tomatensauce oder Tomaten enthält. Wichtig ist hier, dass möglicherweise unvollständige Informationen, die allerdings die Ergebnismenge nicht einschränken sollen, als `OPTIONAL` statiert werden, etwa wenn die Adressangabe unvollständig ist: es soll alles verfügbare in das Ergebnis projeziert, aber nicht die Ergebnismenge eingeschränkt werden.

#bemerkung("Nach der Verbesserung")[
  Durch die Verbesserung hat sich lediglich im `FILTER NOT EXISTS`-Block die Bezeichnung zu `:tomato_ToppingCategory` geändert.
]

== SPARQL.3 -- Durchschnittspreis der Pizza Margherita

Die Abfrage ist insofern unintuitiv, dass es Dinge vom Typ Pizza gehen soll, die genau die Zutaten "Tomate" und "Mozzarella" enthalten. In SPARQL kann dies formuliert werden als "mindestens `Tomate` und `Mozzarella`" und "höchstens `Tomate` und `Mozzarella`" in der Menge der Zutaten. Die Aussage "mindestens" ist durch die Zeile 6 gegeben, jedoch sind es ohne den `FILTER`-Block in der Zeile 11 ff. potentiell Pizzen, die auch mehr enhalten. Für diese Abfrage war es auch entscheidend Preise auszuschließen die ungültige Fließkommazahlen (`NaN`) sind. Dafür sorgt das `FILTER`-statement in der vorletzten Zeile der Abfrage.

#bemerkung("Nach der Verbesserung")[
  Durch die Verbesserung wird nun nach der Tomaten-Expertenkategorie und dem Cluster für Mozzarella gefragt. Dies hat den Durchschnittspreis von \$15 auf \$13 Dollar gesenkt.
  ```
    ?tomato rdf:type :tomato_ToppingCategory.
    ?mozzarella rdf:type :mozzarella_Toppings.
    ?pizza :enthaeltZutat ?tomato, ?mozzarella.
  ```
]

== SPARQL.4 -- Pizzerien sortiert nach Stadt

Die Abfrage ist insofern korrekt, als sie die Anzahl der Pizzerien pro Stadt ermittelt und nach Bundesland sowie Restaurantanzahl sortiert. Durch `rdf:type :Pizzeria` wird die betrachtete Klasse eingegrenzt. Die Adressdaten werden über verschachtelte `OPTIONAL`-Blöcke eingebunden, sodass auch unvollständige Adressen nicht ausgeschlossen werden. Die Gruppierung über `GROUP BY ?region ?locality` sorgt dafür, dass die Zählung eindeutig auf Stadt- und Bundeslandebene erfolgt. `COUNT(?restaurant)` liefert die benötigte Aggregation, während `ORDER BY ?region DESC(?restaurantCount)` die geforderte Sortierung sicherstellt.

== SPARQL.5 -- Pizzerien ohne Postleitzahl

Die Aufgabe fordert, dass alle Restaurants, zu denen kein Eintrag zur Postleitzahl existiert, zurückgeliefert werden sollen. Dies ist dadurch erfüllt, dass das `FILTER`-statement alle Einträge aus der Ergbnismenge entfernt, zu denen keine Postleitzahl vermerkt wurde.

= Alignment
Im Wesentlichen sieht die Aufgabe vor, dass man mit drei verschiedenen Ansätzen ein Alignment von der eigenen zu einer gegebenen Ontologie durchführt und die Ergebnisse des Alignments für die eigene Ontologie evaluiert. Im zweiten Schritt, sollen die Verfahren mit einer Ground Truth getestet werden.
Ich verwende im Rahmen dieses Projekts vier Verfahren:

+ Eigenes, lexikographisches Alignment mit Übersetzung (`own_alignment.py`)

+ AgreementMakerLight

+ BERTMap

+ ChatGPT 4o (beide Ontologien werden einfach eingegeben)

= Embedding

== Konfiguration und Begriffe
Für die Ähnlichkeit und Unähnlichkeit wurden jeweils drei Paare gewählt. Es gibt in dieser Betrachtung zwei Konfigurationen:

- Configuration 1: `embed_size=200, walk_depth=2, reasoner="elk", outfile=cfg1`
- Configuration 2: `embed_size=400, walk_depth=4, reasoner="elk", outfile=cfg2`

Die Konfigurationen entscheiden sich in zweierlei Hinsicht: Der Größe des Merkmalsvektor für das Embedding und der Random-Walk Depth. Die Tiefe der Random Walks in OWL2Vec\* beeinflusst die Qualität der erzeugten Embeddings deutlich. Größere Tiefen erfassen komplexere semantische Zusammenhänge, können jedoch auch irrelevante oder störende Informationen einbeziehen. Daher muss eine geeignete Tiefe gewählt werden, um ein gutes Gleichgewicht zwischen Ausdrucksstärke und Genauigkeit zu erzielen.

Die Paare wurden gewählt um einem ausgewogenen unterschiedlicher Taxonomieebenen und Typen zu repräsentieren. Margherita und Pizza sind sich vermutlich recht ähnlich, da Margherita eine Einschränkung über der 

#let fill_function = (x, y) => if y > 0 and y < 4 { green.lighten(50%) } else if y > 3 {red.lighten(50%)}

#let raw_pairs = csv("../week5/pairs.txt", delimiter: " ")

#figure(
  caption: [Die zur Beobachtung gewählten Paare],
  table(columns: 2, fill: fill_function, [*Term1*], [*Term2*], ..raw_pairs.flatten())
)

Das Embedding wurde zunächst jedoch nur mit 100 Samples aus der ABox angefertigt. 
Das Ergebnis war allerdings eintönig: Die Begriffe waren durch das Embedding nicht wesentlich unterscheidbar.

#figure(
  caption: "Eine Auswahl 20 zufälliger Embeddings, Configuration 1, Sample Size 100",
  image("../week5/random_similarity_report_100_samples.png", width: 70%),
)

Offensichtlich war die Größe der Stichprobe nicht ausreichend um Unterschiede in den Begrifflichkeiten festzustellen, daher wurde die Sample Size auf zunächst 2000 Beispiele erhöht. Dies führte einerseits zu einer Annäherung an die erwarteten Ergebnisse, als auch eine allgemein höhere Streuung. Dies ist allein durch das erhöhen der Stichprobe begründet -- Word2Vec erhält die Gelegenheit die Worte in mehr und unterschiedlichen Kontexten zu observieren und kann dadurch die Bedeutung besser approximieren. Die nachfolgenden zwei Tabellen zeigen die Ergebnisse 

#pagebreak()

#let pairs1 = csv("../week5/similarities1_2000.csv")
#let pairs2 = csv("../week5/similarities2_2000.csv")

#figure(
  table(columns: 4, fill: fill_function, [*Term1*], [*Term2*], [*Cosine Similarity*], [*Euclidean Distance*], ..pairs1.flatten()),
  caption: [Configuration 1, Sample Size 2,000\ Erwartet ähnliche Embeddings sind grün und erwartet unähnliche rot markiert.]
)

#figure(
  table(columns: 4, fill: fill_function, [*Term1*], [*Term2*], [*Cosine Similarity*], [*Euclidean Distance*], ..pairs2.flatten()),
  caption: [Configuration 2, Sample Size 2,000\ Erwartet ähnliche Embeddings sind grün und erwartet unähnliche rot markiert.]
)


#let pairs10k_1 = csv("../week5/similarities1.csv")
#let pairs10k_2 = csv("../week5/similarities2.csv")

#figure(
  table(columns: 4, fill: fill_function, [*Term1*], [*Term2*], [*Cosine Similarity*], [*Euclidean Distance*], ..pairs10k_1.flatten()),
  caption: [Configuration 1, Sample Size 10,000\ Erwartet ähnliche Embeddings sind grün und erwartet unähnliche rot markiert.]
) <looool>

#figure(
  table(columns: 4, fill: fill_function, [*Term1*], [*Term2*], [*Cosine Similarity*], [*Euclidean Distance*], ..pairs10k_2.flatten()),
  caption: [Configuration 2, Sample Size 10,000\ Erwartet ähnliche Embeddings sind grün und erwartet unähnliche rot markiert.]
)

#pagebreak()

Wie schon erwähnt, beeinflussen die Parameter Random-Walk-Tiefe und die Merkmalsvektorgröße wesentlich, wie gut semantische Zusammenhänge durch Embeddings erfasst werden können. Größere Dimensionen und tiefere Random-Walks bieten in der Regel reichhaltigere semantische Informationen, bergen jedoch auch das Risiko, irrelevante oder störende Daten einzubeziehen.


=== Pairs Expected to Be Similar:

1. *margherita and pizza*:

Zwischen "margherita" und "pizza" wurde eine hohe Ähnlichkeit erwartet, da Margherita eine spezifische Pizza-Variante ist. In Konfiguration 1 zeigte sich bei steigender Stichprobengröße von 2000 auf 10.000 Samples zunächst eine hohe Cosine Similarity ($0.8380$), die jedoch überraschend auf $0.3188$ absank, was auf Instabilitäten hindeuten könnte. Configuration 2 hingegen bestätigte die Erwartung konsistenter, mit einem stabilen Rückgang der Cosine Similarity von $0.9014$ auf $0.7744$.

2. *mozzarella and kaese (cheese)*:



   - Expected similarity as Mozzarella is a specific type of cheese.
   - Configuration 1: High cosine similarity at 2000 samples (0.9327), but notably decreases at 10,000 samples (0.6492), suggesting potential dilution of semantic signal with increased sample size.
   - Configuration 2: Moderate similarity at 2000 samples (0.8048), further decreasing slightly at 10,000 samples (0.6192), reflecting an unexpected weakening of semantic relatedness.

3. *zutat (ingredient) and tomatensauce (tomato sauce)*:

   - Strong semantic link anticipated as tomato sauce is clearly an ingredient.
   - Configuration 1: Cosine similarity slightly decreased from 0.8764 at 2000 samples to 0.6761 at 10,000 samples, possibly indicating context dilution.
   - Configuration 2: Initially moderate similarity (0.7766) improving slightly at 10,000 samples (0.7864), illustrating greater stability.

=== Pairs Expected to Be Dissimilar:

1. *margherita and scampi*:

   - Expected to be semantically distant, Margherita being vegetarian pizza, Scampi seafood.
   - Configuration 1: High similarity at 2000 samples (0.8932) drastically decreases at 10,000 samples (0.3230), aligning better with expectations at larger samples.
   - Configuration 2: Moderate similarity at 2000 samples (0.7736), decreasing slightly at 10,000 samples (0.6472), indicating correct semantic distancing at larger samples.

2. *dessert and waehrung (currency)*:

   - Clearly unrelated semantic concepts, thus expecting low similarity.
   - Both configurations surprisingly showed consistently high similarity (Configuration 1: 0.9882 at 2000 samples, dropping slightly to 0.8470 at 10,000; Configuration 2: 0.9773 and 0.8779 respectively), indicating potential embedding anomalies or common co-occurrence patterns unrelated to actual semantic content.

3. *breakfast and schinken (ham)*:

   - Initially considered dissimilar; however, contextually breakfast often includes ham, making semantic overlap plausible.
   - Configuration 1: Initially high similarity at 2000 samples (0.9062), dropping significantly to moderate levels at 10,000 samples (0.4825), showing sensitivity to contextual nuances.
   - Configuration 2: Consistently high similarity (0.8766 at 2000 samples and 0.9005 at 10,000 samples), suggesting embeddings effectively captured relevant contextual associations.

=== Conclusion:

The embeddings' semantic clarity varied significantly with embedding dimension, random walk depth, and sample size. Configuration 2 generally demonstrated greater semantic stability due to its higher dimensionality and deeper contextual exploration, while Configuration 1 exhibited more variability. Large sample sizes sometimes diluted semantic precision due to increased noise or context ambiguity. Unexpected semantic similarities highlight potential limitations or peculiarities of the embedding method, necessitating careful tuning of embedding parameters.
