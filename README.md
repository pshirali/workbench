# WorkBench

[![CircleCI](https://circleci.com/gh/pshirali/workbench.svg?style=shield)](https://circleci.com/gh/pshirali/workbench) | Status: `Alpha` | Docs: [wb.rtfd.io](https://wb.rtfd.io)

![WorkBench Logo](docs/source/_static/logo-black.png)

WorkBench is a hierarchical environment manager for \*nix shells. It sources
shell-code distributed across multiple levels of a folder hierarchy and
invokes environments with the combination. Code could thus be implemented
to operate at different scopes, allowing clear overrides at each folder depth
and easy overall maintenance while managing several hundred environments.
