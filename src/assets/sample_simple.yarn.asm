include "yarn.inc"

SECTION "sample_simple.Start", ROMX
sample_simple_Start::
  db TXT, "<CHARACTER>", Arnaud, "Sample tout con<END>"
  db TXT, "<CHARACTER>", Arnaud, "Vraiment le minimum quoi<END>"
  db RETURN
