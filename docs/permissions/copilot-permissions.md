---
title: GitHub Copilot Custom Instructions
source_url: https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot
fetched_at: 2025-11-29T01:32:23Z
---

# Adding repository custom instructions for GitHub Copilot

Create repository custom instructions files that give Copilot additional context on how to understand your project and how to build, test and validate its changes.

## Tool navigation

## In this article

This version of this article is for using repository custom instructions on the GitHub website. Click the tabs above for information on using custom instructions in other environments. 

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



This version of this article is for using repository custom instructions and prompt files in VS Code. Click the tabs above for instructions on using custom instructions in other environments.

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



This version of this article is for using repository custom instructions in Visual Studio. Click the tabs above for instructions on using custom instructions in other environments.

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



This version of this article is for using repository custom instructions in JetBrains IDEs. Click the tabs above for instructions on using custom instructions in other environments.

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



This version of this article is for using repository custom instructions in Xcode. Click the tabs above for instructions on using custom instructions in other environments.

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



This version of this article is for using repository custom instructions with the GitHub Copilot CLI. Click the tabs above for instructions on using custom instructions in other environments.

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



Note

This feature is currently in public preview and is subject to change.

This version of this article is for using repository custom instructions in Eclipse. Click the tabs above for instructions on using custom instructions in other environments.

## Introduction

Repository custom instructions let you provide Copilot with repository-specific guidance and preferences. For more information, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization).

## Prerequisites for repository custom instructions

  * You must have a custom instructions file (see the instructions below).



  * Your personal choice of whether to use custom instructions must be set to enabled. This is enabled by default. See Enabling or disabling repository custom instructions later in this article.



  * Custom instructions must be enabled. This feature is enabled by default. See Enabling or disabling repository custom instructions later in this article.



  * The **Enable custom instructions...** option must be enabled in your settings. This is enabled by default. See Enabling or disabling repository custom instructions later in this article.



  * The latest version of the Copilot extension must be installed in your JetBrains IDE.



  * The latest version of the Copilot extension must be installed in Xcode.



  * The latest version of the Copilot extension must be installed in Eclipse.



## Creating custom instructions

JetBrains IDEs support a single `.github/copilot-instructions.md` custom instructions file stored in the repository, and a locally stored `global-copilot-instructions.md` file.

You can create the `.github/copilot-instructions.md` file in your repository using the Copilot settings page, or you can create the file manually.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.

### Using the settings page

  1. In your JetBrains IDE, click the **File** menu (Windows), or the name of the application in the menu bar (macOS), then click **Settings**.
  2. Under **Tools** , click **GitHub Copilot** , then click **Customizations**.
  3. Under "Copilot Instructions", click **Workspace** or **Global** to choose whether the custom instructions apply to the current workspace or all workspaces.



### Manually creating a workspace custom instructions file

  1. In the root of your repository, create a file named `.github/copilot-instructions.md`.

Create the `.github` directory if it does not already exist.

  2. Add natural language instructions to the file, in Markdown format.




Once saved, these instructions will apply to the current workspace in JetBrains IDEs that you open with Copilot enabled.

### Manually creating a global custom instructions file

To apply the same instructions across all workspaces in JetBrains IDEs, you can create a global custom instructions file on your local machine.

  1. Open your file explorer or terminal.

  2. Navigate to the appropriate location for your operating system:

     * **macOS** : `/Users/YOUR-USERNAME/.config/github-copilot/intellij/`
     * **Windows** : `C:\Users\YOUR-USERNAME\AppData\Local\github-copilot\intellij\`
  3. Create a file named `global-copilot-instructions.md` in that directory.

  4. Add your custom instructions in natural language, using Markdown format.




Once saved, these instructions will apply globally across all workspaces in JetBrains IDEs that you open with Copilot enabled.

Xcode supports a single `.github/copilot-instructions.md` custom instructions file stored in the repository.

You can create a custom instructions file in your repository via the Copilot settings page.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.

  1. Open the GitHub Copilot for Xcode application.
  2. At the top of the application window, under **Settings** , click **Advanced**.
  3. To the right of "Custom Instructions", click **Current Workspace** or **Global** to choose whether the custom instructions apply to the current workspace or all workspaces.



Eclipse supports two types of repository custom instructions: workspace and project custom instructions.

To create a workspace custom instructions file, you can use the Copilot settings page. To create a project custom instructions file, you can create the file manually in the project directory.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.

### Creating a workspace custom instructions file

  1. To open the Copilot Chat panel, click the Copilot icon () in the status bar at the bottom of Eclipse.
  2. From the menu, select "Edit preferences".
  3. In the left pane, expand GitHub Copilot and click **Custom Instructions**.
  4. Select **Enable workspace instructions**.
  5. In the "Workspace" section, under "Set custom instructions to guide Copilot's code suggestions in this workspace", add natural language instructions to the file, in Markdown format.



### Creating a project custom instructions file

  1. In the root of your project directory, create a file named `.github/copilot-instructions.md`.
  2. Add your custom instructions in natural language, using Markdown format.



Once saved, these instructions will apply to the current project in Eclipse that you open with Copilot enabled.

GitHub Copilot supports three types of repository custom instructions.

  * **Repository-wide custom instructions** , which apply to all requests made in the context of a repository.

These are specified in a `copilot-instructions.md` file in the `.github` directory of the repository. See Creating repository-wide custom instructions.

  * **Path-specific custom instructions** , which apply to requests made in the context of files that match a specified path.

These are specified in one or more `NAME.instructions.md` files within the `.github/instructions` directory in the repository. See Creating path-specific custom instructions.

If the path you specify matches a file that Copilot is working on, and a repository-wide custom instructions file also exists, then the instructions from both files are used. You should avoid potential conflicts between instructions as Copilot's choice between conflicting instructions is non-deterministic.

  * **Agent instructions** are used by AI agents.

You can create one or more `AGENTS.md` files, stored anywhere within the repository. When Copilot is working, the nearest `AGENTS.md` file in the directory tree will take precedence. For more information, see the [openai/agents.md repository](https://github.com/openai/agents.md).

Alternatively, you can use a single `CLAUDE.md` or `GEMINI.md` file stored in the root of the repository.




## Creating repository-wide custom instructions

  1. In the root of your repository, create a file named `.github/copilot-instructions.md`.

Create the `.github` directory if it does not already exist.

  2. Add natural language instructions to the file, in Markdown format.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




## Creating path-specific custom instructions

  1. Create the `.github/instructions` directory if it does not already exist.

  2. Create one or more `NAME.instructions.md` files, where `NAME` indicates the purpose of the instructions. The file name must end with `.instructions.md`.

  3. At the start of the file, create a frontmatter block containing the `applyTo` keyword. Use glob syntax to specify what files or directories the instructions apply to.

For example:
         
         ---
         applyTo: "app/models/**/*.rb"
         ---
         

You can specify multiple patterns by separating them with commas. For example, to apply the instructions to all TypeScript files in the repository, you could use the following frontmatter block:
         
         ---
         applyTo: "**/*.ts,**/*.tsx"
         ---
         

Glob examples:

     * `*` \- will all match all files in the current directory.
     * `**` or `**/*` \- will all match all files in all directories.
     * `*.py` \- will match all `.py` files in the current directory.
     * `**/*.py` \- will recursively match all `.py` files in all directories.
     * `src/*.py` \- will match all `.py` files in the `src` directory. For example, `src/foo.py` and `src/bar.py` but _not_ `src/foo/bar.py`.
     * `src/**/*.py` \- will recursively match all `.py` files in the `src` directory. For example, `src/foo.py`, `src/foo/bar.py`, and `src/foo/bar/baz.py`.
     * `**/subdir/**/*.py` \- will recursively match all `.py` files in any `subdir` directory at any depth. For example, `subdir/foo.py`, `subdir/nested/bar.py`, `parent/subdir/baz.py`, and `deep/parent/subdir/nested/qux.py`, but _not_ `foo.py` at a path that does not contain a `subdir` directory.
  4. Optionally, to prevent the file from being used by either Copilot coding agent or Copilot code review, add the `excludeAgent` keyword to the frontmatter block. Use either `"code-review"` or `"coding-agent"`.

For example, the following file will only be read by Copilot coding agent.
         
         ---
         applyTo: "**"
         excludeAgent: "code-review"
         ---
         

If the `excludeAgent` keyword is not included in the front matterblock, both Copilot code review and Copilot coding agent will use your instructions.

  5. Add your custom instructions in natural language, using Markdown format. Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




VS Code supports three types of repository custom instructions. For details of which GitHub Copilot features support these types of instructions, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization?tool=vscode#support-for-repository-custom-instructions-1).

  * **Repository-wide custom instructions** , which apply to all requests made in the context of a repository.

These are specified in a `copilot-instructions.md` file in the `.github` directory of the repository. See Creating repository-wide custom instructions.

  * **Path-specific custom instructions** , which apply to requests made in the context of files that match a specified path.

These are specified in one or more `NAME.instructions.md` files within the `.github/instructions` directory in the repository. See Creating path-specific custom instructions.

If the path you specify matches a file that Copilot is working on, and a repository-wide custom instructions file also exists, then the instructions from both files are used.

  * **Agent instructions** are used by AI agents.

You can create one or more `AGENTS.md` files, stored anywhere within the repository. When Copilot is working, the nearest `AGENTS.md` file in the directory tree will take precedence. For more information, see the [openai/agents.md repository](https://github.com/openai/agents.md).

Note

Support of `AGENTS.md` files outside of the workspace root is currently turned off by default. For details of how to enable this feature, see [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions#_use-an-agentsmd-file) in the VS Code documentation.




## Creating repository-wide custom instructions

  1. In the root of your repository, create a file named `.github/copilot-instructions.md`.

Create the `.github` directory if it does not already exist.

  2. Add natural language instructions to the file, in Markdown format.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




## Creating path-specific custom instructions

  1. Create the `.github/instructions` directory if it does not already exist.

  2. Create one or more `NAME.instructions.md` files, where `NAME` indicates the purpose of the instructions. The file name must end with `.instructions.md`.

  3. At the start of the file, create a frontmatter block containing the `applyTo` keyword. Use glob syntax to specify what files or directories the instructions apply to.

For example:
         
         ---
         applyTo: "app/models/**/*.rb"
         ---
         

You can specify multiple patterns by separating them with commas. For example, to apply the instructions to all TypeScript files in the repository, you could use the following frontmatter block:
         
         ---
         applyTo: "**/*.ts,**/*.tsx"
         ---
         

Glob examples:

     * `*` \- will all match all files in the current directory.
     * `**` or `**/*` \- will all match all files in all directories.
     * `*.py` \- will match all `.py` files in the current directory.
     * `**/*.py` \- will recursively match all `.py` files in all directories.
     * `src/*.py` \- will match all `.py` files in the `src` directory. For example, `src/foo.py` and `src/bar.py` but _not_ `src/foo/bar.py`.
     * `src/**/*.py` \- will recursively match all `.py` files in the `src` directory. For example, `src/foo.py`, `src/foo/bar.py`, and `src/foo/bar/baz.py`.
     * `**/subdir/**/*.py` \- will recursively match all `.py` files in any `subdir` directory at any depth. For example, `subdir/foo.py`, `subdir/nested/bar.py`, `parent/subdir/baz.py`, and `deep/parent/subdir/nested/qux.py`, but _not_ `foo.py` at a path that does not contain a `subdir` directory.
  4. Optionally, to prevent the file from being used by either Copilot coding agent or Copilot code review, add the `excludeAgent` keyword to the frontmatter block. Use either `"code-review"` or `"coding-agent"`.

For example, the following file will only be read by Copilot coding agent.
         
         ---
         applyTo: "**"
         excludeAgent: "code-review"
         ---
         

If the `excludeAgent` keyword is not included in the front matterblock, both Copilot code review and Copilot coding agent will use your instructions.

  5. Add your custom instructions in natural language, using Markdown format. Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




Visual Studio supports a single `.github/copilot-instructions.md` custom instructions file stored in the repository.

  1. In the root of your repository, create a file named `.github/copilot-instructions.md`.

Create the `.github` directory if it does not already exist.

  2. Add natural language instructions to the file, in Markdown format.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




Copilot on GitHub supports three types of repository custom instructions. For details of which GitHub Copilot features support these types of instructions, see [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization?tool=webui#support-for-repository-custom-instructions).

  * **Repository-wide custom instructions** apply to all requests made in the context of a repository.

These are specified in a `copilot-instructions.md` file in the `.github` directory of the repository. See Creating repository-wide custom instructions.

  * **Path-specific custom instructions** apply to requests made in the context of files that match a specified path.

These are specified in one or more `NAME.instructions.md` files within the `.github/instructions` directory in the repository. See Creating path-specific custom instructions.

If the path you specify matches a file that Copilot is working on, and a repository-wide custom instructions file also exists, then the instructions from both files are used.

  * **Agent instructions** are used by AI agents.

You can create one or more `AGENTS.md` files, stored anywhere within the repository. When Copilot is working, the nearest `AGENTS.md` file in the directory tree will take precedence over other agent instructions files. For more information, see the [openai/agents.md repository](https://github.com/openai/agents.md).

Alternatively, you can use a single `CLAUDE.md` or `GEMINI.md` file stored in the root of the repository.




## Creating repository-wide custom instructions

You can create your own custom instructions file from scratch. See Writing your own copilot-instructions.md file. Alternatively, you can ask Copilot coding agent to generate one for you.

### Asking Copilot coding agent to generate a `copilot-instructions.md` file

  1. Navigate to the agents tab at [github.com/copilot/agents](https://github.com/copilot/agents?ref_product=copilot&ref_type=engagement&ref_style=text).

You can also reach this page by clicking the ****button next to the search bar on any page on GitHub, then selecting**Agents** from the sidebar.

  2. Using the dropdown menu in the prompt field, select the repository you want Copilot to generate custom instructions for.

  3. Copy the following prompt, customizing it if needed:
         
         Your task is to "onboard" this repository to Copilot coding agent by adding a .github/copilot-instructions.md file in the repository that contains information describing how a coding agent seeing it for the first time can work most efficiently.
         
         You will do this task only one time per repository and doing a good job can SIGNIFICANTLY improve the quality of the agent's work, so take your time, think carefully, and search thoroughly before writing the instructions.
         
         <Goals>
         - Reduce the likelihood of a coding agent pull request getting rejected by the user due to
         generating code that fails the continuous integration build, fails a validation pipeline, or
         having misbehavior.
         - Minimize bash command and build failures.
         - Allow the agent to complete its task more quickly by minimizing the need for exploration using grep, find, str_replace_editor, and code search tools.
         </Goals>
         
         <Limitations>
         - Instructions must be no longer than 2 pages.
         - Instructions must not be task specific.
         </Limitations>
         
         <WhatToAdd>
         
         Add the following high level details about the codebase to reduce the amount of searching the agent has to do to understand the codebase each time:
         <HighLevelDetails>
         
         - A summary of what the repository does.
         - High level repository information, such as the size of the repo, the type of the project, the languages, frameworks, or target runtimes in use.
         </HighLevelDetails>
         
         Add information about how to build and validate changes so the agent does not need to search and find it each time.
         <BuildInstructions>
         
         - For each of bootstrap, build, test, run, lint, and any other scripted step, document the sequence of steps to take to run it successfully as well as the versions of any runtime or build tools used.
         - Each command should be validated by running it to ensure that it works correctly as well as any preconditions and postconditions.
         - Try cleaning the repo and environment and running commands in different orders and document errors and and misbehavior observed as well as any steps used to mitigate the problem.
         - Run the tests and document the order of steps required to run the tests.
         - Make a change to the codebase. Document any unexpected build issues as well as the workarounds.
         - Document environment setup steps that seem optional but that you have validated are actually required.
         - Document the time required for commands that failed due to timing out.
         - When you find a sequence of commands that work for a particular purpose, document them in detail.
         - Use language to indicate when something should always be done. For example: "always run npm install before building".
         - Record any validation steps from documentation.
         </BuildInstructions>
         
         List key facts about the layout and architecture of the codebase to help the agent find where to make changes with minimal searching.
         <ProjectLayout>
         
         - A description of the major architectural elements of the project, including the relative paths to the main project files, the location
         of configuration files for linting, compilation, testing, and preferences.
         - A description of the checks run prior to check in, including any GitHub workflows, continuous integration builds, or other validation pipelines.
         - Document the steps so that the agent can replicate these itself.
         - Any explicit validation steps that the agent can consider to have further confidence in its changes.
         - Dependencies that aren't obvious from the layout or file structure.
         - Finally, fill in any remaining space with detailed lists of the following, in order of priority: the list of files in the repo root, the
         contents of the README, the contents of any key source files, the list of files in the next level down of directories, giving priority to the more structurally important and snippets of code from key source files, such as the one containing the main method.
         </ProjectLayout>
         </WhatToAdd>
         
         <StepsToFollow>
         - Perform a comprehensive inventory of the codebase. Search for and view:
         - README.md, CONTRIBUTING.md, and all other documentation files.
         - Search the codebase for build steps and indications of workarounds like 'HACK', 'TODO', etc.
         - All scripts, particularly those pertaining to build and repo or environment setup.
         - All build and actions pipelines.
         - All project files.
         - All configuration and linting files.
         - For each file:
         - think: are the contents or the existence of the file information that the coding agent will need to implement, build, test, validate, or demo a code change?
         - If yes:
            - Document the command or information in detail.
            - Explicitly indicate which commands work and which do not and the order in which commands should be run.
            - Document any errors encountered as well as the steps taken to workaround them.
         - Document any other steps or information that the agent can use to reduce time spent exploring or trying and failing to run bash commands.
         - Finally, explicitly instruct the agent to trust the instructions and only perform a search if the information in the instructions is incomplete or found to be in error.
         </StepsToFollow>
            - Document any errors encountered as well as the steps taken to work-around them.
         
         

  4. Click **Send now** or press `Return`.




Copilot will start a new session, which will appear in the list below the prompt box. Copilot will create a draft pull request, write your custom instructions, push them to the branch, then add you as a reviewer when it has finished, triggering a notification.

### Writing your own `copilot-instructions.md` file

  1. In the root of your repository, create a file named `.github/copilot-instructions.md`.

Create the `.github` directory if it does not already exist.

  2. Add natural language instructions to the file, in Markdown format.

Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




Tip

The first time you create a pull request in a given repository with Copilot coding agent, Copilot will leave a comment with a link to automatically generate custom instructions for the repository.

## Creating path-specific custom instructions

Note

Currently, on GitHub.com, path-specific custom instructions are only supported for Copilot coding agent and Copilot code review.

  1. Create the `.github/instructions` directory if it does not already exist.

  2. Create one or more `NAME.instructions.md` files, where `NAME` indicates the purpose of the instructions. The file name must end with `.instructions.md`.

  3. At the start of the file, create a frontmatter block containing the `applyTo` keyword. Use glob syntax to specify what files or directories the instructions apply to.

For example:
         
         ---
         applyTo: "app/models/**/*.rb"
         ---
         

You can specify multiple patterns by separating them with commas. For example, to apply the instructions to all TypeScript files in the repository, you could use the following frontmatter block:
         
         ---
         applyTo: "**/*.ts,**/*.tsx"
         ---
         

Glob examples:

     * `*` \- will all match all files in the current directory.
     * `**` or `**/*` \- will all match all files in all directories.
     * `*.py` \- will match all `.py` files in the current directory.
     * `**/*.py` \- will recursively match all `.py` files in all directories.
     * `src/*.py` \- will match all `.py` files in the `src` directory. For example, `src/foo.py` and `src/bar.py` but _not_ `src/foo/bar.py`.
     * `src/**/*.py` \- will recursively match all `.py` files in the `src` directory. For example, `src/foo.py`, `src/foo/bar.py`, and `src/foo/bar/baz.py`.
     * `**/subdir/**/*.py` \- will recursively match all `.py` files in any `subdir` directory at any depth. For example, `subdir/foo.py`, `subdir/nested/bar.py`, `parent/subdir/baz.py`, and `deep/parent/subdir/nested/qux.py`, but _not_ `foo.py` at a path that does not contain a `subdir` directory.
  4. Optionally, to prevent the file from being used by either Copilot coding agent or Copilot code review, add the `excludeAgent` keyword to the frontmatter block. Use either `"code-review"` or `"coding-agent"`.

For example, the following file will only be read by Copilot coding agent.
         
         ---
         applyTo: "**"
         excludeAgent: "code-review"
         ---
         

If the `excludeAgent` keyword is not included in the front matterblock, both Copilot code review and Copilot coding agent will use your instructions.

  5. Add your custom instructions in natural language, using Markdown format. Whitespace between instructions is ignored, so the instructions can be written as a single paragraph, each on a new line, or separated by blank lines for legibility.




Did you successfully add a custom instructions file to your repository?

[Yes](https://docs.github.io/success-test/yes.html) [No](https://docs.github.io/success-test/no.html)

## Repository custom instructions in use

The instructions in the file(s) are available for use by Copilot as soon as you save the file(s). The complete set of instructions will be automatically added to requests that you submit to Copilot in the context of that repository. For example, they are added to the prompt you submit to Copilot Chat.

In Copilot Chat ([github.com/copilot](https://github.com/copilot)), you can start a conversation that uses repository custom instructions by adding, as an attachment, the repository that contains the instructions file.

Whenever repository custom instructions are used by Copilot Chat, the instructions file is added as a reference for the response that's generated. To find out whether repository custom instructions were used, expand the list of references at the top of a chat response in the Chat panel and check whether the `.github/copilot-instructions.md` file is listed.

You can click the reference to open the file.

Note

  * Multiple types of custom instructions can apply to a request sent to Copilot. Personal instructions take the highest priority, followed by repository instructions, with organization instructions prioritized last. However, all sets of relevant instructions are still combined and provided to Copilot.
  * Whenever possible, you should avoid providing conflicting sets of instructions. If you are concerned about response quality, you can also choose to temporarily disable repository instructions. See [Adding repository custom instructions for GitHub Copilot](/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot?tool=webui#enabling-or-disabling-repository-custom-instructions).



Custom instructions are not visible in the Chat view or inline chat, but you can verify that they are being used by Copilot by looking at the References list of a response in the Chat view. If custom instructions were added to the prompt that was sent to the model, the `.github/copilot-instructions.md` file is listed as a reference. You can click the reference to open the file.

Custom instructions are not visible in the Chat view or inline chat, but you can verify that they are being used by Copilot by looking at the References list of a response in the Chat view. If custom instructions were added to the prompt that was sent to the model, the `.github/copilot-instructions.md` file is listed as a reference. You can click the reference to open the file.

Custom instructions are not visible in the Chat view or inline chat, but you can verify that they are being used by Copilot by looking at the References list of a response in the Chat view. If custom instructions were added to the prompt that was sent to the model, the `.github/copilot-instructions.md` file is listed as a reference. You can click the reference to open the file.

Custom instructions are not visible in the Chat view or inline chat, but you can verify that they are being used by Copilot by looking at the References list of a response in the Chat view. If custom instructions were added to the prompt that was sent to the model, the `.github/copilot-instructions.md` file is listed as a reference. You can click the reference to open the file.

## Further reading

  * [Custom instructions](/en/copilot/tutorials/customization-library/custom-instructions)—a curated collection of examples



## Enabling or disabling custom instructions for Copilot code review

Custom instructions are enabled for Copilot code review by default but you can disable, or re-enable, them in the repository settings on GitHub.com. This applies to Copilot's use of custom instructions for all code reviews it performs in this repository.

  1. On GitHub, navigate to the main page of the repository.

  2. Under your repository name, click **Settings**. If you cannot see the "Settings" tab, select the ****dropdown menu, then click**Settings**.

  3. In the "Code & automation" section of the sidebar, click **Copilot** , then **Code review**.

  4. Toggle the “Use custom instructions when reviewing pull requests” option on or off.




## Further reading

  * [Custom instructions](/en/copilot/tutorials/customization-library/custom-instructions)—a curated collection of examples



## Enabling or disabling repository custom instructions

You can choose whether or not you want Copilot to use repository-based custom instructions.

### Enabling or disabling custom instructions for Copilot Chat

Custom instructions are enabled for Copilot Chat by default but you can disable, or re-enable, them at any time. This applies to your own use of Copilot Chat and does not affect other users.

  1. Open the Setting editor by using the keyboard shortcut `Command`+`,` (Mac) / `Ctrl`+`,` (Linux/Windows).
  2. Type `instruction file` in the search box.
  3. Select or clear the checkbox under **Code Generation: Use Instruction Files**.



### Enabling or disabling custom instructions for Copilot code review

Custom instructions are enabled for Copilot code review by default but you can disable, or re-enable, them in the repository settings on GitHub.com. This applies to Copilot's use of custom instructions for all code reviews it performs in this repository.

  1. On GitHub, navigate to the main page of the repository.

  2. Under your repository name, click **Settings**. If you cannot see the "Settings" tab, select the ****dropdown menu, then click**Settings**.

  3. In the "Code & automation" section of the sidebar, click **Copilot** , then **Code review**.

  4. Toggle the “Use custom instructions when reviewing pull requests” option on or off.




## Enabling or disabling repository custom instructions

You can choose whether or not you want Copilot to use repository-based custom instructions.

### Enabling or disabling custom instructions for Copilot Chat

Custom instructions are enabled for Copilot Chat by default but you can disable, or re-enable, them at any time. This applies to your own use of Copilot Chat and does not affect other users.

  1. In the Visual Studio menu bar, under **Tools** , click **Options**.

  2. In the "Options" dialog, type `custom instructions` in the search box, then click **Copilot**.

  3. Select or clear the checkbox for **Enable custom instructions to be loaded from .github/copilot-instructions.md files and added to requests**.




### Enabling or disabling custom instructions for Copilot code review

Custom instructions are enabled for Copilot code review by default but you can disable, or re-enable, them in the repository settings on GitHub.com. This applies to Copilot's use of custom instructions for all code reviews it performs in this repository.

  1. On GitHub, navigate to the main page of the repository.

  2. Under your repository name, click **Settings**. If you cannot see the "Settings" tab, select the ****dropdown menu, then click**Settings**.

  3. In the "Code & automation" section of the sidebar, click **Copilot** , then **Code review**.

  4. Toggle the “Use custom instructions when reviewing pull requests” option on or off.




## Further reading

  * [Custom instructions](/en/copilot/tutorials/customization-library/custom-instructions)—a curated collection of examples



## Enabling and using prompt files

Note

  * Copilot prompt files are in public preview and subject to change. Prompt files are only available in VS Code and JetBrains IDEs. See [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization?tool=vscode#about-prompt-files).
  * For community-contributed examples of prompt files for specific languages and scenarios, see the [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-copilot/blob/main/docs/README.prompts.md) repository.



Prompt files let you build and share reusable prompt instructions with additional context. A prompt file is a Markdown file, stored in your workspace, that mimics the existing format of writing prompts in Copilot Chat (for example, `Rewrite #file:x.ts`). You can have multiple prompt files in your workspace, each of which defines a prompt for a different purpose.

