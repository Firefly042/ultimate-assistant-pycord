# Contributing
This is a very small and casual project. Do your best to follow the established format if adding anything. The code is linted with pylint to the best of abilities. All contributions are welcome, even if it's a simple typo correction or clarification! Feature requests can be made in Issues with an appropriate tag, or brought to the [support server](https://discord.gg/VZYKBptWFJ).


## Getting Credit
If you are not comfortable with github, simply ask the developer (@Firefly#7113) for credit via the support server or DM! Be ready to provide proof of your work.

If you are comfortable with github, you may submit a pull request with the 'credit request' label. The template will have a space to provide proof of your work. The steps to do this are:

1. Fork this repository. You will need a github account. The default name is fine.
2. While not explicitly required for this case, it is good practice to make a new **branch** (on your fork) with an informative name.
3. On the new branch, add your credits to `CONTRIBUTORS.md`, following the given format.
4. Commit/Save your changes.
5. Submit a **pull request** to the **main** branch of this repository (Firefly042) following the provided template. Be sure to use the 'credit request' label.


# For Translators
All translators can request access to [this crowdin project](https://crowdin.com/project/ultimate-assistant). Joining the support server is highly recommended to get the fastest response to your request or any question (you'll also get a fancy role).

**Guidelines**
* When referring to boolean options, 'True' and 'False' are not translated at the time of writing. (See `common > visible-desc` for an example).
* Values inside `{}` should be left untranslated as they refer to parameters in the code.
* Do *not* directly edit any localization files in the repository. They are overwritten by the crowdin build.


# For Writers
If you would like to propose a change to names, descriptions, or responses, either create an **Issue** or mention it in the support server. Pull requests with edited strings will not be accepted at this time due to localization procedures. 


# For Coders
You are likely familiar enough with Github's fork and branch workflow. If you're not familiar with discord bots, follow the Hosting instructions on the wiki's Home page.

1. Submit an Issue (bug or feature request) if there isn't one yet. 
2. Lint your changes to the best of ability and follow the established format as closely as possible.
3. Submit a pull request to the **test** branch using the code template. Be sure to include your contribution credit if it's not there.


# Bug Reports and Feature Requests
Something not working as expected? Do you have an ideas for new or existing features? Submit an **Issue** with the appropriate template!
