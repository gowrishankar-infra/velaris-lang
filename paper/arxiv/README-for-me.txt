VELARIS PAPER ON ARXIV - WHAT TO PASTE, AND WHAT IS IN THE PACKAGE

This file is for you, not for arXiv. It is NOT inside
..\arxiv-submission.zip: arXiv asks that a submission hold nothing that
is not needed to build the paper, and anything uploaded becomes part of
the public source.

THE PACKAGE
  ..\arxiv-submission.zip holds two files, at the top level of the zip:
    velaris.tex   the paper, converted from velaris.md by pandoc 3.11
    velaris.bbl   the bibliography, made here by BibTeX with apalike.bst
  On the form, choose the processor "pdflatex" and TeX Live 2025 (the
  default). arXiv uses a .bbl when one is uploaded whose name matches
  the .tex, so it will not run BibTeX; no .bib is uploaded.

  The zip is not committed (.gitignore); in a fresh clone, zip these two
  files again, at the top level.

BEFORE YOU UPLOAD
  arXiv requires authors to report significant use of generative AI in
  the paper itself (info.arxiv.org/help/moderation/index.html). The
  paper's "Use of generative AI" section, between the Conclusion and
  Reproducibility, is that statement; velaris.md and velaris.tex carry
  the same text.

  Still to do: find one endorser who knows your work (a personal
  endorsement is required for a first submission since 2026-01-21), and
  read the PDF arXiv builds before you confirm.

FORM FIELDS - paste as they are

Title:
Velaris: effects in signatures, budgets at run time, and a baseline for a repository's capability surface

Authors:
Gowri Shankar Palakurthi
  (arXiv wants given names first so that it indexes Palakurthi as the
  family name. The PDF's byline, from velaris.md, reads "Palakurthi
  Gowri Shankar"; arXiv does not require the two to match.)

Abstract (1729 characters, one line, plain ASCII; the limit is 1920;
no character needed replacing - the abstract has none outside ASCII):
Code written by language models is increasingly run by people who have not read it. Velaris is a small programming language for that situation. A function's signature declares which of seven effects it may perform, and the compiler checks the declaration across the whole call graph. A runtime refuses any operation outside a budget the operator writes - before the operation happens, and in a way the program cannot catch. Contracts are checked by the Z3 prover where it can settle them, and at run time where it cannot. A repository can commit a baseline of the capability surface its programs need, and a check fails any change that needs more. The central claim is about that surface. Suppose a repository's Velaris programs are held to a committed baseline by a required check. If a change makes a program need an effect, path, host, module or operation count the baseline does not grant, the check fails. It goes on failing at every later commit at which the program still compiles and still needs it, until a person edits the baseline. The claim is not about which function an effect is attributed to: a function renamed in the change that gives it an effect its program already had escapes the function-level rule. On a benchmark of 63 programs, 56 with one defect and 7 correct, each written in Velaris, in JavaScript for Deno and in Python, Velaris caught 54 of the 56 defects, 42 of them before running; Deno caught 32 and Python 28; none of the three flagged a correct program. One of Velaris's two misses is a logic error with no contract; the other no tool should catch. The capability format is published separately, under CC0, with a conformance corpus of 444 cases that an implementation in any language can run.

Comments:
11 pages, 1 figure, 2 tables. Code: https://github.com/gowrishankar-infra/velaris-lang ; format and conformance corpus: https://github.com/gowrishankar-infra/velaris-spec

Primary category:
cs.PL (Programming Languages)

Cross-list:
cs.CR (Cryptography and Security)
  Why: the contribution is a language design and its implementation -
  effects in signatures, the semantics of a budget, contracts, a
  compiler - which is cs.PL's "language features ... compilers". The
  motivation and related work are security, hence the cs.CR
  cross-list; but the paper says the budget is not a security boundary
  and has no attack evaluation, so cs.CR would be the wrong primary.

ACM-class:
D.3.3; D.4.6; D.2.4
  From the 1998 ACM Computing Classification System, which arXiv's
  field uses: D.3.3 Language Constructs and Features; D.4.6 Security
  and Protection; D.2.4 Software/Program Verification (it lists
  correctness proofs and programming by contract). Checked against
  ACM's 1998 list as archived at web.archive.org.

MSC-class, Report-no, Journal-ref, DOI:
leave empty

Licence:
CC BY 4.0 (Creative Commons Attribution)
  Why: the format is CC0 and the implementation MIT; CC BY keeps the
  paper as open as both while keeping attribution, which CC0 would
  give up, and arXiv encourages a liberal licence. The choice cannot be
  changed for this version. Exception: if you mean to send the paper to
  a journal or conference that requires an exclusive copyright
  transfer, read its preprint policy first; the arXiv non-exclusive
  licence commits you to least.

HOW THE PACKAGE WAS MADE AND CHECKED (2026-09-11)
  1. pandoc 3.11:
       pandoc velaris.md --standalone --natbib -V biblio-style=apalike
         --shift-heading-level-by=-1 -V geometry:margin=1in -M date=
         -o velaris.tex
     --shift-heading-level-by=-1 makes the paper's "##" headings
     sections; -M date= leaves out the "Draft ... not submitted" date
     line (arXiv also advises against \today in \date); pandoc turns the
     closing "References" heading into the bibliography's title.
  2. TeX Live 2025 (pdfTeX 1.40.28, BibTeX 0.99d), with the .bib beside
     it: pdflatex, bibtex, pdflatex, pdflatex. That run made velaris.bbl.
  3. As arXiv builds it: velaris.tex and velaris.bbl alone in an empty
     folder, pdflatex twice, no bibtex. Result: 11 pages; no undefined
     citation or reference; no overfull or underfull box; no error. One
     warning, harmless: "Package caption Warning: Unused
     \captionsetup[table]", from pandoc's template.
  4. All 15 cited keys have an entry in velaris.bbl, and every entry is
     cited. Both files are pure ASCII: the names with o-slash and c-caron
     are written as TeX accents ({\o}, {\v{c}}).
  5. Figure 1 is text in a verbatim block: it prints whole on page 2,
     columns aligned, 61 characters at its widest against about 89 that
     fit at 1-inch margins.

  Rebuilt the same way after the "Use of generative AI" section was
  added: the .tex differed from the earlier one by that section alone,
  the .bbl came out byte for byte the same, and step 3 still gave 11
  pages with nothing new in the log. The section prints on page 9.

  Not the same as arXiv's system: arXiv's TeX Live 2025 is the state of
  2025-08-03; this build used the final TeX Live 2025 (March 2026). The
  packages the paper loads are standard ones. If arXiv's form suggests
  a processor other than pdflatex, change it to pdflatex.
