# Error handling policy (BAD example - should trip R3)

If the schema check fails, the pipeline responds: not allowed.

If a task requests an out-of-scope capability, the response is: denied.

Any ambiguous case returns: manual review required.
