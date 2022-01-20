# Robert Koch Institut - Impfquotenmonitoring
## by Leylanur Bodur, Melanie Vogel, Johanna Helene von Wachsmann (Group 6)

### Context
In light of the current pandemic situation due to COVID-19, the Robert Koch Institut (RKI) and the Bundesministerium für Gesundheit (BMG) publish frequently data regarding the pandemic behaviour, like the current incidence numbers and data about the vaccination progress in Germany. What is more, there is also a data set about the vaccination progress per state in Germany, which shows how this progress differs between the states. Furthermore, there is data about the vaccines themselves, the vaccination deliveries, the age groups, facilities, hospitalization and both the numbers of vaccinations and the vaccination rates. 

So, what is a vaccination rate ("Impfquote")? 

The vaccination rate is the proportion of all people in the total population that got vaccinated so far. Since there is no standardized system for the elicitation of vaccination data in Germany, subsamples and representative samples are used in order to allow an assessment of the current vaccination situation. The RKI and BMG officially publish the most updated  and best collection of the vaccination data. 

### Concept
We orientate ourselves by existing visualizations and descriptions of the RKI on the RKI website and on the [Impfdashboard](https://impfdashboard.de/daten). We use a chloropleth map as our map layout, so that we can show a good overbiew of the data in Germany. The number of vaccinations is color-coded, whereas we first had another color scheme, which was too colorful (confusing) and not suitable for colorblind people. 

The map shows the state borders in Germany and the numbers also represent state level. This has several reasons. To begin with, our goal is to give a general, really intuitive and non-confusing overview of the situation, whereas neighborhood level would yield a lot more numbers, borders and colors. This might be very confusing and overwhelming, especially for older people, and is not suitable for our approach, since we also provide a mouse hover feature vor detailed numbers per area. Secondly, direct comparisons of the number of vaccinations between a neighborhood in a metropole region and a country region wouldn't be suitable. Thirdly, the available data from the RKI and the BMG is also divided in states and data for all neighborhoods in Germany is hard / impossible to get our hands on. 

Furthermore, we decided to provide different language settings. The user should be able to choose between German, English, Turkish and Russian. This selection is based on the one on the website of the Impfdashboard, as well as on the fact from an [interview with the Bundesregierung](https://www.bundesregierung.de/breg-de/suche/interview-muttersprache-1721084#:~:text=Zu%20den%20meistgesprochenen%20Sprachen%20in%20Deutschland%20z%C3%A4hlen%2C%20neben%20nat%C3%BCrlich%20dem%20Deutschen%2C%20Russisch%20mit%20bis%20zu%20drei%20Millionen%20Muttersprachlern%2C%20T%C3%BCrkisch%20mit%20mehr%20als%20zwei%20Millionen%20Muttersprachlern), that besides English, these are the three most frequently spoken languages in Germany. 

In general, we want to provide a map from Germany, where the user can hover with the mouse over the different states to see the specific vaccination numbers and rate. There should be a drop down menu to select a specific state. If time permits, the map should be interactive in a way, where the user can also click on the respective state instead of choosing it from the drop down menu. Below the map, there should be more detailed information about the pandemic, general information, vaccination progress and vaccines. Next to it, there should be an overview of the vaccination progress over time and below these, there should be an overview of the vaccination rate per age group in Germany. The latter should change accordingly to a state when chosen, so that the vaccination rate per age group in the respective state is shown. Similar to that, we also want to show the hospitalization status in Germany over time and if time permits, have a comparison to the incidence and vaccination rate in a period of time. Since we want to reach as many people living in Germany as we can, including teenager, adults and seniors, there should be different language settings available on the website, namely German, English, Turkish and Russian. 

What is the purpose of our visualization? 

We want to emphasize the importance of vaccinations in view of hospitalization before and after vaccination progress, as well as the impact of herd immunity. We want to give more information, and also information in greater detail, of subtopics like vaccination rate, hospitalization, vaccination rate per age group for every state, not only whole Germany, number of vaccinations, not only the rate, etc.. We also want to display more visualizations in one place in comparison to existing websites.


### Prototype
On the following two pictures, you can see our current (state: 16/01/2022) prototype, where a lot of the above mentioned is still missing. Don't worry, a lot of it was added and adjusted by now (state 20/01/2022), so this is all a work in progress. You can hover over a state with your mouse to see the number of vaccinations in this state. The map is color-coded by number of vaccinations according to the scale on the right border. On the left side there is a drop down menu, where you can choose a state, which is then shown instead of whole Germany ([Auswahl Berlin]). There are also radio buttons for the selection of the language. 

![Screenshot vom aktuellen Stand der Hauptseite des Prototypes](../prototype_germany.jpg)
![Auswahl Berlin](../prototype_germany.jpg)

### Lookout /  what we work on right now
- prepare different languages for text ressources, figure labels and legends
- number of vaccinations over time divided into first, second and third vaccination
- option to go back to main page within drop down menu
- vaccination rate per age group in each state
- hospitalization vs Vaccination
- figure change when choosing a specific state
- tabs for at least one vaccination, initial immunization and booster vaccination
- data version info
- vaccination rate per age group for whole Germany
- info text
- documentation




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
