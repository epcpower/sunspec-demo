Releasing
=========

Summary
-------

- The sunspec-demo repository uses the `feature branch workflow <https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow>`_ process to control development.
- The ``main`` branch must never be broken.
- Development is performed in feature branches, requiring peer reviewed pull requests to merge into ``main``.
- A release also require a branch, detailed in the step-by-step instructions below.
- The ``versioneer`` package automatically manages version handling code.


Step-by-step
------------

- Define the final release version you are preparing.

  - ``epcpower/sunspec-demo`` uses `SemVer <https://semver.org/>`_ of the form ``MAJOR.MINOR.PATCH``.
  - Normalize the version according to `PEP 440 <https://www.python.org/dev/peps/pep-0440/#normalization>`_.

- Create a release branch with a name of the form ``release-vMAJOR.MINOR.PATCH`` (example: ``release-v1.2.4``) starting from the ``main`` branch.

- Update the ``HISTORY.rst`` file.

  - Summarize all of the features and bug fixes since the previous release.
  - Add a new release section to the top of the list.

    - Sunspec-demo VERSION (DATE)

  - The format of each summarized feature and bug fix should be as follows:

    - Description of feature(s), bug fix(es), etc. (Link to appropriate pull request)

- Commit and push update to the primary repository, not a fork.

- Create a PR named in the form ``Release vMAJOR.MINOR.PATCH``.

- Request a review and address raised concerns until receiving an approval.

- Merge the pull request to ``main``.

- Tag the merged commit in the format ``vMAJOR.MINOR.PATCH`` and push the tag to the primary repository.

  - This will result in another build, which will generate the official release artifacts.
