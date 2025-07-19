#import "dvd.typ": *
#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *

#show: dvdtyp.with(
  title: "Bericht zum Modul Knowledge Graphs",
  subtitle: [Im Sommersemester 2025 von König-Ries, Bachinger, Enderling],
  author: "Bericht von Daniel Motz",

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
  - *glutenfrei* #sym.arrow Analog zu vegan, vegetarisch
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


= Abfrage des RDF-basierten Knowledge Graphs

Zur Abfrage von RDF-basierten Knowledge Graphs wird in aller Regel der ebenfalls von der W3C spezifizierte SPARQL-Formalismus verwendet. Einige Systeme, wie etwa Wikibase/Wikidata, bilden lediglich in das Resource Description Framework ab und verwenden andere interne Repräsentation. 

== SPARLQ.1 -- Reasoning über der Ontologie und den integrierten Daten

Wie in @abs:anreichung_properites angeschnitten können Reasoner verwendet werden um bestimmte Schlussfolgerungen in der TBox zu explizieren. Es ist grundsätzlich nicht sinnvoll die deduktive Hülle zu explizieren, u.a. weil sich dadurch Speicherplatz sparen und Übersichtlichkeit schaffen lässt. Wird in Protégé (mit Reasoner HermiT 1.4.3) ein Ding als Typ verwendet, so wird gefolgert und expliziert, dass es als Klasse aufzufassen ist.“

== SPARQL.2 -- Pizzerien, die Pizza ohne Tomaten servieren

Die Abfrage sucht lediglich nach Dingen vom Typ Pizzeria und filtert anschließend mit `FILTER NOT EXISTS` Dinge aus der Ergebnismenge, die eine Pizza servieren die Tomatensauce oder Tomaten enthält. Wichtig ist hier, dass möglicherweise unvollständige Informationen, die allerdings die Ergebnismenge nicht einschränken sollen, als `OPTIONAL` statiert werden, etwa wenn die Adressangabe unvollständig ist: es soll alles verfügbare in das Ergebnis projeziert, aber nicht die Ergebnismenge eingeschränkt werden.

== SPARQL.3 -- Durchschnittspreis der Pizza Margherita

Die Abfrage ist insofern unintuitiv, dass es Dinge vom Typ Pizza gehen soll, die genau die Zutaten "Tomate" und "Mozzarella" enthalten. In SPARQL kann dies formuliert werden als "mindestens `Tomate` und `Mozzarella`" und "höchstens `Tomate` und `Mozzarella`" in der Menge der Zutaten. Die Aussage "mindestens" ist durch die Zeile 6 gegeben, jedoch sind es ohne den `FILTER`-Block in der Zeile 11 ff. potentiell Pizzen, die auch mehr enhalten. Für diese Abfrage war es auch entscheidend Preise auszuschließen die ungültige Fließkommazahlen (`NaN`) sind. Dafür sorgt das `FILTER`-statement in der vorletzten Zeile der Abfrage.

== SPARQL.4 -- Pizzerien sortiert nach Stadt

Die Abfrage ist insofern korrekt, als sie die Anzahl der Pizzerien pro Stadt ermittelt und nach Bundesland sowie Restaurantanzahl sortiert. Durch `rdf:type :Pizzeria` wird die betrachtete Klasse eingegrenzt. Die Adressdaten werden über verschachtelte `OPTIONAL`-Blöcke eingebunden, sodass auch unvollständige Adressen nicht ausgeschlossen werden. Die Gruppierung über `GROUP BY ?region ?locality` sorgt dafür, dass die Zählung eindeutig auf Stadt- und Bundeslandebene erfolgt. `COUNT(?restaurant)` liefert die benötigte Aggregation, während `ORDER BY ?region DESC(?restaurantCount)` die geforderte Sortierung sicherstellt.

== SPARQL.5 -- Pizzerien ohne Postleitzahl

Die Aufgabe fordert, dass alle Restaurants, zu denen kein Eintrag zur Postleitzahl existiert, zurückgeliefert werden sollen. Dies ist dadurch erfüllt, dass das `FILTER`-statement alle Einträge aus der Ergbnismenge entfernt, zu denen keine Postleitzahl vermerkt wurde.