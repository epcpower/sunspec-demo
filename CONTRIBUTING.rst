Releasing
=========

Summary
-------

- Create a release branch from the develop branch in the original ``epcpower/sunspec-demo`` repository, not in a fork.
- Create a commit for a release candidate inside the release branch.
- Create a Pull Request for the release. The same branch and PR will be used for both the release candidates and  the final release.
- Get an approving review.
- Once approved, tag the last commit in the branch as a release candidate.
- Push the tag. This will trigger a build including the upload of artifacts.
- Prepare a commit for a final release and push it to the release branch.
- Get an approving review for the final release.
- Tag the commit using the final release version. This will trigger the upload of artifacts.
- Merge the release branch.


Step-by-step
------------

- Define the final release version you are preparing.

  - ``epcpower/sunspec-demo`` uses `CalVer <https://calver.org/>`_ of the form ``YYYY.0M.micro`` with the micro version just incrementing.
  - Normalize the version according to `PEP 440 <https://www.python.org/dev/peps/pep-0440/#normalization>`_.

- Create a release branch with a name of the form ``release-v2021.09`` starting from the ``develop`` branch.

  - On the new release branch you will commit all tagged release candidate commits as well as the final tagged release commit.

- Update the version to the release candidate with the first being ``rc1`` (as opposed to 0).

  - In ``src/epcsunspecdemo/_version.py`` the version is set manually formatted such as ``__version__ = "2021.09.0rc1"``

- Commit and push to the primary repository, not a fork.

  - It is important to not use a fork so that pushed tags end up in the primary repository, server provided secrets for publishing to PyPI are available, and maybe more.

- If working on the first release candidate from this branch, create a PR named in the form ``Release v2021.09``.

- Request a review and address raised concerns until receiving an approval.

- Tag that commit in the format ``v2021.09rc1`` and push the tag to the primary repository.

  - This will result in another build which will publish to PyPI.
  - Confirm the presence of the release on PyPI.

- `Dismiss the approving review <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/dismissing-a-pull-request-review>`_.

  - The review process will be reused for any subsequent release candidates, the final release, and the post-release tweaks so it must be cleared at each stage.

- If another release candidate is required:

  - Submit PRs against the release branch to integrate the needed changes. Any PRs could be cherry picks from the ``master`` branch if already resolved there, or direct PRs against the release branch that will be merged back into ``develop`` at the completion of the release.

  - Return to the step where the version is updated and increment the release candidate number.

- If ready for a final release, remove the release candidate indicator from the version.

  - Edit ``src/epcsunspecdemo/_version.py`` to be formatted such as ``__version__ = "2021.09.0"`` to remove the release candidate indication.

- If the final release has been completed, continue below.

- Increment the patch/micro version by one and set to a development version.

  - In ``src/epcsunspecdemo/_version.py`` the version is set manually formatted such as ``__version__ = "2021.09.1+dev"``

- Merge without waiting for an approving review.
