---
description: "Wire up GitHub Actions CI for a .NET 8 project using ag-devops shared workflow templates. Generates an entry workflow and guides selection of the right build, test, lint, and package workflows."
---

Use the `setup-dotnet-ci` skill to configure GitHub Actions CI for a .NET 8 application using the shared templates from `ci/dotnetcore/`.

Ask the developer:
1. What is the solution file path (e.g. `./MySolution.sln`)?
2. Where are the test projects (folder paths)?
3. What coverage threshold is required (default 80%)?
4. Does the project produce a NuGet package or a win-x64 executable?
5. Does the project use gRPC / protobuf?
6. Self-hosted runners or GitHub-hosted (`ubuntu-latest`)?

Then generate the complete `.github/workflows/ci.yml` entry workflow referencing the correct shared templates, and list which workflow files need to be copied from `ci/dotnetcore/` into the app repo.
