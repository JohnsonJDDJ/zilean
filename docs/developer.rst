.. Ideas of this document originate from sci-kit
   learn's "Contributing" page at
   https://scikit-learn.org/stable/developers/contributing.html#ways-to-contribute

Developer Doc
=============

This project is a community effort, and everyone is welcome to 
contribute.

The project is hosted on `<https://github.com/JohnsonJDDJ/zilean>`__.

Ways to Contribute
------------------

There are many ways to contribute to zilean, with the 
most common ones being contribution of **code** or 
**documentation** to the project. 

Improving the documentation is no less important than improving 
the library itself. If you find a typo in the documentation, 
or have made improvements, do not hesitate to send an email to 
johnsondzh@gmail.com or preferably submit a GitHub pull request. 
Full documentation can be found under the ``doc/`` directory.

How to Contribute
-----------------

The preferred way to contribute to zilean is to fork the main 
repository on GitHub, then submit a “pull request” (PR).

#. `Create <https://github.com>`__ a GitHub account if you don't
   have one.
#. Fork the `project repository <https://github.com/JohnsonJDDJ/zilean>`__ 
   click on the "Fork" button near the top of the page. This 
   creates a copy of the code under your account on the GitHub 
   user account.
#. Clone your fork of the zilean repo from your GitHub account to 
   your local disk. Replace ``YourLogin`` with your GitHub username:

    .. code-block:: bash

        $ git clone git@github.com:YourLogin/zilean.git 
        $ cd zilean

#. Add the ``upstream`` remote. This saves a reference to the main 
   zilean repository, which you can use to keep your repository 
   synchronized with the latest changes:

    .. code-block:: bash
    
        $ git remote add upstream git@github.com:JohnsonJDDJ/zilean.git

#. Check that the ``upstream`` and ``origin`` remote aliases 
   are configured correctly by running ``git remote -v`` which 
   should display:

   .. code-block:: bash
    
        origin      git@github.com:YourLogin/zilean.git (fetch)
        origin      git@github.com:YourLogin/zilean.git (push)
        upstream    git@github.com:JohnsonJDDJ/zilean.git (fetch)
        upstream    git@github.com:JohnsonJDDJ/zilean.git (push)

#. You should now have a working installation of zilean, and 
   your git repository properly configured. The next steps now 
   describe the process of modifying code and submitting a **PR**.
#. You need to synchronize your main branch with the upstream/main 
   branch **before** you make any modification:

   .. code-block:: bash

        $ git checkout main
        $ git fetch upstream
        $ git merge upstream/main

#. Create a feature branch to hold your development changes.
   Replace ``my_feature`` with the name of your feature:

    .. code-block:: bash

        $ git checkout -b my_feature

#. Start making changes. It is a good idea to always use a 
   feature branch. As you make changes, use ``git add`` and
   ``git commit`` to record your changes. Then, push the 
   changes to your GitHub account with:

   .. code-block:: bash

        $ git push -u origin my_feature

#. Finally, follow `these <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork>`__ 
   instructions to create a pull request from your fork. 
   Your pull request will be reviewed, and we will follow
   up with you for any further changes.

GL;HF!