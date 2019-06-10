===================
web.dispatch.object
===================

    © 2009-2019 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/web.dispatch.object

..

    |latestversion| |ghtag| |downloads| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|



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
unintentional side-effects when updating.  Use ``web.dispatch.object<3.1`` to get all bugfixes for the current release,
and ``web.dispatch.object<4.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not
installed.


Development Version
-------------------

    |developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`_ in the 
`web.dispatch.object <https://github.com/marrow/web.dispatch.object/>`_ project.  Issue tracking, documentation, and
downloads are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`_, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/web.dispatch.object.git
    pip install -e 'web.dispatch.object[development]'

You can then upgrade to the latest version at any time::

    (cd web.dispatch.object; git pull; pip install -e .)

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
excepting the "mangling" feature which is only `security through obscurity <http://s.webcore.io/image/1X3T0p2h3O0K>`_.

Now that you have a prepared dispatcher, and presuming you have some "base object" to start dispatch from, you'll need
to prepare the path according to the protocol::

    path = "/foo/bar/baz"  # Initial path, i.e. an HTTP request's PATH_INFO.
    path = path.split('/')  # Find the path components.
    path = path[1:]  # Skip the singular leading slash; see the API specification.
    path = deque(path)  # Provide the path as a deque instance, allowing popleft.

Of course, the above is rarely split apart like that. We split apart the invidiual steps of path processing here to
more clearly illustrate. In a web framework the above would happen once per request that uses dispatch. This, of
course, frees your framework to use whatever internal or public representation of path you want: choices of
separators, and the ability for deque to consume arbitrary iterables. An RPC system might ``split`` on a period and
simply not have the possibility of leading separators. Etc.

You can now call the dispatcher and iterate the dispatch events::

    for segment, handler, endpoint, *meta in dispatch(None, some_object, path):
        print(segment, handler, endpoint)  # Do something with this information.

The initial ``None`` value there represents the "context" to pass along to initializers of classes encountered during
dispatch.  If the value ``None`` is provided, classes won't be instantiated with any arguments. If a context is
provided it will be passed as the first positional argument to instantiation.

After completing iteration, check the final ``endpoint``.  If it is ``True`` then the path was successfully mapped to
the object referenced by the ``handler`` variable, otherwise it represents the deepest object that was able to be
found. While some dispatchers might not support partial path resolution and may instead raise ``LookupError`` or a
subclass, such as ``AttriuteError`` or ``KeyError``, object dispatch does not do this. This is to allow the framework
making use of object dispatch to decide for itself how to proceed in the event of failed or partial lookup, in a
somewhat cleaner way than extensive exception handling within a loop.

In the context of a web framework, dispatch being an iterable process makes a lot of sense. In the simplest use of
iteration, path elements would be moved from ``PATH_INFO`` to ``SCRIPT_NAME`` as dispatch progresses, or to build up a
"bread crumb list" of accessible controllers.

You can always just skip straight to the answer if you so choose::

    segment, handler, endpoint, *meta = list(dispatch(None, some_object, path))[-1]

However, providing some mechanism for callbacks or notifications of dispatch is often far more generally useful.

**Note:** It is entirely permissable for dispatchers to return ``None`` as a processed path segment. Object dispatch
will do this to announce the starting point of dispatch. This is especially useful if you need to know if the initial
object was a class that was instantiated.  (In that event ``handler`` will be an instance of ``some_object`` during
the first iteration instead of being literally ``some_object``.)  Other dispatchers may return ``None`` at other
times, such as to indicate multiple steps of intermediate processing.

Python 2 & 3 Compatibility
~~~~~~~~~~~~~~~~~~~~~~~~~~

The dispatch protocol is designed to be extendable in the future by using ``namedtuple`` subclasses, however this has
an impact on usage as you may have noticed the ``*meta`` in there. This syntax, introduced in Python 3, will gather
any extraneous tuple elements into a separate list. If you actually care about the metadata do not unpack the tuple
this way.  Instead::

    for meta in dispatch(None, some_object, path):
        segment, handler, endpoint = step[:3]  # Unpack, but preserve.
        print(segment, handler, endpoint, meta)  # Do something with this information.

This document is written from the perspective of modern Python 3, and throwing away the metadata within the ``for``
statement itself provides more compact examples. The above method of unpacking the first three values is the truly
portable way to do this across versions.


