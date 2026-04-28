==========================
Automation Mojo Interop
==========================

The ``automojo-interop`` package is the central interoperability layer in the automojo suite. It provides the base agent classes, protocol implementations, and manufacturer integrations that higher-level automation code uses to talk to the outside world. The package defines ``ISystemContext`` and ``INetworkClient`` under ``interfaces/`` as the seams other packages build against, and exposes an ``am-interop`` CLI command tree for operator-style interaction. It builds on ``automojo-interfaces``, ``automojo-errors``, ``automojo-networking``, and ``automojo-credentials``, and is in turn consumed by ``automojo-landscaping`` and the ``automojo-interop-ext-*`` extension packages.

Highlights
==========

- Agent bases under ``agents/``: ``SystemAgentBase``, ``SerialAgentBase``, ``PowerAgentBase``, and ``LocalCommandAgent``.
- Protocol implementations under ``protocols/`` covering DNS and mDNS, SSH, serial over TCP, and power control via DLI.
- Aspect-oriented ``Aspects`` object with ``ActionPattern`` and related enums for uniform retry, timeout, and connection behaviour.
- ``ISystemContext`` and ``INetworkClient`` interfaces under ``interfaces/`` for downstream consumers.
- ``InteropLibraryTestJob`` under ``testing/`` — interop-tier base class that adds the landscape-activation lifecycle hooks over the single-host ``automojo-testbase.TestJob``.  Concrete subclasses live in packages that depend on ``automojo-landscaping`` (for example ``automojo-testplus.DistributedTestJob``).
- ``am-interop`` CLI command tree for operator-style interaction.

Repository Structure
====================

- ``development/`` - Runtime environment scripts.
- ``repository-setup/`` - Repository homing and setup scripts.
- ``source/packages/`` - Package source code.
- ``source/testroots/automojo/`` - TestBase test roots.
- ``source/examples/`` - Example usage scripts.
- ``specs/`` - Requirements, design, and task documentation.
- ``userguide/`` - Standards, conventions, and documentation.

Environment Setup
=================

When working in a Codex container:

.. code-block:: bash

   ./development/setup-agent-container

For local development:

.. code-block:: bash

   ./repository-setup/rehome-repository
   ./development/setup-environment

Running Tests
=============

Activate the virtual environment:

.. code-block:: bash

   source .venv/bin/activate

Run the single-host test suite:

.. code-block:: bash

   testbase testing run --root source/testroots/automojo --includes=automojo.tests.interop.singlehost --output=./.output

Standards and Conventions
=========================

- Naming conventions: ``userguide/10-02-naming-conventions.rst``
- Code organization: ``userguide/10-01-code-organization.rst``
- Coding standards: ``userguide/10-00-coding-standards.rst``

Additional Resources
====================

- User guide entry point: ``userguide/userguide.rst``
- Specifications: ``specs/core-interop/``
