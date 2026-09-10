# D1 locked appearance candidate

This is a reference-only candidate, not an installed or approved asset pack.

Open `previews/rastalr_D1_locked_appearance_review.png` for appearance review.
`candidate/*_native.png` contains the actual RGBA artwork.
The main file is standalone/terminal; the repeat file is the nonterminal view.
`*_source_8x.png` is an exact nearest-neighbor working-scale copy.

Previews are assembled from these candidate files, not independently generated images.
Their backgrounds and text labels do not exist in the candidate PNGs.

`sources/` holds unchanged reference inputs, not extra candidates.
`reports/` holds the local checks and candidate specification.
`tools/build_d1_appearance.py` reproduces the files using Pillow and numpy.
No font binaries are included.

No approved production files or repository records were changed.
