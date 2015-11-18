===================
web.dispatch.object
===================

    © 2015 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/web.dispatch.object

..

    |latestversion| |downloads| |masterstatus| |mastercover| |issuecount|



Introduction
============

Dispatch is the process of taking some starting point and a path, then resolving the object that path refers to. This
process is common to almost every web application framework (transforming URLs into controllers), RPC system, and even
filesystem shell. Other terms for this process include: "traversal", "routing", or "lookup".

Object dispatch is a particular flavour of dispatch that attempts to resolve path elements as a chain of object
attributes.  This is similar to how Python's ``import`` machinery would work, with modules being just another object.
A simplified analogy for object dispatch would be that of a filesystem, with "objects" as directories, and
"attributes" as files.

This package speaks a standardized `dispatch protocol <https://github.com/marrow/WebCore/wiki/Dispatch-Protocol>`_ and
is not entirely intended for direct use by most developers. The target audience is instead the authors of frameworks
that may require such modular dispatch for use by their own users.


Installation
============

Installing ``web.dispatch.object`` is easy, just execute the following in a terminal::

    pip install web.dispatch.object

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`_, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`_.

If you add ``web.dispatch.object`` to the ``install_requires`` argument of the call to ``setup()`` in your
application's ``setup.py`` file, this dispatcher will be automatically installed and made available when your own
application or library is installed.  We recommend using "less than" version numbers to ensure there are no
unintentional side-effects when updating.  Use ``web.dispatch.object<2.2`` to get all bugfixes for the current release,
and ``web.dispatch.object<3.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not
installed.


Development Version
-------------------

    |developstatus| |developcover|

Development takes place on `GitHub <https://github.com/>`_ in the 
`web.dispatch.object <https://github.com/marrow/web.dispatch.object/>`_ project.  Issue tracking, documentation, and
downloads are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/web.dispatch.object.git
    (cd web.dispatch.object; python setup.py develop)

You can then upgrade to the latest version at any time::

    (cd web.dispatch.object; git pull; python setup.py develop)

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`_.


Usage
=====

This section is split to cover framework authors who will need to integrate the overall protocol into their systems,
and the object interactions this form of dispatch provides for end users.


Framework Use
-------------

At the most basic level, in order to resolve paths against a tree of objects one must first insantiate the dispatcher::

    from web.dispatch.object import ObjectDispatch
    
    dispatch = ObjectDispatch()  # Opportunity to pass configuration options here.

The object dispatcher currently only has one configurable option: ``protect``. This defaults to ``True``, and will
prematurely end dispatch in the event it encounters a path element beginning with an underscore. This protects Python
magic attributes (such as ``__name__``), mangled "private" methods (such as ``__foo``), and protected-by-convention
single underscore prefixed attributes (such as ``_foo``). Python ordinarily does not enforce such protections,
excepting the "mangling" feature.

Now that you have a prepared dispatcher, and presuming you have some "base object" to start dispatch from, you'll need
to prepare the path according to the protocol::

    path = "/foo/bar/baz"  # Initial path, i.e. the path component of a URL.
    path = path.split('/')  # Find the path components.
    path = path[1:]  # Skip the singular leading slash; see the API specification.
    path = deque(path)  # Provide the path as a deque instance, to allow for optimized ``popleft()``.

Of course, the above is rarely split apart like that. We split apart the invidiual steps of path processing here to
more clearly illustrate the process. In a web framework the above would happen once per request that uses dispatch.

You can now call the dispatcher and iterate the dispatch events::

    for segment, handler, endpoint in dispatch(None, some_object, path):
        print(segment, handler, endpoint)  # Do something with this information.

The initial ``None`` value there represents the "context" to pass along to initializers of classes encountered during
dispatch.  If the value ``None`` is provided, classes won't be instantiated with any arguments. If a context is
provided it will be passed as the first positional argument to instantiation.

After completing iteration, check the final ``endpoint``.  If it is ``True`` then the path was successfully mapped to
the object referenced by ``handler`` variable, otherwise it represents the deepest object that was able to be found.
While some dispatchers might not support partial path resolution and may instead raise ``LookupError`` or a subclass,
such as ``AttriuteError`` or ``KeyError``, object dispatch does not do this. This is to allow the framework making
use of object dispatch to decide for itself how to proceed in the event of failed or partial lookup in a somewhat
cleaner way than extensive exception handling within a loop.

In the context of a web framework dispatch being an iterable process makes a lot of sense. In the simplest use of
iteration, path elements would be moved from ``PATH_INFO`` to ``SCRIPT_NAME`` as dispatch progresses. You can
always just skip straight to the answer::

    segment, handler, endpoint = list(dispatch(None, some_object, path))[-1]

However, providing some mechanism for callbacks or notifications of dispatch is often far more generally useful.


Dispatchable Objects
--------------------

Every object, of every built-in or third-party class in Python, supports object dispatch.



Version History
===============

Version 2.1
-----------

* Massive simplification and conformance to common dispatch protocol.

Version 2.0
-----------

* Extract of the object dispatch mechanism from WebCore.

Version 1.x
-----------

* Process fully integrated in the WebCore web framework.


License
=======

web.dispatch.object has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2015 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. |masterstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.object/master.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object
    :alt: Release Build Status

.. |developstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.object/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object
    :alt: Development Build Status

.. |latestversion| image:: http://img.shields.io/pypi/v/web.dispatch.object.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.object
    :alt: Latest Version

.. |downloads| image:: http://img.shields.io/pypi/dw/web.dispatch.object.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.object
    :alt: Downloads per Week

.. |mastercover| image:: http://img.shields.io/coveralls/marrow/web.dispatch.object/master.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object
    :alt: Release Test Coverage

.. |developcover| image:: http://img.shields.io/coveralls/marrow/web.dispatch.object/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object
    :alt: Development Test Coverage

.. |issuecount| image:: http://img.shields.io/github/issues/marrow/web.dispatch.object.svg?style=flat
    :target: https://github.com/marrow/web.dispatch.object/issues
    :alt: Github Issues

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