Dispatchable Objects
--------------------

Every object, of every built-in or third-party class in Python, supports object dispatch. This is because this form
of dispatch is implemented as a series of basic ``getattr()`` calls happening in a loop. In theory, you can dispatch
against anything. In practice, there are certain expectations and protocols you will have to work within. The first of
these notes is extremely important to keep in mind:

* Bare classes are instantiated with zero or one positional argument, depending on the presence of a context.
* You can override ``getattr()`` by providing a ``__getattr__(self, name)`` method in your object's class.
* Python has no particular distinction between a "real" attribute and one generated by ``__getattr__``, so if
  protection is enabled dispatch would stop and your ``__getattr__`` method would never be called when
  encountering protected path elements.
* If a callable routine is encountered, it is considered the endpoint regardless of the presence of additional path
  elements. This does not extend to classes with ``__call__`` methods, allowing mixed use in that situation.

With those elements out of the way, we'll work up from the simplest possible example, a single function::

    def hola():
        pass

Any path resolved against a plain function will resolve to that plain function. You can't "descend" past any routine;
they are, by definition, endpoints. In this instance there will be only a single dispatch event.

A slightly more complex example involves a class with callable instances::

    class Thing:
        def __call__(self):
            pass

Similar to an isolated function, an instance of the ``Thing`` class will be the endpoint for all paths. As a note,
more specific attributes are preferred over the instance-level ``__call__``, however an empty path (in this example)
will always use the instance as the endpoint, and missing attributes will also use the instance as the endpoint. It is
up to the framework you are using to determine if this is a problem or not, i.e. to allow unprocessed path elements.

In the following example::

    class Thing:
        class foo:
            def bar(self):
                pass

Only dispatch to the paths ``/``, ``/foo``, and ``/foo/bar`` will resolve, and only ``/foo/bar`` finds a recognizable
endpoint. For a somewhat real-world example, the following would successfully represent a database-backed collection
of things, each with their own set of endpoints::

    class Thing:
        def __init__(self, identifier):
            self._thing = identifier  # This might look it up from the DB.
        
        def __call__(self):
            pass  # Handle direct access to an identified thing.
        
        def action(self):
            pass  # This will match any path in the form /<identifier>/action
    
    class Things:
        def __call__(self):
            pass  # This will only handle the path /
        
        def __getattr__(self, identifier):
            return Thing(identifier)

Because there is a ``__getattr__`` method and it does not raise an ``AttributeError`` all first path segments are
valid on the ``Things`` class, giving you such paths as::

    / - Things.__call__
    /foo - Thing.__call__
    /foo/action - Thing.action
    /bar - Thing.__call__
    /bar/action - Thing.action

Et cetera.


Version History
===============

Version 3.0
-----------

* Python 2 support removed and Python 2 specific code eliminated.
* Updated to utilize Python 3 namespace packaging. **Critical Note**: This is not compatible with any Marrow package
  that is backwards compatible with Python 2.

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

Copyright © 2009-2019 Alice Bevan-McGregor and contributors.

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


.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/web.dispatch.object.svg?style=social&label=Watch
    :target: https://github.com/marrow/web.dispatch.object/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/web.dispatch.object.svg?style=social&label=Star
    :target: https://github.com/marrow/web.dispatch.object/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/web.dispatch.object.svg?style=social&label=Fork
    :target: https://github.com/marrow/web.dispatch.object/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.object/master.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/web.dispatch.object/master.svg?style=flat
    :target: https://codecov.io/github/marrow/web.dispatch.object?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/web.dispatch.object.svg
    :target: https://requires.io/github/marrow/web.dispatch.object/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/web.dispatch.object/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/web.dispatch.object/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/web.dispatch.object/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/web.dispatch.object?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/web.dispatch.object.svg
    :target: https://requires.io/github/marrow/web.dispatch.object/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/web.dispatch.object.svg?style=flat
    :target: https://github.com/marrow/web.dispatch.object/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/web.dispatch.object/2.1.0.svg
    :target: https://github.com/marrow/web.dispatch.object/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/web.dispatch.object.svg
    :target: https://github.com/marrow/web.dispatch.object/tree/2.1.0
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/web.dispatch.object.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.object
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/web.dispatch.object.svg?style=flat
    :target: https://pypi.python.org/pypi/web.dispatch.object
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat
