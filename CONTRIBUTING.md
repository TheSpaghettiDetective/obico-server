# Contributing to Obico Server

Thanks for taking the time to improve Obico Server. This guide covers the normal process for opening a pull request against this repository.

## Pull Request Process

1. Start from `master`.

   The `release` branch is for end users and release builds. Do not open contributor pull requests against `release` unless a maintainer explicitly asks you to.

   ```bash
   git checkout master
   git pull --ff-only
   git switch -c your-change-name
   ```

2. Keep the change focused.

   A pull request should solve one problem at a time. If you are changing behavior, include the code, docs, and tests needed to explain and verify that behavior. If the change is exploratory or large, open an issue or draft PR first so maintainers can help shape the approach.

3. Run the server locally when your change affects backend behavior, Docker setup, ML API integration, or full-app workflows.

   For a local development server, use the dev compose override:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose-dev.yml up -d --build
   ```

   The web server runs at:

   ```text
   http://localhost:3334
   ```

   The `docker-compose-dev.yml` override runs Django with `manage.py runserver`, enables `DEBUG`, mounts the local `ml_api` directory, and exposes the ML API on port `3333`.

4. Run the frontend dev server when your change affects Vue code.

   ```bash
   cd frontend
   npm ci
   npm run serve
   ```

   Do not submit bundled frontend output from `npm run build` in your pull request. Commit source changes only.

5. Run the docs site locally when your change affects documentation under `website/`.

   ```bash
   cd website
   yarn
   yarn start
   ```

6. Run the relevant checks before opening the PR.

   For frontend changes:

   ```bash
   cd frontend
   npm run lint
   ```

   For backend changes:

   ```bash
   docker compose -f docker-compose.yml -f docker-compose-dev.yml run --rm web python manage.py test
   ```

   If a check changes files, review those changes before committing them. If you cannot run a relevant check locally, mention that in the PR description.

7. Commit with a clear message.

   Use a short subject that says what changed. Add a body when the reason or tradeoff is not obvious from the diff.

   ```bash
   git status
   git add path/to/changed-files
   git commit -m "Describe the change"
   ```

8. Push your branch and open a pull request against `master`.

   ```bash
   git push -u origin your-change-name
   ```

   In the PR description, include:

   - What changed.
   - Why the change is needed.
   - How you tested it.
   - Screenshots or screen recordings for user-facing UI changes.
   - Any migrations, configuration changes, compatibility concerns, or follow-up work.

9. Respond to review comments.

   Keep follow-up commits on the same branch. If `master` moves significantly while your PR is open, update your branch from `master` and resolve conflicts without rewriting unrelated code.

## Notes for Maintainers and Contributors

- Prefer small, reviewable PRs over broad refactors.
- Match the style and structure of the surrounding code.
- Do not include generated files unless they are intentionally part of the source tree.
- Do not commit secrets, local credentials, or machine-specific configuration.
- If your PR changes setup instructions, update the relevant README or documentation page in the same PR.