### Enabling prompt files

To enable prompt files, configure the workspace settings.

  1. Open the command palette by pressing `Ctrl`+`Shift`+`P` (Windows/Linux) / `Command`+`Shift`+`P` (Mac).
  2. Type "Open Workspace Settings (JSON)" and select the option that's displayed.
  3. In the `settings.json` file, add `"chat.promptFiles": true` to enable the `.github/prompts` folder as the location for prompt files. This folder will be created if it does not already exist.



### Creating prompt files

  1. Open the command palette by pressing `Ctrl`+`Shift`+`P` (Windows/Linux) / `Command`+`Shift`+`P` (Mac).

  2. Type "prompt" and select **Chat: Create Prompt**.

  3. Enter a name for the prompt file, excluding the `.prompt.md` file name extension. The name can contain alphanumeric characters and spaces and should describe the purpose of the prompt information the file will contain.

  4. Write the prompt instructions, using Markdown formatting.

You can reference other files in the workspace by using Markdown links—for example, `[index](../../web/index.ts)`—or by using the `#file:../../web/index.ts` syntax. Paths are relative to the prompt file. Referencing other files allows you to provide additional context, such as API specifications or product documentation.




### Using prompt files

  1. At the bottom of the Copilot Chat view, click the **Attach context** icon ().

  2. In the dropdown menu, click **Prompt...** and choose the prompt file you want to use.

  3. Optionally, attach additional files, including prompt files, to provide more context.

  4. Optionally, type additional information in the chat prompt box.

