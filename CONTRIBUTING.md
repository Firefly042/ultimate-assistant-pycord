# Contributing
This is a very small and casual project. Do your best to follow the established format if adding anything. The code is linted with pylint to the best of abilities. All contributions are welcome, even if it's a simple typo correction or clarification! Feature requests can be made in Issues with an appropriate tag, or brought to the [support server](https://discord.gg/VZYKBptWFJ).

## For Translators
If you are comfortable using command line git, you probably already know what you're doing.

If not, using [Github Desktop](https://github.com/firstcontributions/first-contributions/blob/master/gui-tool-tutorials/github-desktop-tutorial.md) is the recommended method. No code knowledge is required.

If you want to work entirely in-browser, the above reference is still helpful. All contributors can refer to the steps below.

1. Create a Github account.
2. **Fork** this repository. You may keep the default name.
3. In your fork, create a new **branch** with an informative name.
4. Following the existing format, add in your translations to `localization.py`. Guidelines are detailed below. If you are revising a line that has been changed (indicated by a `# REVISED` comment), please add a comment at the end of your line indicating `# UPDATED`.
5. If it's your first time, add your credits to `CONTRIBUTORS.md`.
6. **Commit** your changes and **push** them to your branch. 
7. After saving, go to **Actions**. There should be a pylint notice. Click the notice > build > Analysing code with pylint. It should notify you of any formatting errors.
8. When you are finished, submit a **pull request** to the **localization** branch using the localization template.

**Guidelines**
* Be sure to use valid locale abbreviations as listed [here](https://discord.com/developers/docs/reference#locales).
* When adding a new locale, please maintain alphabetical order (according to English).
* If you are comfortable using the linter, please do so. Otherwise, be very careful with spaces and quotation use. 
* When referring to boolean options, 'True' and 'False' are not translated at the time of writing. (See `strings["common"]["visible-desc"]` for an example).
* Try not to leave a command group partially localized. Discord seems to be finicky with such things and won't display unlocalized commands for autocompletion.

## For Writers
If you would like to propose a change to names, descriptions, or responses, the process is quite different. You must:

1. Same as above.
2. If none exists, submit an **Issue** using the **string rewording** template. If you are proposing more than a typo or grammar fix, bringing the discussion to the support server is also recommended. 
3. Once there is approval for the change, **fork** this repository and make a **branch** to work on.
4. In your branch, you must replace the strings in `localization.py` *and* any files defining default values. If you are significantly adjusting the phrasing, you must also add a comment `# REVISED` on the line in `localization.py` so translaters are aware of the change.
5. Same as above
6. Same as above.
7. Same as above.
8. Submit a **pull request** to the **main** branch using the string rewording template.

## For Coders
You are likely familiar enough with forking and branching. If not, follow the linked guide in the Translator section. If you're not familiar with discord bots, follow the Hosting instructions on the wiki's Home page.

1. Submit an Issue (bug or feature request) if there isn't one yet. 
2. Lint your changes to the best of ability and follow the established format as closely as possible.
3. Submit a pull request to the **test** branch using the code template.
