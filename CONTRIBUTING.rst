Releasing
=========

Summary
-------

- The sunspec-demo repository uses the `feature branch workflow <https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow>`_ process to control development.
- The ``main`` branch must never be broken.
- Development is performed in feature branches, requiring peer reviewed pull requests to merge into ``main``. See step-by-step instructions below.
- A release requires a release branch, detailed in the step-by-step instructions below.
- The ``versioneer`` package automatically manages version handling code.

Step-by-step feature / bug fix
------------------------------

- Create a feature branch with a name identifying the feature or bug fix. Branch names loosely follow the gitflow format.

  - For a feature branch (feature, bug fix), name the branch in the format ``feature/JIRA_ID/short_description``.

- Commits should follow the `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ methodology.

  - For a commit, name the commit in the format ``TYPE (JIRA_ID): short description``.
  - Where ``TYPE = [ fix, feat, chore, build, docs, refactor, test, ci ]``

- When changes are ready, create a draft pull request for the feature branch.

- Update the ``HISTORY.rst`` file.

  - If this is the first change since the previous release, create a new release section at the top of the list.

    - The header should be as follows: Sunspec-demo VERSION (DATE)

  - Update the version depending on the change complexity (major/minor/patch). See the release instructions for the version semantics.
  - Add an entry describing the feature / bug fix for the current feature branch.

    - The description should contain a link to the current pull request (format: ``Description. (PR_LINK)``)

- Request a review for the pull request and address raised concerns until receiving an approval.

- Merge the feature branch pull request.

Step-by-step release
--------------------

- Define the final release version you are preparing.

  - ``epcpower/sunspec-demo`` uses `SemVer <https://semver.org/>`_ of the form ``MAJOR.MINOR.PATCH``.
  - Normalize the version according to `PEP 440 <https://www.python.org/dev/peps/pep-0440/#normalization>`_.

- Create a release branch with a name of the form ``release/MAJOR.MINOR.PATCH`` (example: ``release/1.2.4``) starting from the ``main`` branch.

- Update the ``HISTORY.rst`` file.

  - Edit the date and version, if necessary.
  - Edit any of the change descriptions, if necessary, following the pattern described in the feature / bug fix instructions.

- Commit and push update to the primary repository, not a fork.

- Create a pull request named in the format ``Release vMAJOR.MINOR.PATCH``.

- Request a review and address raised concerns until receiving an approval.

- Merge the release branch pull request to ``main``.

- Tag the merged commit in the format ``vMAJOR.MINOR.PATCH`` and push the tag to the primary repository.

  - This will result in another build, which will generate the official release artifacts.
