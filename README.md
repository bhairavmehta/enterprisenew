# "The Box"

## Introduction

Yes, it is a real thing. Read [design docs](./thebox/docs/design/thebox_design.md) to understand what this is.

## Preparation

### Developing and building using Windows

In Windows please install a few Linux command line tool simulators:

1. Install [Chocolatey](https://chocolatey.org/)
2. Install following tools (make, sed, grep) in elevated command line:

   ```batch
   REM in elevated command line
   choco install make sed grep checksum awk jq gnuwin32-coreutils.portable
   ```
3. Disable Auto CRLF:
   ```
   git config --global core.autocrlf true
   ```

### Developing and building using Linux or WSL 2.0

No specific preparation steps required at the moment.

### Additional tips

- If you are editing the files on Windows box over Samba share (which maps file modes), you can consider to disable file mode check:
    ```
    git config core.fileMode false
    ```

## Building and Testing

For 'The Box' services and containers, dive into this [link](thebox/services/README.md)

## Contribute

Reach out to cosine_catalyst@microsoft.com to get more info how to check-in code and contribute.
