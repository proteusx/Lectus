+++++++++++++++++
Lectus
+++++++++++++++++

WORK IN PROGRESS
________________


Description
___________

Lectus is a script to query dictionay files (only ABBYY Lingvo .dsl for the
moment) and display the results in a Linux terminal.


Installation
____________

Clone the GitHub repository::

   git clone:https://github.com/proteusx/Lectus.git

Copy or link some *.dsl dictionary files into the Lectus directory.



Usage
_____

``lectus DICTIONARY REGEX``

Example: Assuming that you have a copy or a link to the **Photius** dictionary
(photius.dsl), to search for the lemma ``κηπος``::

      lectus photius κηπος

The search term must be typed without accents.

The search term can be a regular expression like: ``κ.*ος`` or ``\^κη\(π\|τ\)ος``.
Any Perl like regular expression is acceptable but symbols that are significant
to the shell, like ``^,|,(,)`` etc. must be escaped.

Lectus displays the first 20 results that match the query.













.. vim: set syntax=rst tw=80 spell fo=tq:
