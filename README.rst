+++++++++++++++++
Lectus
+++++++++++++++++

WORK IN PROGRESS
________________


Description
___________

Lectus is a script to query dictionary files (for the moment, only ABBYY Lingvo
.dsl dictionaries) and display the results in a Linux terminal.

-----------------------------------------------------------------

.. figure:: lectus.png
   :scale: 100
   :align: center
   :alt: Lectus Ilustration

-----------------------------------------------------------------

Installation
____________

Clone the GitHub repository::

   git clone:https://github.com/proteusx/Lectus.git


Copy or link some .dsl dictionary files into the Lectus directory.


Usage
_____


``lectus <LEMMA> [OPTION]``

OPTIONS::

       -i or --index               Index all installed dictionaries
       -l or --lexica              Space separated list of dictionaries
       -d or --directory           Path to the dictionaries directory
                                   ( default directory ./)

If option ``-i`` is given then Lectus will index all dictionaries found in the
default directory ``./dictionaries`` or in the directory specified with by option
``-d``

If option ``-l`` is given and it is followed by one or more dictionary names, these will be
searched, otherwise all dictionaries present in the specified directory, or in the
default current working directory (CWD), will be searched in sequence.

Examples
________

Assuming that you have a copy or a link to the Photius_ lexicon
(file ``photius.dsl``), to search for the lemma ``κηπος``::

      lectus  κηπος -l photius

This will return the meaning of the exact word ``κηπος``. The search term must be typed without accents.
Searching is always case insensitive.

To search all dictionaries for the word ``κηπος``::

      lectus κηπος

The search term can include the SQLlite wildcard characters '%' and '_'::

  lectus κη_ος -l suda

Will return κῆδος, κημός, κῆπος, κῆτος, etc,.

To search all installed dictionaries for words ending in 'κηπος'::

  lectus %κηπος

This will search all dictionaries for entries that include the string
'λεγω' ::

  lectus %λεγω%

Lectus displays in alphabetical order the first 20 results that match the query.


When Lectus sees a dictionary for the first time it will generate an index file
(.db) which records the location of every headword within the .dsl file.
Subsequent queries on the same dictionary will go through this index, find the
headword, read the corresponding index and rapidly locate the answer in the .dsl
file.

.. _Photius: https://github.com/proteusx/Photius-Lexicon
.. _Suda: https://github.com/proteusx/Suda-For-GoldenDict









.. vim: set syntax=rst tw=80 spell fo=tq:


