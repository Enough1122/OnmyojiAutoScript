> AI code review — automated review for reference; please use your judgment.

Good UX addition: the manage-folders mode lists folders with a primary badge, enforces the last-folder guard via disabled+Tip (`minFolderRequired`), keeps the dialog open after adds so users can continue managing, and uses a plain Close footer instead of pretending there's something to save. The min-one-folder rule is enforced at the button level and the add path reuses the existing store action. Points:

1. i18n: the new keys ship as **English text inside every non-English locale file** (`ar.ts` gets "Manage folders", "No folders in this project.", etc.). That matches a fallback convention but produces mixed-language UI for Arabic/Japanese users until translated. If intentional, note it in the PR body so translators know these keys need filling. (nit)
2. The last-folder guard is client-side only; confirm the backend `removeProjectFolder` also refuses to remove the final folder (two racing clients or an API call could otherwise empty the list). One line in the store action's docstring stating where the invariant lives would help. (nit)
3. `removeManagedFolder` and the manage-mode branch of the submit handler duplicate the submitting-guard + try/catch/notify pattern from adjacent modes — a tiny shared runner would shrink the component. (nit)
4. Test updates cover the new mode's mocks; consider one render assertion that the primary badge shows on the primary folder, since that's user-visible state this dialog now owns. (nit)

No blocking issues found.
