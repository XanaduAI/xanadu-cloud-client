# Contributing to the Xanadu Cloud Client

Thank you for taking the time to contribute to the Xanadu Cloud Client (XCC)!
:confetti_ball: :tada: :fireworks: :balloon:

While we will continue working on adding new and exciting features to the Xanadu
Cloud Client, we invite you to join us and suggest improvements or even just to
discuss how the XCC fits into your workflow.

## How can I contribute?

It's up to you!

* **Test the cutting-edge XCC releases** - clone our GitHub repository, and keep
  up to date with the latest features. If you run into any bugs, make a bug
  report on our
  [issue tracker](https://github.com/XanaduAI/xanadu-cloud-client/issues).

* **Report bugs** - even if you are not using the development branch of the XCC,
  if you come across any bugs or issues, make a bug report. See the next section
  for more details on the bug reporting procedure.

* **Suggest new features and enhancements** - use the GitHub issue tracker and
  let us know what will make the XCC even better for your workflow.

* **Contribute to our documentation** - if there is something you would like to
  add to our documentation or you have an idea for an improvement or change, let
  us know - or even submit a pull request directly. All authors who have
  contributed to the XCC codebase will be listed alongside the latest release.

* **Build an application on top of the XCC** - have an idea for an application
  where the XCC is a good match? Consider making a fully separate app that
  builds upon XCC as a base. Ask us if you have any questions, and send a link
  to your application to support@xanadu.ai so we can highlight it in our future
  documentation!

Appetite whetted? Keep reading below for all the nitty-gritty on reporting bugs,
contributing to the documentation, and submitting pull requests.

## Reporting bugs

We use the
[GitHub issue tracker](https://github.com/XanaduAI/xanadu-cloud-client/issues)
to keep track of all reported bugs and issues. If you find a bug, or have a
problem with the XCC, please submit a bug report! User reports help us make the
client better on all fronts.

To submit a bug report, please work your way through the following checklist:

* **Search the issue tracker to make sure the bug wasn't previously reported**.
  If it was, you can add a comment to expand on the issue and share your
  experience.

* **Fill out the issue template**. If you cannot find an existing issue
  addressing the problem, create a new issue by filling out the
  [bug issue template](ISSUE_TEMPLATE/bug-report.yml). This template is added
  automatically to the comment box when you create a new issue. Please try and
  add as many details as possible!

* Try and make your issue as **clear, concise, and descriptive** as possible.
  Include a clear and descriptive title, and include all code snippets and
  commands required to reproduce the problem. If you're not sure what caused the
  issue, describe what you were doing when the issue occurred.

## Suggesting features, document additions, and enhancements

To suggest features and enhancements, use the
[feature request template](ISSUE_TEMPLATE/feature-request.yml). Be sure to:

* **Use a clear and descriptive title**

* **Provide a step-by-step description of the suggested feature**.

    Explain why the enhancement would be useful as well as where and how you
    would like to use it.

## Pull requests

If you would like to contribute directly to the XCC codebase, simply make a
fork of the main branch and submit a
[pull request](https://help.github.com/articles/about-pull-requests). We
encourage everyone to have a go forking and modifying the XCC source code;
however, we have a couple of guidelines on pull requests to ensure the main
branch conforms to existing standards and quality.

### General guidelines

* **Do not make a pull request for minor typos/cosmetic code changes** - create
  an issue instead.
* **For major features, consider making an independent application** that runs
  on top of the XCC (rather than modifying the XCC directly).

### Before submitting

Before submitting a pull request, please make sure the following is done:

* **All new features must include a unit test.** If you've fixed a bug or added
  code that should be tested, add a test to the [`tests/`](tests/) directory!
* **All new classes, functions, and members must be clearly commented and
  documented**.
* **Ensure that the test suite passes.**  Verify that `make test` passes.
* **Ensure that the modified code is formatted correctly.**  Verify that
  `make lint` and `make format` pass.

### Submitting the pull request
* When ready, submit your fork as a
  [pull request](https://help.github.com/articles/about-pull-requests) to the
  XCC repository, filling out the
  [pull request template](PULL_REQUEST_TEMPLATE.md). This template is added
  automatically to the comment box when you create a new PR.

* When describing the pull request, please include as much detail as possible
  regarding the changes made, new features, and performance improvements. If
  including any bug fixes, mention the issue numbers associated with the bugs.

* Once you have submitted the pull request, two things will automatically occur:

  - The **test suite** will automatically run on
    [GitHub Actions](https://github.com/XanaduAI/xanadu-cloud-client/actions) to
    ensure that all tests continue to pass.

  - The **formatter** will automatically run on
    [GitHub Actions](https://github.com/XanaduAI/xanadu-cloud-client/actions) to
    ensure that all the code is properly formatted.

  Based on these results, we may ask you to make small changes to your branch
  before merging the pull request into the main branch. Alternatively, you can
  [grant us permission to make changes to your pull request branch](https://help.github.com/articles/allowing-changes-to-a-pull-request-branch-created-from-a-fork/).

Thank you for contributing to the Xanadu Cloud Client!

\- The XCC team
