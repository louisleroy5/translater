Reading and running IDF files
=============================

`translater` is packed up with some built-in workflows to read, edit and run EnergyPlus files.

Reading
-------

To read an IDF file, simply call :meth:`~translater.idfclass.load_idf` with the path name. For example:

.. code-block:: python

    >>> from translater import get_eplus_dirs, load_idf
    >>> eplus_dir = get_eplus_dirs("9-2-0")  # Getting EnergyPlus install path
    >>> eplus_file = eplus_dir / "ExampleFiles" / "BasicsFiles" / "AdultEducationCenter.idf"  # Model path
    >>> idf = load_idf(eplus_file)  # IDF load

You can optionally pass the weather file path as well:

.. code-block:: python

    >>> weather = eplus_dir / "WeatherData" / "USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw"  # Weather file path
    >>> idf = load_idf(eplus_file, weather_file=weather)  # IDF load

Editing
-------

Editing IDF files is based on the :ref:`eppy` package. The :class:`~translater.idfclass.IDF` object returned by
:meth:`~translater.idfclass.load_idf` exposes the EnergyPlus objects that make up the IDF file. These objects can be
edited and new objects can be created. See the `eppy documentation <https://eppy.readthedocs.io/en/latest/>`_ for
more information on how to edit IDF files.

.. hint:: Pre-sets

    EnergyPlus outputs can be quickly defined using the :class:`translater.idfclass.OutputPrep` class. This class
    and its methods handle adding predefined or custom outputs to an IDF object. For example, the
    idf object created above can be modified by adding a basic set of outputs:

    .. code-block:: python

        >>> from translater import OutputPrep
        >>> OutputPrep(idf=idf, save=True).add_basics()

    See :class:`~translater.idfclass.OutputPrep` for more details on all possible methods.


Running
-------

Running an EnerguPlus file can be done in two ways. The first way is to call the :meth:`translater.idfclass.run_eplus`
function with the path of the IDF file and the path of the weather file. The second method is to call the
:meth:`~translater.idfclass.IDF.run_eplus` method on an :class:`~translater.idfclass.IDF` object that has been
previously read. In both cases, users can also specify run options as well as output options. For example, instead of
creating an OutputPrep object, one can specify custom outputs in the
:py:attr:`translater.idfclass.run_eplus.prep_outputs` attribute. These outputs will be appended to the IDF file before
the simulation is run. See :meth:`~translater.idfclass.run_eplus` for other parameters to pass to `run_eplus`.

For the same IDF object above, the following:

.. code-block:: python

    >>> idf.run_eplus(weather_file=weather)

is equivalent to:

.. code-block:: python

    >>> from translater import run_eplus
    >>> run_eplus(eplus_file, weather)

.. hint:: Caching system.

    When running EnergyPlus simulations, a caching system can be activated to reduce the number of calls to the
    EnergyPlus executable. This can be helpful when `translater` is called many times. This caching system will save
    simulation results in a folder identified by a unique identifier. This identifier is based on the content of the IDF
    file, as well as the various :meth:`~translater.idfclass.run_eplus` options. If caching is activated, then
    subsequent calls to the :meth:`~translater.idfclass.run_eplus` method will return the cached results.

    The caching system is activated by calling the :meth:`translater.utils.config` method, which can also be used to
    set a series of package-wide options. ``config`` would typically be put at the top of a python script:

    .. code-block:: python

        >>> from translater import config
        >>> config(use_cache=True)