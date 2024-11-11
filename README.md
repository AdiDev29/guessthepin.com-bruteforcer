# guessthepin.com-bruteforcer
An easy to use script to rapidly bruteforce guessthepin.com through multithreaded processes.

An adaptation of [bobeci6835's](https://replit.com/@bobeci6835) script from replit. Changes are as follows:

- Easier to use and gives user more flexibility with number of threads to adjust for network conditions.

- Added a feature where program collects all skipped pin tries due to errors, and lets the user re-try them safely at the end with a lower speed.

- Replaced printing all combinations tried with a status bar showing percentage of all posibilities tried along with the "Last skipped pin". This improves speed by eliminating unnecessary print statements.
