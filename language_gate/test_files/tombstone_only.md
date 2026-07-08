# Internal Engineering Note

The Motor kicks off every loop on schedule. We used to be model-agnostic but moved to a fixed router.
Reconciler resolves any state conflicts after the Motor fires.
