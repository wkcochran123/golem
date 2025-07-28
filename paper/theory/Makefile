# Makefile to compile LaTeX document

TEX = logic
PDF = $(TEX).pdf

all: $(PDF)

$(PDF): $(TEX).tex $(TEX).bib
	pdflatex $(TEX).tex 
	bibtex $(TEX)       
	pdflatex $(TEX).tex 
	pdflatex $(TEX).tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot *.synctex.gz