Whether you need to do this or not depends on the contents of the prompt you are using.

  5. Submit the chat prompt.




For more information about prompt files, see [Use prompt files in Visual Studio Code](https://code.visualstudio.com/docs/copilot/customization/prompt-files) in the Visual Studio Code documentation.

## Further reading

  * [Customization library](/en/copilot/tutorials/customization-library)—a curated collection of examples



## Using prompt files

Note

  * Copilot prompt files are in public preview and subject to change. Prompt files are only available in VS Code and JetBrains IDEs. See [About customizing GitHub Copilot responses](/en/copilot/concepts/prompting/response-customization?tool=vscode#about-prompt-files).
  * For community-contributed examples of prompt files for specific languages and scenarios, see the [Awesome GitHub Copilot Customizations](https://github.com/github/awesome-copilot/blob/main/docs/README.prompts.md) repository.



Prompt files let you build and share reusable prompt instructions with additional context. A prompt file is a Markdown file, stored in your workspace, that mimics the existing format of writing prompts in Copilot Chat (for example, `Rewrite #file:x.ts`). You can have multiple prompt files in your workspace, each of which defines a prompt for a different purpose.

When writing prompt instructions, you can reference other files in the workspace by using Markdown links—for example, `[index](../../web/index.ts)`—or by using the `#file:../../web/index.ts` syntax. Paths are relative to the prompt file. Referencing other files allows you to provide additional context, such as API specifications or product documentation.

Once prompt files are saved, their instructions will apply to the current workspace in JetBrains IDEs that you open with Copilot enabled.

### Creating prompt files using the command line

  1. Create the `.github/prompts` directory if it doesn't already exist in your workspace. This directory will be the location for your prompt files.
  2. Create a prompt file in the `.github/prompts` directory. The prompt file name can contain alphanumeric characters and spaces and should describe the purpose of the prompt information the file will contain. The file name must end with the `.prompt.md` file name extension, for example `TESTPROMPT.prompt.md`.
  3. Write the prompt instructions using Markdown formatting, and save the file.



### Creating prompt files using the settings page

  1. In your JetBrains IDE, click the **File** menu (Windows), or the name of the application in the menu bar (macOS), then click **Settings**.
  2. Under **Tools** , under **GitHub Copilot** , click **Edit Settings**.
  3. Under "Settings Categories", click **Customizations**.
  4. Under "Prompt Files", click **Workspace** , to create a prompt file in your workspace.
  5. Enter a name for the prompt file, excluding the `.prompt.md` file name extension. The prompt file name can contain alphanumeric characters and spaces and should describe the purpose of the prompt information the file will contain.
  6. Click **Ok** to save the prompt file name.
  7. Write the prompt instructions using Markdown formatting, and save the file.



### Using prompt files

  1. In the chat input box, type `/` followed by the name of the prompt file. For example, `/TESTPROMPT`.

  2. Optionally, attach additional files, to provide more context.

  3. Optionally, type additional information in the chat prompt box.

Whether you need to do this or not depends on the contents of the prompt you are using.

  4. Submit the chat prompt.




## Further reading

  * [Customization library](/en/copilot/tutorials/customization-library)



## Further reading

  * [Custom instructions](/en/copilot/tutorials/customization-library/custom-instructions)—a curated collection of examples



## Further reading

  * [Using custom instructions to unlock the power of Copilot code review](/en/copilot/tutorials/use-custom-instructions)
  * [Custom instructions](/en/copilot/tutorials/customization-library/custom-instructions)—a curated collection of examples