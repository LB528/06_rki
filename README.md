# Robert Koch Institut - Impfquotenmonitoring
## von Leylanur Bodur, Melanie Vogel, Johanna Helene von Wachsmann (Gruppe 6)

### Kontext
Das Robert Koch Institut veröffentlicht angesichts der aktuellen Pandemiesituation durch COVID-19 regelmäßig Daten zum Pandemieverlauf wie die aktuellen Inzidenzzahlen und Daten zum Impffortschritt in Deutschland. Dabei gibt es auch einen Datensatz der den Impffortschritt pro Bundesland in Deutschland zeigt, wobei sich dieser teilweise sehr unterscheidet zwischen den einzelnen Bundesländern. Desweiteren gibt es Daten zu den Impfstoffen selbst, den Lieferungen, den Altersgruppen und Einrichtungen.

### Konzept
Wir orientieren uns an einer bereits vorhandenen Visualisierung des Robert Koch Instituts (RKIs) auf [dem Impfdashboard](https://impfdashboard.de/daten) und benutzen eine Choropleth Karte als Map Layout um eine gute Übersicht der Daten in Deutschland zeigen zu können. Die Anzahl Impfungen ist farblich hervorgehoben, wobei wir zunächst ein anderes Farbschema hatten, welches jedoch zu bunt war. Das jetztige werden wir bis zum Abschluss des Projekts noch hinsichtlich Farbblindheit und anderen Einschränkungen überprüfen. 
In der Karte sieht man die Abgrenzungen der einzelnen Bundesländer und auch die Zahlen geben wir auf Bundeslandebene aus. Dies hat verschiedene Gründe. Die für uns verfügbaren Daten des RKIs sind auf Bundeslandebene, Landkreise wären höchstwahrscheinlich viel zu unübersichtlich und erdrückend für die Benutzer, und der direkte Vergleich der Impfzahlen würde ggf. schwieriger werden, da es dann Vergleiche zwischen einer Metropole und einem kleinen Landkreis gibt.
Außerdem haben wir noch verschiedene Sprachauswahlmöglichkeiten festgelegt. Die Benutzerin kann dann zwischen Deutsch, Englisch, Türkisch und Russisch auswählen. Diese Auswahl haben wir so getroffen, da diese so auch auf der Seite des Impfdashboards vorhanden sind und laut eines [Interviews der Bundesregierung](https://www.bundesregierung.de/breg-de/suche/interview-muttersprache-1721084#:~:text=Zu%20den%20meistgesprochenen%20Sprachen%20in%20Deutschland%20z%C3%A4hlen%2C%20neben%20nat%C3%BCrlich%20dem%20Deutschen%2C%20Russisch%20mit%20bis%20zu%20drei%20Millionen%20Muttersprachlern%2C%20T%C3%BCrkisch%20mit%20mehr%20als%20zwei%20Millionen%20Muttersprachlern) die drei in Deutschland am häufigsten gesprochenen Sprachen Deutsch, Russisch und Türkisch sind.

### Prototyp
Auf den folgenden zwei Bildern kann man unseren aktuellen Prototypen sehen. Man kann mit der Maus über ein Bundesland hovern und sieht dann in einem Fenster die aktuelle Anzahl Impfungen in diesem Bundesland. Die Karte ist farblich hervorgehoben nach Anzahl Impfungen entsprechend der Skala am rechten Rand. Es gibt auf der linken Seite ein Drop Down Menü, wo man ein Bundesland auswählen kann, welches dann angezeigt wird (siehe [Auswahl Berlin]). Desweiteren gibt es bereits Radio Buttons zum Einstellen der Sprache, wobei die Funktion dahinter noch programmiert werden muss. Die weitere Beschreibung folgt im Ausblick, da wir gerade noch daran arbeiten.

![Screenshot vom aktuellen Stand der Hauptseite des Prototypes](../prototype_germany.jpg)
![Auswahl Berlin](../prototype_germany.jpg)

### Ausblick
Wir arbeiten zurzeit daran, eine Aufteilung ähnlich wie die beim Impfdashboard nach "Mindestens einmal Geimpfte", "Vollständig Geimpfte" und "Geimpfte mit Auffrischimpfungen" zu machen. Außerdem wollen wir auf die Hauptseite mit der gesamten Deutschlandkarte einen Informationstext unter die Karte setzen, sowie die zeitliche Abbildung des Impf-Fortschritts als entsprechenden Graph daneben. Sobald man ein Bundesland auswählt, soll man genauere Informationen zu dem aktuellen Stand in dem Bundesland bekommen. Dazu sollen zwei weitere Graphen entstehen, einmal die Aufteilung der Impfungen nach Altersgruppe und einmal der Zusammenhang zwischen Gesamtanzahl Impfungen und Krankenhausauslastung. Ob und inwiefern wir das letztere umsetzen, überlegen wir zurzeit noch. Außerdem wollen wir noch die Farbskala kontrollieren, sodass diese für alle aus der Zielgruppe akzeptabel ist.




### you can stop reading, the rest is work in progress

### Description with Munzner's “Four Nested Levels of Visualization Design” -not finished yet!!!
#### Domain problem characterization
Unsere Zielgruppe ist die Bevölkerung in Deutschland, die sich über das aktuelle Pandemiegeschehen informieren wollen. Dabei steht momentan hauptsächlich das Impfen im Vordergrund und in Diskussion, sodass wir uns hier auf den Impf-Fortschritt in Deutschland konzentrieren. Es entstehen Fragen wie die Verteilung der Anzahl Impfungen nach Altergruppen, der scheinbaren Auswirkung der Impfungen auf die aktuelle Krankenhausauslastung und Inzidenz und wie sich der Impf-Fortschritt über die Zeit entwickelt hat. Dabei möchte die Zielgruppe ggf. herausfinden, inwiefern die Impfungen eine Wirkung zeigen, die man in den Daten erkennen kann und dass das Impfen sich lohnt, für diejenigen unter der Zielgruppe die sich vielleicht bisher noch nicht für eine Impfung entschieden haben. 

#### Data / task abstraction: Formulate the tasks in a domain-independent vocabulary. Do not forget to describe your data sources based on the data Nutrion label information. How did you prepare (aggregate, filter...) the data to support the tasks? What tasks do you support?


#### Visual encoding / interaction design: Describe the visual encoding and why you decided for it. What interaction types did you use and why? (be precise and try to cover all details in this part)

#### Algorithm design (if this matters at all): How did you make sure that the computational complexity of your solution is appropriate? What is the bottleneck with respect to performance?


### Reflection
#### What did not work as expected (and why?)
#### What would you improve if you had more time?
#### If you used other libraries or frameworks other than Altair please explain briefly why.
