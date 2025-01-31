Change log
==========

Version 1.3.0
-------------

Removed support for incompatible `yet_another_wizz` version 3 and added
deprecation warnings. Please migrate to the simplifed commandline client
shipped with `yet_another_wizz` starting from version 3.1.


Version 1.2.6
-------------

Made code available as image on ``hub.docker.com``.


Version 1.2.5
-------------

Adapted code to new binning configuration class ``yaw.config.BinningConfig``.


Version 1.2.4
-------------

Fixed some parameter docstrings and help texts.


Version 1.2.3
-------------

- Capture all emitted warnings and redirect them to the logger.
- Added very simple test that runs the pipeline of randomyl generated data
  points.


Version 1.2.2
-------------

Added simple unit tests that run a randomised setup.

.. rubric:: Bug fixes

- Fixed the install dependency, which was pointing to ``yet_another_wizz``
  instead of the section in the client setup.
- Fixed formatting errors in the default configuration file: The task sections
  were missing ":" if they were followed by a mapping of default arguments, the
  filepath entry in the randoms sections was not indented correctly.


Version 1.2.1
-------------

.. rubric:: Bug fixes

- Corrected the incorrectly named dependency for ``yet_another_wizz``.


Version 1.2
-----------

Initial release as separate package. Previously the package was bundled with
``yet_another_wizz`` itself.
