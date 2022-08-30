# Zero Balance Inner Transactions

An example of a Smart Contract with a zero minimum balance, but will still send inner transactions.

You can either send payment transactions with messages, or an application call to a target process.

Run `./test.sh` to see a complete run-through.

You can use `python3 contracts.py` to regenerate the .teal files, but the `test.sh` file will do this for you. You can also edit the `test.sh` file to include an existing APP_ID and TARGET_ID if you've already deployed them once before to save you deploying multiple.
