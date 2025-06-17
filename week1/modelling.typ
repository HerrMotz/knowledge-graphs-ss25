#import "@preview/codly:1.3.0": *
#import "@preview/codly-languages:0.1.1": *
#show: codly-init.with()

#codly(languages: codly-languages)

#set page(header: [
  Maximilian Stock, Daniel Motz\
  Gruppenname: _"BECKS"_
])

#set text(lang: "de")
#set par(justify: true)

#set underline(stroke: 1.5pt+lime, offset: 2pt)

#let check = [✅]

= Knowledge Graphs ÜS 1
\

#grid(columns: (2fr, 1fr), column-gutter: 2em, [
== Competency Questions

- Welche #underline("Toppings") hat eine #underline[Pizza] Hawaii?

- Welche #underline[Teigsorten] gibt es?
- Welche #underline[Saucen] können auf einer Pizza sein?
- Kann ich #underline[Brokkoli] auf eine #underline[Pizza Hawaii] legen?
- Ist eine Pizza Hawaii ohne #underline[Ananas] immer noch eine Pizza Hawaii?
- Was gehört zu einer Pizza #underline[Margherita]?
- Welche Zutaten hat eine #underline[Calzone]?
- Welche #underline[Sorten von Pizza] gibt es?
- Welche Pizzen sind #underline[vegetarisch]?
- Welche Pizzen sind #underline[vegan]?
- Gibt es #underline[glutenfreie] Pizzen?
- Welche Pizzen enthalten Mozzarella?
- Welche Pizzen gibt es bei #underline[Mekan]?
- Wie wird die "Pizza FCC" bei Mekan gemacht?
- Wie viel kostet eine Pizza Frutti di Mare bei Giovannis Pizzeria?
- Welche #underline[Maße] hat die Pizza?
- Welche #underline[Form] hat die Pizza?
- Welche Pizza bei Mekan ist am #underline[billigsten]?
- Welche Pizzen enthalten Schinken?
- Welche #underline[laktosefreien] Pizzen gibt es?

], [
  == Derived Terms
  - *Pizza*

  - *Toppings* #sym.arrow *Zutaten*

  - *Sauce*
  - Sorten von Pizza #sym.arrow Unterklassen von Pizza mit Constrains, also "geschützte Sorten" wie "Pizza Hawaii"
  - *vegetarisch*
  - *vegan*
  - *glutenfrei*
  - Mekan #sym.arrow *Lokalität*
  - *Form* / *Maße*
  - *Preis*

  - Laktosefrei #sym.arrow *Milchproduktzutatsklasse*

])

#pagebreak()

== Terms and Classes

Unsere Ontologie modelliert nicht konkrete, real existierende Pizzen, sondern Einträge einer Speisekarte. Anfangs modellierten wir eine am Prozess der Fastfoodkette "Dominos" orientierte Kategorisierung. Wir stellten jedoch fest, dass dies aufwändig ist. Wir stellten jedoch die Anforderung, dass die Ontologie sowohl Pizzen die in einer Pizzeria, als auch für solche, die in den "eigenen vier Wänden", produziert werden, abbilden kann. Die Klasse Pizza umfasst daher die für eine Pizza wesentlichen Eigenschaften, wie etwa eine Zutatenliste, jedoch ist die Eigenschaft  "Preis" nur im Zusammenhang mit einer Pizzeria präsent.

Wir entschieden außerdem, dass weit verbreitete Rezepturen, wie etwa "Pizza Hawaii", als Unterklasse von *Pizza* mit Einschränkungen im Wertebereich der Zutaten modelliert werden. Dafür ist es notwendig, dass wir entweder Klassen für Zutaten anlegen, wie etwa "Schinken" oder aber wir liefern zu unserer TBox eine ABox. Wir haben uns für letzteres entschieden. Dies entstand aus der CQ "Kann man eine Pizza Hawaii ohne Ananas herstellen".

Wir haben uns außerdem dazu entschieden, dass gewisse Zutaten eine eigene Klasse erhalten, nämlich Teig, Sauce und Käse, um erzwingen zu können, dass eine Pizza mindestens aus einem Teig und einer Sauce bestehen muss.

Zu Pizzerien haben wir folgende Gedanken: Eine Pizza kann bei einer Pizzeria hergestellt werden. Dann wird sie zu einem konkreten Preis verkauft und der Preis variiert zudem mit der Größe. In unserer Feldstudie im Raum Jena stellten wir fest, dass es Pizzerien gibt, die an ihrer Speisenkartentafel eigens Klassifizierungen vornehmen. So fanden wir beispielsweise die Aufschrift "Alle Pizzen mit Tomatensauce und Käse#super[g]". Diese Hilfestellung würdigen wir durch Aufnahme in unsere Ontologie als eine eigene Klasse "*Pizza_bei_Mekan*". Wir wissen, a posteriori, dass man auch bei Mekan keine Pizza ohne Teig herstellt, auch wenn der Speisekartenersteller dies nicht expliziert hat.

Anfangs modellierten wir "Toppings" bzw. Beläge (bspw. Schinken, Brokkolli, Blumenkohl und Zwiebeln, aber auch Saucen) in der Klasse *Zutat* und fügten data properties für wie `istGlutenfrei` ein. Dies ersetzten wir durch Typen wie etwa `Glutenfreie`, `Vegetarische` und `Vegane`.

Wir haben Teig nicht als vegan modelliert, damit wir ggf. auch Teige mit Ei erlauben können. Die Einschränkung in vegetarisch erscheint sinnvoll, jedoch wird die Zubereitung des Teigs in unserer Ontologie nicht näher spezifiziert. 

Unsere Ontologie enthält ein Beispiel für eine unerfüllbare Klasse: `VegetarischePizza_Hawaii`, modelliert als Schnitt zwischen `Vegetarische_Pizza` und `Pizza_Hawaii`. Die Bedingungen sind also, dass jedes Individuum dieses Typs ausschließlich vegetarische Zutaten enthält, sowie die für eine Pizza Hawaii notwendigen (Ananas, Tomatensauce, Teig/Boden und Schinken). Da Schinken nicht den Typ `Vegetarische` besitzt, kann es die Anforderungen der Klasse `Vegetarische_Pizza` nicht erfüllen.

== Informelle Hierarchisierung

#show link: it => underline(stroke: (paint: blue, thickness: 1pt, dash: "dashed"), offset: 2.5pt, it)

Die Datei befindet sich im Repositorium unter #link("https://git.uni-jena.de/fusion/teaching/project/2025sose/KnowledgeGraphs/group-05/-/blob/main/terminology-hierarchy.pdf")[`terminology-hierarchy.pdf`].

== Ontologie
Die Datei befindet sich ebenfalls im Repositorium unter #link("https://git.uni-jena.de/fusion/teaching/project/2025sose/KnowledgeGraphs/group-05/-/blob/main/ontology.xml")[`ontology.xml`].

// TODO: fix, dass das nicht überdeckt wird
#place(bottom+left)[#v(1cm)\ "#text(1.2em, super[g])Milch"]

#pagebreak()

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
