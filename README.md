# Hello, world!

And thanks for your interest.

If you came to check out my resume, it's [right here](https://github.com/4min/resume/blob/master/ilya_fomin_cv.md).

I'm accepting pull requests and other collaboration opportunities.

## PDF version

PDF version is available for download on [the releases tab](https://github.com/fominfo/resume/releases). Cloud Build makes it on every push to `master`; `python3 render.py` makes the same PDF on a Mac with `gh` and Chrome.

# Create your own automated resume

Feel free to fork this repo and create an automated resume of your own. References to the source are encouraged, but are not mandatory.

This project consists of 2 parts:
- A simple Markdown (document that can be rendered by GitHub natively
- Configuration for [Google Cloud Build](https://cloud.google.com/cloud-build/) service to render the .md file into a good-looking PDF and upload back to GitHub as a release attachment

Here's what you need to do:
1. Fork this repo
2. Replace ilya_fomin_cv.md with your own Markdown resume file
3. Create a github developer token as [described here](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) with rights to read and write specific resume respository. I recommend using a separate "-machine" account, just to make sure you don't compromize your personal one.
4. Create a GCP account for the automated build. If you want to share the build publically - create a GCP project.
5. Ensure KMS is enabled and works as [described here](https://cloud.google.com/kms/docs/quickstart)
6. Encrypt the GitHub token from step (3) [using Google's KMS](https://cloud.google.com/cloud-build/docs/securing-builds/use-encrypted-secrets-credentials)
7. Update cloudbuild.yaml according to your changes:
   - 'substitutions' section according to your repo and file name, and zoom value to make the printout look nice
   - 'secrets' section with your KMS key and the encrypted token string
1. Install and configure [GitHub GCP integration](https://github.com/marketplace/google-cloud-build)
2. Make any change in your repo and confirm that automated builds triggers, and a new release gets created