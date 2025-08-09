import logging
import os
import shutil

from .. import model, strparse, view
from ..fzf import fzf_choose
from ..puid import inferPUID
from ..rc import VON_BASE_PATH, VON_DEFAULT_AUTHOR, VON_POST_OUTPUT_DIR

parser = view.Parser(prog="po", description="Prepares a LaTeX file to send to Po-Shen!")
parser.add_argument("keys", nargs="*", help="The keys of the problem to propose.")
parser.add_argument("-t", "--title", default=None, help="Title of the LaTeX document.")
parser.add_argument(
    "-s", "--subtitle", default=None, help="Subtitle of the LaTeX document."
)
parser.add_argument(
    "--author", default=VON_DEFAULT_AUTHOR, help="Author of the LaTeX document."
)
parser.add_argument("--date", default=r"\today", help="Date of the LaTeX document.")
parser.add_argument(
    "-k",
    "--sourced",
    action="store_true",
    help="Include the source.",
)
parser.add_argument(
    "--tex",
    action="store_true",
    help="Supply only the TeX source, rather than compiling to PDF.",
)
parser.add_argument(
    "-f",
    "--filename",
    default=None,
    help="Filename for the file to produce (defaults to po.tex).",
)

LATEX_PREAMBLE = r"""\usepackage{amsmath,amssymb,amsthm}
\usepackage[fontset=founder]{ctex}
\usepackage[minimal]{yhmath}
\usepackage{derivative}

\PassOptionsToPackage{svgnames,dvipsnames}{xcolor}
\usepackage{thmtools}
\usepackage[framemethod=TikZ]{mdframed}
\usepackage{listings}

\mdfdefinestyle{mdbluebox}{%
    roundcorner = 10pt,
    linewidth=1pt,
    skipabove=12pt,
    innerbottommargin=9pt,
    skipbelow=2pt,
    linecolor=blue,
    nobreak=true,
    backgroundcolor=TealBlue!5,
}
\declaretheoremstyle[
    headfont=\sffamily\bfseries\color{MidnightBlue},
    mdframed={style=mdbluebox},
    headpunct={\\[3pt]},
    postheadspace={0pt}
]{thmbluebox}

\mdfdefinestyle{mdredbox}{%
    linewidth=0.5pt,
    skipabove=12pt,
    frametitleaboveskip=5pt,
    frametitlebelowskip=0pt,
    skipbelow=2pt,
    frametitlefont=\bfseries,
    innertopmargin=4pt,
    innerbottommargin=8pt,
    nobreak=true,
    backgroundcolor=Salmon!5,
    linecolor=RawSienna,
}
\declaretheoremstyle[
    headfont=\bfseries\color{RawSienna},
    mdframed={style=mdredbox},
    headpunct={\\[3pt]},
    postheadspace={0pt},
]{thmredbox}

\mdfdefinestyle{mdgreenbox}{%
    skipabove=8pt,
    linewidth=2pt,
    rightline=false,
    leftline=true,
    topline=false,
    bottomline=false,
    linecolor=ForestGreen,
    backgroundcolor=ForestGreen!5,
}
\declaretheoremstyle[
    headfont=\bfseries\sffamily\color{ForestGreen!70!black},
    bodyfont=\normalfont,
    spaceabove=2pt,
    spacebelow=1pt,
    mdframed={style=mdgreenbox},
    headpunct={ --- },
]{thmgreenbox}

\mdfdefinestyle{mdblackbox}{%
    skipabove=8pt,
    linewidth=3pt,
    rightline=false,
    leftline=true,
    topline=false,
    bottomline=false,
    linecolor=black,
    backgroundcolor=RedViolet!5!gray!5,
}
\declaretheoremstyle[
    headfont=\bfseries,
    bodyfont=\normalfont\small,
    spaceabove=0pt,
    spacebelow=0pt,
    mdframed={style=mdblackbox}
]{thmblackbox}

\declaretheorem[style=thmbluebox,name=定理]{theorem}
\declaretheorem[style=thmbluebox,name=引理,sibling=theorem]{lemma}
\declaretheorem[style=thmbluebox,name=命题,sibling=theorem]{proposition}
\declaretheorem[style=thmbluebox,name=推论,sibling=theorem]{corollary}
\declaretheorem[style=thmbluebox,name=定理,numbered=no]{theorem*}
\declaretheorem[style=thmbluebox,name=引理,numbered=no]{lemma*}
\declaretheorem[style=thmbluebox,name=命题,numbered=no]{proposition*}
\declaretheorem[style=thmbluebox,name=推论,numbered=no]{corollary*}

\declaretheorem[style=thmgreenbox,name=结论,sibling=theorem]{claim}
\declaretheorem[style=thmgreenbox,name=结论,numbered=no]{claim*}
\declaretheorem[style=thmredbox,name=例子,sibling=theorem]{example}
\declaretheorem[style=thmredbox,name=例子,numbered=no]{example*}
\declaretheorem[style=thmblackbox,name=备注,sibling=theorem]{remark}
\declaretheorem[style=thmblackbox,name=备注,numbered=no]{remark*}

\theoremstyle{definition}
\newtheorem{conjecture}[theorem]{猜想}
\newtheorem{definition}[theorem]{定义}
\newtheorem{fact}[theorem]{事实}
\newtheorem{ques}[theorem]{问题}
\newtheorem{exercise}[theorem]{练习}
\newtheorem{problem}[theorem]{题目}

\newtheorem*{conjecture*}{猜想}
\newtheorem*{definition*}{定义}
\newtheorem*{fact*}{事实}
\newtheorem*{ques*}{问题}
\newtheorem*{exercise*}{练习}
\newtheorem*{problem*}{题目}

\usepackage{mathtools}
\usepackage{hyperref}
\usepackage[shortlabels]{enumitem}
\usepackage{multirow}
\usepackage{ellipsis}
\usepackage{cancel}

\usepackage{epic} % diagrams
\usepackage{tikz-cd} % diagrams
\usepackage{asymptote} % more diagrams
\begin{asydef}
defaultpen(fontsize(10pt));
size(8cm); // set a reasonable default
usepackage("amsmath");
usepackage("amssymb");
settings.tex="pdflatex";
settings.outformat="pdf";
// Replacement for olympiad+cse5 which is not standard
import geometry;
// recalibrate fill and filldraw for conics
void filldraw(picture pic = currentpicture, conic g, pen fillpen=defaultpen, pen drawpen=defaultpen)
    { filldraw(pic, (path) g, fillpen, drawpen); }
void fill(picture pic = currentpicture, conic g, pen p=defaultpen)
    { filldraw(pic, (path) g, p); }
// some geometry
pair foot(pair P, pair A, pair B) { return foot(triangle(A,B,P).VC); }
pair orthocenter(pair A, pair B, pair C) { return orthocentercenter(A,B,C); }
pair centroid(pair A, pair B, pair C) { return (A+B+C)/3; }
// cse5 abbreviations
path CP(pair P, pair A) { return circle(P, abs(A-P)); }
path CR(pair P, real r) { return circle(P, r); }
pair IP(path p, path q) { return intersectionpoints(p,q)[0]; }
pair OP(path p, path q) { return intersectionpoints(p,q)[1]; }
path Line(pair A, pair B, real a=0.6, real b=a) { return (a*(A-B)+A)--(b*(B-A)+B); }
// cse5 more useful functions
picture CC() {
    picture p=rotate(0)*currentpicture;
    currentpicture.erase();
    return p;
}
pair MP(Label s, pair A, pair B = plain.S, pen p = defaultpen) {
    Label L = s;
    L.s = "$"+s.s+"$";
    label(s, A, B, p);
    return A;
}
pair Drawing(Label s = "", pair A, pair B = plain.S, pen p = defaultpen) {
    dot(MP(s, A, B, p), p);
    return A;
}
path Drawing(path g, pen p = defaultpen, arrowbar ar = None) {
    draw(g, p, ar);
    return g;
}
\end{asydef}

\usepackage{tkz-euclide}
\usepackage{tkz-elements}
\tikzset {
  dots/.style={shape=circle, color=#1!30!black, fill=#1!70!black, minimum size=2},
  dots/.default=black,
  lines/.style={line width=0.8pt, color=#1},
  lines/.default=black,
  helplines/.style={line width=0.8pt, color=#1, densely dashed},
  helplines/.default=green!70!black
}

\catcode`。=\active
\def。{．}
\newcommand{\lt}{<}
\newcommand{\gt}{>}
\let\le=\leqslant
\let\ge=\geqslant
\let\leq=\leqslant
\let\gep=\geqslant
\mathcode`≤=\leqslant
\mathcode`≥=\geqslant
\catcode`≠=\active
\def≠{\ne}
\mathcode`△=\triangle
\mathcode`⊿=\triangle
\def\Rt{\text{Rt}}
\newcommand{\degree}{\ensuremath{^\circ}}
\catcode`°=\active
\def°{\degree}
\mathcode`∠=\angle
\mathcode`⊥=\perp
\mathcode`∵=\because
\mathcode`∴=\therefore
\mathcode`⊙=\odot
\mathcode`×=\times
\mathcode`÷=\div
\mathcode`∞=\infty
\mathcode`∈=\in
\mathcode`∩=\cap
\mathcode`∪=\cup
\mathcode`Γ=\Gamma
\mathcode`Δ=\Delta
\mathcode`Θ=\Theta
\mathcode`Λ=\Lambda
\mathcode`Ξ=\Xi
\mathcode`Π=\Pi
\mathcode`Σ=\Sigma
\mathcode`Φ=\Phi
\mathcode`Ψ=\Psi
\mathcode`Ω=\Omega
\mathcode`α=\alpha
\mathcode`β=\beta
\mathcode`γ=\gamma
\mathcode`δ=\delta
\mathcode`ε=\epsilon
\mathcode`ζ=\zeta
\mathcode`η=\eta
\mathcode`θ=\theta
\mathcode`ι=\iota
\mathcode`κ=\kappa
\mathcode`λ=\lambda
\mathcode`μ=\mu
\mathcode`ν=\nu
\mathcode`ξ=\xi
\mathcode`π=\pi
\mathcode`ρ=\rho
\mathcode`σ=\sigma
\mathcode`τ=\tau
\mathcode`υ=\upsilon
\mathcode`φ=\phi
\mathcode`χ=\chi
\mathcode`ψ=\psi
\mathcode`ω=\omega
\DeclarePairedDelimiter\abs\lvert\rvert

\usepackage[headsepline]{scrlayer-scrpage}
\addtolength{\textheight}{3.14cm}
\setlength{\footskip}{0.5in}
\setlength{\headsep}{10pt}
\lehead{\normalfont\footnotesize\textbf{AUTHOR}}
\lohead{\normalfont\footnotesize\textbf{AUTHOR}}
\rehead{\normalfont\footnotesize\textbf{TITLE}}
\rohead{\normalfont\footnotesize\textbf{TITLE}}
\pagestyle{scrheadings}

\providecommand{\arc}[1]{\wideparen{#1}}
\newcommand{\hrulebar}{
\par\hspace{\fill}\rule{0.95\linewidth}{.7pt}\hspace{\fill}
\par\nointerlineskip \vspace{\baselineskip}}

\addtokomafont{paragraph}{\color{orange!35!black}\P\ }"""


def main(self: object, argv: list[str]):
    opts = parser.process(argv)

    keys = opts.keys
    if len(keys) == 0:
        keys = [fzf_choose()]

    # Better default title:
    if opts.title is not None:
        title = opts.title
    elif len(keys) == 1:
        entry = model.getEntryByKey(keys[0])
        if entry is not None:
            title = entry.source
        else:
            title = "解答"
    else:
        title = "解答"

    s = r"\documentclass[11pt]{scrartcl}" + "\n"
    s += LATEX_PREAMBLE.replace("AUTHOR", opts.author).replace("TITLE", title)
    s += r"\begin{document}" + "\n"
    s += r"\title{" + title + "}" + "\n"
    if opts.subtitle is not None:
        s += r"\subtitle{" + opts.subtitle + "}" + "\n"
    s += r"\author{" + opts.author + "}" + "\n"
    s += r"\date{" + opts.date + "}" + "\n"
    s += r"\maketitle" + "\n"
    s += "\n"
    for key in keys:
        entry = model.getEntryByKey(key)
        if entry is None:
            logging.error(key + " not found")
        elif entry.secret and not opts.brave:
            logging.error(f"Problem `{entry.source}` not shown without --brave")
            return
        else:
            problem = entry.full
            s += r"\begin{problem}" if len(keys) > 1 else r"\begin{problem*}"
            if opts.sourced:
                s += "[" + entry.source + "]"
            s += "\n"
            s += strparse.demacro(problem.bodies[0]) + "\n"
            s += r"\end{problem}" if len(keys) > 1 else r"\end{problem*}"
            if entry.url:
                s += r"\noindent\emph{链接}: \url{" + entry.url + "}" + "\n"
            if len(problem.bodies) > 1:
                s += "\n" + r"\hrulebar" + "\n\n"
                s += strparse.demacro(problem.bodies[1]) + "\n"
            s += r"\pagebreak" + "\n\n"
    s += r"\end{document}"
    if opts.tex:
        view.out(s)
    else:
        if opts.filename is not None:
            fname = opts.filename
        elif len(keys) == 1:
            fname = view.file_escape(title)
        else:
            fname = "po"
        if not os.path.exists(VON_POST_OUTPUT_DIR):
            os.mkdir(VON_POST_OUTPUT_DIR)
        filepath = os.path.join(VON_POST_OUTPUT_DIR, f"{fname}.tex")
        with open(filepath, "w") as f:
            print(s, file=f)
        tikz_path = os.path.join(VON_BASE_PATH, "tikz")
        if os.path.exists(tikz_path):
            dest_path = os.path.join(VON_POST_OUTPUT_DIR, "tikz")
            if not os.path.exists(dest_path):
                os.mkdir(dest_path)
            puids = [
                inferPUID(entry.source)
                for key in keys
                if (entry := model.getEntryByKey(key)) is not None
            ]
            for file in os.listdir(tikz_path):
                for puid in puids:
                    if file.startswith(puid) and file.endswith("tkz"):
                        shutil.copy(os.path.join(tikz_path, file), dest_path)
        os.chdir(VON_POST_OUTPUT_DIR)
        os.system(
            "latexmk -pdflua -e '$pdf_previewer=q[start \"/mnt/c/Program Files/SumatraPDF/SumatraPDF.exe\" %%O %%S]' -pv %s"
            % filepath
        )
