************
 NHL ranker
************

Track current rankings, as well as trends and recent patterns for your favorite
team.

Model the probability of winning the next game, making playoffs, winning
specific playoff games, or the championship as a whole.


Notes
#####

I hope to extend this to include individual/player statistics at some point
too.

Initially available as a **command line interface**.

Eventually this will be hosted as a website rendered by a Flask API and
Svelte front-end, and available in a more dynamic, engaging format.

I suggest using ``direnv`` to automatically load/unload the ``venv`` shell.

.. code-block:: bash

  sudo apt install direnv


Running
~~~~~~~

Requires ``Python3`` and ``venv``.  See the ``argcomplete`` package page for
details on how to set it up with various shells, the tab-completion is working
on this project and highly useful to anyone using this program.

.. code-block:: bash

  git clone https://github.com/nutratech/nhlrank.git
  cd nhlrank

  make init
  make deps

  ./sp fetch  # if CSV is out of date
  ./sp stand -c  # "-c" means used cached, e.g. don't fetch
  ./sp stand -c -t "Detroit Red Wings"  # show details for a team
  ./sp stand -c -s rating  # sort teams in standings by Glicko rating

  # sort teams in standings by average opponent, include team details
  ./sp stand -c -t "Anaheim Ducks" -s avg_opp

  # show help
  ./sp -h
  ./sp stand -h


Shortcut for testing
~~~~~~~~~~~~~~~~~~~~

You can create a symbolic link for quick testing.

.. code-block:: bash

  sudo ln -s "<FULL_PATH_TO_sp>" /usr/local/bin/sp

Test it.

.. code-block:: bash

  sp stand -h
