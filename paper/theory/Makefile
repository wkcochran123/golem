# Makefile to compile LaTeX document

TEX = logic forward
PDF = $(TEX:%=%.pdf)

all: $(PDF)

%.pdf: %.tex golem.bib
	pdflatex $*
	bibtex $*
	pdflatex $*
	pdflatex $*


clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.synctex.gz

