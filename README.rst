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

Copy or link some *.dsl dictionary files into the Lectus directory.



Usage
_____

``lectus DICTIONARY REGEX``

Examples
________

Assuming that you have a copy or a link to the **Photius** dictionary
(photius.dsl), to search for the lemma ``κηπος``::

      lectus photius κηπος

Τhis will return all the headwords that include the string ``κηπος``.
The search term must be typed without accents.
Searching is always case insensitive.

The search term can be a regular expression like::

  lectus photius κ.*ος

Will return all words that include that starts with a "κ" followed by any number
of characters and ends with a 'ς'::

 lectus suda \^κη\(π\|τ\)ος

This will return words like ``κῆπος`` and ``κῆτος``.


Any Perl like regular expression is acceptable input, but symbols that are
significant to the shell, like ``^,|,(,)`` etc. must be escaped.

Lectus displays the first 20 results that match the query.


When Lectus sees a dictionary for the first time it will generate an index file
(.idx) which records the location of every headword within the .dsl file.
Subsequent queries on the same dictionary will go through this index, find the
headword, read the corresponding index and rapidly locate the answer in the .dsl
file.













.. vim: set syntax=rst tw=80 spell fo=tq:
